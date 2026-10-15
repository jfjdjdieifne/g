# Escobar hook / 30 seconds / v1 REJECTED by user

**Editorial status (2026-10-15): v1 rejected.** Linking was good; still choices, quotation-slide pauses, captions and montage were rejected. Model showed progress but is not approved/professional and does not read sufficiently as a prison. No revised video created. Read `editorial_review.json` and `ARCHIVE_PREFLIGHT.json` first. **Do not render a revision until real news/presenter clips are acquired, viewed and heard.** Commands below are historical v1 reproduction only.

User-approved narrator: **voice-02**, explicit approval 15 October 2026. This profile reuses the approved recording verbatim; no fresh audition/generation. English-only on-screen editorial copy and narration. Conversation/internal notes may be Arabic.

## Source of truth

- `SCRIPT_EN.md`: approved narrator text and actual edit timing.
- `voice_preview.json`: approval and exact source MP3 hash.
- `display.json`: validated English editorial strings / scene-first gate.
- `PLAN.md`: scene choices with citations to existing viewed reference-study moments.
- `SOURCES_AND_RIGHTS.md`: modern photo date, CC BY-SA attribution/adaptation notice, short retrospective quotations, no fabricated news.
- `QC.md`: actual performed checks and remaining limitations (written at completion).

## Rebuild

From the `youtube_documentary` directory, with Python 3.11:

```sh
python3 -m pip install --break-system-packages numpy pillow imageio-ffmpeg bpy==4.2.23
python3 tools/bootstrap_bpy_headless.py
LD_LIBRARY_PATH=/home/user/build/blender_libs python3 tools/escobar_hook30_models.py --historical-rebuild
python3 tools/escobar_hook30_finish.py --historical-rebuild
python3 tools/escobar_hook30_qa.py
python3 -m unittest discover -s tools/tests -v
```

`bootstrap_bpy_headless.py` requires configured `gh`; downloads only hash-pinned sysroot libraries to the excluded build directory, never installs them system-wide. Expected hashes are in `engine/runtime/blender_headless_libs.json`. Old X/GL compatibility libraries are for isolated CPU rendering, not network-facing services. Dependencies and build outputs are volatile; selected source media and scripts are tracked.

Output: `/home/user/build/escobar_hook30/render/escobar_hook30_v1.mp4`.

`--preview` on `tools/escobar_hook30.py` creates quick layout stills. Without the Cycles cache those stills use an intentionally simpler software preview; **not** the final deliverable. Final encoding refuses missing model frames. Model frames are sampled at **960×540 / 6fps** in Cycles and motion-compensated to 24fps **within each shot only**. Typography/photo compositing/output are 1920×1080 / 24fps. This sampling compromise is disclosed, not claimed as native 1080p 24fps 3D rendering.

## Architecture

One shared XYZ runtime (`engine/runtime/xyz_scene.py`) and optional shared Cycles backend (`blender_xyz.py`), with a per-film staging/edit profile (`tools/escobar_hook30.py`). `escobar_hook30_models.py` orchestrates scene sampling; `escobar_hook30_finish.py` interpolates/composites. No new bank cards or claims of a fully autonomous general documentary engine.

## Scope / outstanding

Only the first 30 seconds. The video still needs the user's visual/editorial review. Authentic TV/news audio was **not acquired**; narrator-free moments use brief, visibly sourced **1997 transcript / 2023 article** excerpts, not period news footage. The model is an illustration, not a measured historical reconstruction; its gate/figure movement is symbolic, not evidence of the real escape route. No uncertain-rights Escobar portrait, stock watermark, TV reconstruction or fabricated anchor used.

The render, model and finish CLIs now refuse production while this editorial review is blocked. `--historical-rebuild` is for debugging the rejected old cut only, never a bypass to label it a revision. No new footage or revised video has been acquired/created by the feedback update.
