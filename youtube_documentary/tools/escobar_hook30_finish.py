#!/usr/bin/env python3
"""Expand each independently-rendered 6fps shot to 24fps with motion compensation.
Never interpolate across an edit, and never interpolate the original narration.
Blender samples are 960x540; compositing / text / final delivery are 1920x1080.
"""
import json
import argparse
import shutil
import subprocess
from pathlib import Path
import imageio_ffmpeg
from escobar_hook30 import BUILD,PROJECT

parser=argparse.ArgumentParser();parser.add_argument('--shot',choices=['design','escape']);parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
ff=imageio_ffmpeg.get_ffmpeg_exe();cache=BUILD/'model_frames';cache.mkdir(exist_ok=True)
# Delete only the initial standalone lighting test, not any required scene sample.
for a,b,name in [(128,272,'design'),(360,720,'escape')]:
    if args.shot and name!=args.shot:continue
    marker=BUILD/f'{name}_interpolation.done'
    if marker.exists() and all((cache/f'{n:04d}.jpg').exists() for n in range(a,b+1)):continue
    seq=BUILD/f'input_{name}';seq.mkdir(exist_ok=True)
    for i,n in enumerate(range(a,b+1,4)):
        src=BUILD/'cycles_samples'/f'{n:04d}.jpg'
        if not src.exists():raise RuntimeError(f'Missing actual Cycles sample: {src}')
        dst=seq/f'{i:04d}.jpg'
        if not dst.exists():dst.symlink_to(src)
    temp=BUILD/f'interpolated_{name}';temp.mkdir(exist_ok=True)
    duration=(b-a)/24
    subprocess.run([ff,'-y','-v','warning','-framerate','6','-i',str(seq/'%04d.jpg'),
        '-vf','tpad=stop_mode=clone:stop_duration=0.5,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none',
        '-frames:v',str(b-a+1),'-q:v','2','-start_number',str(a),str(temp/'%04d.jpg')],check=True)
    for p in temp.glob('*.jpg'):shutil.copy2(p,cache/p.name)
    required=[cache/f'{n:04d}.jpg' for n in range(a,b+1)]
    if not all(p.exists() for p in required):raise RuntimeError('Incomplete interpolated shot')
    marker.write_text('Per-shot MCI complete; source Cycles samples verified present.\n')
if args.prepare_only:raise SystemExit(0)
if args.shot:raise RuntimeError('Single shot requires --prepare-only; do not composite an incomplete scene')
# Explicit provenance, including resolution and frame interpolation (no false claim).
(BUILD/'image_pipeline.json').write_text(json.dumps({
    'backend':'Blender 4.2.23 LTS / Cycles CPU',
    'model_sample_resolution':[960,540],'model_sample_fps':6,
    'model_samples':128,'model_interpolation':'ffmpeg minterpolate mci/aobmc/bidir, per shot',
    'composite_resolution':[1920,1080],'delivery_fps':24,
    'original_voice_untouched_except_gain_and_silent_split':True,
    'historical_architectural_reconstruction':False,
    'limitations':['Illustrative geometry, not a measured plan','6fps model renders interpolated to 24fps; inspect fences and gate for ghosting','No authentic news audio acquired']
},indent=2)+'\n')
print('Interpolation done. Compositing approved narration.',flush=True)
subprocess.run(['python3',str(Path(__file__).with_name('escobar_hook30.py'))],check=True)
