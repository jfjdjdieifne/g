"""Explicit clause-level speech retiming, separate from speech_edit's no-stretch API.
Only original AI narration may use this stage. Never retime source witnesses.
Raw files remain untouched; all source/output intervals and factors are audited.
"""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from film_runtime import FF,decode,wav


def shape(source,words,destination,*,target_wpm=188.2,emphasis=(),pause=.16):
    """Group at real pauses, protect all samples between words, stretch per clause.
    ASR drives boundaries only; it is NOT a human-verified transcript.
    Emphasis is a list of contiguous word-index ranges [first,last_exclusive].
    """
    if not words or not 120<=target_wpm<=230:raise ValueError('Words and sane pacing required')
    source=Path(source);destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    x=decode(source);sr=48000;D=len(x)/sr;n=len(words)
    if any(w['end']<w['start'] or w['start']<0 or w['end']>D+.03 for w in words):raise ValueError('ASR bounds outside source')
    special={i for a,b in emphasis for i in range(a,b)}
    breaks={0,n}
    for a,b in emphasis:
        if not 0<=a<b<=n:raise ValueError('Invalid emphasis range')
        breaks.update([a,b])
    last=0
    for i in range(1,n):
        gap=words[i]['start']-words[i-1]['end']
        if (gap>.35 and i-last>=4) or (i-last>=18 and gap>.08):breaks.add(i);last=i
    cuts=sorted(breaks);out=[];audit=[];at=0
    for k,(a,b) in enumerate(zip(cuts,cuts[1:])):
        focus=all(i in special for i in range(a,b))
        # Preserve 60ms phoneme margins where there is space. Never remove words.
        left=0 if a==0 else (words[a-1]['end']+words[a]['start'])/2
        right=D if b==n else (words[b-1]['end']+words[b]['start'])/2
        start=max(left,words[a]['start']-.065);end=min(right,words[b-1]['end']+.08)
        if end<=start:raise ValueError('Overlapping/empty detected phrase')
        raw_rate=(b-a)/(end-start)*60
        factor=1.0 if focus else float(np.clip(target_wpm/raw_rate,1.02,1.45))
        buf=np.asarray(x[round(start*sr):round(end*sr)],dtype='<f4').tobytes()
        data=subprocess.check_output([FF,'-v','error','-f','f32le','-ar',str(sr),'-ac','1','-i','pipe:0','-af',f'atempo={factor:.8f}','-f','f32le','pipe:1'],input=buf)
        y=np.frombuffer(data,dtype='<f4').astype(float).copy()
        fade=min(round(.003*sr),len(y)//2);ramp=np.linspace(0,1,fade)
        if fade:y[:fade]*=ramp;y[-fade:]*=ramp[::-1]
        after=0 if b==n else min(pause,max(.055,words[b]['start']-words[b-1]['end']))
        if focus:after=min(.19,after+.025)
        audit.append({'word_first':a,'word_last_exclusive':b,'text_asr':' '.join(w['word'] for w in words[a:b]),'source_in':start,'source_out':end,'tempo_factor':factor,'emphasis':focus,'output_in':at,'output_out':at+len(y)/sr,'pause_after':after})
        out.extend([y,np.zeros(round(after*sr))]);at+=len(y)/sr+round(after*sr)/sr
    result=np.concatenate(out);wav(destination,result)
    report={'method':'Pitch-preserving clause retiming of AI narration; original slower raws retained. Not faster raw acting. No archive witnesses retimed.','source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_seconds':D,'output_seconds':len(result)/sr,'recognized_words':n,'overall_recognized_wpm':n/(len(result)/sr)*60,'target_clause_wpm':target_wpm,'regions':audit,'manual_listening_claimed':False}
    destination.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
