"""Extract encoded review evidence; never marks human/creative approval itself."""
import sys,json,subprocess,math
from pathlib import Path
from PIL import Image,ImageDraw
import imageio_ffmpeg
B=Path('/home/user/build/escobar_intro3');R=B/'review/encoded';R.mkdir(parents=True,exist_ok=True);FF=imageio_ffmpeg.get_ffmpeg_exe();VIDEO=B/'Escobar_Expanded_Intro_Revision3.mp4'

def sheet(files,path,cols=4,labels=None):
    rows=math.ceil(len(files)/cols);im=Image.new('RGB',(400*cols,248*rows),(10,12,14));d=ImageDraw.Draw(im)
    for i,f in enumerate(files):
        p=Image.open(f).convert('RGB');p.thumbnail((400,225));x=i%cols*400;y=i//cols*248;im.paste(p,(x,y));d.text((x+8,y+228),str(labels[i] if labels else f.stem),fill='white')
    im.save(path,quality=94)

subprocess.run([FF,'-v','error','-i',str(VIDEO),'-vf','select=not(mod(n\,12)),scale=400:225','-vsync','0','-q:v','2','-y',str(R/'half_%04d.jpg')],check=True)
files=sorted(R.glob('half_[0-9][0-9][0-9][0-9].jpg'))
for i in range(0,len(files),16):sheet(files[i:i+16],R/f'half_sheet_{i//16+1}.jpg',labels=[f'{(j+i)*.5:.2f}s' for j in range(len(files[i:i+16]))])
# All actual joins, including every press-name match. Inspect encoded neighbors.
cuts=[5.15,8.5,9.5,17.8,23.84,29.3,35.3,40.7,46.3,50.2,54,57.8]+[57.8+.25*i for i in range(1,10)]+[60.3]
indices=sorted(set([max(0,math.ceil(t*24)-1) for t in cuts]+[math.ceil(t*24) for t in cuts]+[math.ceil(t*24)+1 for t in cuts]+list(range(202,231,2))))
expr='+'.join(f'eq(n,{n})' for n in indices)
subprocess.run([FF,'-v','error','-i',str(VIDEO),'-vf',f'select={expr.replace(chr(44),chr(92)+chr(44))},scale=400:225','-vsync','0','-q:v','2','-y',str(R/'join_%04d.jpg')],check=True)
files=sorted(R.glob('join_[0-9][0-9][0-9][0-9].jpg'))
for i in range(0,len(files),16):sheet(files[i:i+16],R/f'join_sheet_{i//16+1}.jpg',labels=[f'frame {n} / {n/24:.4f}s' for n in indices[i:i+16]])
# Full encoded frame and AV checks. Invalid/truncated frames fail ffmpeg.
result=subprocess.run([FF,'-hide_banner','-i',str(VIDEO),'-af','loudnorm=I=-16:TP=-1.4:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
m=json.loads(result[result.rfind('{'):result.rfind('}')+1]);(R/'loudness.json').write_text(json.dumps(m,indent=2));print(result[:1000]);print('Loudness',m);print('half-second frames',len(list(R.glob('half_[0-9][0-9][0-9][0-9].jpg'))),'(includes sheets separately)');print('join frames',len(files));print('Video bytes',VIDEO.stat().st_size)
