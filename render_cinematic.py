"""Animate generated, spatially aligned eye/lip textures over detailed still art.

All video rendering is local. Mouth timing comes from the neural speech model.
The animation is a limited 2D facial composite, not a 3D character rig.
"""
from pathlib import Path
import json,math,subprocess,sys,functools
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont,ImageFilter

ROOT=Path(__file__).resolve().parent;ASSET=ROOT/'assets';WORK=ROOT/'work';OUT=ROOT/'deliverables'
W,H=1280,720;FPS=30;FRAMES=900
BASE=Image.open(ASSET/'Garden_Base.png').convert('RGB')
AH=Image.open(ASSET/'Garden_Ah_Blink.png').convert('RGB').resize(BASE.size)
OH=Image.open(ASSET/'Garden_Oh.png').convert('RGB').resize(BASE.size)
SW,SH=BASE.size;TL=json.loads((WORK/'timeline.json').read_text())
FONT=str(ASSET/'DejaVuSans-Bold.ttf')
MOUTH={'Max':(432,296,525,360),'Mia':(1219,312,1313,381)}
EYES={'Max':[(387,202,478,272),(490,180,539,248)],
      'Mia':[(1205,201,1264,275),(1280,224,1375,300)]}
HEAD={'Max':(168,0,612,451),'Mia':(1156,27,1556,474)}
BLINKS={'Max':[1.7,5.7,9.6,13.8,18.2,22.5,26.8],
        'Mia':[2.9,7.4,11.8,16.1,20.3,24.6,28.8]}

def mask(w,h,feather=5,inset=8):
    a=Image.new('L',(w,h));d=ImageDraw.Draw(a)
    d.rounded_rectangle((inset,inset,w-inset-1,h-inset-1),radius=12,fill=255)
    return a.filter(ImageFilter.GaussianBlur(feather))

PATCH={}
for char,box in MOUTH.items():
    orig=BASE.crop(box);a=AH.crop(box);o=OH.crop(box);mw,mh=orig.size
    anchor=20 if char=='Max' else 25
    # Mouth openings for consonants use the same rendered lips, compressed gently.
    def compressed(source,factor):
        # Compress the lip opening, pin both patch edges, and never sample outside
        # the texture. A plain affine crop would introduce black edge pixels.
        bottom=mh-14
        ys=np.interp(np.arange(mh),[0,anchor,anchor+(bottom-anchor)*factor,mh-1],
            [0,anchor,bottom,mh-1])
        xx,yy=np.meshgrid(np.arange(mw),ys)
        data=np.asarray(source,dtype=float)
        result=np.stack([ndimage.map_coordinates(data[:,:,c],[yy,xx],order=3,mode='nearest') for c in range(3)],axis=-1)
        return Image.fromarray(np.clip(result,0,255).astype('uint8'))
    PATCH[char]={'M':orig,'A':a,'E':compressed(a,.65),'S':compressed(a,.42),'O':o,
        'mask':mask(mw,mh,4,8)}
    PATCH[char]['eyes']=[(box,AH.crop(box),mask(box[2]-box[0],box[3]-box[1],3,6)) for box in EYES[char]]

def phone_state(phone):
    if phone in 'mbp':return 'M'
    if phone in 'oɔʊuwɒ':return 'O'
    if phone in 'aɑæʌɐ':return 'A'
    if phone in 'eiɪɛɜɚəɹr':return 'E'
    if phone in ' ˈˌ.,!?;:—':return 'M'
    return 'S'

CONTROLS={}
for char in ['Max','Mia']:
    states=['M']*FRAMES
    for row in TL:
        if row['character']!=char:continue
        for pi,ph in enumerate(row['phones']):
            phone=ph['phone']
            # Stress and vowel-length marks have model durations but are not
            # independent mouth poses. Carry the adjacent spoken vowel through.
            if phone in 'ˈˌ':
                phone=next((p['phone'] for p in row['phones'][pi+1:] if p['phone'] not in 'ˈˌː'),' ')
            elif phone=='ː':
                phone=next((p['phone'] for p in reversed(row['phones'][:pi]) if p['phone'] not in 'ˈˌː'),' ')
            first=max(0,math.floor((ph['start']-.015)*FPS));last=min(FRAMES,math.ceil((ph['end']-.015)*FPS))
            for i in range(first,last):states[i]=phone_state(phone)
    CONTROLS[char]=states

def blink_amount(char,t):
    nearest=min(abs(t-x) for x in BLINKS[char])
    if nearest<.038:return 1.0
    if nearest<.097:return .5+.5*math.cos(math.pi*(nearest-.038)/.059)
    return 0.0

def local_warp(image,box,t,char):
    """Very small head drift with zero displacement at the ROI boundary."""
    roi=image.crop(box);width,height=roi.size;cx,cy=width*.52,height*.48
    phase=.6 if char=='Max' else 2.7
    dx=1.15*math.sin(t*.82+phase);dy=.9*math.sin(t*1.22+phase)
    theta=.0019*math.sin(t*.95+phase)
    def pt(x,y):
        rr=((x-cx)/(width*.53))**2+((y-cy)/(height*.54))**2
        strength=max(0,1-rr)**1.4
        return (x-strength*(dx-theta*(y-cy)),y-strength*(dy+theta*(x-cx)))
    mesh=[];step=28
    for y in range(0,height,step):
        for x in range(0,width,step):
            xx=min(x+step,width);yy=min(y+step,height)
            quad=sum((pt(a,b) for a,b in [(x,y),(x,yy),(xx,yy),(xx,y)]),())
            mesh.append(((x,y,xx,yy),quad))
    warped=roi.transform(roi.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)
    image.paste(warped,box[:2])

def animated(t):
    image=BASE.copy();fi=min(FRAMES-1,max(0,round(t*FPS)))
    for char in ['Max','Mia']:
        state=CONTROLS[char][fi];previous=CONTROLS[char][max(0,fi-1)]
        texture=PATCH[char][state]
        # One-frame transition softens abrupt phoneme changes without smearing lips.
        if previous!=state:texture=Image.blend(PATCH[char][previous],texture,.80)
        if state!='M' or previous!='M':image.paste(texture,MOUTH[char][:2],PATCH[char]['mask'])
        b=blink_amount(char,t)
        if b>.001:
            for box,closed,alpha in PATCH[char]['eyes']:
                partial=Image.blend(BASE.crop(box),closed,b)
                image.paste(partial,box[:2],alpha)
        local_warp(image,HEAD[char],t,char)
    return image

# Conversational cuts: wide two-shot, speaker close-ups, then a shared recap.
SHOTS=[
 (0,'wide'),(TL[3]['start']-.18,'Max'),(TL[4]['start']-.18,'Mia'),
 (TL[5]['start']-.18,'wide'),(TL[6]['start']-.18,'Max'),
 (TL[7]['start']-.18,'Mia'),(TL[8]['start']-.18,'Max'),
 (TL[9]['start']-.18,'Mia'),(TL[10]['start']-.18,'wide')]
VIEW={'wide':(0,0,SW,SH),'Max':(57,12,1097,597),'Mia':(684,42,1664,593.25)}

def camera(image,t):
    index=max(i for i,(at,name) in enumerate(SHOTS) if t>=at)
    at,name=SHOTS[index];end=SHOTS[index+1][0] if index+1<len(SHOTS) else 30
    u=np.clip((t-at)/max(.1,end-at),0,1)
    left,top,right,bottom=VIEW[name]
    # A slow 1.3% push-in maintains the illustration's detail and calm motion.
    zoom=1+.013*u;cx=(left+right)/2;cy=(top+bottom)/2
    ww=(right-left)/zoom;hh=(bottom-top)/zoom
    box=(cx-ww/2,cy-hh/2,cx+ww/2,cy+hh/2)
    return image.resize((W,H),Image.Resampling.LANCZOS,box=box),name,box

def caption_lines(text,font,max_width):
    words=text.split();lines=[];line=''
    for word in words:
        trial=(line+' '+word).strip()
        if font.getlength(trial)>max_width and line:lines.append(line);line=word
        else:line=trial
    if line:lines.append(line)
    return lines

@functools.lru_cache(maxsize=24)
def captions(text):
    layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    font=ImageFont.truetype(FONT,34);lines=caption_lines(text,font,1120)
    y=H-53-(len(lines)-1)*43
    for line in lines:
        d.text((W//2,y),line,font=font,anchor='mm',fill='white',stroke_width=3,stroke_fill='#151717')
        y+=43
    return layer

def frame(t):
    image,shot,box=camera(animated(t),t);image=image.convert('RGBA')
    d=ImageDraw.Draw(image)
    d.text((W/2,28),'Flower names',font=ImageFont.truetype(FONT,23),anchor='mm',
        fill='#ffdc83',stroke_width=1,stroke_fill='#665029')
    row=next((r for r in TL if r['start']-.04<=t<=r['end']+.10),None)
    if row:image.alpha_composite(captions(row['text']))
    names=[]
    if shot=='wide':
        if TL[2]['start']<=t<TL[5]['start']:names=[('ROSE',(592,703))]
        elif TL[5]['start']<=t<TL[7]['start']:names=[('SUNFLOWER',(840,704))]
        elif t>=TL[10]['start']:names=[('ROSE',(592,703)),('SUNFLOWER',(840,704)),('TULIP',(1074,703))]
    elif shot=='Mia' and TL[7]['start']<=t<=TL[7]['end']+.2:
        d.text((80,103),'TULIP',font=ImageFont.truetype(FONT,28),anchor='lm',fill='#ffe59b',stroke_width=2,stroke_fill='#3d3424')
    for name,(x,y) in names:
        x=(x-box[0])/(box[2]-box[0])*W;y=(y-box[1])/(box[3]-box[1])*H
        if y<H-115:
            d.text((x,y),name,font=ImageFont.truetype(FONT,21),anchor='mm',fill='#ffe59b',stroke_width=2,stroke_fill='#3d3424')
    return image.convert('RGB')

def main():
    if '--stills' in sys.argv:
        for i in [0,3,4,6,7,8,10,11]:
            t=(TL[i]['start']+TL[i]['end'])/2
            frame(t).save(WORK/f'still_{i:02}.jpg',quality=94)
        for t in [1.60,1.67,1.70,1.77,1.84]:frame(t).save(WORK/f'blink_{t:.2f}.jpg',quality=95)
        return
    dest=OUT/'Flower_Friends_30_Seconds.mp4'
    cmd=['ffmpeg','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-i',str(WORK/'audio.wav'),'-i',str(OUT/'Flower_Friends_Cinematic_Subtitles.srt'),
        '-map','0:v','-map','1:a','-map','2:s','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',
        '-c:a','aac','-b:a','256k','-c:s','mov_text','-metadata:s:s:0','language=eng',
        '-metadata','title=Flower Friends — cinematic revision','-t','30','-movflags','+faststart',str(dest)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(FRAMES):
        proc.stdin.write(frame(i/FPS).tobytes())
        if i%90==0:print(f'Rendered {i/FPS:.0f} / 30 seconds',flush=True)
    proc.stdin.close();status=proc.wait()
    if status:raise RuntimeError(f'Encoder exited {status}')
    frame(1.2).save(OUT/'Flower_Friends_Preview.jpg',quality=95)
    print('CINEMATIC RENDER COMPLETE',flush=True)

if __name__=='__main__':main()