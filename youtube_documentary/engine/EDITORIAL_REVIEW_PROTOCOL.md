> **Supporting technical/reference document.** [Current entry](../../START_HERE.md); current user rules and approval/state registries in `../../studio/` take precedence. This document is not the current assignment or a new approval.

# Mandatory scene-by-scene editorial review — all future films

User instruction, 2026-10-15: do not hand over basic creative mistakes for the user to fix. Inspect and understand every proposed scene and the delivered montage before presenting it. Applies to every topic and duration, not only Escobar.

This is an authoring/review discipline, **not an automatic certificate of professionalism**. Technical correctness, a checklist, 3D, a passed encode or a test count cannot substitute for actual editorial judgement.

## Before constructing each scene

Record a short concrete answer to each question:

1. **What does this scene tell the viewer?** State the actual new fact, implication or emotional/narrative function. “Looks cinematic” is not an answer.
2. **Why this exact material?** Verify the person, place, original date and source. A modern site photograph does not depict a historical event. A generic illustration is not evidence. A relevant video with its actual audio is not interchangeable with a quote slide.
3. **What is the speaker actually saying?** Obtain and inspect original clip audio; timecodes/transcript/speaker identity must be grounded in the source. ASR is an aid, not proof of correct speaker identification or a claim of human listening.
4. **What is the visual idea, beyond a box and label?** Specify composition, meaningful action, focus and how the viewer recognises the important object. A model that fails to read as a prison is not fixed by adding “PRISON”.
5. **Why does the camera move or the edit cut here?** Follow meaning, attention and continuity. Do not animate merely to keep the picture busy.
6. **Does text genuinely add information?** Default narrative captions OFF. No decorative repetitions such as “HIS GUARDS”. Permit a necessary date/source, or a motivated word-motion scene with a clear reason.
7. **What is the source-to-narrator handoff?** Select the real soundbite first. The narrator must continue/explain/reframe its specific meaning, not deliver an unrelated prepared paragraph after arbitrary “news”. No obligatory fixed archive/narrator template.
8. **What would make this scene fail?** Anticipate irrelevant imagery, false historical implication, unclear shapes, toy-like models, weak staging, empty pauses, visual monotony, caption clutter, unreadability, interpolation artifacts and audio discontinuity. Resolve problems before spending on the full render.

## Before final presentation

- Review **the encoded deliverable**, not merely source stills or the renderer plan.
- Inspect every scene, the opening hook and every handoff/cut. Check semantic fit, pacing, continuity, image treatment and small-screen readability.
- Create chronological samples at least every 0.5s plus frames **between** rendered/interpolated keyframes around motion/edits. A 2fps sample grid can accidentally miss all interpolated frames.
- Review audio content/timing and the mix. Keep evidence for what was actually checked; do not claim full listening/playback if only ASR, frame sampling and measurements were performed.
- Compare applicable choices to **already viewed reference evidence**. A reference technique is a basis for decisions, not permission to recreate an unsuitable superficial layout.
- Reject weak scenes yourself. Do not hand them to the user as “professional” because the code/codec/tests passed. No delivery with unresolved foundational failures.
- Clearly separate user-approved voice/direction from unapproved visuals. Do not repeatedly re-audition an approved voice to compensate for poor editing.
- If essential authentic media is unavailable, report the specific acquisition blocker. Do not fill the hole with slides and call the requested archive-led cut finished.

## Records

Keep per-scene source/timecode decisions and actual visual-review findings in the film profile. The common production policy links to this document. No new full documentary or reference study is authorised by improving this workflow.

## Material/idea review added after revision2 feedback

Follow `DOCUMENTARY_MATERIALS_AND_IDEAS.md` for every film. Ask whether attractive generated/model shots have displaced available real subject material. Review the premise and editorial variety before polishing cameras; an excellent model does not repair a weak script. Check provenance, temporal context, authentic spoken handoffs and genuinely present press words. Photo-derived generation needs inspected references, preserved-feature/unknown-area records and disclosure; it is not archive or a watermark-removal workaround. No fixed asset quota or fixed intro length replaces judgement.


## Source-internal cuts and packet-copy final assembly

- A file or sparse overview labelled “lab”, “football” or “government” is not evidence that every second contains that subject. Check the exact in/out range, including native cuts and crossfades. A muted interview face under a different narrator can misattribute speech even when the wider source is relevant. Replace the actual shot; decorative attribution does not repair the wrong source selection.
- Extract review evidence from the final encoded delivery, not just a preview or source. Include every half-second, ±one frame at planned AND detected source-internal cuts, and12fps evidence through authored map/depth movement. Inspection is a recorded human/agent observation, never an automatic render flag.
- Keep the decoder frame index global when concatenated H264 changes benign square-pixel SAR metadata: FFmpeg filter reinitialization can reset select(n), silently mislabeling evidence. Disable reinitialization for fixed-dimension review extraction, assert exact evidence counts, and clear stale numbered files before regeneration.
- When a real witness interrupts narration, inspect the return picture too. Do not resume an accidental fraction-of-a-second fragment before the next scene; choose a motivated continuation. Inspect a long final native shot through its OUT point before adding a fade.
- Locked approval belongs to actual approved pixels, samples and identity, not merely a filename. Verify input SHA, all decoded approved picture frames, and ALL approved audio samples. AAC packet-copy priming must be compensated on the audio clock, not by globally speeding or stretching approved content. Report boundaries honestly; do not declare an opening unchanged after checking only an early subsection.
- Automatic recognition, loudness and complete decode are useful technical evidence, not manual listening, voice naturalness, creative approval, or publication-rights clearance.

### Source-native cut tails and review reuse
- A quote's picture may need to leave before its unchanged audio. Use a motivated L-cut onto verified contextual footage rather than inheriting an unrelated source cut, freezing a speaking face, or clipping the last word. Inspect the encoded return; coalesce duplicate source cues so it does not replay/flash.
- Rounded source clocks are candidates, not cut-safe bounds. Check both ends with fine frames; an unwanted two-frame interview tail can survive a sparse source overview.
- After a visual-only correction, evidence may be reused ONLY at identical global decoded frame indices with exact image hashes and an actually inspected predecessor. Inspect every changed/new sample; persist the chain, observations and old/new video hashes. A hash match does not itself make an earlier missed defect acceptable.
- ASR from a prior picture encode is applicable to a revised encode only with explicit provenance and exact decoded-audio identity; keep both video hashes. This remains automatic recognition, not ear-listening.


## Named styles —2026-10-16
Read STYLE_GUIDE.md and STYLE_REGISTRY.json before choosing material. Pure-documentary and pure-explainer are different valid treatments, not a universal archive-first recipe. New projects need a style contract; the actual rendered scene must still match it. For an explanatory board, inspect persistent anchors, motivated attention/camera travel, causal state changes, selective word/audio timing and the return to the same world.2D is acceptable when meaningful; shadows/tilt do not establish3D. A liked concept is not a finished approved benchmark. Inspect the actual final encode, not just a fulfilled JSON contract; no test guarantees exceptional editing or zero errors. Historical review/ASR logs keep their original scope and dates after later user approval.
