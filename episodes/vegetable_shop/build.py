#!/usr/bin/env python3
"""Vegetable Shop: locally synthesize timed Kokoro dialogue and render aligned 2D plates.

No eSpeak fallback: if neural TTS/production expression plates are unavailable,
stop with an actionable error instead of publishing an inferior video.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import math
import subprocess
import sys
from pathlib import Path

DURATION = 120.0
FPS = 30
SIZE = (1280, 720)
SR = 48000
VOICE = {'Max': 'am_puck', 'Mia': 'af_heart'}
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ASSETS = HERE / 'assets'
OUT = HERE / 'output'


def load_script(path=HERE / 'script.json'):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, list) or not data:
        raise ValueError('script.json must contain nonempty list')
    for i, row in enumerate(data, 1):
        if not isinstance(row, dict) or row.get('speaker') not in VOICE:
            raise ValueError(f'Line {i} must identify Max or Mia')
        if not isinstance(row.get('text'), str) or not row['text'].strip():
            raise ValueError(f'Line {i} needs text')
    return data


def phone_to_pose(phone):
    """Conservative viseme groups; no mouth movement for silences or stress marks."""
    if not phone or phone.strip(' ˈˌː.,!?;:') == '':
        return 'rest'
    if phone[0].lower() in 'mbp':
        return 'rest'
    if phone[0].lower() in 'oɔʊuwɒ':
        return 'oh'
    if phone[0].lower() in 'aɑæʌɐ':
        return 'ah'
    if phone[0].lower() in 'eiɪɛɜɚə':
        return 'ah'
    return 'soft'


def plan_timing(durations, *, target=DURATION, minimum_gap=.22, maximum_gap=.78):
    """Plan timing without resampling/destroying prosody; fail if dialogue won't fit."""
    if not durations or any(not math.isfinite(d) or d <= 0 for d in durations):
        raise ValueError('All speech durations must be positive and finite')
    total = sum(durations)
    count = len(durations) - 1
    room = target - total - 1.2  # minimum intro/outro holds
    if room < count * minimum_gap - 1e-5:
        raise ValueError('Dialogue too long: shorten lines or increase Kokoro speaking speed')
    gap = max(minimum_gap, min(maximum_gap, room / max(1, count)))
    if target - total - count * gap > 8.0:
        raise ValueError('Too little dialogue for 120 seconds; expand the script')
    slack = target - total - count * gap
    lead = min(1.8, max(.6, slack / 2))
    cursor = lead
    starts = []
    for d in durations:
        starts.append(cursor)
        cursor += d + gap
    if starts[-1] + durations[-1] > target - .35:
        raise ValueError('Last line exceeds duration limit')
    return starts, gap


def timecode(value):
    millis = int(round(value * 1000))
    return f'{millis // 3600000:02}:{millis // 60000 % 60:02}:{millis // 1000 % 60:02},{millis % 1000:03}'


def write_srt(rows, path):
    blocks = []
    for index, row in enumerate(rows, 1):
        blocks.append(f"{index}\n{timecode(row['start'])} --> {timecode(row['end'])}\n{row['speaker']}: {row['text']}")
    Path(path).write_text('\n\n'.join(blocks) + '\n', encoding='utf-8')


def synthesize(script, *, speed=1.0, model_dir=REPO / 'models'):
    try:
        import onnxruntime as ort
        from kokoro_onnx import Kokoro
    except ImportError as err:
        raise RuntimeError('Neural speech unavailable; install root requirements.txt, not eSpeak') from err
    model_file = model_dir / 'kokoro-v1.0.fp16.onnx'
    voice_file = model_dir / 'voices-v1.0.bin'
    if not model_file.is_file() or not voice_file.is_file():
        raise FileNotFoundError('Kokoro weights missing: run python setup_audio_models.py')
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    session = ort.InferenceSession(str(model_file), options, providers=['CPUExecutionProvider'])
    engine = Kokoro.from_session(session, str(voice_file))
    if not engine.has_timings:
        raise RuntimeError('Kokoro model must expose phoneme-duration output')
    clips = []
    for i, row in enumerate(script):
        audio, native_sr, phones = engine.create_timed(
            row['text'], voice=VOICE[row['speaker']], lang='en-us', speed=speed,
            sentence_pause=.10, clause_pause=.05)
        clips.append((audio, native_sr, [dataclasses.asdict(p) for p in phones]))
        print(f'Neural speech {i + 1}/{len(script)}', flush=True)
    return clips


def make_audio(*, script_file=HERE / 'script.json', music=None):
    import numpy as np
    import soundfile as sf
    sys.path.insert(0, str(REPO))
    from improve_audio import polish_voice, resample, master

    script = load_script(script_file)
    clips = synthesize(script, speed=1.0)
    def lengths(clips):
        return [len(samples) / rate for samples, rate, _ in clips]
    try:
        starts, gap = plan_timing(lengths(clips))
    except ValueError:
        # A small neural voice-rate change is acceptable; post-hoc time compression is not.
        first = lengths(clips)
        wanted = DURATION - 1.2 - .24 * (len(first) - 1)
        adjusted = min(1.16, max(1.02, sum(first) / wanted * 1.02))
        clips = synthesize(script, speed=adjusted)
        starts, gap = plan_timing(lengths(clips))
    target_samples = int(DURATION * SR)
    speech = np.zeros((target_samples, 2), dtype=np.float64)
    timeline = []
    for row, (samples, rate, phones), start in zip(script, clips, starts):
        cleaned, _ = polish_voice(samples, rate, target_lufs=-19.0)
        cleaned = resample(cleaned, rate, SR)
        offset = round(start * SR)
        finish = offset + len(cleaned)
        if finish > target_samples:
            raise ValueError('Dialogue audio extends beyond video')
        pan = .035 if row['speaker'] == 'Mia' else -.035
        speech[offset:finish, 0] += cleaned * (1 - pan)
        speech[offset:finish, 1] += cleaned * (1 + pan)
        ph = [{'phone': p['phoneme'], 'start': start + p['start'],
               'end': start + p['end']} for p in phones]
        timeline.append({**row, 'start': start, 'end': finish / SR, 'phones': ph})
    backing = None
    if music:
        music_signal, music_rate = sf.read(music, dtype='float64')
        backing = resample(music_signal, music_rate, SR)
    result, report = master(speech, SR, backing, target_lufs=-16.5)
    OUT.mkdir(parents=True, exist_ok=True)
    sf.write(OUT / 'vegetable_shop.wav', result, SR, subtype='PCM_24')
    (OUT / 'timeline.json').write_text(json.dumps(timeline, indent=2, ensure_ascii=False), encoding='utf-8')
    (OUT / 'audio_quality.json').write_text(json.dumps({**report, 'engine': 'Kokoro timed ONNX',
        'music_enabled': bool(music), 'dialogue_lines': len(script), 'gap_seconds': gap}, indent=2))
    write_srt(timeline, OUT / 'vegetable_shop.srt')
    print('Written 120-second neural dialogue, timing, and subtitles')
    return timeline


def require_expression_plates():
    paths = [ASSETS / name for name in ('Scene_Base.png', 'Scene_Ah_Blink.png', 'Scene_Oh.png')]
    missing = [p.name for p in paths if not p.is_file()]
    if missing:
        raise FileNotFoundError('Aligned expression plates required; refusing crude mouth overlays: '
                                + ', '.join(missing) + '. See README.md')
    from PIL import Image
    plates = [Image.open(p).convert('RGB') for p in paths]
    if len({im.size for im in plates}) != 1:
        raise ValueError('Expression plates must have IDENTICAL pixel dimensions')
    return plates


def active_pose(rows, character, at):
    for row in rows:
        if row['speaker'] != character or not row['start'] <= at < row['end']:
            continue
        for ph in row.get('phones', []):
            if ph['start'] <= at < ph['end']:
                return phone_to_pose(ph['phone'])
        return 'rest'
    return 'rest'


def render_video():
    """Use spatially-aligned mouth/eye image patches, not painted oval overlays."""
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import soundfile as sf
    base, ah, oh = require_expression_plates()
    timeline_path = OUT / 'timeline.json'
    audio_path = OUT / 'vegetable_shop.wav'
    if not timeline_path.exists() or not audio_path.exists():
        raise FileNotFoundError('Generate neural audio first: python build.py --audio')
    rows = json.loads(timeline_path.read_text(encoding='utf-8'))
    audio_info = sf.info(audio_path)
    if abs(audio_info.duration - DURATION) > .001:
        raise ValueError('Audio duration must be exactly 120 seconds')
    ow, ohh = base.size
    # Coordinates are fractional and MUST be calibrated to each aligned plate set.
    rig_file = ASSETS / 'rig.json'
    rig = json.loads(rig_file.read_text(encoding='utf-8')) if rig_file.is_file() else None
    if not rig:
        raise FileNotFoundError('assets/rig.json required; never guess facial coordinates')
    for who in VOICE:
        if who not in rig or 'mouth' not in rig[who] or 'eyes' not in rig[who]:
            raise ValueError(f'Missing calibrated facial ROIs for {who}')
    def box(coords):
        if len(coords) != 4 or any(not 0 <= n <= 1 for n in coords):
            raise ValueError('Each ROI must contain 4 normalized 0-1 numbers')
        x0,y0,x1,y1 = coords
        if x1 <= x0 or y1 <= y0:
            raise ValueError('ROI must have positive area')
        return tuple(map(int, (x0*ow,y0*ohh,x1*ow,y1*ohh)))
    def patch(image, reference, rectangle, strength):
        if strength <= 0:
            return
        b = box(rectangle)
        w,h = b[2]-b[0], b[3]-b[1]
        mask = Image.new('L', (w,h), 0)
        inset = max(2, min(w,h)//7)
        ImageDraw.Draw(mask).rounded_rectangle((inset,inset,w-inset,h-inset), radius=max(2,inset), fill=round(strength*255))
        mask = mask.filter(ImageFilter.GaussianBlur(max(1,inset//2)))
        image.paste(reference.crop(b), b[:2], mask)
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    font = ImageFont.truetype(font_path if Path(font_path).exists() else 'DejaVuSans.ttf', 29)
    sub_font = ImageFont.truetype(font_path if Path(font_path).exists() else 'DejaVuSans.ttf', 24)
    OUT.mkdir(parents=True, exist_ok=True)
    outfile = OUT / 'Vegetable_Shop_Neural_2min.mp4'
    cmd = ['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
           '-s',f'{SIZE[0]}x{SIZE[1]}','-r',str(FPS),'-i','-', '-i',str(audio_path),
           '-i',str(OUT / 'vegetable_shop.srt'), '-map','0:v','-map','1:a','-map','2:s',
           '-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',
           '-c:a','aac','-b:a','224k','-c:s','mov_text','-t','120',
           '-movflags','+faststart',str(outfile)]
    proc = subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(round(DURATION*FPS)):
            t = i / FPS
            image = base.copy()
            for who in VOICE:
                pose = active_pose(rows, who, t)
                if pose != 'rest':
                    patch(image, oh if pose == 'oh' else ah, rig[who]['mouth'], .88 if pose=='soft' else 1)
                # Blink from aligned eye keyframes, never erased/repainted pupils.
                offset = 1.6 if who == 'Mia' else 2.5
                blink = ((t - offset + .06) % 4.7) < .12
                if blink:
                    for eye in rig[who]['eyes']:
                        patch(image, ah, eye, 1)
            # Very slow camera push; no frame-duplication (actual 30 fps animation).
            joke_bounce = sum(.004 * math.exp(-abs(t-r['end'])*7) * math.sin(18*(t-r['end'])) for r in rows if r.get('joke') and abs(t-r['end']) < .4)
            drift = 1.0 + .007 * math.sin(t*.26) + joke_bounce
            if drift != 1:
                cx,cy = ow/2,ohh/2
                region = (cx-ow/(2*drift),cy-ohh/(2*drift),cx+ow/(2*drift),cy+ohh/(2*drift))
                image = image.resize(SIZE, Image.Resampling.LANCZOS,box=region)
            else:
                image = image.resize(SIZE,Image.Resampling.LANCZOS)
            draw = ImageDraw.Draw(image)
            row = next((x for x in rows if x['start']-.05 <= t < x['end']+.05), None)
            if row:
                draw.rounded_rectangle((48,602,1232,690),radius=18,fill=(14,30,28))
                draw.text((66,612),row['speaker'].upper(),font=sub_font,fill=(255,212,117) if row['speaker']=='Max' else (144,244,217))
                message = row['text']
                if draw.textlength(message, font=sub_font) > 1140:
                    words = message.split()
                    first = ''
                    while words and draw.textlength((first + ' ' + words[0]).strip(), font=sub_font) < 1110:
                        first = (first + ' ' + words.pop(0)).strip()
                    draw.text((66,641),first,font=sub_font,fill='white')
                    if words: draw.text((66,667),' '.join(words),font=sub_font,fill='white')
                else:
                    draw.text((66,648),message,font=sub_font,fill='white')
                if row.get('joke') and row['end']-.35 <= t < row['end']+.22:
                    draw.text((1040,48),'HA HA!',font=font,fill=(255,222,111),stroke_width=2,stroke_fill=(49,48,31))
            proc.stdin.write(image.tobytes())
            if i % 300 == 0: print(f'Rendered {i}/{round(DURATION*FPS)}',flush=True)
    except (BrokenPipeError,OSError):
        proc.kill()
        raise RuntimeError('FFmpeg encoder terminated early')
    finally:
        if proc.stdin and not proc.stdin.closed: proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError('FFmpeg failed to encode final video')
    print('Created',outfile)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-script', action='store_true', help='Offline checks; no model download')
    parser.add_argument('--audio', action='store_true', help='Kokoro neural voices and exact timing')
    parser.add_argument('--render', action='store_true', help='Render aligned 2D expression plates')
    parser.add_argument('--music', type=Path, help='Optional licensed music; off by default')
    args = parser.parse_args(argv)
    rows = load_script()
    if args.check_script or not (args.audio or args.render):
        print(f'Script valid: {len(rows)} lines, characters Max & Mia, target 120s')
    if args.audio: make_audio(music=args.music)
    if args.render: render_video()


if __name__ == '__main__':
    main()