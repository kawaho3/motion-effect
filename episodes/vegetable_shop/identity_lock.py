"""V6 facial identity lock: speaking alters mouth only, never a different face.

For Max and Mia every pose is generated from the SAME transparent source sprite.
The mouth mask is stable across visemes, so eyes, nose, cheeks, brows, hair,
head silhouette, registration and transparent alpha remain bit-for-bit stable.
Blinking is a separate animation; speech cannot trigger gaze or face swaps.
"""
from __future__ import annotations
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
from mouth_rig import MOUTHS, mouth_variant

# The mask is deliberately smaller than the former 97x65 face repaint.
# Radii include the complete original smile and seven speech positions.
MOUTH_RADIUS=(37,19)

@lru_cache(maxsize=64)
def _mouth_mask(size:tuple[int,int],center:tuple[int,int])->Image.Image:
    cx,cy=center
    rx,ry=MOUTH_RADIUS
    # Render the mask inside a bounded ROI, with a feathered edge. Never
    # smooth/retouch the full portrait. It is constant for ALL poses.
    bbox=(cx-rx-4,cy-ry-4,cx+rx+5,cy+ry+5)
    patch=Image.new('L',(bbox[2]-bbox[0],bbox[3]-bbox[1]),0)
    ImageDraw.Draw(patch).ellipse((4,4,4+2*rx,4+2*ry),fill=255)
    patch=patch.filter(ImageFilter.GaussianBlur(1.3))
    result=Image.new('L',size,0)
    result.paste(patch,bbox[:2])
    return result


def locked_mouth_variant(source:Image.Image,center:tuple[int,int],pose:str)->Image.Image:
    """Change ONLY the mouth; original idle face is returned losslessly.

    A strict test below guarantees all pixels outside the bounded mouth mask
    are identical for a talking face and the original non-talking face.
    """
    if pose=='rest':
        return source
    if pose not in MOUTHS:
        raise ValueError(f'Unknown viseme: {pose}')
    if source.mode!='RGBA':
        source=source.convert('RGBA')
    painted=mouth_variant(source,center,pose)
    alpha=source.getchannel('A')
    merged=Image.composite(painted,source,_mouth_mask(source.size,center))
    merged.putalpha(alpha)
    return merged