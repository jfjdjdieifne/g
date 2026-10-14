# docengine — reusable premium documentary motion engine

Software documentary studio: script + VO + timeline in → art-directed,
word-synchronized 1080p scenes out. Not Escobar-specific: projects are
data packages under `projects/<id>/`.

## Architecture
- `src/scene-model.mjs` — resolves declarative scene JSON + forced-alignment
  timeline into a fully scheduled render scene. Enforces EXACT narration
  typography (visible tokens must equal the script sentence).
- `src/typography.mjs` — per-word scheduling: emphasized words readable
  onset−60ms, standard words readable exactly at onset. Explicit `preRoll`
  policy for words that cannot animate before frame zero ("on_screen" |
  "compress"). No universal lead. No char-by-char typing.
- `src/camera.mjs` — deterministic keyframed camera (pos/look/fov,
  smoothstep). Pure function of time; identical frames on every run.
- `src/qc.mjs` — Gate A (assets: existence, license status, upscale limit,
  placeholder ban) + Gate B (layout: safe-frame, text overlaps,
  text-over-subject coverage, from live DOM getBoundingClientRect + projected
  3D subject rects).
- `runtime/scene.html` — Three.js/DOM composite renderer: full-bleed photo
  environment, feathered photographic planes in 3D space (graded at
  texture-build), masked word reveals driven by the schedule, dust
  atmosphere, scene fade-in. `__setTime(t)` deterministic; `__measure()`
  feeds QC with real rendered geometry.
- `cli/storyboard.mjs` — renders storyboard frames at declared times,
  runs Gates A/B, writes `qc_report.json` + PNGs.

## Pipeline gates (directive §16)
A assets → B composition storyboard → C motion preview → D audio-sync
diagnostic (verify from decoded MP4 frames, not JSON) → E final.
C/D/E land next; B and A are live in this commit.

## Projects
`projects/<id>/project.json` + `assets.manifest.json` (provenance + license
per asset, storyboard_only status propagates QC warnings) +
`scenes/*.json` (strategy, layers, camera keys, phrase typography) +
`slates/` (approved gate outputs).

## Runtime deps (sandbox)
Node 22 + three + puppeteer-core + @sparticuz/chromium from DEPS_DIR
(currently /tmp/probe3); Chromium binary /tmp/chromium with
LD_LIBRARY_PATH=/tmp/deblibs. FFmpeg for encoding. Fonts from
assets_global/fonts. See project.json for input package shape.
