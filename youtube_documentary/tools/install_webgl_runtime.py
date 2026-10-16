#!/usr/bin/env python3
"""Install the pinned shared toolchain to an external cache, never vendored assets."""
import sys,json,subprocess,venv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if len(sys.argv)!=2:raise SystemExit('Usage: python3 tools/install_webgl_runtime.py /absolute/external/cache')
base=Path(sys.argv[1]).resolve()
if base==ROOT.parent or ROOT.parent in base.parents:raise SystemExit('Choose an external cache, not a source/repository directory.')
deps=json.loads((ROOT/'engine/runtime/webgl_dependencies.json').read_text());base.mkdir(parents=True,exist_ok=True)
venv.create(base/'venv',with_pip=True);py=base/'venv/bin/python'
subprocess.run([str(py),'-m','pip','install',*[k+'=='+v for k,v in deps['python'].items()]],check=True)
subprocess.run(['npm','install','--prefix',str(base/'node'),'--no-audit','--no-fund',*[k+'@'+v for k,v in deps['node'].items()]],check=True)
print('export DOCENGINE_NODE_MODULES='+str(base/'node/node_modules'));print('export DOCENGINE_PYTHON='+str(py))
