"""Original rhythm score and editorial transitions; not purported archive sound.
Reusable synthesis/mix primitives. The project chooses tempo, entrances and cuts.
"""
import numpy as np
from film_runtime import decode,rms,wav

def mix(plan,build,bpm=144):
    if plan.get('score_sections'):
        from long_score import mix_sections
        return mix_sections(plan,build)
    sr=48000;D=plan['frames']/plan['fps'];n=round(D*sr);t=np.arange(n)/sr;rng=np.random.default_rng(506)
    dialog=np.zeros(n);music=np.zeros(n);fx=np.zeros(n);audit=[]
    for c in plan['audio']:
        x=decode(c['file']);gain=min(.145/max(rms(x),1e-8),.78/max(abs(x)));at=round(c['start']*sr);m=min(len(x),n-at);dialog[at:at+m]+=x[:m]*gain
        audit.append({**c,'gain':gain,'input_rms':rms(x)})
    def add(dest,at,x,gain=1):
        a=round(at*sr)
        if a>=n:return
        if a<0:x=x[-a:];a=0
        m=min(len(x),n-a);dest[a:a+m]+=x[:m]*gain
    def tone(freq,length,attack=.01):
        u=np.arange(round(length*sr))/sr;phase=2*np.pi*freq*u
        # Detuned bowed/saw-like harmonics, not a single sustained sine.
        a=sum(np.sin(phase*k+np.sin(2*np.pi*.3*u)*.018*k)/k**1.55 for k in range(1,9))
        a+=.22*np.sin(phase*1.003);return a*np.minimum(1,u/attack)*np.exp(-u/(length*.40))
    beat=60/bpm;notes=[73.416,73.416,87.307,69.296,73.416,65.406,69.296,65.406]
    for i,at in enumerate(np.arange(0,D,beat/2)):
        # Syncopated low strings with deliberate holes for archive voices.
        if i%8 in [0,1,3,4,6]:add(music,at,tone(notes[(i//8)%len(notes)],.30),.35 if i%8==0 else .22)
        if i%8 in [0,3,6]:add(music,at+.015,tone(notes[(i//8)%8]*2,.17),.09)
    for i,at in enumerate(np.arange(0,D,beat)):
        u=np.arange(round(.28*sr))/sr
        kick=np.sin(2*np.pi*(47*u+29*.035*(1-np.exp(-u/.035))))*np.exp(-u/.075)
        add(music,at,kick,.37 if i%4==0 else .24)
        if i%4 in [1,3]:
            noise=rng.normal(size=len(u));noise=np.convolve(noise,np.ones(3)/3,'same');add(music,at+.003,noise*np.exp(-u/.035),.12)
    for i,at in enumerate(np.arange(0,D,beat/2)):
        u=np.arange(round(.055*sr))/sr;noise=rng.normal(size=len(u));noise-=np.convolve(noise,np.ones(15)/15,'same');add(music,at,noise*np.exp(-u/.009),.035 if i%2==0 else .018)
    # Suspended minor chord instead of a victorious ending/outcome payoff.
    for at in [0,8,16,24,30]:
        for f in [146.832,174.614,220]:add(music,at,tone(f,min(6,D-at),attack=.5),.045)
    for cut in plan['effects']:
        u=np.arange(round(.20*sr))/sr;noise=rng.normal(size=len(u));noise=np.convolve(noise,np.ones(12)/12,'same');swish=noise*np.sin(np.pi*np.minimum(1,u/.2))**2
        add(fx,max(0,cut-.14),swish,.7)
    # Music falls back when a source witness speaks, without changing that voice.
    duck=np.ones(n)
    for c in plan['audio']:
        if c['kind']=='archive':
            a=round(c['start']*sr);b=round(c['end']*sr);duck[a:b]=.57
    music*=duck
    music*=.040/max(rms(music),1e-9)
    # Each transition effect must stay at least 7.9 dB under its local music window.
    effect_levels=[]
    for cut in plan['effects']:
        a=max(0,round((cut-.14)*sr));b=min(n,round((cut+.06)*sr));level=rms(fx[a:b]);bed=rms(music[a:b]);fx[a:b]*=min(1,.40*bed/max(level,1e-9));effect_levels.append({'at':cut,'relative_to_local_music_db':20*np.log10(max(rms(fx[a:b]),1e-12)/max(bed,1e-12))})
    # Avoid a fixed-wall beat on every picture cut. Sound effects are editorial.
    envelope=np.minimum(1,t/.07)*np.minimum(1,np.maximum(0,D-t)/.25);music*=envelope;fx*=envelope
    y=dialog+music+fx;y*=min(1,.92/max(abs(y)))
    wav(build/'dialogue.wav',dialog);wav(build/'music.wav',music);wav(build/'editorial_fx.wav',fx);wav(build/'premix.wav',y)
    return {'dialogue':audit,'per_event_effects':effect_levels,'music_rms':rms(music),'effects_rms':rms(fx),'effects_vs_music_db':20*np.log10(rms(fx)/rms(music)),'music_type':'Original synthesized 144 BPM minor-key industrial pulse; editorial effects, not archive location sound.','global_speedup':False}
