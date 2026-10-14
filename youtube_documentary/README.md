# YouTube Documentary Engine Project

Reusable scene engines and tools for a cinematic true-crime / documentary
YouTube channel. This folder is self-contained source: engines, scene
configs, shared assets, fonts, and production docs. Rendered videos,
frame caches, and generated QA screenshots are NOT kept in Git.

## Engines

| Engine | File | Use |
|---|---|---|
| board | `tools/engines/board_engine.html` | Board/file layout: full photo (never cropped, no frame), name, signature, silhouette/light-trace, question |
| geo | `tools/engines/geo_engine.html` | Real-earth globe (NASA texture), source/destination, route arrow, camera keyframes |
| story | `tools/engines/story_engine.html` | Board-less story shots: establish, walk, counter, walkaway |

Engines read `window.SCENE_CONFIG` (injected from a scene JSON) and expose
`window.seek(t)`. Fonts are loaded by relative path from
`DEMO1_ESCOBAR/assets/fonts/` (`../../DEMO1_ESCOBAR/...` from
`tools/engines/`), so the whole `youtube_documentary/` folder must keep
its internal structure.

## Layout

- `00_PROJECT_UNDERSTANDING.md` — consolidated brief (Arabic): what the project is, the montage rules learned from the reference studies, current state, environment constraints, and next steps. Read this first.
- `config/` — scene configs (`escobar_scene01.json`, `geo_scene01.json`, `bank_scene01.json`). Asset paths inside them are relative to this folder.
- `tools/` — `build_scene.py` (config -> frames -> SFX -> MP4), `qa_frame.py` (frame QA), render helpers, `synth_sfx*.py`, `prep_hero_asset.py`, `setup_env.sh`.
- `assets_global/` — shared assets: `bank/` (facade, hall, walk cycles), `earth/` (earth_2048.jpg, earth_4096.jpg).
- `DEMO1_ESCOBAR/` — Escobar demo assets, fonts, and board prototypes.
- Root `*.md` / `*.yaml` / `*.csv` — channel system, workflow, motion references, and templates. `12_PRO_MOTION_ENCYCLOPEDIA.md` is a text reference, not executable code.

## Paths and working directory

Run commands from this folder (`youtube_documentary/`, the project root):

```bash
cd youtube_documentary
python3 tools/build_scene.py config/geo_scene01.json
```

`tools/build_scene.py`, `tools/qa_frame.py`, and `tools/render_engine.py`
derive the project root from their own file location
(`pathlib.Path(__file__).resolve().parents[1]`), so config, asset, engine,
`.cache/`, and `renders/` paths resolve relative to this folder, not to
`/home/user` and not to an arbitrary working directory. Generated frames,
QA screenshots, and renders go to `.cache/` and `renders/` inside this
folder and are excluded from Git by `.gitignore`.

No motion-preset library exists yet; motion names in the docs are
proposals, not callable presets.

## Setup

```bash
cd youtube_documentary
bash tools/setup_env.sh
```

Requires Python 3, pip, Chromium (via Playwright), and ffmpeg.

## Verify file integrity

```bash
cd youtube_documentary
sha256sum -c SHA256SUMS.txt
```

This proves the files are byte-identical to the recorded copies. It is
not a runtime test of the engines.

## Rules that always apply

- No music, ever. Dry, short SFX only when they serve the action; silence is part of the rhythm.
- English on-screen text in the current style; every core verb in the script must survive visually.
- Text inside a wide safe area. Real/archive photos shown whole, never cropped, no frames or polaroid borders.
- No generated face for a real person. Generated material is only for generic, unattributed scenes/objects, and is logged as generated.
- Do not re-render or replace approved old videos without an explicit request.
