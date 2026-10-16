#!/usr/bin/env python3
"""Fetch hash-pinned optional libraries for bpy's headless CPU renderer.
No system-library changes. Uses configured gh auth, never stores credentials.
Run after: pip install --break-system-packages bpy==4.2.23
Then: LD_LIBRARY_PATH=/home/user/build/blender_libs python3 ...
The old sysroot libraries are for isolated offline rendering, not new services.
"""
import base64
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'engine/runtime/blender_headless_libs.json').read_text())
out=Path(manifest['destination']);out.mkdir(parents=True,exist_ok=True)


def fetch(repo,path,depth=0):
    if depth>5:raise RuntimeError('Too many upstream symlinks')
    data=json.loads(subprocess.check_output(['gh','api',f'repos/{repo}/contents/{path}']))
    raw=base64.b64decode(data['content'])
    if raw.startswith(b'\x7fELF'):return raw
    target=raw.decode().strip()
    if '/' in target or target.startswith('.'):raise RuntimeError('Unexpected nonlocal library symlink')
    return fetch(repo,str(Path(path).parent/target),depth+1)


for name,expected in manifest['sha256'].items():
    path=out/name
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==expected:continue
    if name in ['libxkbcommon.so.0','libSM.so.6','libICE.so.6']:
        repo='eXtern-OS/eXternOS-Base';base='squashfs-root/usr/lib/x86_64-linux-gnu'
    else:
        repo='webosose/chromium53';base='src/build/linux/debian_wheezy_amd64-sysroot/usr/lib/x86_64-linux-gnu'
    raw=fetch(repo,f'{base}/{name}')
    if hashlib.sha256(raw).hexdigest()!=expected:raise RuntimeError(f'Hash mismatch: {name}; abort, do not silently trust changed binaries')
    path.write_bytes(raw);print('Verified',name)
print('Headless library hashes verified:',out)
