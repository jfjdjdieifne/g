> **Supporting technical/reference document.** [Current entry](../../START_HERE.md); current user rules and approval/state registries in `../../studio/` take precedence. This document is not the current assignment or a new approval.

> **تحديث أولوية — 2026-10-16:** ابدأ بـ`../START_HERE.md` ثم `engine/STYLE_GUIDE.md` و`engine/STYLE_REGISTRY.json` (المسارات من جذر youtube_documentary). «وثائقي بحت» ستايل مسمّى معتمد من مثال إسكوبار، **مو قاعدة لكل فيديو**. الستايلات الشرحية لا تُجبر على الأرشيف؛ البحث والصدق والمراجعة إلزامية دائماً. التعليمات التاريخية المخالفة تُقرأ ضمن سياقها القديم.

# Documentary substance before rendering polish

Standing user direction,15October2026, after Escobar revision2. Applies to **every subject and duration**. The user strongly liked the progress,3D and shots; the opening's writing, ideas, diversity and substitution of a schematic for real prison imagery need improvement. This is not blanket approval of the delivered script or an instruction to add random effects.

## Decision order

1. Define a concrete **premise/contradiction and payoff**, not just a topic or a tour of objects. Why should this introduction exist?
2. Find and inspect actual material: exact people/place/events, reports, interviews, photographs, magazine/newspaper issues. Verify dates, speaker, words and context; record acquisition/rights separately. Search hits are leads, not viewed assets.
3. Develop script and material together. An archive speaker may introduce, contradict, explain or advance a fact; the narrator reacts, connects or reframes. Do not lock a monologue and decorate it afterwards. Do not require identical archive/narrator ordering in every film.
4. Compare alternative treatments for each beat. Real footage/photo is normally better for showing a real subject; a model may be better for an inaccessible mechanism or spatial relation. Keep excellent3D as part of the vocabulary, not the entire documentary's material.
5. Inspect representative compositions and the **idea/rhythm** before an expensive full encode. Too many interchangeable good-looking shots can still be a weak opening. No media-type quota or diversity score certifies quality.

## When a needed view does not exist

- Inspect a real photographic/filmed reference first. Do not pick a generic plausible prison because it is easy to model.
- Record source ID/date/rights, retained features, requested change, unknown/invented parts, generation lineage and output review. An actual photograph used as-is stays authentic; generated surroundings or a new viewpoint are **derived illustration**, not period evidence.
- Use a depth-separated photo/2.5D projection when modest parallax is sufficient; real3D geometry for camera travel/occlusion that requires it. Avoid revealing unobserved surfaces as documented architecture. Do not call a flat zoom real3D.
- Disclose generated/reconstructed material in the film as appropriate and in source records. Never generate a fake archival newspaper, signature, presenter, quote or supposed historic event as evidence.
- Never erase stock-preview marks, or use generation to launder a marked preview into a supposedly authentic clean original. Seek the appropriate original/license or use a separately sourced genuine reference for a clearly identified illustration.
- No arbitrary creative cap:100 or1000 images are acceptable **if needed**. That is permission to pursue necessary ideas, not a quota, a substitute for sources or a reason to skip per-asset/encoded-shot review. Keep large media out of Git and persist via authorized storage.

## Optional press-name match montage

User example: successive genuine newspaper/magazine crops contain **Pablo Escobar**. Keep the name at approximately one screen anchor while each original page/crop changes, then hand the rhythm into a purposeful final phrase/typographic scene.

Before building: inspect every real scan, identify publication/issue/date, verify the exact visible word and crop, retain enough context to avoid misrepresentation, and distinguish multiple crops of one issue from independent coverage. Do not invent headlines to obtain the motion. Verify readable anchor, timing and joins in the actual encode; sound/text movement should land with the narrator's thought, not decorate every syllable.

This is **an option suggested by the user**, not a newly viewed reference technique or a compulsory ending for every project. Choose it only when media saturation/identity/repetition is the actual narrative function.

## Planning contract and limitations

New `tools/director.py` plans accept `documentary_material_plan` with:

- `assets`: unique `id`, `kind`, `description`; authentic entries add `source`, `date_context`, `review_status: inspected`, `review_evidence`, `rights_status`. Accepted kinds: `archive_video`, `interview`, `real_photo`, `press_scan`, `generated_from_photo`, `generated_illustration`, `original_model`, `graphic`, `typography`.
- Derived generation adds `reference_id` resolving to an inspected real visual, `preserve`, `unknown_or_invented`, `presented_as_archive: false`, `disclosure`.
- `beats`: `id` matches director row number exactly, `function`, `material_ids`, `choice_reason`, `why_not_real` (why authentic material is used, or why a justified alternative explains better).
- Archive-owned speech needs exact sourced quote, speaker, source boundaries and honest audio-review method on the referenced footage. `press_word_match` needs `word`, genuine `press_scan` entries containing it in `verified_crop_text`, and `semantic_reason`.

`tools/documentary_materials.py` validates **declarations and references**, not actual images, meaning, listening, legal clearance or artistic quality. A complete declared material plan plus display/design requirements can make a director plan structurally render-ready; actual source inspection and the editorial self-review protocol remain mandatory. Missing plans leave legacy files usable for planning, never ready for a new render. Authoring stills/tests are not final-film approval.

Opening length follows material and story, not an arbitrary30-second ceiling. This feedback permits broader planning, **not automatic approval of a new runtime, a new spoken performance, the full documentary or the next reference study**. Preserve the approved voice identity/style and original take; propose new words before generating replacement narration. All film content remains English.
