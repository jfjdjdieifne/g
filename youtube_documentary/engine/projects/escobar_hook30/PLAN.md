# Escobar — first 30 seconds / historical v1 plan — REJECTED

User rejected this slide-based archive workaround and decorative captions on 2026-10-15. Do NOT reuse this plan as the revision brief. Preserve continuity and approved voice only. See `editorial_review.json` and `ARCHIVE_PREFLIGHT.json`.

Scope: only this 30-second opening. English picture and narration. No full documentary or next reference study. Voice-02 and its complete performance were explicitly approved on 2026-10-15; use that recording, not a new generation.

## Editorial decisions

| Timeline | Scene / meaning | Camera / sound |
|---|---|---|
| 0.00–3.00 | A newly typeset excerpt from the real 1997 FRONTLINE transcript. Not a screenshot, original newspaper, or 1991 breaking-news bulletin. | Two paper planes share an actual perspective camera; restrained push. No narrator, no manufactured anchor. |
| 3.00–5.90 | Actual former prison site in a clearly dated **2019** photograph. Establishes which place “This is…” refers to; does not show the prison in 1991. | Slow photographic crop; modern date and photographer/license visible. |
| 5.45–11.30 | Continuous illustrative architectural cutaway: design → guards → business. Same fence, rooms and desk remain in the world. | One moving XYZ camera, height-dependent parallax, occlusion, lit surfaces, contact shadows. No independent popup cards. |
| 11.30–15.00 | A clearly identified **2023 article excerpt**, “not maximum security, but maximum comfort.” The retrospective article, not PBS, is its source. | Deliberate narrator-free reading window. Not authentic broadcast audio. |
| 15.00–28.50 | Return to the same cutaway; June 1991 → July 1992; the illustrative gate opens and a neutral figure moves outside. Camera subsequently pulls back while the narrator asks about the agreement. | Shared location and persistent objects, not a new card for each line. Escape movement is symbolic, NOT the documented escape route. |
| 28.10–30.00 | Restrained identity/title reveal over the receding location. | The approved recording finishes; final hold and short fade. |

## Source audio timing

The 21.84-second nominal / 21.799-second decoded approved take is split at **source 8.30s**, inside its measured paragraph silence (7.987–8.672s). Source 0–8.30s goes at timeline 3.00s; source 8.30s–end goes at 15.00s. No speed/pitch modification or regenerated words. Only constant gain, the silent edit, and a quiet synthetic underscore/soft transitions. No synthetic newsreader. SFX are below the underscore.

## Reference-informed choices (existing viewed studies; no new evidence claims)

- `reference_lab/Vaping_BREAKDOWN_2fps_full_v2.md`, **0:00–0:07**: editorial/article-led cold opening. Apply the narrative function, not a copied layout.
- Same study, **0:07–0:13**, especially **0:10–0:13**: let source material carry a beat and isolate the operative words. Here the source is written, not acquired broadcast sound.
- Same study, **0:48–1:00**: movement connects meanings/objects. Here design, guards, office, gate and escape occupy one world.
- `reference_lab/TRANSITION_ATLAS.md`: moving scenes can also be joined with deliberate hard cuts. Continuous motion is not an obligation to dissolve every cut.
- `ENGINES.json` and `tools/ww2demo_v4_depth.py`: read before implementation. Reuse perspective-camera concepts; implement the common geometry/camera backend in `engine/runtime/xyz_scene.py`, optional physically lit rendering in `engine/runtime/blender_xyz.py`. The Escobar files are **film profiles/orchestration**, not a new universal engine per film.

## Rendering honesty

The model is an **illustration**, not a measured historical reconstruction. No invented period photo, face, map route or news evidence. Model sampling: Cycles CPU, 960×540 at 6fps, motion-compensated to 24fps separately within each continuous shot. Typography, photo compositing and final encode are 1920×1080 at 24fps. Inspect thin fences/gate for interpolation artifacts; do not call this native 1080p/24fps 3D sampling. A low-detail Pillow fallback exists for fast layout checks only and must not silently replace missing final Cycles frames.

## Release limitation

Original news audio remains unacquired. This is a narrated review cut with sourced, newly typeset excerpts, **not the final broadcast-led archival version**. Quote use is short editorial quotation, not a blanket license to the underlying programs/articles. See `SOURCES_AND_RIGHTS.md` before publication. Art direction remains subject to the user's video review; technical tests are not aesthetic approval.
