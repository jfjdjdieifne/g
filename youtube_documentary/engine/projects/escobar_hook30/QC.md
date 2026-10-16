# QC — Escobar 30s review cut v1 / 2026-10-15

**SUBSEQUENT USER VERDICT: REJECTED.** Technical results below describe the historical file, NOT editorial success. User approved continuity only; rejected stills, slide-based pauses, decorative captions and montage. Prison model shows progress but remains insufficiently legible/professional. See `editorial_review.json`; revision blocked pending real acquired/viewed/heard news clips.

## Actual delivered file

- `/home/user/build/escobar_hook30/render/escobar_hook30_v1.mp4`
- **30.00s**, **1920×1080**, **24fps**, **720 decoded frames**, H.264 / AAC, **21,084,945 bytes**.
- Drive: https://drive.google.com/file/d/1u5iEILmRSzMnIFsGxtDdP3ikXi8j7ufW/view
- Credits: https://drive.google.com/file/d/1cCDi-1AUstrNWJVY3fNA3Zf2KCgD06VJ/view
- Plan: https://drive.google.com/file/d/1QKKcIjWz2YeQtTlZ5hXmn-AjAJ-7sK81/view

## Performed checks

- **21/21 unit tests PASS** across hook, v3 and v4 suites. Hook-specific 10 tests: explicit voice approval + exact MP3 SHA256, English/scene-first gates, modern photo/date/credit, no false PBS attribution for comfort quotation, perspective center at different resolutions, height parallax, unclipped press text region, continuous model camera, actual moving gate/figure geometry, shared cylinder/render helper.
- Full final-video decode: **720 frames**, no decode error; metadata duration/fps/dimensions asserted.
- **60 half-second samples viewed** across three contact sheets. These happen to align with 6fps model sample times, so they alone do NOT test interpolated motion.
- Accordingly, **eight additional genuinely interpolated delivery frames** viewed (indices **141, 189, 237, 269, 451, 475, 499, 523**) in two four-image sheets. Gate, figures, office edges and thin fences checked. Minor softness/doubled thin-fence edges from interpolation/low sample count remain; no claim of artifact-free native sampling.
- Final encoded 13.0s source excerpt and 29.0s title viewed at full frame. Earlier full-frame photo/source/model layout checks also performed. No clipped main quotation or empty-box glyph observed in inspected frames.
- Original approved narrator MP3 SHA256: `523220dab1465d8958a24345978de76982953396e05b9bcf7ed012da44c7485d`.
- Decoded narration: 1,046,355 samples at 48kHz (**21.7990625s**, nominal MP3 container approximately 21.84s). Source split **8.30s**, timeline placements **3.00–11.30s** and **15.00–28.4990625s**. No regenerated words, pitch shift or speed shift. Constant gain 1.3539197767, plus a silent edit and quiet original synthetic underscore/soft transitions.
- Final encoded audio measured (FFmpeg loudnorm analysis only, **not** an applied dynamic-normalization pass): **−15.34 LUFS integrated**, **−0.93 dBTP**, **9.40 LU loudness range**. Mixed source sample peak −1.01 dBFS. Synthetic SFX are below the synthetic underscore.
- Photo source/date/author/license checked; modern 2019 label and credit included on screen; full attribution/license/change notice in MP4 metadata and accompanying source document.
- Final encoding refuses absent Cycles/interpolated model frames, instead of silently shipping the low-detail software layout preview.

## Explicit limits / review status

- User approved the **narrator performance**, not yet this video/art direction. Technical tests are **not aesthetic approval** or proof of equivalence to the references.
- No full real-time audiovisual playback/listening-based certification was performed by the agent. Narrator take was previously heard/approved by the user. Full decode, sample viewing and audio measurements are what was actually checked.
- Model is **960×540 / 6fps Cycles CPU sampling**, interpolated to 24fps per shot, then composited with native 1080p text/photo processing. Do not advertise native 1080p/24fps 3D rendering. No interpolation across the press/model hard cuts.
- Architectural cutaway and figure/gate motion are **illustrative**, not a measured La Catedral plan or documented escape mechanism/route.
- Authentic news/TV audio **not acquired**. Written 1997 and 2023 retrospective source excerpts occupy the narrator-free windows. No fabricated anchor or fake period footage.
- Brief third-party editorial quotations are attributed; no blanket PBS/article clearance or legal approval asserted. Source photo adaptation remains CC BY-SA 4.0. No uncertain-rights portrait, watermark or TV recreation used.
- Scope ends at 30 seconds. Await the user's feedback before further film production.
