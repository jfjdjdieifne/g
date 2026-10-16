#!/usr/bin/env python3
"""Render per-film XYZ shots with the optional shared Cycles CPU backend."""
import argparse
import sys
import time
from escobar_hook30 import camera,world_scene,BUILD,FPS,ROOT,PROJECT
sys.path.insert(0,str(ROOT/'engine/runtime'))
from blender_xyz import CyclesWorldRenderer
from production_policy import enforce_editorial_review

p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');p.add_argument('--historical-rebuild',action='store_true');args=p.parse_args()
enforce_editorial_review(PROJECT,args.historical_rebuild)
out=BUILD/'cycles_samples';out.mkdir(parents=True,exist_ok=True)
r=CyclesWorldRenderer(width=960,height=540,samples=4)
frames=[240] if args.test else list(range(128,273,4))+list(range(360,721,4))
if args.test:frames=frames[:1]
r.set_world(world_scene(6.5));start=time.time();done=0
for n in frames:
    t=n/FPS;path=out/f'{n:04d}.jpg'
    if path.exists():continue
    if t>=18.6:r.set_world(world_scene(t))
    r.render(camera(t),path);done+=1
    print(f'MODEL {n}/720 / {done} renders / {time.time()-start:.1f}s',flush=True)
print('MODEL_RENDER_COMPLETE',flush=True)
