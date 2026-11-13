#!/usr/bin/env python3
"""Offline FFprobe / FFmpeg QA for the 120s, 12-background vegetable video."""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path


def probe(path):
    cmd=['ffprobe','-v','error','-show_entries',
        'format=duration:stream=codec_name,codec_type,width,height,avg_frame_rate,nb_frames',
        '-of','json',str(path)]
    return json.loads(subprocess.run(cmd,check=True,capture_output=True,text=True).stdout)


def sample(path,time,width=64,height=36):
    cmd=['ffmpeg','-v','error','-ss',f'{time:.2f}','-i',str(path),
         '-frames:v','1','-vf',f'scale={width}:{height}', '-pix_fmt','gray',
         '-f','rawvideo','-']
    r=subprocess.run(cmd,check=True,capture_output=True).stdout
    if len(r)!=width*height:raise RuntimeError('Could not decode video sample')
    return r


def check(path,strict_samples=True):
    data=probe(path)
    video=next((s for s in data['streams'] if s['codec_type']=='video'),None)
    audio=[s for s in data['streams'] if s['codec_type']=='audio']
    subtitle=[s for s in data['streams'] if s['codec_type']=='subtitle']
    length=float(data['format']['duration'])
    if not video or (video.get('width'),video.get('height'))!=(1280,720):
        raise ValueError('Expected 1280x720 video stream')
    if video.get('avg_frame_rate') not in ('30/1','30000/1000'):
        raise ValueError('Expected a true 30 fps video stream')
    if abs(length-120)>.1:raise ValueError(f'Expected 120 seconds, got {length}')
    if video.get('nb_frames') not in ('3600',None):raise ValueError('Expected 3600 video frames')
    if len(audio)!=1 or audio[0].get('codec_name')!='aac':raise ValueError('Expected exactly one AAC voice track')
    if len(subtitle)<1:raise ValueError('Embedded subtitles missing')
    diffs=[]
    if strict_samples:
        shots=[sample(path,k*10+5) for k in range(12)]
        for a,b in zip(shots,shots[1:]):
            delta=sum(abs(x-y) for x,y in zip(a,b))/len(a)
            diffs.append(round(delta,2))
            if delta<4:raise ValueError('Two adjacent 10-second locations look nearly identical')
    return {'duration_seconds':length,'frames':video.get('nb_frames'),
            'fps':video.get('avg_frame_rate'),'resolution':[1280,720],
            'audio_streams':len(audio),'subtitle_streams':len(subtitle),
            'scene_changes_verified':len(diffs)+1 if diffs else None,
            'adjacent_scene_pixel_differences':diffs}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('path',type=Path)
    p.add_argument('--skip-scene-samples',action='store_true')
    args=p.parse_args()
    report=check(args.path,not args.skip_scene_samples)
    print(json.dumps(report,indent=2))
    return 0

if __name__=='__main__':sys.exit(main())