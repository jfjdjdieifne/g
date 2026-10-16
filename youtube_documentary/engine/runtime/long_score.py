"""Shared section-scored documentary mix. Data chooses harmony/density/tempo.
No literal gunshots, explosions or fake historical location sound are synthesized.
"""
import numpy as np
from film_runtime import decode,wav,rms


def mix_sections(plan,build):
    sr=48000;D=plan['frames']/plan['fps'];n=round(D*sr);rng=np.random.default_rng(17101993)
    dialog=np.zeros(n);music=np.zeros(n);fx=np.zeros(n);audit=[]
    def add(dest,at,x,gain=1):
        a=round(at*sr)
        if a<0:x=x[-a:];a=0
        m=min(len(x),n-a)
        if m>0:dest[a:a+m]+=x[:m]*gain
    def tone(freq,length,attack=.012):
        t=np.arange(round(length*sr))/sr;p=2*np.pi*freq*t
        return (np.sin(p)+.23*np.sin(p*2.002)+.11*np.sin(p*3.001))*np.minimum(1,t/attack)*np.exp(-t/(length*.38))
    for c in plan['audio']:
        x=decode(c['file'],c.get('source_in',0),c.get('duration'));gain=min(.145/max(rms(x),1e-8),.78/max(abs(x)));add(dialog,c['start'],x,gain)
        audit.append({**c,'gain':gain,'input_rms':rms(x)})
    score_audit=[]
    for section in plan['score_sections']:
        start,end=section['start'],section['end'];bpm=section['bpm'];mode=section['mode'];root=section.get('root',73.416);beat=60/bpm;density=section.get('density',1)
        for i,at in enumerate(np.arange(start,end,beat/2)):
            # Distinct harmonic movement every 8 bars, with breathing spaces.
            semitone=[0,0,-2,3,0,-5,-2,-2][(i//32)%8];freq=root*2**(semitone/12)
            if mode=='sparse':
                if i%16==0:add(music,at,tone(freq,3.4,attack=.3),.075*density)
                if i%16==9:add(music,at,tone(freq*2,.9,attack=.07),.025*density)
            else:
                pattern=[0,3,6] if mode=='pressure' else [0,4,7]
                if i%8 in pattern:add(music,at,tone(freq,.34 if mode=='pressure' else .62),.12*density)
                if i%16==10:add(music,at,tone(freq*1.5,.7),.045*density)
                if i%4==0:
                    t=np.arange(round(.23*sr))/sr;tap=np.sin(2*np.pi*(43*t+1.2*(1-np.exp(-t/.025))))*np.exp(-t/.055);add(music,at,tap,.12*density)
                if i%4==2:
                    t=np.arange(round(.06*sr))/sr;noise=rng.normal(size=len(t));noise-=np.convolve(noise,np.ones(10)/10,'same');add(music,at,noise*np.exp(-t/.012),.012*density)
        # The pad is sectional, not the opening's hardcoded 0/8/16/24/30 loop.
        for at in np.arange(start,end,8*beat):
            for ratio in [1,1.189207,1.498307]:add(music,at,tone(root*ratio,min(8*beat,end-at+1),attack=.7),.027*density)
        score_audit.append(section)
    music*=.031/max(rms(music),1e-9)
    duck=np.ones(n)
    for c in plan['audio']:
        if c['kind']=='archive':
            a=max(0,round(c['start']*sr));b=min(n,round(c['end']*sr));duck[a:b]=.42
            fade=round(.16*sr)
            if a>=fade:duck[a-fade:a]=np.minimum(duck[a-fade:a],np.linspace(1,.42,fade))
            if b+fade<n:duck[b:b+fade]=np.minimum(duck[b:b+fade],np.linspace(.42,1,fade))
    for a,b in plan.get('music_holes',[]):duck[round(a*sr):round(b*sr)]=.12
    music*=duck
    effects=[]
    for cut in plan.get('effects',[]):
        t=np.arange(round(.18*sr))/sr;noise=rng.normal(size=len(t));noise=np.convolve(noise,np.ones(15)/15,'same');x=noise*np.sin(np.pi*t/.18)**2
        a=max(0,round((cut-.12)*sr));m=min(len(x),n-a);bed=rms(music[a:a+m]);x=x[:m]*(.38*bed/max(rms(x[:m]),1e-9));fx[a:a+m]+=x
        effects.append({'at':cut,'relative_to_local_music_db':20*np.log10(max(rms(x),1e-12)/max(bed,1e-12))})
    edge=round(.14*sr);music[:edge]*=np.linspace(0,1,edge);fade=round(1.3*sr);music[-fade:]*=np.linspace(1,0,fade)
    result=dialog+music+fx;result*=min(1,.92/max(abs(result)))
    for name,x in [('dialogue',dialog),('music',music),('editorial_fx',fx),('premix',result)]:wav(build/(name+'.wav'),x)
    return {'dialogue':audit,'score_sections':score_audit,'per_event_effects':effects,'music_rms':rms(music),'effects_rms':rms(fx),'music_type':'Original section-specific synthesized documentary score. Not source sound.','global_speedup':False,'native_archive_audio_retimed':False}
