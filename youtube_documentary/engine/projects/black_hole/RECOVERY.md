# Black-hole film — source and raw-voice recovery

## What this is

A new English-only pure explainer requested after the user rejected the traffic topic as weak: “حلو بس الفكره سخيفه بدي افكار اقوى ومشوقه وبتجيب مشاهدات عملي فيديو هيك”. Strong topic selection, surprise/stakes and explanatory payoff matter; attractive rendering alone does not approve a topic. No view counts are guaranteed. This film is not user-approved until an actual response to the delivered movie.

`SCRIPT.md`, `CREATIVE_BRIEF.md`, `FACT_CHECK.md`, `MATERIALS.json`, `display_manifest.json`, `render.json` and `scene.mjs` describe this film. `scene.mjs` is a profile of the common stage/capture/mix system, NOT a separate renderer. Original generic suit/ship and seeded sky texture; no archive, no actual recording from inside, no calibrated lensing or physical scale.

## Build prerequisites

System Python3, Node, npm and access to the pinned package registries. Install large dependencies EXTERNALLY, not inside the recovery/source tree:

```sh
python3 youtube_documentary/tools/install_webgl_runtime.py /absolute/external/cache
# Use the two DOCENGINE_* exports printed by the installer.
```

The installer is shared. Its pinned versions are in `engine/runtime/webgl_dependencies.json`. The actual first toolchain installation was executed successfully for this film. A portable capsule/extraction verification does NOT itself mean a fresh dependency installation and full render were repeated from that capsule.

## Direct reconstruction

The supplied paced `narration/01.flac` through `04.flac` are the actual performance used, with the previously approved voice-02 identity. Do NOT re-audition or regenerate the voice. Raw originals are preserved in this repository profile's `raw_voice/`, mapped once to the capsule's root `raw_voice/`; ASR/processing audits/recipe are in this profile. Preserve both. Fallible ASR timing is not human listening.

```sh
node youtube_documentary/tools/render_webgl_profile.mjs youtube_documentary/engine/projects/black_hole
$DOCENGINE_PYTHON youtube_documentary/tools/mix_webgl_profile.py youtube_documentary/engine/projects/black_hole
$DOCENGINE_PYTHON youtube_documentary/tools/review_webgl_profile.py \
  youtube_documentary/engine/projects/black_hole \
  /home/user/build/black_hole/What_If_You_Fell_Into_a_Black_Hole_1080p.mp4 \
  /home/user/build/black_hole/rebuilt_review
```

`DOCENGINE_BUILD=/absolute/external/build` overrides the default build directory if needed, for capture AND mixing. Use that same path for review. Output:1920×1080,24fps,2990frames,124.583333s. Captions OFF. All display and speech English. The stage does not use a remote CDN at render time.

Final `scene.mjs` directly includes the small-hole/interior spatial corrections and65s heading-contrast correction. You do NOT need to repeat the iterative patches when reconstructing the final source. `history/scene_base_capture.mjs`, `base_capture_source_manifest.json` and `spatial_clarity_revision.json` describe the first capture and later correction; the historical manifest is NOT the final source inventory. Picture replacement re-encodes the entire picture: no approved-pixel preservation claim. Approved Escobar is untouched.

## Review and source checks

```sh
python3 youtube_documentary/tools/style_contract.py check --project youtube_documentary/engine/projects/black_hole
python3 youtube_documentary/tools/production_policy.py youtube_documentary/engine/projects/black_hole/display_manifest.json
node youtube_documentary/tools/tests/test_horizon_motion.mjs
```

These only check declared style/language/design and bounded authored mathematics. They do not certify visual professionalism, listening, calibrated astrophysical predictions or user approval. Inspect the actual final encode at0.5s cadence plus finer joins/motion and native key frames. `review_inspection.json` and `QC.md` bind the actual observations to the final delivered SHA; generated-but-unopened sheets are not reviewed.

## Excluded heavy/cache files

No node_modules, browser binaries, Python environment, Vosk model, intermediate render or movie bytes are vendored. The movie is stored separately from the compact source/voice/review capsule. The final delivery receipt supplies its Drive pointer and hashes.

Optional ASR model used: `vosk-model-small-en-us-0.15`, retrieved through GitHub API raw content, `https://api.github.com/repos/kercre123/vosk-models/contents/vosk-model-small-en-us-0.15.zip`;41,205,931B ZIP, SHA256 `30f26242c4eb449f948e42cb302dd7a686cb29a3423a8367f99ff41780942498`. Model is a fallible transcription aid, not part of rendering or a substitute for ears. Use the supplied raw ASR and processed FLACs; a model download is not needed merely to render.

Final movie SHA256: `959ebb08c76d0c0003742c537413411a472568f8462f6f86f3bc8e07404693ae`. Film: https://drive.google.com/file/d/14Iew5HQ8gxORHRgA3pviQj1dFvBEpbNx/view . The capsule cannot contain its own post-upload Drive identifier/hash: use the separately verified delivery/handoff receipt for that pointer. All29final review sheets and eight native key frames were actually opened; this is not ear-listening.
