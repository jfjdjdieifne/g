#!/usr/bin/env python3
"""Rebuild a film's processed narration from preserved raw takes and audited ASR.
No new voice synthesis. Never overwrite raw recordings or speed up source witnesses.
"""
import argparse,json,sys,hashlib,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'engine/runtime'))
from film_runtime import FF
from speech_pacing import shape
p=argparse.ArgumentParser();p.add_argument('profile');p.add_argument('--raw-dir',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
project=ROOT/'engine/projects'/a.profile;audits=json.loads((project/'narration_pacing.json').read_text());a.output_dir.mkdir(parents=True,exist_ok=True)
for key,old in audits.items():
    source=a.raw_dir/(key+'_raw.wav')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=old['source_sha256']:raise ValueError('Preserved take does not match audit: '+key)
    j=json.loads((project/'narration'/(key+'_raw.asr.json')).read_text());words=[w for s in j['segments']for w in s.get('result',[])]
    emphasis=[(r['word_first'],r['word_last_exclusive'])for r in old['regions']if r['emphasis']]
    dest=a.output_dir/(key+'.wav');result=shape(source,words,dest,target_wpm=old['target_clause_wpm'],emphasis=emphasis,pause=.16)
    subprocess.run([FF,'-v','error','-y','-i',str(dest),'-c:a','flac',str(dest.with_suffix('.flac'))],check=True)
    print(key,result['output_seconds'],result['overall_recognized_wpm'],flush=True)
