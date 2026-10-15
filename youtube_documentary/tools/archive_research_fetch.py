#!/usr/bin/env python3
"""Retrieve a bounded, unreferenced research object from our session CI job.
No media is added to a branch/release or treated as rights-cleared. Public job
metadata is read without privileged Actions credentials. Auth stays inside gh.
"""
import argparse
import base64
import io
import json
import re
import subprocess
import tarfile
import time
import urllib.request
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--run',type=int,required=True);p.add_argument('--prefix',default='Research object ');p.add_argument('--out',type=Path,required=True);args=p.parse_args()
base='https://api.github.com/repos/jfjdjdieifne/g'
for attempt in range(28):
    with urllib.request.urlopen(base+f'/actions/runs/{args.run}/jobs',timeout=20) as r:data=json.load(r)
    jobs=data.get('jobs',[])
    for job in jobs:
        for step in job.get('steps',[]):
            if not step['name'].startswith(args.prefix):continue
            match=re.search(r'\b[a-f0-9]{40}\b',step['name'])
            if not match:continue
            sha=match.group();print('RETRIEVING',sha,flush=True)
            raw=subprocess.check_output(['gh','api',f'repos/jfjdjdieifne/g/git/blobs/{sha}'])
            blob=json.loads(raw);payload=base64.b64decode(blob['content'])
            args.out.mkdir(parents=True,exist_ok=True)
            with tarfile.open(fileobj=io.BytesIO(payload),mode='r:gz') as tar:
                for member in tar.getmembers():
                    if not member.isfile() or Path(member.name).name!=member.name:raise RuntimeError('Unexpected archive member')
                    if member.size>100_000_000:raise RuntimeError('Member size cap exceeded')
                    (args.out/member.name).write_bytes(tar.extractfile(member).read())
            (args.out/'retrieval.json').write_text(json.dumps({'run':args.run,'blob_sha':sha,'rights_cleared':False,'viewed':False,'heard':False},indent=2)+'\n')
            print('RESEARCH_READY',args.out,flush=True);raise SystemExit(0)
    if jobs and all(j['status']=='completed' for j in jobs):raise SystemExit('Job ended without a retrievable research object: '+str([(j['name'],j['conclusion']) for j in jobs]))
    print('Waiting for research job',args.run,attempt,flush=True);time.sleep(25)
raise SystemExit('Research retrieval timed out; remote job may still be running. Inspect before retry.')
