#!/usr/bin/env python3
"""Generate a two-character idle/talking QA atlas and pixel-invariance report."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from identity_lock import MOUTHS, MOUTH_RADIUS, locked_mouth_variant

HERE=Path(__file__).resolve().parent
POSES=('rest','closed','soft','e','a','o','f')


def evaluate(output:Path):
    items=[]
    tile=(252,267)
    canvas=Image.new('RGB',(tile[0]*len(POSES),tile[1]*2),(240,238,231))
    draw=ImageDraw.Draw(canvas)
    for row,(name,cy) in enumerate((('Max',149),('Mia',162))):
        source=Image.open(HERE/'assets'/f'{name}_Standing.png').convert('RGBA')
        original=np.array(source)
        h,w=original.shape[:2]
        mask=np.zeros((h,w),bool)
        rx,ry=MOUTH_RADIUS
        mask[max(0,cy-ry-5):min(h,cy+ry+6),max(0,166-rx-5):min(w,166+rx+6)]=True
        for col,pose in enumerate(POSES):
            animated=locked_mouth_variant(source,(166,cy),pose)
            diff=np.any(np.array(animated)!=original,axis=2)
            changed_outside=int((diff&(~mask)).sum())
            alpha_match=bool(np.array_equal(original[:,:,3],np.array(animated)[:,:,3]))
            if changed_outside or not alpha_match:
                raise AssertionError(f'Identity or transparency changed: {name}, {pose}: {changed_outside}')
            x0,y0=col*tile[0],row*tile[1]
            zoom=animated.crop((91,73 if name=='Max' else 86,242,221 if name=='Max' else 234)).resize((246,240),Image.Resampling.LANCZOS)
            canvas.paste(zoom,(x0+3,y0+3),zoom)
            draw.text((x0+7,y0+244),f'{name}  {pose}',fill=(32,32,38))
            items.append({'character':name,'pose':pose,'changed_pixels_outside_mouth':changed_outside,'alpha_identical':alpha_match,'changed_pixels_within_mouth':int((diff&mask).sum())})
    output.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(output,quality=91)
    report={'version':'identity-lock-v6','source':'same original Max/Mia standing PNG for all poses','results':items,
            'outside_mouth_pixels_unchanged':all(x['changed_pixels_outside_mouth']==0 for x in items),
            'identical_alpha_for_all_poses':all(x['alpha_identical'] for x in items)}
    output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,default=HERE/'output'/'Identity_Locked_Max_Mia.jpg')
    args=ap.parse_args()
    info=evaluate(args.output)
    print(json.dumps({'atlas':str(args.output),'poses':len(info['results']),'identity_verified':info['outside_mouth_pixels_unchanged']},indent=2))