#!/usr/bin/env python3
"""Revision2 authoring orchestration. Uses the shared World/Cycles backend.
Stills are preproduction scene tests, never an approved movie or a v1 rebuild.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'engine/projects/escobar_hook30'
PROFILE=PROJECT/'revision2'
BUILD=Path('/home/user/build/escobar_hook30/revision2')
sys.path.insert(0,str(ROOT/'engine/runtime'))
from blender_xyz import CyclesWorldRenderer
spec=importlib.util.spec_from_file_location('escobar_revision2_scene',PROFILE/'scene.py')
scene=importlib.util.module_from_spec(spec);spec.loader.exec_module(scene)


def renderer(width=1280,height=720,samples=12,detail=False):
    r=CyclesWorldRenderer(width=width,height=height,samples=samples)
    # Authoring profile sets a restrained physical studio; renderer stays generic.
    r.scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.035,.05,.06,1)
    r.scene.world.node_tree.nodes['Background'].inputs[1].default_value=.25
    r.bpy.data.objects['Ground'].location.z=-1.05
    r.scene.view_settings.exposure=.40
    r.set_world(scene.build_world(detail=detail))
    # Palette-based surface response, no rasterized fake evidence.
    for key,mat in r.materials.items():
        shader=mat.node_tree.nodes.get('Principled BSDF')
        if tuple(key[0]) in [scene.STEEL,scene.WIRE]:
            shader.inputs['Metallic'].default_value=.65
            shader.inputs['Roughness'].default_value=.38
        if tuple(key[0])==scene.WOOD:shader.inputs['Roughness'].default_value=.48
    for color in [scene.WOOD,(148,104,62),(133,87,50)]:r.style_surface(color,'wood',.52)
    for color in [(183,184,164),(225,218,194)]:r.style_surface(color,'cloth',.94)
    return r


def stills():
    folder=BUILD/'stills';folder.mkdir(parents=True,exist_ok=True)
    r=renderer(samples=12)
    for shot in scene.SHOTS:
        r.set_world(scene.build_world(detail=shot['id']=='office'))
        t=(shot['start']+shot['end'])/2
        r.render(scene.shot_camera(shot,t),folder/(shot['id']+'.jpg'),shot['focus'],shot['aperture'])
        print('PREPRODUCTION_STILL',shot['id'],flush=True)


def verify_edit_gate():
    review=json.loads((PROFILE/'editorial_review.json').read_text())
    if not review.get('internal_edit_authorized'):raise ValueError('Revision2 internal edit not authorized')
    sources=[(Path('/home/user/build/escobar_archive_official/original_opening.mp4'),review['source_file_sha256']),
             (PROJECT/'assets/narrator_approved.mp3',review['voice_sha256'])]
    for path,sha in sources:
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
            raise ValueError('Missing or altered actual source: '+str(path))
    return review


def render_samples():
    verify_edit_gate()
    r=renderer(width=960,height=540,samples=4)
    r.scene.cycles.seed=193
    start=time.time()
    previous_detail=False
    for shot in scene.SHOTS:
        resolution=shot.get('resolution',[960,540])
        r.scene.render.resolution_x,r.scene.render.resolution_y=resolution
        detail=shot['id']=='office'
        if detail!=previous_detail:r.set_world(scene.build_world(detail=detail));previous_detail=detail
        folder=BUILD/'samples'/shot['id'];folder.mkdir(parents=True,exist_ok=True)
        count=math.ceil((shot['end']-shot['start'])*8)+1
        for i in range(count):
            dest=folder/f'{i:05d}.jpg'
            if dest.exists():continue
            t=min(shot['end'],shot['start']+i/8)
            r.render(scene.shot_camera(shot,t),dest,shot['focus'],shot['aperture'])
            print(f"SAMPLE {shot['id']} {i+1}/{count} elapsed={time.time()-start:.1f}s",flush=True)
    (BUILD/'samples_complete.json').write_text(json.dumps({'fps':8,'default_resolution':[960,540],'resolution_overrides':{'office':[1280,720]},'samples':4,'shots':scene.SHOTS},indent=2))
    print('ALL_SAMPLES_COMPLETE',flush=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stills',action='store_true');ap.add_argument('--render-samples',action='store_true');a=ap.parse_args()
    if a.stills:stills()
    elif a.render_samples:render_samples()
    else:ap.error('Choose --stills or --render-samples.')

if __name__=='__main__':main()
