"""Film-specific authored script / cue selection over SHARED narration processing.
Run from repository root after the four approved-identity takes and raw ASR exist.
Never synthesize here, never overwrite raw takes, never alter archive witnesses.
"""
import sys,json,subprocess,math,hashlib,os
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from speech_pacing import shape
from film_runtime import FF
B=Path(os.environ.get('DOCENGINE_BUILD','/home/user/build/black_hole'));B.mkdir(parents=True,exist_ok=True)
# Prefer preserved originals; the portable capsule stores these once at its root.
V=next((v for v in [P/'raw_voice',ROOT.parent.parent/'raw_voice',B/'voice'] if (v/'01_raw.wav').is_file()),B/'voice')
scripts=[
"You could cross a black hole's point of no return and feel absolutely nothing. No wall. No impact. Just another second on your watch. But try sending one last message home, and it will never arrive. Here's the trick: the edge of a black hole isn't a surface. It's a boundary between places that can still send light out, and places that can't. So let's follow one astronaut in, while a friend watches from a ship far away. For this trip, we're choosing a quiet, supermassive black hole. No blazing disk of gas.",
"That choice matters. A small black hole could tear you apart before you even reach its edge. Gravity pulls harder on your feet than your head, stretching you lengthwise. Around a supermassive black hole, that difference can be much gentler at the horizon. You could cross it alive. Now watch the astronaut's flashing beacon. To the friend outside, the flashes arrive farther and farther apart. Their light shifts redder and grows fainter. You don't remain a clear, frozen statue at the edge. Your image fades out.",
"But you're not frozen. Your watch keeps ticking normally beside you. You cross the horizon in a finite amount of your own time. So why can't you turn around? Forget the idea that you just need a bigger engine. In this simplified, nonrotating black hole, every possible path into your future leads deeper inward. Even a beam aimed directly outward can't reach larger distances from the center once it's inside. The horizon isn't a wall blocking the exit. Beyond it, the exit is no longer in your future.",
"And crossing alive doesn't mean surviving the journey. Deeper in, the tidal forces grow. The difference between the pull on your head and your feet becomes destructive. Classical relativity takes that fall toward a singularity. But that isn't a confirmed portal, or a place we've photographed. It's a sign that our theory is incomplete. These are explanatory diagrams, not a camera recording from inside. The unsettling part is what we do know: you could pass the point of no return without a dramatic warning. The universe doesn't owe you an alarm."
]
(P/'SCRIPT.md').write_text('# What If You Fell Into a Black Hole?\n\nEnglish narration, original script. Display captions OFF.\n\n'+'\n\n'.join(f'## Take {i+1:02d}\n\n{s}'for i,s in enumerate(scripts))+'\n')
all_words={};audits={};starts={};at=.14;parts=[]
for i in range(1,5):
 k=f'{i:02d}';j=json.loads((P/'narration'/f'{k}_raw.asr.json').read_text());words=[w for row in j['segments']for w in row.get('result',[])];all_words[k]=words
 focus=[['no','return'],['cross','it','alive'],['deeper','inward'],['dramatic','warning']][i-1]
 ix=next((a for a in range(len(words)-len(focus)+1)if [w['word']for w in words[a:a+len(focus)]]==focus),None)
 emph=[]if ix is None else [(ix,ix+len(focus))]
 f=B/f'{k}_paced.wav';a=shape(V/f'{k}_raw.wav',words,f,target_wpm=188.2,emphasis=emph,pause=.16);audits[k]=a
 subprocess.run([FF,'-v','error','-y','-i',str(f),'-c:a','flac',str(P/'narration'/f'{k}.flac')],check=True)
 starts[k]=at;parts.append({'id':'narration_'+k,'kind':'narration','file':f'narration/{k}.flac','start':at,'end':at+a['output_seconds'],'duration':a['output_seconds']});at+=a['output_seconds']+(.55 if i<4 else 0)
def cue(k,phrase):
 words=all_words[k];terms=phrase.split();idx=next(a for a in range(len(words)-len(terms)+1)if [w['word']for w in words[a:a+len(terms)]]==terms);w=words[idx]
 reg=next(r for r in audits[k]['regions']if r['word_first']<=idx<r['word_last_exclusive'])
 return starts[k]+reg['output_in']+(w['start']-reg['source_in'])/(reg['source_out']-reg['source_in'])*(reg['output_out']-reg['output_in'])
C={name:cue(k,phrase)for name,k,phrase in [
('nothing','01','absolutely nothing'),('message','01','try sending'),('never','01','never arrive'),('surface','01','isn\'t a surface'),('boundary','01','a boundary'),('follow','01','follow one astronaut'),('quiet','01','a quiet'),
('small','02','a small black hole'),('pull','02','gravity pulls'),('large','02','around a supermassive'),('alive','02','cross it alive'),('beacon','02','now watch'),('friend','02','friend outside'),('apart','02','farther and farther'),('red','02','light shifts'),('fade','02','your image fades'),
('watch','03','your watch keeps'),('cross','03','you cross the horizon'),('turn','03','turn around'),('engine','03','a bigger engine'),('model','03','in this simplified'),('future','03','every possible path'),('outward','03','directly outward'),('exit','03','the exit is no longer'),
('survival','04','crossing alive'),('tides','04','deeper in'),('destroy','04','becomes destructive'),('singularity','04','classical relativity'),('portal','04','confirmed portal'),('unknown','04','theory is incomplete'),('diagrams','04','explanatory diagrams'),('return','04','the unsettling part'),('point','04','the point of no return'),('alarm','04','the universe')]}
D=math.ceil((at+2.0)*24)/24
cfg={'build':str(B),'width':1920,'height':1080,'fps':24,'duration':D,'background':'#030712','exposure':1.05,'environmentIntensity':.55,'batchMeshes':False,'silent_output':'picture.mp4','cues':C,'audio_parts':parts,'title':'What If You Fell Into a Black Hole?','model_notice':'Authored conceptual diagrams; not a calibrated optical simulation or recording from inside. Nonrotating model for causal paths. Not to scale.','movie_output':'What_If_You_Fell_Into_a_Black_Hole_1080p.mp4','score_sections':[
{'start':0,'end':C['surface'],'bpm':112,'mode':'pressure','root':65.406,'density':.75},
{'start':C['surface'],'end':C['small'],'bpm':106,'mode':'sparse','root':73.416,'density':.6},
{'start':C['small'],'end':C['beacon'],'bpm':116,'mode':'pressure','root':65.406,'density':.75},
{'start':C['beacon'],'end':starts['03'],'bpm':102,'mode':'sparse','root':87.307,'density':.65},
{'start':starts['03'],'end':C['future'],'bpm':110,'mode':'pulse','root':73.416,'density':.65},
{'start':C['future'],'end':C['survival'],'bpm':116,'mode':'pressure','root':65.406,'density':.8},
{'start':C['survival'],'end':C['unknown'],'bpm':118,'mode':'pressure','root':58.27,'density':.75},
{'start':C['unknown'],'end':D,'bpm':100,'mode':'sparse','root':65.406,'density':.5}],
'effects':[C[x]for x in ['message','small','beacon','cross','future','tides','return']],
'review_joins':[C[x]for x in ['message','surface','follow','small','large','beacon','red','watch','cross','model','future','outward','survival','singularity','unknown','return','alarm']],
'review_motion_windows':[[max(0,C[x]-.2),min(D,C[x]+1.0)]for x in ['message','surface','small','large','beacon','fade','watch','cross','model','future','outward','destroy','unknown','return','alarm']]+[[D-1,D]]}
(P/'render.json').write_text(json.dumps(cfg,indent=2)+'\n');(P/'narration_pacing.json').write_text(json.dumps(audits,indent=2)+'\n');(P/'narration_recipe.json').write_text(json.dumps({'voice_identity':'Previously user-approved voice-02, reused without re-audition','target_clause_wpm':188.2,'pause_seconds':.16,'source':'Raw WAVs retained untouched in external recovery capsule; processed FLACs directly renderable in profile.','cue_method':'Fallible ASR word positions mapped through actual shared clause processing; not ear-certified alignment.','manual_listening_claimed':False},indent=2)+'\n')
print('DURATION',D,'FRAMES',round(D*24),'WORDS',sum(len(s.split())for s in scripts));print(json.dumps(C,indent=2))
