# v4 depth / English QC — 2026-10-15

Final: `escobar_ww2drive_v4_depth_en.mp4` — **10,880,450 bytes**, 16.00s, 384 frames, 1920×1080 @24fps, H.264 High / yuv420p, AAC stereo /48kHz.

- Full final MP4 decode: PASS, no decode error.
- Final decoded 2fps sheets: 32/32 samples visually reviewed, plus full-size layout stills. Not a claim of individual visual review of all 384 frames or full audiovisual playback.
- 11 automated tests PASS: English-only display and Latin accents; rejection of Arabic letters/digits/punctuation; scene-first and declared depth policy; country/convoy containment; 384-timestamp camera continuity and complete atlas coverage; XYZ/plane-projection equality at multiple Z levels; measurable height-dependent parallax; exact route-endpoint surface anchors; planner policy propagation; no implicit Arabic narrative→caption fallback.
- Audio synthesis / cue timings reused from v3, no VO, no new loud impact layer. Mean -19.6 dBFS, peak -10.9 dBFS. Listening assessment not claimed.
- Expanded the world atlas after finding missing-background corners in the first oblique preview. Re-rendered after correcting the elevated route's Miami endpoint to meet the base surface rather than floating at Colombia's height.
- Initial temporary Drive draft was replaced with the corrected final upload; the temporary draft is in trash, not permanently deleted.

## Artistic scope
v3's design direction was approved by the user. That does not automatically approve this v4 depth treatment. Stylized extruded map, not a terrain/globe or physically based render. Other legacy renderers still need an adapter/call to the production gate before new output. Route/path/tint narrative limitations remain as documented in PLAN.md.
