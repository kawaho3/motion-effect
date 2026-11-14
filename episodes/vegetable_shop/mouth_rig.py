"""Face-local 2D mouth rig for watercolor characters.

Purpose: render actual mouth articulation on a fixed illustrated character,
not simply squeeze the character's existing smile. Six visible phoneme groups
are generated from a restored skin patch with softly antialiased lip outlines,
teeth and tongue. The rest pose is untouched original artwork.

Everything is deterministic and runs offline. A true artist-aligned mouth atlas
would offer better fidelity; the procedural atlas is a licensed-source-independent
baseline, not a claim of full neural facial animation.
"""
from __future__ import annotations
import math
from PIL import Image, ImageDraw, ImageFilter
import cv2
import numpy as np

# Shapes: half-width, half-open height, lip line width, teeth fraction.
# Native PNG sprite pixels, before resize to video space.
MOUTHS = {
    'closed': (25.0, 0.6, 1.8, 0.00),
    'soft':   (22.0, 5.3, 1.7, 0.18),
    'e':      (25.5, 7.0, 1.7, 0.44),
    'a':      (23.5, 13.0, 2.0, 0.27),
    'o':      (11.2, 11.0, 2.0, 0.00),
    'f':      (22.5, 3.1, 1.6, 0.68),
    'rest':   (0, 0, 0, 0)
}

def _inpaint_smile(image: Image.Image, mouth: tuple[int,int]):
    """Remove only original smile; preserve painterly skin around it."""
    rgba=np.asarray(image.convert('RGBA')).copy()
    rgb=rgba[:,:,:3]
    h,w=rgb.shape[:2]
    cx,cy=mouth
    # Original smiles are about 57px wide with shallow teeth.
    mask=np.zeros((h,w),dtype=np.uint8)
    cv2.ellipse(mask,(cx,cy+1),(35,13),0,0,360,255,-1,cv2.LINE_AA)
    filled=cv2.inpaint(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),mask,7,cv2.INPAINT_TELEA)
    filled=cv2.cvtColor(filled,cv2.COLOR_BGR2RGB)
    a=cv2.GaussianBlur(mask,(0,0),2.3).astype('float32')[:,:,None]/255.0
    rgb=np.clip(rgb*(1-a)+filled*a,0,255).astype('uint8')
    rgba[:,:,:3]=rgb
    return Image.fromarray(rgba,'RGBA')

def _interp_curve(cx,cy,rx,ry,samples=49):
    u=np.linspace(-1,1,samples)
    # Mouth edges turn upward and meet in a smile; interior opens centrally.
    upper=[(cx+rx*t, cy-ry*0.36*(1-t*t)-1.0*t*t) for t in u]
    lower=[(cx+rx*t, cy+ry*0.72*(1-t*t)-1.0*t*t) for t in u]
    return upper,lower

def _scale_pts(points,factor):
    return [(int(round(x*factor)),int(round(y*factor))) for x,y in points]

def mouth_variant(source:Image.Image, mouth:tuple[int,int], pose:str)->Image.Image:
    """Render one of six distinct naturally shaded phoneme mouth shapes."""
    if pose=='rest':return source
    if pose not in MOUTHS:raise ValueError('Unknown viseme '+str(pose))
    cx,cy=mouth
    base=_inpaint_smile(source,mouth)
    # Draw the small mouth at 4x resolution for natural lip edges.
    scale=4
    box=(cx-47,cy-25,cx+48,cy+26)
    patch=base.crop(box).resize(((box[2]-box[0])*scale,(box[3]-box[1])*scale),Image.Resampling.BICUBIC)
    d=ImageDraw.Draw(patch,'RGBA')
    rx,ry,line,teeth=MOUTHS[pose]
    lx,ly=(cx-box[0],cy-box[1])
    upper,lower=_interp_curve(lx,ly,rx,ry)
    up=_scale_pts(upper,scale)
    lo=_scale_pts(lower,scale)
    border=(111,47,44,235)
    inner=(69,28,35,255)
    if pose=='closed':
        # Deliberate tight M/B/P closure: lips together, no oval.
        shape=[(lx+rx*t,ly+0.9*(1-t*t)-2*t*t) for t in np.linspace(-1,1,65)]
        d.line(_scale_pts(shape,scale),fill=border,width=7,joint='curve')
        d.arc(((lx-23)*scale,(ly-3)*scale,(lx+23)*scale,(ly+6)*scale),0,178,fill=(185,83,70,110),width=2)
    else:
        poly=up+list(reversed(lo))
        d.polygon(poly,fill=inner)
        # Anti-aliased lip contour and modest watercolor highlight.
        d.line(up,fill=border,width=max(5,round(line*scale)),joint='curve')
        d.line(lo,fill=(139,66,61,188),width=max(4,round((line-.3)*scale)),joint='curve')
        if pose in ('a','e','f','soft'):
            if teeth>0:
                # Teeth are a narrow pale curved band, not a white rectangle.
                band=[]
                for t in np.linspace(-.78,.78,40):
                    inset=(1-t*t)
                    band.append((lx+rx*t,ly-ry*.23*inset))
                bottom=[]
                for t in np.linspace(.78,-.78,40):
                    inset=(1-t*t)
                    bottom.append((lx+rx*t,ly+(ry*(teeth-.29))*inset))
                d.polygon(_scale_pts(band+bottom,scale),fill=(247,221,199,255))
        if pose in ('a','o'):
            tw=rx*(.58 if pose=='a' else .47)
            top=ly+ry*.42
            d.ellipse((int((lx-tw)*scale),int(top*scale),int((lx+tw)*scale),int((ly+ry*.67)*scale)),fill=(184,77,85,210))
    # Blend only within small feathered patch, so edits avoid visible seams.
    overlay=patch.resize((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS)
    feather=Image.new('L',overlay.size,0)
    fd=ImageDraw.Draw(feather)
    fd.ellipse((5,5,overlay.width-5,overlay.height-5),fill=255)
    feather=feather.filter(ImageFilter.GaussianBlur(3))
    base.paste(overlay,box[:2],feather)
    base.putalpha(source.getchannel('A'))  # preserve every silhouette pixel exactly
    return base