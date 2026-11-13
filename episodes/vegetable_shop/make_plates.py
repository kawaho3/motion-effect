"""Build *illustrative preview* mouth/blink plates from the original concept.

These procedural expressions are for evaluating timing and alignment, NOT an
artist's final painted facial poses. Always review the exported close-up.
"""
from pathlib import Path
import json
import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
ART = HERE / 'assets'
BASE = ART / 'Scene_Concept.jpg'
FACES = {
    'Max': {'mouth':(458,102,10,4), 'eyes':[(438,75,9,6),(468,76,9,6)]},
    'Mia': {'mouth':(797,139,12,5), 'eyes':[(771,118,9,6),(813,117,9,6)]},
}

def paint_mouth(canvas, center, shape):
    x,y,rx,ry=center
    # Locally reconstruct skin under the existing smile before replacing only lips.
    img=canvas.copy()
    mask=np.zeros(img.shape[:2],np.uint8)
    cv2.ellipse(mask,(x,y),(rx+1,ry+1),0,0,360,255,-1,cv2.LINE_AA)
    clean=cv2.inpaint(img,mask,4,cv2.INPAINT_TELEA)
    canvas[:]=clean
    overlay=canvas.copy()
    if shape=='AH':
        # Deliberately restrained lip opening. Retain face texture/teeth, avoid giant ovals.
        sx, sy = max(4,int(rx*.72)), max(2,int(ry*.95))
        cv2.ellipse(overlay,(x,y+1),(sx,sy),0,0,360,(79,83,111),-1,cv2.LINE_AA)
        cv2.line(overlay,(x-sx+2,y-sy+1),(x+sx-2,y-sy+1),(217,221,224),1,cv2.LINE_AA)
    else:
        sx,sy=max(3,int(rx*.43)),max(3,int(ry*.92))
        cv2.ellipse(overlay,(x,y+1),(sx,sy),0,0,360,(75,74,105),-1,cv2.LINE_AA)
        cv2.ellipse(overlay,(x,y+1),(max(2,sx-1),max(2,sy-1)),0,0,360,(57,55,87),1,cv2.LINE_AA)
    blend=np.zeros(img.shape[:2],dtype=np.float32)
    cv2.ellipse(blend,(x,y),(rx+3,ry+4),0,0,360,0.82,-1,cv2.LINE_AA)
    blend=cv2.GaussianBlur(blend,(0,0),1.7)[...,None]
    canvas[:]=np.uint8(np.clip(canvas*(1-blend)+overlay*blend,0,255))

def paint_blink(canvas, eye):
    x,y,rx,ry=eye
    before=canvas.copy()
    mask=np.zeros(canvas.shape[:2],np.uint8)
    cv2.ellipse(mask,(x,y),(rx,ry),0,0,360,255,-1,cv2.LINE_AA)
    clean=cv2.inpaint(canvas,mask,5,cv2.INPAINT_TELEA)
    alpha=cv2.GaussianBlur(mask,(0,0),1.8).astype('float32')[...,None]/255
    canvas[:]=np.uint8(np.clip(before*(1-alpha)+clean*alpha,0,255))
    # Upper eyelid curve, using dark warm watercolor lash color from the drawing.
    cv2.ellipse(canvas,(x,y+1),(rx,3),0,195,350,(52,65,70),1,cv2.LINE_AA)

def main():
    image=cv2.imread(str(BASE))
    if image is None: raise FileNotFoundError(BASE)
    if image.shape[1::-1] != (1280,720):raise ValueError('Calibrated for 1280x720 concept art')
    ah=image.copy();oh=image.copy()
    for who,params in FACES.items():
        paint_mouth(ah,params['mouth'],'AH')
        paint_mouth(oh,params['mouth'],'OH')
        for eye in params['eyes']:
            paint_blink(ah,eye)
    cv2.imwrite(str(ART/'Scene_Base.jpg'),image,[cv2.IMWRITE_JPEG_QUALITY,94])
    cv2.imwrite(str(ART/'Scene_Ah_Blink.jpg'),ah,[cv2.IMWRITE_JPEG_QUALITY,94])
    cv2.imwrite(str(ART/'Scene_Oh.jpg'),oh,[cv2.IMWRITE_JPEG_QUALITY,94])
    rig={}
    W,H=1280,720
    for who,p in FACES.items():
        x,y,rx,ry=p['mouth']
        def norm(box):return [round(box[0]/W,6),round(box[1]/H,6),round(box[2]/W,6),round(box[3]/H,6)]
        rig[who]={'mouth':norm((x-rx-5,y-ry-6,x+rx+6,y+ry+7)),
                  'eyes':[norm((a-b-4,c-d-4,a+b+5,c+d+5)) for a,c,b,d in p['eyes']]}
    (ART/'rig.json').write_text(json.dumps(rig,indent=2)+'\n')
    print('Generated preview plates; inspect faces before publishing')

if __name__=='__main__':main()