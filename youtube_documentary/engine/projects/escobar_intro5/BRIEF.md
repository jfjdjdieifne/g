> UPDATE: The user approved this complete33.125s opening and authorized a4–9minute full film. The opening is locked, byte-identically reconstructed (sameSHA256). Later body narration is separately pending pace approval; earlier candidate/unapproved wording below is historical.

# Revision 5 — source-led opening, not another shortening pass

**33.125 seconds. Candidate for the user's review, not approved. Opening only.**

Revision4 was substantially rejected despite technical checks. Its recycled interview/photo structure, disembodied opening voice and repeated-name marker/shutter motif are not carried forward.

## New narrative

Immediate contradictory facts: a cocaine trafficker on a billionaire list, an elected alternate congressman, a housing benefactor and a source of terror. An industrial comparison from a real DEA interview hands off to the economics of a flight. A different insider then describes a price on his own head. The closing question connects coercive power and public support, without revealing Escobar's fate, escape, death or major payoffs.

`SCRIPT_EN.json` contains the three used narrator passages. These are newly generated performances of the already-approved **voice-02 identity**. Raw takes and the original approved recording are preserved. The industry take's unused second half is NOT silently discarded. Working takes and emotional performance remain unapproved.

Protected quiet-pause edits retain phoneme speed/pitch: hook **179 WPM**, numerical explanation **149 WPM**, question **186 WPM**. There is no atempo, global voice/movie acceleration or archival speech retiming. These measurements do not prove naturalness or excitement; no manual ear listening is claimed.

## Actual media, and honest limits

- Two distinct interview contexts, **Thomas Cash** and **Max Mermelstein**, both from **the same FRONTLINE programme (1995)**. They are NOT multiple independent newscasts. Unlike the rejected cut, each person is actually shown and identified on the relevant original speech. Mermelstein's recorded appearance is in disguise.
- Cash enters 10 frames/0.4167s before his own picture. His source picture stays aligned with source sound. A 7% editorial push is added; it is not claimed as newly filmed historical camera motion. His source's brief native cutaway at the end is retained.
- The insider's threat is a real attributed statement, not synthetic narration or an unattributed quotation slide. Fallible ASR is not certified verbatim human transcription.
- Actual Escobar moving footage, aircraft/cockpit/runway/surveillance imagery, estate footage and Miami street imagery from FRONTLINE. The report's aircraft imagery is **contextual**, not independently verified footage of the particular 400kg/$10M flight. The street scene is an operating-environment illustration, not a claim that the visible car belongs to Escobar. The source itself briefly reuses night-street imagery in its prologue; this is not counted as an extra independent source.
- Historical responders/fire aftermath from Al Jazeera's 2018 retrospective: no bodies/medical close-up selected, no added literal explosion or gunfire.
- BBC's **2013** residents and Al Jazeera's **2018** mural illustrate contemporary public legacy, explicitly dated. No claim that a pictured individual received a specific home or personally endorsed a particular quoted view. No source English dub is falsely assigned to another face.
- Four genuine still/document assets, each used **once**: Forbes' 1987 Escobar entry, the congressional photo, the actual 1983 housing construction photo and the 1983 football/public-appearance photo. Original-pixel camera staging; the last uses the common 2.5D runtime with disclosed inferred depth/inpainted edge gutters. These are not recorded live movement.
- One end film title over a real mural, with an approximately one-second editorial freeze. No name/shutter/marker loop. Ordinary dialogue captions remain OFF. Authored display and foreground speech are English. Broadcaster marks and original incidental source imagery remain intact.

The film has **17 authored visual segments**, with additional native cuts within some source excerpts; this is not a claim of 17 independent source recordings. Material selection is documented beat by beat in `MATERIALS.json`.

## Sound and common engine

Original 144 BPM synthesized minor-key rhythm score with strings-like harmonics, bass and percussion; it is not a purchased orchestral track or recovered historical sound. Music ducks beneath source speakers. Seven editorial transition effects are individually held about **7.96 dB below their local music window**. No effect is presented as evidentiary location audio.

Shared runtime: `sequence_runtime.py`, `score_runtime.py`, `film_runtime.py`, `photo_depth.py`, `speech_edit.py`, `encoded_review.py`. Film-specific material/timing lives in this profile. Render through:

```sh
python3 youtube_documentary/tools/render_film_profile.py escobar_intro5 --render
```

Restore selected external source clips using the object/run in `source_retrieval.json` and `tools/archive_research_fetch.py`; do not add full programmes to Git. `MATERIALS.json` records selected source hashes. Source and display gates run before future encoding. The finished candidate was also validated before delivery.

**Rights are unresolved.** Publicly accessible material is not permission to publish. This is an internal editorial review delivery. The 1920x1080 composition contains lower-resolution archive/reproduction material, not native-HD historical photography. Technical checks and AI frame inspection are not a professional/human approval certificate.
