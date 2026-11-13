#!/usr/bin/env python3
"""Vegetable Adventure: 12 ten-second scenes, face-safe visemes and natural blinks.

Uses *existing* Kokoro audio/timeline produced by build.py --audio.  No eSpeak,
no model/API at render time.  Faces and mouths are image-warped rather than
painted ovals.  A true-alpha sprite keeps both characters consistent across
12 independently generated storybook locations.
"""
from __future__ import annotations
import argparse
import bisect
import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from journey_backgrounds import STOPS, render_background

HERE=Path(__file__).resolve().parent
ASSETS=HERE/'assets'
OUT=HERE/'output'
FPS=30
DURATION=120.0
WIDTH,HEIGHT=1280,720
VOICE={'Max':'am_puck','Mia':'af_heart'}
SCENE_SECONDS=10
# Native transparent sprite coordinates, after deterministic cropping.
FACES={
    'Max':{'mouth':(166,149),'eyes':[(139,111,17,10),(191,106,17,10)]},
    'Mia':{'mouth':(166,162),'eyes':[(137,123,19,12),(196,120,19,12)]},
}
POSES=('rest','closed','a','e','o','soft')


def load_timeline(path=None):
    p=Path(path or OUT/'timeline.json')
    timeline=json.loads(p.read_text(encoding='utf8'))
    if not timeline or set(x['speaker'] for x in timeline)!={'Max','Mia'}:
        raise ValueError('Expected a 2-character Kokoro timeline')
    for row in timeline:
        if not 0<=row['start']<=row['end']<=DURATION+.05:
            raise ValueError('Timeline event outside 120-second programme')
    return timeline


def phoneme_pose(p):
    """Six restrained original-image visemes for speech-synchronized motion."""
    p=(p or '').lower().strip()
    if not p or p in (' ','ˈ','ˌ','ː','.','!','?',','):
        return 'rest'
    c=p[0]
    if c in 'mbp':return 'closed'
    if c in 'aɑæʌɐ':return 'a'
    if c in 'oɔʊuwɒ':return 'o'
    if c in 'eiɪɛɜɚə':return 'e'
    return 'soft'


def build_controls(timeline,fps=FPS,length=DURATION):
    n=int(round(fps*length))
    pose={who:['rest']*n for who in VOICE}
    line={who:[False]*n for who in VOICE}
    joke={who:[False]*n for who in VOICE}
    for row in timeline:
        who=row['speaker']
        first=max(0,int(math.floor(row['start']*fps)))
        last=min(n,int(math.ceil(row['end']*fps)))
        for f in range(first,last):
            line[who][f]=True
            joke[who][f]=bool(row.get('joke'))
        for entry in row.get('phones',[]):
            first=max(0,int(math.floor((entry['start']-.012)*fps)))
            last=min(n,int(math.ceil((entry['end']-.012)*fps)))
            v=phoneme_pose(entry['phone'])
            for f in range(first,last):pose[who][f]=v
    return pose,line,joke


def _rgba_source(who):
    src=ASSETS/f'{who}_Standing.png'
    if not src.is_file():
        raise FileNotFoundError(f'Missing character PNG: {src}. See episodes/vegetable_shop/README.md')
    im=Image.open(src).convert('RGBA')
    if im.getchannel('A').getextrema()==(255,255):
        raise ValueError('Character sprite requires real transparency')
    return im


def _eye_closed_patch(img,eyes):
    """Short soft blinks; paint an eyelid, never a full rectangular eye swap."""
    import cv2
    import numpy as np
    rgba=np.array(img)
    bgr=cv2.cvtColor(rgba[:,:,:3],cv2.COLOR_RGB2BGR)
    mask=np.zeros(bgr.shape[:2],dtype='uint8')
    for x,y,rx,ry in eyes:
        cv2.ellipse(mask,(x,y+2),(rx+2,ry+3),0,0,360,255,-1,cv2.LINE_AA)
    repaired=cv2.inpaint(bgr,mask,4,cv2.INPAINT_TELEA)
    for x,y,rx,ry in eyes:
        px=[(int(x+t),int(y+4+2*(1-(t/rx)**2))) for t in range(-rx+2,rx-1,2)]
        cv2.polylines(repaired,[np.array(px,dtype='int32')],False,(61,65,76),1,cv2.LINE_AA)
    out=cv2.cvtColor(repaired,cv2.COLOR_BGR2RGB)
    mask=cv2.GaussianBlur(mask,(0,0),3.4).astype('float32')[:,:,None]/255
    rgba[:,:,:3]=np.clip(rgba[:,:,:3]*(1-mask)+out*mask,0,255).astype('uint8')
    return Image.fromarray(rgba,'RGBA')


def _mouth_warp(im,mouth,pose):
    """Warp the painted *original* smile, retaining source color and teeth detail."""
    if pose=='rest':return im
    import cv2
    import numpy as np
    x,y=mouth
    # (source x-scale,source y-scale).  No invented solid-color ellipses.
    sx,sy={
        'closed':(1.0,1.60),'a':(1.0,.77),
        'e':(.82,.92),'o':(1.37,.78),'soft':(1.06,1.15)
    }[pose]
    rgba=np.array(im)
    x0=max(0,x-51);x1=min(rgba.shape[1],x+52)
    y0=max(0,y-30);y1=min(rgba.shape[0],y+30)
    region=rgba[y0:y1,x0:x1,:]
    xx,yy=np.meshgrid(np.arange(x0,x1,dtype='float32'),np.arange(y0,y1,dtype='float32'))
    dx=xx-x;dy=yy-y
    influence=np.exp(-((dx/31)**4+(dy/13)**4))
    mapx=xx+dx*(sx-1)*influence
    mapy=yy+dy*(sy-1)*influence
    warped=cv2.remap(rgba,mapx,mapy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    opacity=np.exp(-((dx/37)**4+(dy/19)**4))*.98
    rgba[y0:y1,x0:x1,:]=np.clip(region*(1-opacity[...,None])+warped*opacity[...,None],0,255).astype('uint8')
    return Image.fromarray(rgba,'RGBA')


def _gaze_shift(im,eyes,direction):
    if direction==0:return im
    import cv2
    import numpy as np
    rgba=np.array(im)
    for cx,cy,rx,ry in eyes:
        x0=max(0,cx-rx-5);x1=min(rgba.shape[1],cx+rx+6)
        y0=max(0,cy-ry-4);y1=min(rgba.shape[0],cy+ry+5)
        xx,yy=np.meshgrid(np.arange(x0,x1,dtype='float32'),np.arange(y0,y1,dtype='float32'))
        w=np.maximum(0,1-((xx-cx)/(rx+3))**2-((yy-cy)/(ry+3))**2)**2
        move=cv2.remap(rgba,xx-direction*2.0*w,yy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
        rgb=rgba[y0:y1,x0:x1,:]
        rgba[y0:y1,x0:x1,:]=np.uint8(rgb*(1-w[...,None])+move*w[...,None])
    return Image.fromarray(rgba,'RGBA')


class Actor:
    """Cache natural smiling mouth shapes, gaze directions and blink poses."""
    def __init__(self,who,height=650):
        self.who=who
        self.native=_rgba_source(who)
        self.scale=height/self.native.height
        self.width=max(1,round(self.native.width*self.scale))
        self.height=height
        self.face=FACES[who]
        self.cache={}
        self.closed_base=_eye_closed_patch(self.native,self.face['eyes'])
        # Native sprite is high resolution; all variants downscale with LANCZOS.

    def image(self,pose='rest',gaze=0,closed=False):
        key=(pose,gaze,closed)
        if key not in self.cache:
            source=self.closed_base if closed else self.native
            img=_mouth_warp(source,self.face['mouth'],pose)
            if not closed:img=_gaze_shift(img,self.face['eyes'],gaze)
            self.cache[key]=img.resize((self.width,self.height),Image.Resampling.LANCZOS)
        return self.cache[key]


def _fade_blink(t,who):
    # Vary spacing between blinks, avoid synchronized eye closures.
    offset=2.1 if who=='Max' else 3.6
    interval=4.9 if who=='Max' else 5.7
    phase=(t-offset)%interval
    if not 0<=phase<.17:return 0.0
    return math.sin(math.pi*phase/.17)**2


def _font(size=26):
    candidates=[
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
        'DejaVuSans.ttf'
    ]
    for p in candidates:
        try:return ImageFont.truetype(p,size)
        except OSError:continue
    return ImageFont.load_default()


def _subtitle_lines(text,draw,font,max_width=1060):
    words=text.split();lines=[];line=''
    for word in words:
        candidate=(line+' '+word).strip()
        if line and draw.textlength(candidate,font=font)>max_width:
            lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    return lines[:3]


def _title_and_captions(frame,t,timeline):
    d=ImageDraw.Draw(frame,'RGBA')
    scene=int(min(11,t//SCENE_SECONDS))
    age=t-scene*SCENE_SECONDS
    # Title placard fades out after 2.3 sec each new location.
    opacity=210 if age<1.65 else int(210*max(0,1-(age-1.65)/.65))
    if opacity>0:
        d.rounded_rectangle((20,17,483,77),radius=18,fill=(22,38,32,opacity))
        d.text((34,26),f'{scene+1:02}/12  {STOPS[scene][0]}',font=_font(23),fill=(255,251,223,opacity))
    # Small progress line: shows a real ten-second scene rhythm.
    d.rounded_rectangle((20,92,190,98),radius=3,fill=(255,255,255,90))
    d.rounded_rectangle((20,92,20+round(170*age/10),98),radius=3,fill=(251,199,101,226))
    row=next((r for r in timeline if r['start']-.025<=t<r['end']+.07),None)
    if row:
        label=row['speaker'].upper()
        font=_font(25)
        lines=_subtitle_lines(row['text'],d,font)
        h=47+31*(len(lines)-1)
        y0=HEIGHT-h-23
        d.rounded_rectangle((125,y0,1155,HEIGHT-12),radius=14,fill=(26,37,34,168))
        d.text((144,y0+9),label,font=_font(22),fill=(251,212,133,255) if label=='MAX' else (159,253,226,255))
        for i,line in enumerate(lines):
            d.text((720,y0+22+31*i),line,font=font,anchor='mm',fill=(255,255,249,255),stroke_width=2,stroke_fill=(34,39,34,235))
    return frame


def _actor_image(actor,pose,gaze,t,transition=None):
    sprite=actor.image(pose,gaze,False)
    if transition is not None:
        old,beta=transition
        if old!=pose and beta<1:
            sprite=Image.blend(actor.image(old,gaze,False),sprite,beta)
    blink=.78*_fade_blink(t,actor.who)
    if blink>.003:
        sprite=Image.blend(sprite,actor.image(pose,gaze,True),blink)
    return sprite


def render_frame(t,timeline,controls,actors,backgrounds):
    frameidx=min(len(controls[0]['Max'])-1,int(t*FPS))
    scene=min(len(STOPS)-1,int(t/SCENE_SECONDS))
    bg=backgrounds[scene]
    since=t-scene*SCENE_SECONDS
    # A gentle 0.26s cross dissolve exposes another clear location on every boundary.
    if scene>0 and since<.26:
        bg=Image.blend(backgrounds[scene-1],bg,since/.26)
    frame=bg.copy()
    pose,line,jokes=controls
    for who,actor in actors.items():
        p=pose[who][frameidx]
        old=pose[who][max(0,frameidx-1)]
        # Three-frame changeovers instead of one-frame lip snapping.
        run=0
        if old!=p:
            run=0
        else:
            for i in range(1,5):
                if frameidx-i<0 or pose[who][frameidx-i]!=p:break
                run=i
        transition=(pose[who][max(0,frameidx-run-1)],min(1,(run+1)/3.)) if run<3 else None
        # When one actor speaks, the other occasionally looks toward them.
        gazedir=(1 if who=='Max' else -1) if not line[who][frameidx] else 0
        if int(t*1.1)%4==0:gazedir=0
        sprite=_actor_image(actor,p,gazedir,t,transition)
        # Distinct, gentle joke responses; bodies stay standing, feet stay grounded.
        jitter=0.0
        for row in timeline:
            if row.get('joke') and abs(t-row['end'])<.38:
                if row['speaker']==who:
                    jitter+=2.8*math.exp(-abs(t-row['end'])*7)*math.sin((t-row['end'])*23)
                else:
                    jitter+=1.5*math.exp(-abs(t-row['end'])*7)*math.sin((t-row['end'])*16)
        sway=1.8*math.sin(t*.85+(0 if who=='Max' else 2.1))
        dy=round(sway+jitter)
        x=276 if who=='Max' else 826
        # Small location-specific movement makes them feel like visitors, not pasted posters.
        x+=int(10*math.sin(scene*.9+(0 if who=='Max' else 1.7)))
        y=HEIGHT-actor.height-23+dy
        frame.paste(sprite,(x,y),sprite)
    return _title_and_captions(frame,t,timeline)


def _make_contact(actors,timeline,controls,backgrounds,path):
    w,h=384,216
    result=Image.new('RGB',(w*4, (h+27)*3),(27,36,30))
    d=ImageDraw.Draw(result)
    for k,(name,_,_) in enumerate(STOPS):
        t=k*10+4.5
        fr=render_frame(t,timeline,controls,actors,backgrounds)
        small=fr.resize((w,h),Image.Resampling.LANCZOS)
        x=k%4*w;y=k//4*(h+27)
        result.paste(small,(x,y))
        d.text((x+6,y+h+2),f'{k*10:03}-{k*10+10:03}s  {name}',font=_font(16),fill=(249,245,219))
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    result.save(path,quality=91)


def audio_probe(path):
    import soundfile as sf
    info=sf.info(path)
    if abs(info.duration-DURATION)>.001 or info.samplerate!=48000 or info.channels!=2:
        raise ValueError(f'Expected a 120s/48kHz/stereo neural WAV, got {info}')
    return info


def render(seconds=DURATION,contact_only=False,quality=21):
    if not 0<seconds<=DURATION:raise ValueError('Duration must be within (0,120]')
    if len(STOPS)!=12 or SCENE_SECONDS*len(STOPS)!=DURATION:
        raise ValueError('Exactly 12 scenes each lasting 10 seconds required')
    timeline=load_timeline()
    audio=OUT/'vegetable_shop.wav'
    audio_probe(audio)
    actors={'Max':Actor('Max',height=648),'Mia':Actor('Mia',height=626)}
    backgrounds=[render_background(k) for k in range(12)]
    controls=build_controls(timeline)
    _make_contact(actors,timeline,controls,backgrounds,OUT/'Vegetable_Adventure_12_Places.jpg')
    (OUT/'journey_scenes.json').write_text(json.dumps({
        'total_seconds':DURATION,'fps':FPS,'scenes':[{
            'index':i+1,'start':10*i,'end':10*i+10,'location':name,'topic':topic,'setting':setting
        } for i,(name,topic,setting) in enumerate(STOPS)]},indent=2)+'\n',encoding='utf8')
    if contact_only:
        print('Created 12-location contact sheet');return None
    OUT.mkdir(parents=True,exist_ok=True)
    filename='Vegetable_Adventure_2_Minutes.mp4' if abs(seconds-120)<1e-5 else 'Vegetable_Adventure_Preview.mp4'
    video=OUT/filename
    command=['ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','rawvideo','-pix_fmt','rgb24','-s',f'{WIDTH}x{HEIGHT}','-framerate',str(FPS),'-i','pipe:0',
        '-i',str(audio),'-i',str(OUT/'vegetable_shop.srt'),
        '-map','0:v:0','-map','1:a:0','-map','2:s:0',
        '-c:v','libx264','-preset','ultrafast','-crf',str(quality),'-pix_fmt','yuv420p',
        '-c:a','aac','-b:a','224k','-c:s','mov_text','-t',f'{seconds:.3f}',
        '-movflags','+faststart',str(video)]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for i in range(round(seconds*FPS)):
            t=i/FPS
            frame=render_frame(t,timeline,controls,actors,backgrounds)
            proc.stdin.write(frame.tobytes())
            if i%300==0:print(f'Adventure frame {i}/{round(seconds*FPS)} (scene {int(t/10)+1}/12)',flush=True)
    except Exception:
        proc.kill();raise
    finally:
        if proc.stdin and not proc.stdin.closed:proc.stdin.close()
    if proc.wait():raise RuntimeError('FFmpeg encoding failed')
    print('Wrote',video,'bytes',video.stat().st_size)
    return video


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--contact-sheet',action='store_true',help='Preview all 12 locations without 120s encoding')
    p.add_argument('--preview-seconds',type=float,default=None)
    p.add_argument('--quality',type=int,default=21,help='H.264 CRF (smaller is better)')
    args=p.parse_args()
    render(args.preview_seconds or DURATION,contact_only=args.contact_sheet,quality=args.quality)

if __name__=='__main__':main()