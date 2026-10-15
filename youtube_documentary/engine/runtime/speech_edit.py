"""Sample-accurate pause edits. No speech time-stretch/pitch change.
All removals and source→output mappings are exposed for editorial audit.
"""
import numpy as np


def tighten(samples,words,sr=48000,explicit=(),threshold=.44,target=.26,fade_ms=4):
    x=np.asarray(samples)
    if x.ndim!=1 or sr<=0:raise ValueError('Mono samples and positive sample rate required')
    duration=len(x)/sr;cuts=[(float(a),float(b),'explicit phrase removal') for a,b in explicit]
    for left,right in zip(words,words[1:]):
        a,b=left['end'],right['start'];gap=b-a
        if gap<=threshold or any(a<d and b>c for c,d,_ in cuts):continue
        remove=gap-target;start=(a+b-remove)/2;end=start+remove
        # Protect margins around detected words, even if ASR timing is imperfect.
        if start<a+.07 or end>b-.07:continue
        section=x[round(start*sr):round(end*sr)]
        if not len(section) or np.sqrt(np.mean(section**2))>.018:continue
        cuts.append((start,end,'quiet pause shortened'))
    if words and words[0]['start']>.09:
        b=max(0,words[0]['start']-.07);section=x[:round(b*sr)]
        if len(section) and np.sqrt(np.mean(section**2))<=.018:cuts.append((0,b,'head silence'))
    if words and duration-words[-1]['end']>.14:
        a=words[-1]['end']+.10;section=x[round(a*sr):]
        if len(section) and np.sqrt(np.mean(section**2))<=.018:cuts.append((a,duration,'tail silence'))
    cuts=sorted(cuts);merged=[]
    for a,b,why in cuts:
        if not 0<=a<b<=duration:raise ValueError('Invalid source removal bounds')
        if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(b,merged[-1][1]),merged[-1][2]+'; '+why)
        else:merged.append((a,b,why))
    intervals=[];at=0
    for a,b,_ in merged:
        if a>at:intervals.append((round(at*sr),round(a*sr)))
        at=b
    if at<duration:intervals.append((round(at*sr),len(x)))
    result=np.array([],dtype=x.dtype);mapping=[];fade=round(sr*fade_ms/1000)
    for a,b in intervals:
        part=x[a:b].copy();n=min(fade,len(result),len(part));out_start=len(result)-n
        if n:
            ramp=np.linspace(0,1,n);result[-n:]=result[-n:]*(1-ramp)+part[:n]*ramp
        result=np.concatenate([result,part[n:]])
        mapping.append({'source_in':a/sr,'source_out':b/sr,'output_in':out_start/sr,'output_out':len(result)/sr})
    audit={'method':'Delete quiet pauses/explicit phrase;4ms boundary crossfades, no time stretching/pitch shift','original_duration':duration,'edited_duration':len(result)/sr,'cuts':[{'in':a,'out':b,'reason':why} for a,b,why in merged],'mapping':mapping}
    return result,audit


def map_time(t,mapping):
    for m in mapping:
        if m['source_in']<=t<=m['source_out']:return m['output_in']+t-m['source_in']
    return None
