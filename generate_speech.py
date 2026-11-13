from pathlib import Path
import json,dataclasses,time
import numpy as np
import onnxruntime as ort
import soundfile as sf
from kokoro_onnx import Kokoro
from improve_audio import polish_voice,resample,master

ROOT=Path(__file__).resolve().parent;WORK=ROOT/'work';OUT=ROOT/'deliverables'
WORK.mkdir(exist_ok=True);OUT.mkdir(exist_ok=True)
SCRIPT=[
 ('Mia',"Let's meet three flowers!",'intro'),
 ('Max','Do they tell jokes?','intro'),
 ('Mia','This is a rose.','rose'),
 ('Max','A rose with a nose?','rose'),
 ('Mia','No, silly! Just lovely petals.','rose'),
 ('Mia','This is a sunflower.','sunflower'),
 ('Max','Does it need sunglasses?','sunflower'),
 ('Mia','Maybe yours! And this is a tulip.','tulip'),
 ('Max','Two lips? Can it whistle?','tulip'),
 ('Mia',"Tulip! It's a flower!",'tulip'),
 ('Max','Rose, sunflower, tulip!','recap'),
 ('Mia',"Now you're a flower expert!",'recap'),
]
options=ort.SessionOptions();options.intra_op_num_threads=2;options.inter_op_num_threads=1
options.log_severity_level=3
session=ort.InferenceSession(str(ROOT/'models/kokoro-v1.0.fp16.onnx'),options,providers=['CPUExecutionProvider'])
engine=Kokoro.from_session(session,str(ROOT/'models/voices-v1.0.bin'))
assert engine.has_timings,'The downloaded model must provide phoneme durations.'
VOICES={'Mia':'af_heart','Max':'am_puck'}

def synthesize(speed,pass_no):
    clips=[]
    for j,(char,text,scene) in enumerate(SCRIPT):
        a,sr,phones=engine.create_timed(text,voice=VOICES[char],speed=speed,
            lang='en-us',sentence_pause=.12,clause_pause=.075)
        path=WORK/f'neural_raw_{j:02}.wav';sf.write(path,a,sr,subtype='FLOAT')
        clip={'character':char,'text':text,'scene':scene,'audio':a,'rate':sr,
            'phones':[dataclasses.asdict(p) for p in phones]}
        clips.append(clip)
        print(f'Voice pass {pass_no}: {j+1}/12, {char}, {len(a)/sr:.2f}s',flush=True)
    return clips

clips=synthesize(.96,1)
speech_time=sum(len(c['audio'])/c['rate'] for c in clips)
lead=.45;tail=.65;min_gap=.24;max_gap=.52
target_speech=30-lead-tail-11*.34
if not 30-lead-tail-11*max_gap <= speech_time <= 30-lead-tail-11*min_gap:
    speed=np.clip(.96*speech_time/target_speech,.80,1.20)
    clips=synthesize(float(speed),2)
    speech_time=sum(len(c['audio'])/c['rate'] for c in clips)
else:speed=.96
gap=(30-lead-tail-speech_time)/11
if not .10<=gap<=.70:raise RuntimeError(f'Unnatural timing budget: {gap:.3f}s gaps. Revise the script.')

SR=48000;voice=np.zeros((SR*30,2),float);timeline=[];reports=[];cursor=lead
for j,c in enumerate(clips):
    clean,report=polish_voice(c['audio'],c['rate'],target_lufs=-18.5,
        low_cut=85 if c['character']=='Mia' else 70)
    clean=resample(clean,c['rate'],SR);sf.write(WORK/f'neural_clean_{j:02}.wav',clean,SR,subtype='PCM_24')
    start=round(cursor*SR);end=start+len(clean)
    if end>len(voice):raise RuntimeError('Dialogue would be cut off.')
    pan=.05 if c['character']=='Mia' else -.05
    voice[start:end,0]+=clean*(1-pan);voice[start:end,1]+=clean*(1+pan)
    row={k:c[k] for k in ['character','text','scene']};row.update(start=cursor,end=end/SR)
    row['phones']=[{'phone':p['phoneme'],'start':cursor+p['start'],'end':cursor+p['end']} for p in c['phones']]
    timeline.append(row);reports.append(dict(line=j+1,character=c['character'],**report))
    cursor=end/SR+(gap if j<11 else 0)

# An original, sparse, warm instrumental bed; automatically ducked under speech.
music=np.zeros_like(voice)
def note(at,freq,gain=.025,duration=2.0,pan=0):
    t=np.arange(round(duration*SR))/SR
    attack=np.minimum(t/.012,1)
    sound=sum((1/(k*k))*np.sin(2*np.pi*freq*k*t)*np.exp(-t*(1.8+k*.45)) for k in range(1,5))*attack*gain
    i=round(at*SR);n=min(len(sound),len(music)-i)
    if n>0:music[i:i+n]+=np.column_stack([sound[:n]*(1-pan),sound[:n]*(1+pan)])
for bar in range(8):
    root=[130.81,146.83,164.81,130.81][bar%4]
    for k,ratio in enumerate([1,1.5,2.5]):note(bar*4+k*.7,root*ratio,.022,2.6,(-.3 if k%2 else .3))
for k,n in enumerate([523.25,659.25,783.99,1046.5]):note(28.7+k*.2,n,.018,.8)
music[:SR//3]*=np.linspace(0,1,SR//3)[:,None];music[-SR//2:]*=np.linspace(1,0,SR//2)[:,None]
sf.write(WORK/'music.wav',music,SR,subtype='PCM_24')
sf.write(WORK/'dialogue.wav',voice,SR,subtype='PCM_24')
audio,report=master(voice,SR,music,target_lufs=-16.5)
sf.write(WORK/'audio.wav',audio,SR,subtype='PCM_24')
sf.write(OUT/'Flower_Friends_Improved_Audio.wav',audio,SR,subtype='PCM_24')
report.update(engine='Kokoro ONNX 0.6.1 / v1.0 fp16, local CPU',voices=VOICES,
    native_synthesis_speed=float(speed),interline_pause_seconds=float(gap),last_word_end=cursor,line_processing=reports)
(WORK/'audio_report.json').write_text(json.dumps(report,indent=2))
(WORK/'timeline.json').write_text(json.dumps(timeline,indent=2))
def stamp(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(OUT/'Flower_Friends_Cinematic_Subtitles.srt').write_text('\n\n'.join(f"{j+1}\n{stamp(r['start'])} --> {stamp(r['end']+.08)}\n{r['text']}" for j,r in enumerate(timeline))+'\n')
(OUT/'Flower_Friends_Script.txt').write_text('\n'.join(f"{r['start']:.2f}–{r['end']:.2f}  {r['character']}: {r['text']}" for r in timeline)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='line_processing'},indent=2),flush=True)