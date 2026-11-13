#!/usr/bin/env python3
"""Probe media, sample real alpha, and verify character exports are silent.

Uses only Python standard library plus ffprobe and ffmpeg on PATH.
No neural model, private inputs, external API, or plugin required.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


def media_info(path):
    p = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries',
         'format=duration,size:stream=index,codec_name,codec_type,width,height,pix_fmt,avg_frame_rate,nb_frames:stream_tags=alpha_mode',
         '-of', 'json', str(path)], check=True, capture_output=True, text=True)
    return json.loads(p.stdout)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def alpha_sample(path, video, time_seconds):
    width, height = video['width'], video['height']
    command = ['ffmpeg', '-hide_banner', '-loglevel', 'error']
    if video.get('codec_name') == 'vp9':
        command += ['-c:v', 'libvpx-vp9']  # Required to decode VP9 alpha on some builds
    command += ['-ss', str(round(time_seconds, 6)), '-i', str(path),
                '-map', '0:v:0', '-frames:v', '1', '-pix_fmt', 'rgba', '-f', 'rawvideo', '-']
    run = subprocess.run(command, capture_output=True)
    if run.returncode:
        raise RuntimeError(run.stderr.decode('utf8', 'replace'))
    if len(run.stdout) != width * height * 4:
        raise RuntimeError('Unexpected RGBA decoded frame length')
    channel = run.stdout[3::4]
    total = len(channel)
    return {'time': round(time_seconds, 3), 'minimum': min(channel), 'maximum': max(channel),
            'transparent_fraction': round(sum(v < 255 for v in channel) / total, 6),
            'opaque_fraction': round(sum(v == 255 for v in channel) / total, 6)}


def check_file(path, include_hash=True):
    info = media_info(path)
    videos = [s for s in info['streams'] if s.get('codec_type') == 'video']
    audios = [s for s in info['streams'] if s.get('codec_type') == 'audio']
    if not videos:
        raise ValueError('No video stream found')
    video = videos[0]
    duration = float(info['format']['duration'])
    fps = video.get('avg_frame_rate', '0/1')
    fps_num, fps_den = map(int, fps.split('/'))
    period = fps_den / fps_num if fps_num else 0.05
    times = sorted({0.0, round(duration / 2, 3), max(0, round(duration - 2 * period, 3))})
    samples = [alpha_sample(path, video, t) for t in times]
    is_alpha = all(s['minimum'] < 255 and s['maximum'] > 0 for s in samples)
    report = {
        'filename': path.name, 'bytes': path.stat().st_size,
        'duration_seconds': duration, 'video_codec': video['codec_name'],
        'width': video['width'], 'height': video['height'], 'frame_rate': fps,
        'pixel_format': video.get('pix_fmt'), 'alpha_tag': video.get('tags', {}).get('ALPHA_MODE'),
        'audio_streams': len(audios), 'alpha_samples': samples,
        'verified_real_alpha_on_sampled_frames': is_alpha,
        'verified_silent': len(audios) == 0,
        'passes_sampled_export_checks': is_alpha and len(audios) == 0,
        'limitations': 'Samples only three decoded frames; this does not prove absence of visual artifacts or preservation of original movement.'
    }
    if include_hash:
        report['sha256'] = sha256(path)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('paths', nargs='+', type=Path)
    ap.add_argument('--json', type=Path, dest='json_output', help='Write JSON report to this path')
    ap.add_argument('--strict', action='store_true', help='Exit nonzero if any alpha/silence check fails')
    args = ap.parse_args(argv)
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        ap.error('Install FFmpeg and ffprobe on PATH')
    results = []
    for path in args.paths:
        if not path.is_file():
            ap.error(f'File not found: {path}')
        results.append(check_file(path))
    result = {'files': results}
    output = json.dumps(result, indent=2) + '\n'
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(output, encoding='utf8')
    print(output)
    if args.strict and not all(x['passes_sampled_export_checks'] for x in results):
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())