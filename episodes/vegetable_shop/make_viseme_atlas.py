#!/usr/bin/env python3
"""Render a contact sheet of the exact reference-calibrated visemes used in video.

This is deterministic using tracked original character sprite PNGs, and makes
face/teeth regression review possible without running a full video render.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from mouth_rig import mouth_variant,MOUTHS

ROOT=Path(__file__).resolve().parent
HERE=ROOT/'assets'
DEST=ROOT/'output'/'Vegetable_Adventure_v5_Visemes.jpg'
FACE_CENTERS={'Max':(166,149),'Mia':(166,162)}


def create_atlas(path=DEST):
    poses=list(MOUTHS)
    cell_w,cell_h=245,240
    result=Image.new('RGB',(len(poses)*cell_w,2*cell_h),(246,230,213))
    draw=ImageDraw.Draw(result)
    for i,(who,center) in enumerate(FACE_CENTERS.items()):
        source=Image.open(HERE/f'{who}_Standing.png').convert('RGBA')
        for j,pose in enumerate(poses):
            variant=mouth_variant(source,center,pose)
            cx,cy=center
            face=variant.crop((cx-63,cy-48,cx+63,cy+55)).resize((238,205),Image.Resampling.LANCZOS)
            canvas=Image.new('RGB',face.size,(230,199,175))
            canvas.paste(face,mask=face.getchannel('A'))
            result.paste(canvas,(j*cell_w,i*cell_h+25))
            draw.text((j*cell_w+5,i*cell_h+5),f'{who}: {pose}',fill=(35,35,35))
    dest=Path(path);dest.parent.mkdir(parents=True,exist_ok=True)
    result.save(dest,quality=92)
    return dest

if __name__=='__main__':print(create_atlas())