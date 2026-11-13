"""Gentle, deterministic voice polishing and music ducking.

This is custom DSP, not a wrapper around a speech-enhancement service.
Requires numpy, scipy, soundfile and pyloudnorm. It does not synthesize speech.
Example: python improve_audio.py voice.wav polished.wav --music music.wav
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy import signal, ndimage

def db(value):
    return 20*np.log10(np.maximum(np.asarray(value),1e-12))

def resample(audio, source_rate, target_rate=48000):
    if source_rate==target_rate:return np.asarray(audio,dtype=np.float64)
    divisor=math.gcd(source_rate,target_rate)
    return signal.resample_poly(audio,target_rate//divisor,source_rate//divisor,axis=0)

def envelope(values,rate,attack=.010,release=.120):
    """Attack/release follower at a 200 Hz control rate, interpolated per sample."""
    hop=max(1,round(rate/200));n=len(values)
    points=np.arange(0,n,hop);sampled=np.asarray(values)[points]
    result=np.empty_like(sampled,dtype=float);last=float(sampled[0])
    up=np.exp(-hop/(rate*attack));down=np.exp(-hop/(rate*release))
    for i,value in enumerate(sampled):
        coefficient=up if value>last else down
        last=coefficient*last+(1-coefficient)*value;result[i]=last
    return np.interp(np.arange(n),points,result)

def peak_eq(audio,rate,frequency,gain_db,q):
    """RBJ peaking biquad; intentionally small corrections for clean neural speech."""
    A=10**(gain_db/40);w=2*np.pi*frequency/rate;alpha=np.sin(w)/(2*q)
    b=np.array([1+alpha*A,-2*np.cos(w),1-alpha*A])
    a=np.array([1+alpha/A,-2*np.cos(w),1-alpha/A])
    return signal.lfilter(b/a[0],a/a[0],audio,axis=0)

def soften_sibilance(audio,rate):
    """Reduce only unusually strong 5.2–10 kHz sibilance; maximum cut 2.7 dB."""
    upper=min(10000,rate*.44)
    if upper<=5300:return audio,0.0
    high=signal.sosfiltfilt(signal.butter(2,[5200,upper],btype='bandpass',fs=rate,output='sos'),audio)
    window=max(1,int(rate*.018))
    rms=np.sqrt(ndimage.uniform_filter1d(audio*audio,window)+1e-12)
    high_rms=np.sqrt(ndimage.uniform_filter1d(high*high,window)+1e-12)
    ratio=high_rms/np.maximum(rms,.001)
    reduction=np.clip((ratio-.29)*7,0,2.7)*(high_rms>.012)
    reduction=envelope(reduction,rate,.004,.065)
    return audio+high*(10**(-reduction/20)-1),float(reduction.max())

def gentle_compressor(audio,rate,threshold_db=-20,ratio=1.65,knee_db=6):
    rms=np.sqrt(ndimage.uniform_filter1d(audio*audio,max(1,int(rate*.012)))+1e-12)
    level=db(rms);over=level-threshold_db;k=knee_db
    reduction=np.where(over<=-k/2,0,
        np.where(over>=k/2,over*(1-1/ratio),((over+k/2)**2/(2*k))*(1-1/ratio)))
    reduction=np.minimum(reduction,4.5)
    reduction=envelope(reduction,rate,.008,.130)
    return audio*10**(-reduction/20),float(reduction.max())

def loudness(audio,rate):
    if len(audio)<rate*.4:return float(db(np.sqrt(np.mean(audio*audio)+1e-12)))
    return float(pyln.Meter(rate).integrated_loudness(audio))

def normalize_loudness(audio,rate,target=-18.5):
    measured=loudness(audio,rate)
    if not np.isfinite(measured):return audio
    gain=np.clip(target-measured,-18,18)
    return audio*10**(gain/20)

def true_peak(audio,rate):
    return float(np.max(np.abs(signal.resample_poly(audio,4,1,axis=0))))

def protect_true_peak(audio,rate,ceiling_db=-1.5):
    """Oversampled peak check followed by transparent gain reduction, never clipping."""
    peak=true_peak(audio,rate);ceiling=10**(ceiling_db/20)
    gain=min(1,ceiling/max(peak,1e-12))
    return audio*gain,float(db(gain))

def polish_voice(audio,rate,target_lufs=-18.5,low_cut=75):
    audio=np.asarray(audio,dtype=np.float64)
    if audio.ndim>1:audio=audio.mean(axis=1)
    if not len(audio):raise ValueError('The input audio is empty.')
    if not np.all(np.isfinite(audio)):raise ValueError('Non-finite input samples.')
    before=loudness(audio,rate)
    audio=audio-float(audio.mean())
    audio=signal.sosfiltfilt(signal.butter(2,low_cut,btype='highpass',fs=rate,output='sos'),audio)
    audio=peak_eq(audio,rate,230,-1.0,.75)
    audio=peak_eq(audio,rate,2800,.8,.7)
    audio,deess=soften_sibilance(audio,rate)
    audio,compression=gentle_compressor(audio,rate)
    audio=normalize_loudness(audio,rate,target_lufs)
    fade=min(int(rate*.008),len(audio)//4)
    if fade:
        ramp=np.sin(np.linspace(0,np.pi/2,fade))**2
        audio[:fade]*=ramp;audio[-fade:]*=ramp[::-1]
    audio,peak_gain=protect_true_peak(audio,rate,-1.5)
    return audio,{'before_lufs':before,'after_lufs':loudness(audio,rate),
        'maximum_deess_db':deess,'maximum_compression_db':compression,
        'peak_safety_gain_db':peak_gain,'true_peak_dbtp':float(db(true_peak(audio,rate)))}

def duck_music(voice,music,rate):
    """Smooth speech-driven attenuation; preserve the speech signal unchanged."""
    mono=voice.mean(axis=1) if voice.ndim==2 else voice
    rms=np.sqrt(ndimage.uniform_filter1d(mono*mono,max(1,int(rate*.025)))+1e-12)
    activity=np.clip((db(rms)+42)/16,0,1)
    activity=ndimage.maximum_filter1d(activity,max(1,int(rate*.060)))
    activity=envelope(activity,rate,.010,.280)
    gain=10**((-7-16*activity)/20)
    if music.ndim==2:gain=gain[:,None]
    return music*gain

def master(voice,rate,music=None,target_lufs=-16.5):
    voice=np.asarray(voice,float)
    if voice.ndim==1:voice=np.column_stack([voice,voice])
    mix=voice.copy()
    if music is not None:
        if music.ndim==1:music=np.column_stack([music,music])
        music=np.pad(music,((0,max(0,len(voice)-len(music))),(0,0)))[:len(voice)]
        music=normalize_loudness(music,rate,-25)
        mix+=duck_music(voice,music,rate)
    mix=normalize_loudness(mix,rate,target_lufs)
    mix,peak_gain=protect_true_peak(mix,rate,-1.5)
    return mix,{'sample_rate':rate,'duration':len(mix)/rate,
        'integrated_lufs':loudness(mix,rate),'true_peak_dbtp':float(db(true_peak(mix,rate))),
        'peak_safety_gain_db':peak_gain,'clipped_samples':int(np.count_nonzero(np.abs(mix)>=1))}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--music',type=Path);p.add_argument('--target-lufs',type=float,default=-16.5)
    args=p.parse_args();audio,sr=sf.read(args.input,dtype='float64')
    audio=resample(audio,sr,48000);sr=48000
    voice,details=polish_voice(audio,sr)
    bed=None
    if args.music:
        bed,bsr=sf.read(args.music,dtype='float64');bed=resample(bed,bsr,sr)
    result,report=master(voice,sr,bed,args.target_lufs)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    sf.write(args.output,result,sr,subtype='PCM_24')
    report['processing']=details
    args.output.with_suffix('.audio_report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()