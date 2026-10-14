# REFERENCE ACCESS REPORT — what was actually accessed, and what was not
Date: 2026-10-14 · Environment: Arena sandbox (outbound network restricted)

## 0. The honest headline
**Frame-level access to the reference videos is NOT available in this sandbox.**
Tested directly: `i.ytimg.com`, `googlevideo.com` and all video CDNs fail to connect
(curl exit 000 on all 9 video IDs). Per the directive, no timestamps, shot
descriptions or "watched it" claims below are fabricated. What WAS accessed is real
and listed per video: official watch-page metadata, chapter lists, and the **full
narration transcripts**. Official key art was retrieved and visually verified for
exactly one video (Kurzgesagt). For the other eight, the official thumbnail URLs are
listed in §3 for one-click manual opening.

## 1. Successfully accessed reference videos (deliverable 1)
| # | Video (ID) | Channel | Length | Metadata | Transcript | Chapters | Official key art |
|---|---|---|---|---|---|---|---|
| 1 | The Disturbing TRUTH About Vaping (`xkfctt5038w`) | MagnatesMedia | 27:27 | ✅ | ✅ full | ✅ 8 ch. | ❌ URL only |
| 2 | The Dark Truth About PayPal (`DwTK_VT54OY`) | MagnatesMedia | 57:34 | ✅ | ✅ full | ✅ 13 ch. | ❌ URL only |
| 3 | The Incredibly Satisfying Collapse of Dubai (`rWgWd-4L9uY`) | Moon | 3:01:42 | ✅ | ✅ full (long-form) | ❌ none | ❌ URL only |
| 4 | Crypto: The World's Greatest Scam. (`ORdWE_ffirg`) | James Jani | 54:18 | ✅ | ✅ full | ❌ none | ❌ URL only |
| 5 | Apple Is Now Completely F*cked (`jnQBhiipsQM`) | Moon | 17:29 | ✅ | ✅ full | ❌ none | ❌ URL only |
| 6 | AI Just Crossed the Terrifying Line (`ujkD4SxPKOI`) | Kurzgesagt | 21:44 | ✅ | ✅ full | ❌ none | ✅ **retrieved & verified** |
| 7 | Why Everything is Going Wrong for Saudi Arabia (`U_UoAZrOTNU`) | RealLifeLore | 25:20 | ✅ | ✅ full | ❌ none | ❌ URL only |
| 8 | WW2 — OverSimplified Part 1 (`_uk_6vfqwTA`) | OverSimplified | 13:45 | ✅ | ✅ full | ❌ none | ❌ URL only |
| 9 | WW2 — OverSimplified Part 2 (`fo2Rb9h788s`) | OverSimplified | 15:34 | ✅ | ✅ full | ❌ none | ❌ URL only |

Also documented from the same pages: each channel's **declared production pipeline**
(OverSimplified: "Adobe After Effects and Photoshop" — video description; Kurzgesagt:
Illustrator + After Effects flat design — channel's own statements; RealLifeLore:
"GEOlayers 3, MapTiler/OpenStreetMap, Getty Images, AP Archive" — video description;
MagnatesMedia: After Effects-based workflow — magnates.media/editing; James Jani:
Epidemic Sound/Artlist/MotionArray + sells his editing templates). These are primary
self-declarations, quoted, not guesses.

## 2. Exact time ranges analyzed (deliverable 2)
- **Narration layer:** 100% of all nine transcripts were read (multi-chunk fetches).
  Transcript-level pacing, segment construction, chapter architecture and
  narrator/quote/archive interleaving were analyzed end-to-end (e.g. PayPal's 13
  chapters 00:00→55:37; Vaping's 8 chapters; the Dubai 3-hour film's cold-open build).
- **Visual layer:** only stills, no motion. Retrieval attempts (direct CDN, search
  mirrors, third-party rehosters) returned either blocked connections or unverifiable
  rehosted images, which were rejected. The single verified still is in
  `engine/reference_lab/stills/`. **No motion-sample analysis has been done yet.**
  Anything in the technique database that normally requires frame evidence is labeled
  `INFERRED` with its actual basis (transcript structure + declared pipeline + key art).

## 3. Representative frames (deliverable 3)
- Verified: `stills/kurzgesagt_ai_line_official_thumb.jpg` — official thumbnail of
  video #6 (flat-vector identity, oversized display type, radial burst composition).
- Official thumbnail URLs for manual opening (blocked from sandbox):
  `i.ytimg.com/vi/<ID>/maxresdefault.jpg` for the 9 IDs above.

## 4. Two concrete paths to full frame-level analysis (your call)
1. **Upload path (works today):** drop any reference video file (or 30–60s clips of
   the sequences you care most about) into the Drive folder. I run
   `tools/reference_ingest.py` on them locally: automatic shot-boundary detection,
   contact sheets, shot-length CSVs — then do the real Phase 2 frame-by-frame
   breakdown on actual pixels and upgrade every `INFERRED` label.
2. **Your-machine path:** run `tools/reference_ingest.py` where downloads are allowed
   on files you legally obtain, and upload its outputs (contact sheets + cuts.csv) —
   I analyze from those.
