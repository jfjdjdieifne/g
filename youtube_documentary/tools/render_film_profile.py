#!/usr/bin/env python3
"""One renderer, separate film profiles. Never imports a film-specific engine."""
import argparse,importlib.util,sys,json,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'engine/runtime'));sys.path.insert(0,str(ROOT/'tools'))
from sequence_runtime import SequenceFilm
from score_runtime import mix
from film_runtime import FF
p=argparse.ArgumentParser();p.add_argument('profile');p.add_argument('--render',action='store_true');a=p.parse_args()
f=ROOT/'engine/projects'/a.profile/'profile.py';s=importlib.util.spec_from_file_location('film_profile',f);P=importlib.util.module_from_spec(s);s.loader.exec_module(P)
from production_policy import enforce_display,enforce_design,enforce_editorial_review
from documentary_materials import material_errors
enforce_editorial_review(P.PROJECT)
display=json.loads((P.PROJECT/'display_manifest.json').read_text());enforce_display(display);enforce_design(display['design'])
errors=material_errors(json.loads((P.PROJECT/'MATERIALS.json').read_text()))
if errors:raise ValueError('; '.join(errors))
plan=P.prepare();
# Check actual rendered credits too, not only an independently typed manifest.
enforce_display({'language':'en','texts':{s['id']:' / '.join(s['credit']) for s in plan['shots']}});
materials=json.loads((P.PROJECT/'MATERIALS.json').read_text())
for shot in plan['shots']:
    if shot['kind']!='video':continue
    asset=next((x for x in materials['assets'] if x.get('source_file')==Path(shot['path']).name),None)
    if not asset or hashlib.sha256(Path(shot['path']).read_bytes()).hexdigest()!=asset.get('sha256'):raise ValueError('Verified original video changed: '+shot['id'])
(P.BUILD/'timeline.json').write_text(json.dumps(plan,indent=2));audit=mix(plan,P.BUILD,P.BPM)
(P.BUILD/'mix_audit.json').write_text(json.dumps(audit,indent=2))
# Two-pass loudness measures the actual premix; preserve source/dialogue rhythm.
r=subprocess.run([FF,'-hide_banner','-i',str(P.BUILD/'premix.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);j=json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}')+1]);(P.BUILD/'premix_loudness.json').write_text(json.dumps(j,indent=2))
filt=f"loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run([FF,'-v','error','-y','-i',str(P.BUILD/'premix.wav'),'-af',filt,'-ar','48000',str(P.BUILD/'mix.wav')],check=True)
if a.render:SequenceFilm(P,plan).render(P.BUILD/P.OUTPUT)
print('FILM_PROFILE_READY',plan['frames']/P.FPS,'seconds',len(plan['shots']),'shots',flush=True)
