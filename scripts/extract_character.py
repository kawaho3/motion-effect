#!/usr/bin/env python3
"""Free local baseline: strip background and sound from an existing character video.

Requires FFmpeg/ffprobe and Pillow+rembg (pip install -r requirements.txt).
First invocation downloads a free segmentation model, then runs locally.
Important: per-frame segmentation is NOT temporal video matting; preserve
input timing only for constant-frame-rate clips in this baseline.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path


def run(command):
    subprocess.run(command, check=True)


def probe_rate(source):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
         'stream=avg_frame_rate,r_frame_rate', '-of', 'json', str(source)],
        capture_output=True, text=True, check=True)
    streams = json.loads(result.stdout).get('streams', [])
    if not streams:
        raise ValueError('Input has no video stream')
    for name in ('avg_frame_rate', 'r_frame_rate'):
        rate = streams[0].get(name, '0/0')
        try:
            if Fraction(rate) > 0:
                return rate
        except (ValueError, ZeroDivisionError):
            pass
    raise ValueError('Cannot determine input frame rate')


def encode_command(pattern, output, fps, crf=24, mov_codec='prores'):
    command = ['ffmpeg', '-hide_banner', '-loglevel', 'warning', '-y',
               '-framerate', fps, '-i', str(pattern), '-an']
    if output.suffix.lower() == '.webm':
        command += ['-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p',
                    '-auto-alt-ref', '0', '-b:v', '0', '-crf', str(crf)]
    elif output.suffix.lower() == '.mov':
        if mov_codec == 'prores':
            command += ['-c:v', 'prores_ks', '-profile:v', '4',
                        '-pix_fmt', 'yuva444p10le', '-alpha_bits', '16']
        elif mov_codec == 'qtrle':
            command += ['-c:v', 'qtrle', '-pix_fmt', 'argb']
        else:
            raise ValueError('MOV codec must be prores or qtrle')
    else:
        raise ValueError('Output must be .webm or .mov (standard MP4 is not an alpha output)')
    return command + [str(output)]


def process_frames(input_dir, output_dir, model):
    try:
        from PIL import Image
        from rembg import new_session, remove
    except ImportError as exc:
        raise RuntimeError('Install dependencies: python -m pip install -r requirements.txt') from exc
    session = new_session(model_name=model)
    frames = sorted(input_dir.glob('frame_*.png'))
    if not frames:
        raise RuntimeError('FFmpeg produced no video frames')
    for i, source in enumerate(frames):
        with Image.open(source) as rgb:
            output = remove(rgb.convert('RGB'), session=session)
            if not isinstance(output, Image.Image):
                raise TypeError('rembg did not return a PIL image')
            output.convert('RGBA').save(output_dir / source.name)
        if i % 30 == 0 or i + 1 == len(frames):
            print(f'Processed {i + 1}/{len(frames)} frames', flush=True)
    return len(frames)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Input video')
    parser.add_argument('output', type=Path, help='Silent video with actual alpha (.webm/.mov)')
    parser.add_argument('--model', default='u2net', help='rembg model (default u2net)')
    parser.add_argument('--crf', type=int, default=24, help='VP9 output quality: 0 best, 63 worst')
    parser.add_argument('--mov-codec', choices=('prores', 'qtrle'), default='prores',
                        help='Alpha MOV codec: prores (default) or qtrle')
    parser.add_argument('--keep-frames', type=Path, help='Optional folder to keep RGBA frames')
    args = parser.parse_args(argv)
    if not args.input.is_file():
        parser.error(f'Input not found: {args.input}')
    if args.output.suffix.lower() not in ('.mov', '.webm'):
        parser.error('Output must end with .mov or .webm')
    if args.input.resolve() == args.output.resolve():
        parser.error('Input and output must be different files')
    if not 0 <= args.crf <= 63:
        parser.error('--crf must be in [0,63]')
    for binary in ('ffmpeg', 'ffprobe'):
        if not shutil.which(binary):
            parser.error(f'{binary} not found on PATH')
    if args.keep_frames and args.keep_frames.exists() and list(args.keep_frames.glob('frame_*.png')):
        parser.error('--keep-frames directory must not contain existing frame_*.png files')
    fps = probe_rate(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='background_extractor_') as temporary:
        root = Path(temporary)
        input_frames = root / 'rgb'
        output_frames = args.keep_frames or root / 'rgba'
        input_frames.mkdir()
        output_frames.mkdir(parents=True, exist_ok=True)
        run(['ffmpeg', '-hide_banner', '-loglevel', 'warning', '-y', '-i',
             str(args.input), '-map', '0:v:0', '-vsync', '0',
             str(input_frames / 'frame_%06d.png')])
        count = process_frames(input_frames, output_frames, args.model)
        run(encode_command(output_frames / 'frame_%06d.png', args.output,
                           fps, args.crf, args.mov_codec))
        print(f'Wrote {args.output} ({count} frames, silent)')
    return 0


if __name__ == '__main__':
    sys.exit(main())