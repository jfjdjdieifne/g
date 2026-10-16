#!/usr/bin/env python3
"""Compact portable film-source/raw-voice/review capsule, not a dependency bundle.
Requires an explicit actual-encode visual-inspection receipt. Cold checks are only
source/declaration/hash checks: they never certify listening or artistic approval.
"""
import sys,json,zipfile,tempfile,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
p,video,review_dir,raw_dir,out=map(lambda s:Path(s).resolve(),sys.argv[1:6])
digest=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
inspection=json.loads((p/'review_inspection.json').read_text());assert inspection['video_sha256']==digest(video) and inspection['visual_inspection_status']=='inspected'
assert inspection['manual_listening_claimed'] is False
files={}
def add(f,name=None):
 f=Path(f)
 if f.is_file():files[name or str(f.relative_to(REPO))]=f
for f in p.rglob('*'):
 # Raw takes have one canonical capsule location, even when stored in-profile.
 if raw_dir in f.resolve().parents:continue
 if '__pycache__' not in f.parts and f.suffix not in ['.pyc'] and f.name not in ['recovery_local_receipt.json']:add(f)
for f in (ROOT/'engine/runtime').glob('*'):
 if f.suffix in ['.py','.mjs','.json']:add(f)
for n in ['render_webgl_profile.mjs','mix_webgl_profile.py','review_webgl_profile.py','replace_picture_frames.py','package_webgl_profile.py','install_webgl_runtime.py','transcribe_archive_vosk.py','production_policy.py','style_contract.py','documentary_materials.py']:add(ROOT/'tools'/n)
add(ROOT/'tools/tests/test_traffic_motion.mjs');add(ROOT/'tools/tests/test_horizon_motion.mjs');add(ROOT/'tools/tests/test_documentary_materials.py')
for f in ['AGENTS.md','START_HERE.md']:add(ROOT/f)
add(REPO/'AGENTS.md')
for f in ['STYLE_REGISTRY.json','STYLE_GUIDE.md','PRODUCTION_POLICY.json','EDITORIAL_REVIEW_PROTOCOL.md','ENGINES.json']:add(ROOT/'engine'/f)
for f in ['DejaVuSans.ttf','DejaVuSans-Bold.ttf','DejaVu_LICENSE.txt']:add(ROOT/'assets_global/fonts'/f)
for f in raw_dir.glob('*_raw.wav'):add(f,'raw_voice/'+f.name)
for f in review_dir.glob('*sheet_*.jpg'):add(f,'encoded_review/'+f.name)
for f in review_dir.glob('native_*.png'):add(f,'encoded_review/'+f.name)
for n in ['audit.json','loudness.json','full_decode.log','review_spec.json','final.asr.json']:add(review_dir/n,'encoded_review/'+n)
manifest=json.loads((p/'source_manifest.json').read_text())
for row in manifest['files']:
 if 'capsule_path' in row:assert digest(files[row['capsule_path']])==row['sha256']
 if 'path' in row:assert digest(files[row['path']])==row['sha256'],row['path']
index={k:{'bytes':f.stat().st_size,'sha256':digest(f)}for k,f in sorted(files.items())}
out.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
 for name,f in sorted(files.items()):z.write(f,name)
 z.writestr('CAPSULE_INDEX.json',json.dumps({'film_sha256':digest(video),'scope':'Film recovery only. Final film stored separately; dependencies installed externally. No claim of ear-listening or user approval.','files':index},indent=2))
with tempfile.TemporaryDirectory(prefix='film-cold-check-')as d:
 d=Path(d)
 with zipfile.ZipFile(out)as z:z.extractall(d)
 for name,row in index.items():assert digest(d/name)==row['sha256'],name
 project=d/p.relative_to(REPO)
 commands=[[sys.executable,str(d/'youtube_documentary/tools/style_contract.py'),'check','--project',str(project)],[sys.executable,str(d/'youtube_documentary/tools/production_policy.py'),str(project/'display_manifest.json')],['node',str(d/'youtube_documentary/tools/tests/test_traffic_motion.mjs')],['node','--check',str(d/'youtube_documentary/tools/render_webgl_profile.mjs')]]
 if (d/'youtube_documentary/tools/tests/test_horizon_motion.mjs').exists():commands.append(['node',str(d/'youtube_documentary/tools/tests/test_horizon_motion.mjs')])
 commands.append(['node','--check',str(project/'scene.mjs')])
 logs=[]
 for command in commands:
  r=subprocess.run(command,cwd=d,capture_output=True,text=True,check=True);logs.append('$ '+' '.join(command)+'\n'+r.stdout+r.stderr)
 log='Fresh independent extraction. Every included file hash checked. No render/ear-listening/art-approval claim.\n\n'+'\n'.join(logs)
(p/'recovery_cold_check.log').write_text(log)
r={'path':str(out),'bytes':out.stat().st_size,'sha256':digest(out),'md5':hashlib.md5(out.read_bytes()).hexdigest(),'included_files':len(files),'cold_checks':'Every extracted file hash, style/material declarations, English/display declaration, authored motion invariants and shared capture syntax PASS. Not a fresh film render or artistic certificate.'}
(p/'recovery_local_receipt.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
