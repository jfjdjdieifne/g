#!/usr/bin/env python3
"""Mix session-selected narration with a restrained cold-open score and sparse factual accents."""
import math, subprocess
from pathlib import Path
import numpy as np
import imageio_ffmpeg

ROOT=Path(__file__).parent
VOICE=ROOT/'voice_take_v1.mp3'; OUT=ROOT/'audio_mix_v1.wav'
SR=48000; DURATION=48.98; N=int(SR*DURATION)
ff=imageio_ffmpeg.get_ffmpeg_exe()
raw=subprocess.run([ff,'-v','error','-i',str(VOICE),'-f','f32le','-ac','1','-ar',str(SR),'-'],stdout=subprocess.PIPE,check=True).stdout
voice=np.frombuffer(raw,dtype='<f4').copy()
if len(voice)<N: voice=np.pad(voice,(0,N-len(voice)))
voice=voice[:N]
# Speech source is preserved as generated; set an even, broadcast-safe level without speed/pitch change.
rms=np.sqrt(np.mean(voice**2)); voice*=0.105/max(rms,1e-8)
# Cold-open bed from the project sound-bank direction: D-minor low strings, soft pulse, no melody.
t=np.arange(N,dtype=np.float64)/SR
fade=np.minimum(1,t/0.8)*np.minimum(1,(DURATION-t)/1.5)
intensity=np.interp(t,[0,8.5,25,38,DURATION],[0.45,0.48,0.64,0.52,0.35])
trem=0.78+0.22*np.sin(2*np.pi*5.1*t+0.3)
# Detuned low-string partials; narrow and deliberately quiet beneath the dialogue.
strings=(0.48*np.sin(2*np.pi*73.42*t)+0.25*np.sin(2*np.pi*110.0*t+0.2)+0.16*np.sin(2*np.pi*146.83*t+0.4)+0.07*np.sin(2*np.pi*220.5*t+0.6))
# Slightly rising held fifths during the widening of the crisis, then resolve to the opening sonority.
strings += np.where((t>16.5)&(t<38),0.17*np.sin(2*np.pi*174.61*t+0.1),0.0)
score=0.012*intensity*fade*trem*strings
# 90 BPM felt pulses, not a clock tick: each falls only at meaningful beats and stays very low.
beat=60/90
for k in range(1,int(DURATION/beat)):
    at=k*beat
    env=np.exp(-np.maximum(0,t-at)*18)*(t>=at)*(t<at+0.20)
    score += 0.0026*env*np.sin(2*np.pi*(57-12*np.minimum(1,(t-at)/0.20))*np.maximum(0,t-at))
# Sparse custom low impacts on actual declared-war/invasion cues; no whoosh on every camera move.
for at,gain,f0,f1 in [(8.65,0.007,69,48),(17.2,0.005,64,46),(24.4,0.0075,74,45)]:
    u=t-at; mask=(u>=0)&(u<0.68); dur=np.maximum(u,0)
    freq=f0*(f1/f0)**(dur/0.68)
    phase=2*np.pi*np.cumsum(freq)/SR
    env=np.exp(-dur*7)*mask
    score += gain*env*np.sin(phase)
# Dialogue centered; score kept far below it. Gentle master soft clip only catches summed peaks.
mix=np.stack([voice+score*0.92,voice+score*1.08],axis=1)
mix=np.tanh(mix*1.03)/1.03
peak=np.max(np.abs(mix));
if peak>0.86: mix*=0.86/peak
pcm=(mix*32767).astype('<i2')
import wave
with wave.open(str(OUT),'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f'Wrote {OUT}; voice source RMS={rms:.6f}; mix peak={peak:.4f}; duration={len(pcm)/SR:.3f}s')
