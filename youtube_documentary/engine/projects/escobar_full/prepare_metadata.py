"""Rebuild this film's MATERIALS/display/fact metadata; NOT a second rendering engine.
Run from the repository root. New source hashes are retrieved, never auto-inspected.
Final-encode visual observations are separate and must not be inferred from this CLI.
"""
import json,sys,hashlib,importlib.util
from pathlib import Path
sys.path.insert(0,'youtube_documentary/engine/runtime');f=Path('youtube_documentary/engine/projects/escobar_full/profile.py');spec=importlib.util.spec_from_file_location('P',f);P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P);plan=P.prepare();proj=P.PROJECT
intro=json.loads((proj.parent/'escobar_intro5/MATERIALS.json').read_text());assets=[];paths={};beats=[]
previous=json.loads((proj/'MATERIALS.json').read_text()) if (proj/'MATERIALS.json').exists() else {'assets':[]}
known={(x['id'],x.get('sha256')):x for x in previous['assets']}
for s in plan['shots']:
 if s['kind']=='video':
  file=Path(s['path']);aid=file.stem
  if aid not in paths:
   digest=hashlib.sha256(file.read_bytes()).hexdigest();prior=known.get((aid,digest),{});paths[aid]=True;assets.append({'id':aid,'kind':'archive_video','description':'Original source programme; only selected bounds are used. Selected scenes visually inspected, never count a programme chunk as a different broadcaster.','source_file':file.name,'source':s['source_url'],'sha256':digest,'date_context':'BBC News 2013' if 'bbc_' in aid else 'Al Jazeera English 2018' if 'aj_' in aid else 'FRONTLINE 1995','review_status':prior.get('review_status','retrieved'),'review_evidence':'Source-level inventory inherited only for an identical previously inventoried SHA. NOT proof that every second or newly selected bound was viewed. Exact-bound final-encode observations belong in editorial_review.json and encoded_qc/. No manual ear-listening claim.','rights_status':'Internal review only; public access does not confer publication rights. Licensing unresolved.'})
 elif s['kind']=='route':
  aid='geographic_network'
  if aid not in paths:paths[aid]=True;assets.append({'id':aid,'kind':'original_model','description':'Explanatory Natural Earth map with perspective camera and raised XYZ routes; conceptual network, NOT an actual shipment path or satellite evidence. Andean inputs branch independently into Colombia.'})
 else:
  name=s['asset'];old=next(a for a in intro['assets'] if a.get('path','').endswith(name));aid=old['id']
  if aid not in paths:paths[aid]=True;assets.append(old)
 beats.append({'id':s['id'],'function':s['meaning'],'choice_reason':'Exact-subject real source first; camera/motion selected for this explanation, not arbitrary popup captions.','why_not_real':'Real source used.' if s['kind']!='route' else 'No historic footage records this abstract whole network; explicitly disclosed geographical explanation replaces fabricated historical action.','material_ids':[aid]})
# Source transcript backs the short extracts; ASR supplies fallible word bounds, not independent listening.
quotes=[{'speaker':'Stephen Murphy, DEA agent','source':P.PBS,'source_in_out':[4191.35,4195.69],'exact_quote':'The prison itself contained its own discotheque, its own bar.','audio_review_method':'Published FRONTLINE transcript plus original-recording Vosk word times. Pictures inspected at 1-second intervals. No human listening claimed.'},{'speaker':'Jack Blum, Senate investigator','source':P.PBS,'source_in_out':[4877.43,4882.08],'exact_quote':"It didn't change the pace of trafficking. It didn't raise or lower the price of cocaine.",'audio_review_method':'Published FRONTLINE transcript plus original-recording Vosk word times. Speaker visible at selected bounds. No human listening claimed.'}]
(proj/'MATERIALS.json').write_text(json.dumps({'assets':assets,'beats':beats,'source_quotes':quotes,'rights_cleared':False},indent=2))
texts={s['id']:' / '.join(s['credit']) for s in plan['shots']};texts['map_labels']='Peru / Bolivia / Colombia / Bahamas / Miami'
(proj/'display_manifest.json').write_text(json.dumps({'language':'en','texts':texts,'design':{'unit_of_design':'scene','generic_popups':[],'claims_3d':True,'depth_features':['perspective_camera','world_space_xyz','height_dependent_projection','occlusion_or_depth_ordering'],'method':'Native-speed authentic footage; source logo protection; three disclosed cartographic scenes with raised XYZ route arcs and a moving perspective camera; one original-pixel 2.5D public-appearance photograph. No fabricated historical action. Captions OFF; source attribution only.'}},indent=2))
(proj/'editorial_review.json').write_text(json.dumps({'production_blocked':False,'status':'first_full_cut_in_production_not_user_approved','approved_opening_locked':True,'pace_user_authorized':'V3 slightly slower; proceed','source_visual_review':'Overview sheets and quote/source fine candidates inspected. Encoded full sequence review pending.','manual_listening_claimed':False,'publication_rights_cleared':False},indent=2))
(proj/'FACT_CHECK.md').write_text('''# Fact and interpretation ledger — internal review cut

- Supply chain and cooperation: FRONTLINE transcript, sections on pilots, processing, Ochoas, Carlos Lehder and pooled loads. Network arrows are conceptual; Peru and Bolivia feed Colombia independently, not a claim of Peru-to-Bolivia routing.
- Source transcript: https://www.pbs.org/wgbh/pages/frontline/shows/drugs/archive/godfathercocaine.html
- 1982: alternate congressman, NOT president. https://www.britannica.com/biography/Pablo-Escobar ; genuine El Tiempo 1983 group photograph already in approved opening materials.
- Housing and football aid were real; never assert that all grateful residents supported crimes. Genuine 1983 Edgar El Chino Jimenez / El Pais construction photo and actual FRONTLINE Flores household sequences, identified by its transcript.
- Rodrigo Lara Bonilla exposed trafficking background and was assassinated in April 1984. Use his genuine public address at original2068s and damaged-car aftermath at2732s. Do not confuse the Ramirez family interview at2640s with Lara's family.
- Extradition: sending a wanted person abroad for legal proceedings. Prison/court imagery supports the explanation, not an invented specific trial.
- 1989: Luis Carlos Galan assassinated. Use actual rally images from original3621–3700s. Do NOT treat contested claims about Escobar's role in the Palace of Justice siege as established; that sequence is not used.
- 1991 constitutional reform was a larger democratic process. It prohibited extradition of Colombian nationals. Escobar benefited; do not imply he wrote the constitution himself.
- June1991 surrender; La Catedral; continued criminal operations; killing two associates; July1992 escape. Britannica supports two associates; old FRONTLINE narration says four and is not reused for that assertion. https://www.britannica.com/biography/Pablo-Escobar
- Los Pepes: violent vigilante enemies of his network, NOT a clean or lawful solution. FRONTLINE original4340s onward supplies source context for targeted property, with DEA witness discussion.
- 2December1993: Colombian forces located him in Medellin; rooftop shootout; responsibility for fatal bullet disputed. Do not confidently assign it. Britannica biography and https://www.britannica.com/topic/How-Did-Pablo-Escobar-Die . Corpse close-ups are excluded.
- Jack Blum's extract concerns the trade in the1995 programme's context. It is not a current market statistic or proof that nothing changed for victims.
- BBC2013 and Al Jazeera2018 images are explicitly dated later context, never passed off as1980s footage or proof that a pictured person received a1983 home.

## Review limits
Visual source review, exact-clock picture/audio matching, source transcripts, and fallible ASR are distinct. No manual ear-listening is claimed. Public accessibility is not rights clearance; this is an internal editorial review cut, not publication authorization.
''')
print('METADATA',len(plan['shots']),len(assets),'body seconds',plan['frames']/24)
