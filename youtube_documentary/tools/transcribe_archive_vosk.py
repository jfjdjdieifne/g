#!/usr/bin/env python3
"""Local CPU speech inspection aid. ASR is NOT a verified quotation/listening.
Model data must already exist; no network, no fabricated newsreader.
"""
import argparse
import json
import subprocess
from pathlib import Path
import imageio_ffmpeg
from vosk import Model,KaldiRecognizer,SetLogLevel

p=argparse.ArgumentParser();p.add_argument('video',type=Path);p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
SetLogLevel(-1);model=Model(str(args.model));rec=KaldiRecognizer(model,16000);rec.SetWords(True)
proc=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(args.video),'-vn','-ac','1','-ar','16000','-f','s16le','-'],stdout=subprocess.PIPE)
rows=[]
while True:
    chunk=proc.stdout.read(8000)
    if not chunk:break
    if rec.AcceptWaveform(chunk):
        result=json.loads(rec.Result())
        if result.get('text'):rows.append(result)
result=json.loads(rec.FinalResult())
if result.get('text'):rows.append(result)
if proc.wait():raise RuntimeError('Audio decode failed')
args.out.parent.mkdir(parents=True,exist_ok=True)
args.out.write_text(json.dumps({'method':'Automatic Vosk small-en ASR; fallible, NOT independently verified quotations or listening','source':str(args.video),'segments':rows},indent=2)+'\n')
for row in rows:
    words=row.get('result',[])
    if words:print(f'{words[0]["start"]:.2f}–{words[-1]["end"]:.2f}: {row["text"]}')
