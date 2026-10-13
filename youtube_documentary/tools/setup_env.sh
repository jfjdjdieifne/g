#!/usr/bin/env bash
# One-time environment setup for the render pipeline (re-run after any sandbox reset).
set -e
pip install -q playwright numpy scipy pillow 2>/dev/null || pip install playwright numpy scipy pillow
python3 -m playwright install chromium
python3 -m playwright install-deps chromium 2>/dev/null || true
which ffmpeg >/dev/null || sudo -n apt-get install -y -qq ffmpeg
echo "env ready: $(python3 -c 'import playwright,numpy,scipy,PIL;print("py ok")') | $(ffmpeg -version 2>/dev/null | head -1 | cut -c1-30)"
