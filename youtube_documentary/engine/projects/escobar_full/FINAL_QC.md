# Final encoded review — Escobar

**Artifact:** `Escobar_Full_Film_Review.mp4` · 96,129,645bytes · SHA256 `7c10862acc22982b2db0ba1df4f97ee15b32c2924778ee14cbb7edb9cb15ee14`.

| Check | Observed result |
|---|---|
| Picture | 1920×1080,24fps,9850frames,410.4167seconds |
| Body | 97authored shots,9055frames,377.2917seconds |
| Approved opening | Every795decoded frames exact;1,590,000samples/channel in both audio channels exact; max difference0 |
| Final decode | FFmpeg full decode/loudness pass completed; logs in QC capsule |
| Loudness, measured input | −16.06LUFS integrated;−1.29dBTP; LRA3.9 |
| Visual grid | 821half-second samples;481planned/detected-join samples;271motion samples at12fps |
| Automated tests | 31passed across full profile, speech pacing, approved opening sequence and documentary-materials modules |
| Manual listening | **Not performed/claimed** |
| Full-film user approval | **Pending**; opening and production/pace direction already approved |
| Publication rights | **Unresolved**; internal review cut |

## Visual evidence actually inspected

1. Initial complete half-second grid: all26sheets/821samples actually inspected. Source/image and return-flash issues were found and corrected, not automatically passed.
2. Next encode `ba39427cb5f44791703db6c2397cd2907b6222d8fa96e11999838b4bae7ec823`:627half-samples exactly matched those viewed; all194changed samples were inspected in7additional sheets. All15join sheets and all9movement sheets were actually inspected.
3. Join inspection found three further native-cut issues. Final corrections: aftermath starts at3949.5; targeted-property clip starts4369.3; Murphy's picture leaves0.375seconds earlier, before the source party-photo cut, while his unchanged audio finishes over the genuine La Catedral office. Consecutive duplicate source cues are coalesced, without a replay/flash. No frozen talking face or witness retiming was introduced.
4. Final encode:794half-samples,462join samples and all271motion samples are exact-JPEG-hash matches at the same global decoded frame indices to the preceding inspected encode. **Every remaining27half-samples and19join samples was actually inspected** in `final_changed_half_1.jpg` and `final_changed_join_1.jpg`. No unrelated speaker/plane leak was observed in these final corrected samples. Maps, full authored photograph motion, witness reveals, approved opening seam and ending fade are covered.

This is complete coverage of the stated sampling grids, **not** a claim to have viewed every24fps frame or a guarantee of artistic quality. Hash reuse requires an actually inspected predecessor; it cannot automatically excuse an earlier missed defect. Both generations of identity proof and the actually inspected predecessor sheets are preserved in the QC capsule.

## Audio evidence and limits

The fallible Vosk transcript was read for narration continuity and quote handoffs. Names, numbers and word boundaries are recognition estimates, not proof of pronunciation mistakes or exact independent transcription. No manual ear review, naturalness approval or lip-sync test is claimed.

ASR ran on the preceding picture encode `ba39427…ec823`. The final full decoded stereo float32 PCM hash is exactly unchanged:

`1ea2bcc7449f40ab95adf4fd93fab696ca0ba211c4987729de3d46a19e2413e4`

`encoded_qc/final_audio_identity.json` records both movie hashes. The last correction changed only four picture shots; the audio timeline, total frames and actual decoded audio are identical. `asr_on_identical_audio.json` therefore applies to the final audio through that explicit provenance, not by silently relabeling the recognition job as a new listening pass.

The locked opening retains its original stereo audio. Body narration is approved-identity AI speech with disclosed, pitch-preserving clause pacing; original raw takes remain separately archived. Genuine Murphy/Blum recordings were not synthesized or speed-changed.

## Historical/material limits

Source transcript and historical fact ledger are separate from visual inspection and automatic recognition. The final death-site image is a source camera pan over the site, **not filmed footage of the fatal shooting**. Modern city/merchandise/memory footage is dated. An old lab image illustrates the business historically, not a recorded post1993transaction. Unverified people shown in source footage are not named as particular criminals or victims. Conceptual map links are not recorded shipment routes. See `FACT_CHECK.md` and `MATERIALS.json`.

The QC/project capsules are recovery and evidence packages, not rights licenses. All-repository tests were not claimed to pass; only the31targeted tests listed in `targeted_tests.log` were run for this final version.
