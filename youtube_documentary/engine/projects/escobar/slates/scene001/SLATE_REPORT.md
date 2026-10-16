# Scene 001 engine slate — Gate A/B
Strategy: spatial-canvas. 3 frames @ t=0.27/2.37/6.70 from the production
runtime itself. Gate A/B: PASS_WITH_WARNINGS (2 known asset warnings:
medellin 612px source is storyboard-only, upscale 3.14x — full-res licensed
replacement required before production; flagged automatically by QC).

Self-critique findings caught and fixed this round:
1. Word spacing collapsed (text nodes at UA font size) → spacing moved to
   .mask margin in em. Verified in re-render.
2. Bars layer painted UNDER base photo (DOM insert order) → crossfade never
   visible; layers now append in declared order. Verified.
3. Mugshot halo (light archival background) → photographic grade + warm tone
   composited under feather inside the texture. Verified.
4. First two words required animation before frame zero → explicit preRoll
   policy added to typography director; "In" on-screen at 0, "1993," readable
   60ms before its onset.

QC also verified: exact-script token check PASS (17/17 words), schedule
valid (no readable-after-onset, no negative animStart), no text outside
safe frame, no text-text overlap, no text over subject beyond threshold.
