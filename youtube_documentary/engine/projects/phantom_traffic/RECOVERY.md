# The Jam With No Blockage — reproducible pure-explainer demonstration

Requested by user on 2026-10-16. This is NOT yet a user-approved style benchmark. Do not change the approved Escobar film or its reference status.

## What is original / what is factual

English narration/display, voice-02 identity, no narrative captions. Original geometry, road, cars, cameras, authored wave motion, semantic marks and synthesized score. No archive or generated historical event imagery. See SCRIPT.md, FACT_CHECK.md and retained Flow project research. The analytic animation illustrates the mechanism; it is not an independent scientific simulation, measured traffic or a road prediction.

## Common engine, film-specific profile

- `engine/runtime/webgl_stage.mjs`: shared Three.js materials/lights/projection/text.
- `engine/runtime/traffic_motion.mjs`: reusable authored wave/space primitive, no claim of calibrated car following.
- `tools/render_webgl_profile.mjs`: common style-gated browser capture and picture encode.
- `tools/mix_webgl_profile.py` + existing `speech_pacing.py`, `long_score.py`, `film_runtime.py`, `encoded_review.py`: common voice/audio/review pipeline.
- This folder's `scene.mjs`, `render.json`, MATERIALS and script contain directing choices. Changing film does not require a new engine.

## Restore and render

Keep this folder at `youtube_documentary/engine/projects/phantom_traffic` and common tools at their included relative paths. Install Node 22+, Python 3.11+, and dependencies pinned in `engine/runtime/webgl_dependencies.json` into EXTERNAL cache directories, not committed dependencies. The Chromium package includes a matching Linux binary and NSS/NSPR libraries, automatically extracted for minimal hosts.

```bash
# Optional one-command external-cache setup:
# python3 youtube_documentary/tools/install_webgl_runtime.py /absolute/external/cache
export DOCENGINE_NODE_MODULES=/absolute/external/cache/node_modules
export DOCENGINE_PYTHON=/absolute/external/venv/bin/python
export DOCENGINE_BUILD=/absolute/external/render/phantom_traffic
node youtube_documentary/tools/render_webgl_profile.mjs youtube_documentary/engine/projects/phantom_traffic --stills 1.5,13.8,28.5,33,49.5,65.5
node youtube_documentary/tools/render_webgl_profile.mjs youtube_documentary/engine/projects/phantom_traffic
$DOCENGINE_PYTHON youtube_documentary/tools/mix_webgl_profile.py youtube_documentary/engine/projects/phantom_traffic
```

Narration FLACs in `narration/` are processed clause-wise from preserved original WAV takes. No re-audition, identity substitution, regeneration or whole-film speedup. `narration_pacing.json` contains exact source/output hashes, per-region timing and ASR-derived word anchors. Raw WAVs belong in the external recovery capsule, not a discarded build cache. Audio is preserved but no human/agent ear-listening is claimed: automatic ASR and measured mix checks are distinct from actual listening. Music and sound effects are original editorial sound, not claimed road recordings; effects stay below their local music bed.

Encoded half-second review and subsecond joins/motion are extracted from the final MP4, not source stills. Their evidence and actual inspection notes are retained separately. A passed manifest gate is not an artistic approval.

## Actual delivery

Final film: https://drive.google.com/file/d/1qzcn1eHS0z8dVK1tbltClRklZb8G24Bd/view

SHA256 `27d3d24f3e41d631a5815ce99d42434a63f1d93ed15105738e4fc4f4daa5c935`. Metadata in delivery.json. Current scene source directly renders the final corrected camera/labels; frame-range patch tools are optional iteration tools, not required to reconstruct the corrected whole sequence. Sources, untouched raw voice WAVs, paced FLACs and actual encoded review sheets are in this compact capsule. Node dependencies and the41MB Vosk model are intentionally excluded. Model provenance, if a new ASR is genuinely needed: GitHub kercre123/vosk-models, vosk-model-small-en-us-0.15.zip. Existing final ASR and timing anchors are already included.
