> **2026-10-16 update:** User praised this completed film and named its authentic-material approach **«وثائقي بحت»**. Full-film approval is now recorded in USER_FEEDBACK.json. Prior pending-approval review logs/capsules remain historical. Read ../../STYLE_GUIDE.md; other style families are not automatically approved. Rights and listening limits are unchanged.

# Escobar — full documentary review cut

**Delivered cut:** 6:50.4167, 1920×1080, 24fps, 9,850frames, H.264/AAC.

- Film: https://drive.google.com/file/d/1xCd3MbgY00MhV57FQIzL3_0Ydj28-zNw/view
- Working/archive folder: https://drive.google.com/drive/folders/1hYHn40_IawAQkBO1u0zoFPU1h4-6KXYC
- Exact MP4: `Escobar_Full_Film_Review.mp4`, 96,129,645bytes.
- SHA256: `7c10862acc22982b2db0ba1df4f97ee15b32c2924778ee14cbb7edb9cb15ee14`.
- MD5: `7ef7af1ca8d833c938265ee75c797468` (also returned by Drive).

This is the completed **review cut**, now a user-approved style reference, but not publication-rights clearance. Conversation is Arabic; narration, quoted speech and authored graphics are English. Genuine historical images retain their original incidental signage.

## Direction and structure

The user approved Revision5's opening and later authorized the full4–9minute documentary, with narration a tiny bit slower than processedV3. No further pace question is pending. Voice identity remains approved `voice-02`. Raw full-body performances were rejected as slow; the derived clause-paced performance is disclosed, not described as naturally faster raw acting. Baseline factors are0.965×V3, with occasional slower emphasis and short pauses. See `USER_FEEDBACK.json`, `narration_pacing.json` and `pace_test/pace_eased_recipe.json`.

The opening remains packet-copied, never rerendered. Its795decoded frames and1,590,000samples in **each of two channels** match the approved opening exactly; maximum audio difference0. Body:97authored shots,377.2917seconds, seven chapters: business/network; protection/public support; politics/Lara; extradition/terror; La Catedral/escape; manhunt/death; conflicting legacy and surviving trade. Opening-only spoiler restrictions do not apply to the authorized remaining film.

One common renderer, not a film-specific engine: `engine/runtime/sequence_runtime.py`, `sequence_segments.py`, `geo_route.py`, `long_score.py`, `speech_pacing.py`. Film choices live in `profile.py`. Source-native motion and witnesses are not speed-changed. Three explanatory map movements and one original-pixel2.5D photograph are disclosed, not fabricated historical action. No default subtitles or compulsory quote-slide template.

## Actual review and limits

Read `editorial_review.json`, `encoded_qc/` and `FINAL_QC.md`. Final grid:821half-second samples,481join samples and271movement samples at12fps. Every grid image is covered by actual visual inspection or exact-image identity to an actually inspected predecessor; every changed/new sample was inspected. This is **not** a claim to have watched every24fps frame or listened to the film.

Vosk's fallible transcript was read. It ran on the preceding picture encode; exact full decoded stereo-audio identity links that result to the final cut. The ASR provenance records both movie hashes. No manual ear-listening is claimed. Measured final loudness:−16.06LUFS integrated,−1.29dBTP, LRA3.9.31targeted tests passed; no whole-repository test-pass claim. Technical results do not establish artistic quality, naturalness, historical certainty or user approval.

## Preserve/recover without regenerating the voice

The project capsule includes this profile, processed FLACs, raw-take ASRs/pacing recipes, shared runtime/tools, required still assets, fonts, geo data and QC metadata. The separate QC capsules preserve final contact sheets, prior actually inspected sheets and hash-linked evidence. These capsules do not duplicate the final MP4 or the large original-source archives.

Original research MP4s are saved privately in Drive; hashes/IDs are in `source_retrieval.json`:

1. `Full_Film_Original_Sources_Part1.zip` → extract `primary_media/` and `industry_media/` into `/home/user/build/escobar_intro5/`.
2. Parts2and3 → extract `research/` into `/home/user/build/escobar_film/`.
3. Restore the approved opening from Drive `1H62QuxCmfmEEnUZFw-GQddiaOfqYqEuI` as `/home/user/build/escobar_intro5/Escobar_Intro_Revision5_New_Cut.mp4`. Its SHA256 must be `1a05ed7c029b7f910cd1d62be1bd911745fefc23b96652292b1bea9ceec0894d`.
4. Original, untouched full-body voice takes: Drive ZIP `1NxeTyKABBS35oTOBq__oOyfCjy4wWL5J`. Restore `01_business_raw.wav` through `07_legacy_raw.wav` into `/home/user/build/escobar_film/voice/`. SHA256 values are in `narration_pacing.json`.

Run from the repository root. Python3.11; rendering needs `numpy`, `Pillow`, `opencv-python-headless`, `imageio-ffmpeg`. The production environment versions are saved in `encoded_qc/environment.json`. Existing processed FLACs already suffice to rebuild without new voice generation or Vosk.

```bash
# Only if deliberately rebuilding processed VO; verifies raw SHA before processing:
python youtube_documentary/tools/shape_narration.py escobar_full \
  --raw-dir /home/user/build/escobar_film/voice \
  --output-dir /home/user/build/escobar_film/rebuilt_voice

# Rebuild body with the shared renderer and current profile:
python youtube_documentary/tools/render_film_profile.py escobar_full --render --historical-rebuild
python youtube_documentary/tools/join_locked_prefix.py escobar_full

# Re-extract actual encoded evidence (does NOT mark it visually reviewed):
python youtube_documentary/tools/review_film_profile.py escobar_full \
  --file /home/user/build/escobar_film/Escobar_Full_Film_Review.mp4 \
  --out /home/user/build/escobar_film/encoded_review

# Check approved prefix without overwriting the movie:
python youtube_documentary/tools/join_locked_prefix.py escobar_full --verify-only
```

`prepare_metadata.py` is a maintenance/rebuild helper, **not needed to play or restore the delivered cut**. It resets editorial observations to pending and rewrites the fact ledger; do not run it merely to update delivery links. Rebuilt encodes must be reviewed again; no cross-version byte-identical body-encode guarantee is made. Never replace the approved prefix with a reconstruction when the approved file is available.

## Rights

FRONTLINE1995 is the principal archive; BBC2013 and Al Jazeera2018 are explicitly dated later context. Multiple interviewees from one programme are not multiple broadcasters. Public accessibility is not a publication license. Exact selected bounds, genuine quotes and interpretation caveats are in `MATERIALS.json`, `timeline.json` and `FACT_CHECK.md`. This cut is for internal editorial review; rights remain unresolved.
