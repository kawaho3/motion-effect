#!/usr/bin/env python3
"""Generate a copyright-free moving 2D test character and reference alpha clip.

Requires Pillow (pip install -r requirements.txt) and FFmpeg on PATH.
Creates only geometric drawings; no external characters, speech or videos.
"""
import argparse
import math
import subprocess
from pathlib import Path


def make_demo(output_dir, frames=48, width=360, height=480, fps=24):
    from PIL import Image, ImageDraw
    output_dir = Path(output_dir)
    frames_dir = output_dir / 'rgb_frames'
    alpha_dir = output_dir / 'ground_truth_rgba'
    frames_dir.mkdir(parents=True, exist_ok=True)
    alpha_dir.mkdir(parents=True, exist_ok=True)
    for i in range(frames):
        time = i / fps
        canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        d = ImageDraw.Draw(canvas)
        x = width // 2 + int(45 * math.sin(time * 2.8))
        y = height // 2 + int(15 * math.cos(time * 3.2))
        # Simple geometric character with clearly moving arms and head.
        d.ellipse((x - 43, y - 142, x + 43, y - 56), fill=(240, 173, 100, 255))
        d.ellipse((x - 22, y - 116, x - 12, y - 105), fill=(45, 29, 29, 255))
        d.ellipse((x + 12, y - 116, x + 22, y - 105), fill=(45, 29, 29, 255))
        d.arc((x - 15, y - 111, x + 15, y - 82), 0, 180, fill=(90, 32, 29, 255), width=3)
        d.rounded_rectangle((x - 35, y - 50, x + 35, y + 77), radius=18, fill=(33, 127, 169, 255))
        swing = int(22 * math.sin(time * 8))
        d.line((x - 30, y - 28, x - 58 - swing, y + 29), fill=(240, 173, 100, 255), width=16)
        d.line((x + 30, y - 28, x + 58 + swing, y + 29), fill=(240, 173, 100, 255), width=16)
        d.line((x - 16, y + 70, x - 21 + swing // 4, y + 151), fill=(58, 57, 87, 255), width=18)
        d.line((x + 16, y + 70, x + 21 - swing // 4, y + 151), fill=(58, 57, 87, 255), width=18)
        canvas.save(alpha_dir / f'frame_{i + 1:06d}.png')
        background = Image.new('RGBA', (width, height), (212, 231, 212, 255))
        bg_draw = ImageDraw.Draw(background)
        for j in range(0, width + height, 48):
            bg_draw.line((j - height, 0, j, height), fill=(190, 214, 203, 255), width=8)
        Image.alpha_composite(background, canvas).convert('RGB').save(frames_dir / f'frame_{i + 1:06d}.png')
    run = lambda args: subprocess.run(args, check=True)
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-framerate', str(fps),
         '-i', str(frames_dir / 'frame_%06d.png'), '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
         str(output_dir / 'synthetic_source.mp4')])
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-framerate', str(fps),
         '-i', str(alpha_dir / 'frame_%06d.png'), '-an', '-c:v', 'prores_ks',
         '-profile:v', '4', '-pix_fmt', 'yuva444p10le', '-alpha_bits', '16',
         str(output_dir / 'synthetic_reference_alpha.mov')])
    return output_dir / 'synthetic_source.mp4', output_dir / 'synthetic_reference_alpha.mov'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir', default='output/synthetic-demo')
    args = ap.parse_args()
    source, reference = make_demo(args.output_dir)
    print('Source:', source)
    print('Reference alpha:', reference)


if __name__ == '__main__':
    main()