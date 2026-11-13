"""Deterministic hand-drawn vegetable adventure scenery (no stock images / API).

Each place is deliberately distinct.  All primitives are drawn with Pillow and
then gently textured so the original watercolor character sprites remain readable.
"""
from __future__ import annotations
import math
import random
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WIDTH, HEIGHT = 1280, 720
STOPS = [
    ("Village vegetable shop", "WELCOME", "market"),
    ("Tomato greenhouse", "TOMATOES", "glass"),
    ("Carrot country garden", "CARROTS", "field"),
    ("Potato farm", "POTATOES", "barn"),
    ("Onion market lane", "ONIONS", "market"),
    ("Cucumber greenhouse", "CUCUMBERS", "glass"),
    ("Broccoli valley", "BROCCOLI", "field"),
    ("Spinach garden", "SPINACH", "garden"),
    ("Bell pepper nursery", "BELL PEPPERS", "glass"),
    ("Eggplant courtyard", "EGGPLANTS", "market"),
    ("Pumpkin harvest farm", "PUMPKINS", "field"),
    ("Sunset harvest festival", "GOODBYE", "festival"),
]

PALETTES = [
    ((231, 224, 194), (119, 181, 152), (203, 156, 111)),
    ((197, 233, 220), (80, 168, 116), (156, 143, 97)),
    ((174, 218, 241), (134, 181, 112), (147, 104, 65)),
    ((197, 227, 242), (160, 180, 111), (173, 130, 84)),
    ((224, 207, 178), (165, 139, 104), (139, 101, 66)),
    ((206, 244, 223), (92, 166, 137), (158, 157, 116)),
    ((196, 233, 246), (106, 173, 112), (150, 122, 86)),
    ((189, 229, 202), (106, 162, 119), (122, 107, 75)),
    ((234, 235, 192), (135, 184, 112), (176, 126, 91)),
    ((220, 200, 205), (155, 115, 144), (146, 98, 106)),
    ((243, 208, 163), (148, 175, 106), (160, 116, 81)),
    ((238, 169, 137), (137, 122, 150), (116, 88, 96)),
]


def _blend_color(a, b, amount):
    return tuple(int(a[i] * (1 - amount) + b[i] * amount) for i in range(3))


def _seed(idx):
    return random.Random(1907 + idx * 173)


def _canvas(idx):
    rng = np.random.default_rng(504 + idx)
    top, horizon, earth = PALETTES[idx]
    y = np.arange(HEIGHT, dtype='float32')[:, None]
    blend = np.clip(y / 470, 0, 1)
    base = np.empty((HEIGHT, WIDTH, 3), dtype='float32')
    for c in range(3):
        base[:, :, c] = top[c] * (1 - blend) + horizon[c] * blend
        ground = np.clip((y - 475) / 220, 0, 1)
        base[:, :, c] = base[:, :, c] * (1 - ground) + earth[c] * ground
    # Very small seeded paper grain: consistent from one run to the next.
    noise = rng.normal(0, 3.6, (HEIGHT, WIDTH, 1))
    base = np.clip(base + noise, 0, 255).astype('uint8')
    return Image.fromarray(base, 'RGB')


def _foliage(d, cx, cy, radius, rng, color=(55, 119, 58), density=14):
    for _ in range(density):
        dx, dy = rng.uniform(-radius, radius), rng.uniform(-radius*.7, radius*.5)
        rx = rng.randint(max(3, int(radius*.11)), max(5,int(radius*.35)))
        ry = rng.randint(max(3, int(radius*.11)), max(5,int(radius*.33)))
        col = _blend_color(color,(160, 208, 110),rng.uniform(.05,.48))
        d.ellipse((cx+dx-rx,cy+dy-ry,cx+dx+rx,cy+dy+ry),fill=col)
    d.arc((cx-radius*.8,cy-radius*.4,cx+radius*.9,cy+radius*.6),190,345,fill=(49,91,47),width=2)


def _hills(d, rng):
    for line,(y,col) in enumerate([(350,(154,192,157)),(395,(115,164,119)),(444,(84,142,98))]):
        points=[(-20,HEIGHT),(WIDTH+20,HEIGHT),(WIDTH+20,y+15)]
        for x in range(WIDTH,-30,-28):
            points.append((x,y + 24*math.sin(x/97+line) + 13*math.sin(x/43+line*2)))
        d.polygon(points,fill=col)
    for x in range(0,1320,115):
        h=rng.randrange(16,45)
        d.line((x,410,x,410-h),fill=(62,109,61),width=5)
        _foliage(d,x,410-h,21,rng,(53,111,66),9)


def _row_field(d, idx, rng, crop='carrot'):
    vp=(620,385)
    d.polygon([(0,720),(1280,720),(850,413),(390,413)],fill=(137,101,72))
    for side in [-1,1]:
        for b in range(1,7):
            dx=b*42
            x0=vp[0]+side*(30+dx)
            x1=vp[0]+side*(95+b*155)
            d.polygon([(x0,414),(x0+side*28,414),(x1+side*60,720),(x1- side*35,720)],fill=(88,133,73))
            for j in range(11):
                yy=425+j*j*2.5
                xx=x0+(x1-x0)*((yy-413)/307)
                rr=5 + (yy-413)/12
                if yy>704 or xx < -70 or xx>1350: continue
                _vegetable(d, xx+ rng.uniform(-rr,rr)*.22, yy, crop, rr*.68, rng)
    d.polygon([(560,440),(684,440),(795,720),(446,720)],fill=(196,161,113))
    for k in range(12):
        y=440+(k/12)**1.85*280
        d.line((620-(y-440)*.6,y,620+(y-440)*.6,y), fill=(170,136,105),width=max(1,round((y-430)/80)))


def _greenhouse(d,rng, crop):
    d.polygon([(0,0),(1280,0),(1190,500),(90,500)],fill=(211,236,221))
    for y in range(25,465,82):
        d.line((0,y,1280,y+12),fill=(244,250,237),width=12)
    for x in range(0,1350,165):
        d.line((x,0,620+(x-620)*.6,470),fill=(229,247,231),width=11)
        d.line((x,0,620+(x-620)*.6,470),fill=(117,152,129),width=2)
    d.polygon([(400,458),(880,458),(1280,720),(0,720)],fill=(191,164,125))
    for side in [-1,1]:
        for depth in range(5):
            xx=620 + side*(210+depth*210)
            d.line((xx,90,xx,560),fill=(62,105,62),width=5)
            for j in range(8):
                yy=160+j*44
                xx2=xx+17*math.sin(j*3+depth)
                _foliage(d,xx2,yy,35+depth*3,rng,(49,123,67),9)
                if j%2==0:
                    _vegetable(d,xx2+side*18,yy+18,crop,22,rng)


def _wood_planks(d,rect,rng,light=True):
    x0,y0,x1,y1=rect
    color=(130,87,56) if light else (91,65,57)
    d.rectangle(rect,fill=color)
    for x in range(x0+24,x1,52):
        d.line((x,y0,x,y1),fill=(171,123,82) if light else (130,92,74),width=3)
        d.line((x+12,y0+5,x+5,y1-5),fill=(104,71,56),width=1)
    for y in range(y0+18,y1,88):
        d.line((x0,y,x1,y),fill=(67,53,44),width=7)


def _market(d,idx,rng):
    dark=idx in (9,11)
    sky = (188,145,157) if dark else (220,204,174)
    d.rectangle((0,0,1280,405),fill=sky)
    for x in (0,145,1110,1230):
        _wood_planks(d,(x,72,x+45,625),rng,not dark)
    d.polygon([(0,80),(1280,80),(1280,156),(0,145)],fill=(247,235,205))
    for x in range(-50,1320,170):
        d.polygon([(x,72),(x+83,75),(x+83,160),(x+20,163)],fill=(186,77,69) if idx in (0,11) else (115,99,145))
    _wood_planks(d,(0,410,1280,535),rng)
    d.rectangle((0,534,1280,720),fill=(154,120,101) if not dark else (99,75,97))
    for j in range(9):
        x=j*155+20
        _crate(d,x,420+25*math.sin(j),rng)
        crop=['tomato','carrot','potato','onion','cucumber','broccoli','pepper','eggplant','pumpkin'][j]
        for p in range(6):
            _vegetable(d,x+43+ rng.randint(-22,22),425+rng.randint(-20,8),crop,18,rng)
    if dark:
        for x in (100,360,620,880,1120):
            d.line((x,100,x,174),fill=(66,57,56),width=3)
            d.ellipse((x-18,160,x+18,202),fill=(255,219,145),outline=(146,101,64),width=4)


def _barn(d,rng):
    _hills(d,rng)
    d.rectangle((80,185,430,460),fill=(161,75,61))
    d.polygon([(40,205),(260,89),(473,205)],fill=(90,75,66))
    d.rectangle((209,315,317,462),fill=(87,66,58))
    for x in range(112,413,32):d.line((x,210,x,445),fill=(200,112,83),width=3)
    for x in (0,1090):
        d.ellipse((x,160,x+140,325),fill=(71,126,77))
        d.rectangle((x+55,280,x+80,470),fill=(120,82,66))
    _row_field(d,3,rng,'potato')


def _festival(d,rng):
    _market(d,11,rng)
    d.polygon([(0,420),(1280,420),(1280,720),(0,720)],fill=(119,94,112))
    for i in range(0,1250,74):
        y=75 + 27*math.sin(i/130)
        d.line((i,y,i+74,75+27*math.sin((i+74)/130)),fill=(125,80,71),width=3)
        d.ellipse((i+25,y+5,i+38,y+18),fill=(255,208,115))
    for x in [20,1220]:
        d.ellipse((x-52,285,x+55,394),fill=(245,164,102),outline=(157,94,67),width=9)


def _crate(d,x,y,rng):
    d.rounded_rectangle((x,y,x+93,y+70),radius=9,fill=(156,106,68),outline=(87,65,48),width=5)
    for yy in (y+20,y+43):d.line((x+9,yy,x+83,yy),fill=(206,157,102),width=5)


def _vegetable(d,x,y,kind,r,rng):
    x=int(x);y=int(y);r=max(3,int(r))
    if kind=='tomato':
        d.ellipse((x-r,y-r,x+r,y+r),fill=(204+rng.randrange(30),55+rng.randrange(30),43),outline=(133,49,37),width=2)
        d.polygon([(x-9,y-r+3),(x,y-r-7),(x+10,y-r+3),(x+1,y-r+1)],fill=(40,118,64))
        d.ellipse((x-r*.45,y-r*.62,x-r*.2,y-r*.38),fill=(255,169,105))
    elif kind=='carrot':
        d.polygon([(x-r*.7,y-r*.5),(x+r*.7,y-r*.5),(x+r*.15,y+r*1.55)],fill=(240,139,59),outline=(158,96,45),width=2)
        for q in range(3):d.line((x,y-r*.4,x+rng.randrange(-r,r+1),y-r*1.4),fill=(53,131,66),width=3)
    elif kind=='potato':
        d.ellipse((x-r*1.2,y-r*.7,x+r*1.2,y+r*.7),fill=(185,147,97),outline=(117,94,66),width=2)
        for _ in range(4):
            px=x+rng.randrange(-r,r+1);py=y+rng.randrange(-r//2,r//2+1)
            d.ellipse((px,py,px+2,py+2),fill=(133,107,67))
    elif kind=='onion':
        d.ellipse((x-r,y-r*.75,x+r,y+r),fill=(178,103,142) if rng.random()>.5 else (231,185,108),outline=(113,78,91),width=2)
        d.polygon([(x-5,y-r*.7),(x,y-r*1.3),(x+5,y-r*.7)],fill=(136,87,70))
    elif kind=='cucumber':
        d.rounded_rectangle((x-r*1.8,y-r*.4,x+r*1.6,y+r*.55),radius=r//2,fill=(49,130,71),outline=(33,91,56),width=3)
        d.line((x-r,y-r*.2,x+r,y-r*.2),fill=(134,176,94),width=3)
    elif kind=='broccoli':
        d.rectangle((x-4,y,x+5,y+r),fill=(107,146,94))
        for dx,dy in [(-.8,0),(.8,0),(0,-.55),(-.2,-.1),(.4,-.2)]:
            _foliage(d,x+dx*r,y+dy*r,r*.62,rng,(47,113,68),8)
    elif kind=='spinach':
        for q in range(5):
            theta=q*1.26
            xx=x+math.sin(theta)*r;yy=y+math.cos(theta)*r
            d.ellipse((xx-r*.55,yy-r*.85,xx+r*.55,yy+r*.2),fill=(53+rng.randrange(28),133+rng.randrange(34),60))
            d.line((x,y+r,xx,yy-r*.5),fill=(34,94,48),width=1)
    elif kind=='pepper':
        color=rng.choice([(230,66,58),(238,186,65),(79,165,74)])
        for dx in [-r*.5,0,r*.5]:d.ellipse((x+dx-r*.5,y-r*.7,x+dx+r*.5,y+r),fill=color)
        d.line((x,y-r*.7,x+3,y-r*1.16),fill=(48,112,57),width=4)
    elif kind=='eggplant':
        d.ellipse((x-r*.85,y-r,x+r*.85,y+r*1.25),fill=(107,62,130),outline=(63,40,86),width=3)
        d.polygon([(x-r*.7,y-r*.85),(x,y-r*1.25),(x+r*.7,y-r*.85),(x,y-r*.67)],fill=(72,137,72))
        d.ellipse((x-r*.48,y-r*.75,x-r*.23,y+r*.5),fill=(162,117,175))
    elif kind=='pumpkin':
        for dx in [-r*.55,0,r*.55]:
            d.ellipse((x+dx-r*.7,y-r*.7,x+dx+r*.7,y+r*.7),fill=(225,129+int(dx*0),54),outline=(154,92,50),width=2)
        d.line((x,y-r*.6,x+3,y-r*1.1),fill=(62,112,60),width=5)


def _extra_products(d,idx,rng):
    key=['tomato','tomato','carrot','potato','onion','cucumber','broccoli','spinach','pepper','eggplant','pumpkin','pumpkin'][idx]
    if idx in [1,5,8]:
        # Rounded vegetable beds along greenhouse floor.
        d.ellipse((0,475,390,740),fill=(62,120,71))
        d.ellipse((885,475,1340,740),fill=(60,119,76))
    elif idx in [0,4,9,11]:
        for x in [35,1120]:
            _crate(d,x,555,rng)
    for side in (-1,1):
        for j in range(23):
            x=(70 if side<0 else 1202)+side*rng.randint(-190,135)
            y=rng.randint(390,635)
            rr=rng.randint(11,30) + (y-390)//50
            _vegetable(d,x,y,key,rr,rng)


def _watercolor_edge_details(im, idx):
    """Borrow only edge foliage/produce texture from owned concept artwork.

    Masked edge collages preserve the distinct greenhouse/field silhouettes and
    avoid recycling the original two people or the same full shop background.
    """
    art=Path(__file__).resolve().parent/'assets'/'Scene_Concept.jpg'
    if not art.exists():return im
    src=Image.open(art).convert('RGB').resize((WIDTH,HEIGHT),Image.Resampling.LANCZOS)
    # Small painterly accents at the far left/right, away from subject faces.
    for box,alpha in [((0,215,315,515),.57),((986,165,1280,505),.57),((0,0,255,160),.23),((1080,0,1280,180),.19)]:
        x0,y0,x1,y1=box
        crop=src.crop(box).convert('RGBA')
        mask=Image.new('L',(x1-x0,y1-y0),0)
        d=ImageDraw.Draw(mask)
        border=min(32,(y1-y0)//5)
        d.rounded_rectangle((border,border,x1-x0-border,y1-y0-border),radius=border,fill=int(255*alpha))
        mask=mask.filter(ImageFilter.GaussianBlur(36))
        im.paste(crop,(x0,y0),mask)
    return im


def render_background(index, width=WIDTH,height=HEIGHT):
    """Produce exactly one independently identifiable location image."""
    if index not in range(len(STOPS)):
        raise ValueError('There are exactly 12 unique 10-second scene settings')
    rng=_seed(index)
    im=_canvas(index)
    d=ImageDraw.Draw(im)
    mode=STOPS[index][2]
    if mode=='market':
        _market(d,index,rng)
    elif mode=='glass':
        _greenhouse(d,rng, ['tomato','tomato','carrot','potato','onion','cucumber','broccoli','spinach','pepper'][index])
    elif mode=='barn':
        _barn(d,rng)
    elif mode=='festival':
        _festival(d,rng)
    else:
        _hills(d,rng)
        crop=['carrot','carrot','carrot','potato','onion','cucumber','broccoli','spinach','pepper','eggplant','pumpkin','pumpkin'][index]
        _row_field(d,index,rng,crop)
        if mode=='garden':
            # Pergola with flowering vines makes this stop distinct from the fields.
            for x in range(60,1250,105):
                d.line((x,10,x+33,460),fill=(102,88,59),width=4)
                _foliage(d,x,50,56,rng,(39,133,70),22)
    _extra_products(d,index,rng)
    # Paint a narrow, light walking platform behind the actors' feet.
    d.ellipse((225,644,1060,725),fill=(165,137,104))
    for i in range(18):
        x=rng.randrange(90,1230);y=rng.randrange(555,714)
        d.arc((x,y,x+14,y+6),190,340,fill=(190,170,135),width=2)
    # For market stops use the original high-detail watercolor setting with
    # the people locally replaced by repeated produce/foliage; for farm and
    # greenhouse stops retain clearly different hand-drawn architecture.
    market_file=Path(__file__).resolve().parent/'assets'/'Market_No_People.jpg'
    if market_file.is_file() and index in (0,4,9,11):
        market=Image.open(market_file).convert('RGB').resize((WIDTH,HEIGHT),Image.Resampling.LANCZOS)
        if index in (4,9):
            # Enter a neighboring stall: the produce layout is viewed from
            # the reverse direction with warmer/cooler lighting.
            market=market.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if index == 4:
            market=Image.blend(market,Image.new('RGB',(WIDTH,HEIGHT),(201,176,154)),.17)
        if index == 9:
            market=Image.blend(market,Image.new('RGB',(WIDTH,HEIGHT),(177,131,166)),.24)
        if index == 11:
            market=Image.blend(market,Image.new('RGB',(WIDTH,HEIGHT),(223,140,112)),.20)
            fest=ImageDraw.Draw(market)
            for x in range(50,1280,92):
                y=25+int(11*math.sin(x/170))
                fest.line((x,y,x,y+24),fill=(94,70,67),width=2)
                fest.ellipse((x-8,y+23,x+8,y+39),fill=(255,216,120))
        im=market
    else:
        im=im.filter(ImageFilter.GaussianBlur(.38))
    if (width,height)!=(WIDTH,HEIGHT):im=im.resize((width,height),Image.Resampling.LANCZOS)
    return im


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).parent/'output'/'backgrounds')
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    for i,(name,_,_) in enumerate(STOPS):
        file=args.out/f'{i:02}_{name.lower().replace(" ","_")}.jpg'
        render_background(i).save(file,quality=91)
        print(file)

if __name__=='__main__':main()