# Escobar archive — actual acquisition and review, 15 October 2026

**No revised film created. v1 remains rejected. Exact approved voice-02 unchanged.**

## Decisive result: an official, unmarked program source is now acquired

The official Charlie Rose segment **Andrew and Leslie Cockburn**, aired **12 November 1992**, matches the later discussion in the MOBFAX compilation. The primary program catalog and the separate Reelin' In The Years catalog agree on the date; the latter identifies its interview as item **58597**.

- [3](https://charlierose.com/videos/15564): official segment, program/date/guests and public video.
- [Licensor catalog](https://www.footage.net/clipdetail?supplier=reelin&key=32618363): Andrew Cockburn & Leslie Cockburn, *Interview Re: Pablo Escobar*, 11-12-1992, ID58597.
- Official English captions: URL and selected original cues are saved in `official_source_evidence.json` and `primary_caption_excerpt.vtt`.

The official first 120 seconds were actually acquired through CI and retrieved locally, not merely found in search. This is a bounded research transcode of the broadcaster's public player, **not an HD master or a publication license**. Probed original excerpt: 720×480, progressive, 30000/1001fps, square pixels. No watermark was erased/cropped. The viewed official frames contain none of the repost's WAZEE/ABC timecodes/MOBFAX overlays.

### Specific soundbite candidate — select meaning before timeline

> “his decision to allow himself to be put in a prison of his own making”

Speaker: **Charlie Rose, interviewer**. This is the final fragment of a question to Andrew Cockburn, not an independent declarative news bulletin. The complete primary-caption context is saved alongside this note. Do not portray the interview as live coverage of the surrender or escape: it aired after the escape.

Candidate source range **30.18–37.18s in local `original_opening.mp4`**, not in the 43-minute repost. Cut boundaries remain provisional. Local ASR of both the repost and the official source agree on the prison phrase; the **primary program captions independently corroborate the wording**. Their cue timing is not exactly aligned to this local media, so do not cut by VTT timestamps alone.

Narrative handoff:

- Actual interviewer: “…a prison of his own making.”
- Approved narrator: “This is Pablo Escobar's prison. He helped design it, picked his own guards…”

This is a real semantic connection, not generic drug-war footage in a prepared silence. About seven seconds of archive plus the intact 21.8-second approved performance fits the 30-second scope with a small transition/end allowance. This is a timing feasibility check, **not a final approved montage**. Do not introduce another empty pause to fill a predetermined slot.

### What was actually reviewed

- Official opening overview: first 16 samples, approximately every five seconds, actually displayed in a contact sheet.
- Candidate: all 15 generated approximately 2fps samples displayed in a separate sheet.
- The native edit begins on Andrew listening, then cuts back to Charlie speaking roughly three seconds into this candidate. Preserve native picture/audio; do not imply that Andrew speaks Charlie's line.
- Local Vosk ASR run on the official 120s and on two repost excerpts.
- Primary program English VTT retrieved and quote context checked against it.
- **No claim of continuous AV playback or manual listening.** Frame sheets, ASR and caption verification are distinct evidence, not listening.
- No mixed deliverable or revised prison scene has been reviewed, because neither exists yet.

## Recoverable research objects — all jobs completed

Use `python3 tools/archive_research_fetch.py --run RUN --out DIRECTORY` from `youtube_documentary`. The blobs are unreferenced research objects, **not private** and not rights grants. Local build directories/model installs are volatile.

| Purpose | Run | Git blob | Local directory |
|---|---|---|---|
| Compilation opening 180s | 38731224770 | `802e541d801ec9c7fe3f414713b3ed8f9784189e` | `/home/user/build/escobar_archive_research` |
| Compilation overview, source1500–1620, final180s | 38732086674 | `5293237295dab9baf397563b32508ff30362c174` | `/home/user/build/escobar_archive_research_remaining` |
| Compilation interview opening, source1660–1840 | 38732525316 | `4f3dfadbddd65cbcadcd404197da74379bde3dc0` | `/home/user/build/escobar_archive_interview` |
| **Official program opening120s** | **38732941054** | **`4e7114018505ee78e1aedf93d38f007c6bd2b10b`** | **`/home/user/build/escobar_archive_official`** |

There is **no pending acquisition job**. Do not resume old failed watchers or redo the entire source search. The official program is the useful current lead.

## Do not generalize the compilation's opening watermark to the entire file

Actual sample inspection found:

- Opening CBS packages: intrusive central WAZEE stock-preview mark; reject this copy for delivery. Exact CBS edition(s)/anchors have not been independently matched. Do not identify the female anchor as Connie Chung from appearance, or assign the entire compilation the date of one indexed bulletin.
- Middle ABC raw prison tour: ABC VideoSource licensing logo and timecodes; not a clean final asset.
- Roughly28m–end: Charlie Rose discussion; only the MOBFAX corner mark in inspected repost samples, no central WAZEE/ABC mark. Now superseded for the candidate by the acquired official program.

`middle_1500.mp4` is **ABC reporter takes**, not Charlie Rose. `middle_1660.mp4` includes the transition into the discussion. `ending.mp4` is the last180s, source offset2445.328s. Ending ASR discusses bribery, fugitivity and a letter; it is not preferable to the newly found specific prison soundbite. No need to force generic remarks into this hook.

## Remaining editorial work — not an approval checklist

1. Finish exact source-boundary/audio-transition review and document a valid use basis. Public playback does not mean a publication license was obtained; no such license is claimed.
2. Make a **new** source-led scene plan. Do not automatically reuse the rejected v1 shot sequence, quote slides or decorative captions.
3. Establish the prison spatially and legibly, with a justified camera and clear material/action. Do not fix ambiguity by inventing a generic fortress, unsupported towers, measured floorplan or escape route. Any approximate reconstruction must be identified as illustrative, not period evidence.
4. “Picked his own guards” needs a scene that communicates control, not a decorative HIS GUARDS caption. “Running his business” needs a meaningful visual, not arbitrary glowing arcs or repeated thumbnails.
5. Inspect representative composed scenes **before** a long render. Reject weak staging proactively. Then inspect the actual encoded montage at every0.5s plus interstitial motion, cuts, source/narrator handoff and mix evidence. Do not call codec success or a passed test suite professional art approval.

The old render/model/finish gate remains blocked. No new video, delivery approval or video upload has occurred. Handoff notes may be synchronized separately. `editorial_review.json`, `ARCHIVE_PREFLIGHT.json` and the evidence JSON record these distinctions.

Technical regression only: `python3 -m unittest discover -s tools/tests -v` —22testsPASS in5.698s. This is not new video QC, creative approval or rights clearance.
