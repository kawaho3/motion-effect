"""Reference-calibrated, watercolor mouth visemes for Max and Mia.

The source video uses a handful of conspicuous, held 2D mouth states, not
continuous smile stretching. This rig keeps the original character's painted
face and alpha, inpaints just the original resting smile, and renders shaded
viseme artwork in supersampled pixel space. No reference-video pixels are used.

Key v5 fix: all paths, including upper/lower lip outlines, are drawn in the
same supersampled coordinate system. The previous version drew contours at
unscaled coordinates and produced a flat dark slash.
"""
from __future__ import annotations
import math
from PIL import Image, ImageDraw, ImageFilter
import cv2
import numpy as np

# half-width, approx max opening height, teeth visibility (0-1)
MOUTHS = {
    'rest': (0,0,0),
    'closed': (24, 0, 0),
    'soft': (20, 5.8, .12),
    'e': (27, 9.5, .75),
    'a': (24, 17, .16),
    'o': (13.5, 17, 0),
    'f': (23, 4.0, .80),
}


def _hide_resting_smile(source, center):
    rgb=np.asarray(source.convert('RGB')).copy()
    cx,cy=center
    mask=np.zeros(rgb.shape[:2],np.uint8)
    # Feather only the original mouth, not the nose or chin. Preserve cheeks.
    cv2.ellipse(mask,(cx,cy+1),(32,12),0,0,360,255,-1,cv2.LINE_AA)
    repair=cv2.inpaint(rgb,mask,7,cv2.INPAINT_TELEA)
    weight=cv2.GaussianBlur(mask,(0,0),2.1).astype(np.float32)/255.0
    painted=np.clip(rgb*(1-weight[...,None])+repair*weight[...,None],0,255).astype('uint8')
    painted_img=Image.fromarray(painted,'RGB').convert('RGBA')
    painted_img.putalpha(source.getchannel('A'))
    return painted_img


def _pixel_points(points,s):
    return [(round(x*s),round(y*s)) for x,y in points]


def _curves(cx,cy,rx,height,rounding=.48):
    us=np.linspace(-1,1,65)
    upper=[];lower=[]
    for t in us:
        shoulder=max(0,1-t*t)**rounding
        upper.append((cx+rx*t,cy-height*.39*shoulder-1.4*t*t))
        lower.append((cx+rx*t,cy+height*.62*shoulder-1.4*t*t))
    return upper,lower


def mouth_variant(source:Image.Image, center:tuple[int,int], pose:str)->Image.Image:
    """Return an unchanged-alpha, fully registered original-art viseme image."""
    if pose=='rest':return source
    if pose not in MOUTHS:raise ValueError('Unknown mouth pose '+str(pose))
    cx,cy=center
    base=_hide_resting_smile(source,center)
    x0,y0,x1,y1=cx-48,cy-31,cx+49,cy+34
    crop=base.crop((x0,y0,x1,y1))
    scale=4
    high=crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.BICUBIC)
    art=ImageDraw.Draw(high,'RGBA')
    local_x,local_y=cx-x0,cy-y0
    rx,h,teeth=MOUTHS[pose]
    x=int(local_x*scale);y=int(local_y*scale)
    if pose=='closed':
        t=np.linspace(-1,1,65)
        curve=_pixel_points([(local_x+rx*u,local_y+1.2*(1-u*u)-1.2*u*u) for u in t],scale)
        art.line(curve,fill=(96,44,42,255),width=6,joint='curve')
        # Lower lip is modest shading, as in the source face.
        offset=[(px,py+4) for px,py in curve[4:-4]]
        art.line(offset,fill=(197,92,83,120),width=3,joint='curve')
    else:
        top,bot=_curves(local_x,local_y,rx,h,.68 if pose=='o' else .45)
        top_px=_pixel_points(top,scale)
        bot_px=_pixel_points(bot,scale)
        outline=top_px+list(reversed(bot_px))
        art.polygon(outline,fill=(73,30,37,255))
        # Subtle oral cavity vertical tone, not an unshaded dark ellipse.
        if pose in ('a','o','soft'):
            ry=max(3,round(h*.37*scale))
            art.ellipse((x-int(rx*.56*scale), y+int(.27*h*scale),
                         x+int(rx*.56*scale),y+int(.27*h*scale)+ry),fill=(139,49,68,160))
        if teeth>0:
            # Teeth use creamy watercolor rather than a solid neon white bar.
            height=max(2,h*teeth*.45)
            tooth_top=[];tooth_bottom=[]
            for u in np.linspace(-.80,.80,50):
                swell=max(0,1-u*u)**.55
                tooth_top.append((local_x+rx*u,local_y-h*.35*swell+1.0))
            for u in np.linspace(.80,-.80,50):
                swell=max(0,1-u*u)**.55
                tooth_bottom.append((local_x+rx*u,local_y+(-h*.35+height)*swell+1.0))
            art.polygon(_pixel_points(tooth_top+tooth_bottom,scale),fill=(243,216,195,252))
            # Tooth highlight along upper edge, kept narrow.
            art.line(_pixel_points(tooth_top,scale),fill=(255,239,220,170),width=2)
        # SUPER-SAMPLED PATH FIX (old implementation omitted scale here).
        art.line(top_px,fill=(111,48,45,255),width=7,joint='curve')
        art.line(bot_px,fill=(163,76,67,227),width=6,joint='curve')
        # Lip corners and a soft lower-lip shine blend with native face texture.
        for px,py in (top_px[0],top_px[-1]):
            art.ellipse((px-3,py-3,px+3,py+3),fill=(95,47,42,255))
        if h>=8:
            mid=bot_px[len(bot_px)//2]
            art.arc((mid[0]-round(rx*.59*scale),mid[1]-2,
                     mid[0]+round(rx*.59*scale),mid[1]+11),5,177,
                     fill=(229,126,109,100),width=3)
    patch=high.resize(crop.size,Image.Resampling.LANCZOS)
    feather=Image.new('L',patch.size,0)
    d=ImageDraw.Draw(feather)
    d.ellipse((3,3,patch.width-4,patch.height-4),fill=255)
    feather=feather.filter(ImageFilter.GaussianBlur(3.2))
    base.paste(patch,(x0,y0),feather)
    base.putalpha(source.getchannel('A'))
    return base