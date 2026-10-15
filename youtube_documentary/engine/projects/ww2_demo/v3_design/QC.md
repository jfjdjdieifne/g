# QC v3 — 2026-10-15

- Final file: `escobar_ww2drive_v3_design_test.mp4`, 7,806,545 bytes, 16.00 s.
- H.264 High / yuv420p / 1920×1080 / 24 fps, 384 frames decoded with no decode error.
- AAC stereo / 48 kHz / ~190 kb/s. `volumedetect`: mean -19.6 dBFS; peak -10.9 dBFS. Listening assessment not claimed.
- 32 decoded samples at 2fps viewed across two final contact sheets. Country-name/caption collision found in prior render and removed before final render. Full-size 1.8 / 7.8 / 13.8 second stills inspected during layout iteration.
- 4 automated tests pass: country containment (including every convoy path point), camera continuity over all 384 timestamps, Arabic layer bounds, atlas/screen inverse projection over all 384 timestamps.
- No claim that these checks certify professional art direction, or that all 384 frames were individually visually inspected.

## Reproduce
```
python3 -m pip install -r tools/requirements_ww2_v3.txt
python3 -m unittest discover -s tools/tests -v
python3 tools/ww2demo_v3.py --preview
python3 tools/ww2demo_v3.py
```
Outputs go to `/home/user/build/ww2_demo_v3` and are not committed. Canonical geometry stays in the repository. Temporary atlas caching uses version 4; remove the temporary atlas/version files if changing the geometry or art direction.

## Remaining artistic limits
This is one cartographic continuity study, not a demonstration of documentary-wide professional montage. No authored character rig, archival compositing sequence, or 3D scene was built. Camera holds, map material and path design remain subject to user review. Symbolic routes and full-country tint are not historical reconstructions. Do not promote this study to the approved engine list.
