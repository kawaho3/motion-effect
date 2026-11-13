#!/usr/bin/env python3
"""Strict media stream QA; fails rather than proclaiming an unverified export."""
import argparse
import json
import math
import subprocess
from pathlib import Path


def inspect(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_streams',
                             '-show_format', '-of', 'json', str(path)],
                            check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def verify(path, *, expected_seconds=120.0, fps=30):
    info = inspect(path)
    duration = float(info.get('format', {}).get('duration', 0))
    if not math.isfinite(duration) or abs(duration - expected_seconds) > .15:
        raise ValueError(f'Wrong duration: {duration} (expected {expected_seconds})')
    video = [s for s in info['streams'] if s['codec_type'] == 'video']
    audio = [s for s in info['streams'] if s['codec_type'] == 'audio']
    if len(video) != 1 or len(audio) != 1:
        raise ValueError(f'Expected one video and one audio track, got {len(video)}, {len(audio)}')
    num, den = map(int, video[0]['avg_frame_rate'].split('/'))
    if den == 0 or abs(num / den - fps) > .01:
        raise ValueError('Incorrect output frame rate')
    if (video[0]['width'], video[0]['height']) != (1280, 720):
        raise ValueError('Incorrect video dimensions')
    return {'duration': duration, 'fps': num / den, 'audio_streams':len(audio),
            'dimensions':[video[0]['width'],video[0]['height']]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('video', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.video), indent=2))


if __name__ == '__main__':
    main()