#!/usr/bin/env python3
"""Shared original-score mix / final mux for a WebGL film profile.
No live recordings or historical sound are synthesized. Does not certify listening.
"""
import sys,json,subprocess,hashlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'engine/runtime'),str(ROOT/'tools')]
from long_score import mix_sections
from film_runtime import FF
from style_contract import enforce_project_style

def main():
 p=Path(sys.argv[1]).resolve();c=json.loads((p/'render.json').read_text());enforce_project_style(p,json.loads((p/'MATERIALS.json').read_text()))
 b=Path(os.environ.get('DOCENGINE_BUILD',c['build']));b.mkdir(parents=True,exist_ok=True);D=c['duration']
 # Profile may provide its own score; these are sparse original editorial tones,
 # never an assertion of native traffic/location sound.
 sections=c['score_sections']
 for a in c['audio_parts']:
  if not Path(a['file']).is_absolute():a['file']=str(p/a['file'])
 audit=mix_sections({'fps':c['fps'],'frames':round(D*c['fps']),'audio':c['audio_parts'],'score_sections':sections,'effects':c.get('effects',[])},b)
 analysis=subprocess.run([FF,'-hide_banner','-i',str(b/'premix.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 parsed=json.loads(analysis.stderr[analysis.stderr.rfind('{'):analysis.stderr.rfind('}')+1]);audit['normalization_first_pass']=parsed
 f='loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}:linear=true:print_format=json'.format(**parsed)
 out=b/c['movie_output'];r=subprocess.run([FF,'-hide_banner','-y','-i',str(b/c.get('silent_output','picture.mp4')),'-i',str(b/'premix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af',f,'-ar','48000','-ac','2','-c:a','aac','-b:a','192k','-t',str(D),'-movflags','+faststart',str(out)],capture_output=True,text=True,check=True)
 (b/'final_mux.log').write_text(r.stderr);audit['encoded_file']=str(out);audit['encoded_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();audit['manual_listening_claim']=False
 (p/'mix_audit.json').write_text(json.dumps(audit,indent=2));print(out)
if __name__=='__main__':main()
