"""Profile-specific review boundaries; generic extraction lives in the common runtime."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'engine/runtime'))
from encoded_review import review
B=Path('/home/user/build/escobar_intro4');shots=json.loads((B/'shots.json').read_text());r=json.loads((B/'render.json').read_text());clips=json.loads((B/'timeline.json').read_text())['clips']
windows=[(s['start'],s['end']) for s in shots if s['kind']=='turn']+[(s['start'],s['start']+.65)for s in shots if s['kind']in ['press','entry_name']]
review(B/'Escobar_Intro_Revision4_Faster_Rhythm.mp4',B/'review/encoded',r['fps'],r['frames'],[s['start']for s in shots[1:]]+[c['start']for c in clips[1:]],windows)
