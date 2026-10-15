# Escobar — first30seconds, English — revision2

This is a new source-led editorial review cut, not a rebuild or approval of the rejected v1. Only the first30seconds are authorized. Voice-02's exact approved recording is retained as one intact take.

## Concrete direction

A real interviewer's question establishes the contradiction: a prison of the prisoner's own making. The narrator identifies Escobar and explains control of design, security and business. A single persistent three-dimensional world supplies all the subsequent views; the shots are not quotation slides, image cards or independently popping labels.

| Time | Actual picture | Reason |
|---|---|---|
| 0–7.6 | Official Charlie Rose interview video, native camera edits, original speech | Specific prison soundbite first; not generic news in a silence |
| 7.6–11.8 | Lit architectural schematic with perimeter, gate, two guards, pitch, rooms | Establish secure custody and private amenities simultaneously |
| 11.8–13.3 | Guard inside the enclosure, fence behind | Focus follows “picked his own guards”; no decorative caption |
| 13.3–16.15 | Persistent office's telephone, desk and fax | Business continues inside; no arbitrary floating networks or forged document |
| 16.15–21.95 | Pitch, comfortable interior and fencing seen together | Explain the contradiction in “not quite the way you'd expect” |
| 21.95–24.5 | Empty room/bed in the same building | Visual absence, not a fabricated escape route or gate-walk reenactment |
| 24.5–30 | Return to the entire custody arrangement | Hold the narrator's two unanswered questions; no closing title slide |

Only necessary on-screen identifiers are used: program/date, place, and **Illustrative cutaway**. Narrative captions default OFF. The model is a conceptual illustration, **not a measured La Catedral floorplan**. Its architecture, anonymous figures and object placement are not documentary evidence of precise historic appearance.

## Art checks before spending on the full render

Six representative views were generated and viewed. The first guard shot was rejected because the foreground mesh obscured him; its camera moved inside the boundary. A block-bodied figure was rejected and rebuilt with tapered torso, articulated limbs and rounded boots/cap. Bedding became a continuous cloth surface instead of a rectangle; decorative faceted trees were removed. Material response and physical depth of field were added using the existing shared renderer. No invented guard tower or escape trajectory was added.

A separately encoded first13.29-second motion diagnostic was sampled across the source/illustration handoff, guard cut and interpolated frames. It is an excluded build diagnostic, not a deliverable. Final encoded review is separate; see `QC.md`. Technical success is never user or professional-art approval.

## Reference basis, not a new study

Existing viewed study `engine/reference_lab/Vaping_BREAKDOWN_2fps_full_v2.md`,0:00–0:07, documents a media/article/real-presenter opening. Its0:48–1:00 entry explains connected spatial movement. Apply those narrative/spatial functions, not literal copied layouts. `engine/reference_lab/TRANSITION_ATLAS.md` supports deliberate cuts alongside continuous motion; no obligation to dissolve every scene. No new unseen footage is claimed to have been studied here.

## Shared architecture and truthful sampling

`scene.py` is this film's staging/camera profile. Geometry/cameras and optional Cycles CPU rendering remain in the existing shared `engine/runtime/xyz_scene.py` and `blender_xyz.py`. The shared backend gained opt-in physical focus/depth of field and object-space surface recipes; older profiles retain their defaults. The two tools are orchestration, not a new general renderer for every film.

- Official archive research excerpt:720×480,29.97fps, bounded transcode, not restored HD.
- Model:960×540 (office macro1280×720),8rendered samples/second,4Cycles samples/pixel.
- Motion compensation:each shot separately to24fps, **never across an edit**.
- Composition/text/encoding:1920×1080,24fps,30seconds.
- No claim of native1080p/24fps model rendering.
- Original AI narration:21.7990625decoded seconds from7.6 to29.3990625, unretimed, unsplit, constant gain only.
- Original synthesized ambient underscore; transition SFX measured9dB below the local music bed.
- Audio content checked with source captions, ASR and measurements. Do not claim manual listening or continuous playback when only those methods were used.

## Reproduction

From `youtube_documentary`, after restoring the official excerpt and existing bpy runtime:

```sh
LD_LIBRARY_PATH=/home/user/build/blender_libs python3 tools/escobar_hook30_revision2.py --stills
# Inspect the representative scenes and record real findings before authorizing samples.
LD_LIBRARY_PATH=/home/user/build/blender_libs python3 tools/escobar_hook30_revision2.py --render-samples
python3 tools/escobar_hook30_revision2_finish.py --audio
python3 tools/escobar_hook30_revision2_finish.py --finish
python3 tools/escobar_hook30_revision2_qa.py
python3 -m unittest discover -s tools/tests -v
```

The renderer verifies actual source and approved-voice SHA256s. The finisher refuses absent render samples rather than silently substituting a software placeholder. Build output is excluded and volatile. Deliverable location: `/home/user/build/escobar_hook30/revision2/Escobar_First30_English_Revision2.mp4` (completed; durable Drive link and hash are in `delivery.json`). Do not present diagnostics as the finished film.

## Rights

See `SOURCES_AND_RIGHTS.md`. This short, acknowledged quotation is used in an editorial explanation/review, **not evidence that a publication license was obtained**. Original program/date are independently corroborated. No third-party stock-preview watermark is removed. User approval of voice is not approval of new visuals or rights clearance.

## Current delivery

[Open the revised30-second film](https://drive.google.com/file/d/1Wd71BUBgJlAdhXZtcg3f8oI6XbP6uthD/view). Sampled encoded review complete; user visual approval and publication rights remain open. See `QC.md` and `delivery.json`. Office macro uses a corrected drawer-detail LOD of the same staged furniture. Initial encoded artifact was withheld and replaced, not delivered.
