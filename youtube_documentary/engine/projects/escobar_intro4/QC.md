# Revision4 — actual QC and source use

## Delivered internal-review cut (not user-approved)

- **53.833333s**,1292frames,1920x1080,24fps,H.264/AACstereo,fast-startMP4.
-21,330,143bytes;MD5`ad83950d3a43573579e9c30cb7a3c2e4`.
- SHA256`b30d20d13b0c42ccb117f4575d44259890132c506bc2372c9bac4bffa0c0ca71`.
- Drive:https://drive.google.com/file/d/1L4SFgVFKbqMVVMiW4_0WhR2ngcssnHn5/view
- Revision3was63.25s:9.416667s shorter (about14.9%), despite two additional genuine source-name bites. No global speech/video speed-up, pitch shift or new voice generation.
- Native1080pcomposition, **not native-HD claims for lower-resolution archive/photos**.

## Actual rhythm decisions

- Original voice-02identity/performance reused from revision3, source MP3s unchanged. The original explicitly approved recording also remains SHA256`523220dab1465d8958a24345978de76982953396e05b9bcf7ed012da44c7485d`.
- Remove only “Think about that” and “Now listen to the other side of the story”, plus measured quiet pauses/head/tail silence. Preserve every substantive narrated fact/question.4mscrossfades; full source/output maps and removed-word detection in voice_edits.json. New nonquiet-head/tail safeguard changes NONE of the production cuts/timings.
- Archive name voices:host11.36–12.63,guest38.72–39.78. **Two voices, ONE CharlieRoseprogramme**, not multiple news networks. Official/source/VTTrecord plus ASRtiming; not an invented newscast.
- Scale67.26–71.53,most-wanted12.66–15.30,fear76.74–82.25 from the same genuine source. Relevant intact words, not silent news props. Full AACASR confirms both name bites, planeloads/shiploads, wealth, homes/football, most-wanted, organization/fear and the closing questions/name. Proper-name and kilo/keeler recognition errors remain flagged as machine fallibility, not silently claimed heard.
-25authored visual beats; average2.15s, varied lengths~0.65–4.39s, not a mandatory2secondtemplate. Longer archive sentence preserves meaning; faster social/press interplay doesn't mechanically speed speech.
- During first encoded review, rejected adjacent nearly identical print-portrait holds and a naturally soft campaign-crowd crop. Final edit intercuts real Semana portrait into wealth; most-wanted audio now contrasts with the actual congressional image; questions change source; exact housing detail replaces weak crowd filler.
- Houses and football photos change on their actual spoken nouns, not unrelated generic stock. Source caption confirms SinTuguriosconstruction1983. Full original1200x811photo inspected; lower-resolution photos remain honestly credited. Original football/city2.5D/XYZ/page-turn methods retained.
- Closing real Escobar words:48.2855–50.2855 Guardian,50.2855–52.2855 ElPais.2seconds each, static scale/matched ink anchor, no text blur or4Hzmicrocuts. Marker multiplies original pixels; black original letters remain visible. Both are **modern public webpage renderings**, not historical print scans. Source/date stated on screen. Forbes is the actual1987print entry and also receives an editorial name highlight.
- Original110BPMprocedural music/pulse; editorial camera-shutter/paper accents. SFX target8dBbelow local musicRMS. Not represented as historical production sound.

## Actual final encoded inspection — not just the staging render

- SHA-bound finalMP4 decoded with ffmpeg`-xerror`:all1292frames, no decode failure.
- Opened/visually inspected all **108exact0.5sframes**, without skipping any sampled interval:7half sheets; **73encoded join neighbors**:5join sheets; **35subsecond page-turn/marker frames**:3motion sheets. Counts overlap across groups; do not call these216distinct frames or claim every1292frame was individually watched.
-0–6.85s:real two-voice name opening and intact source scale passage; no fake independent broadcaster claim or extraneous source cover.
-6.85–18.96s:actual Forbes cover/full page turn/entry; real b&wportrait interrupts paper repetition; real full printed-name highlight remains readable. No assertion Escobar was ForbesNo1.
-18.96–32.20s:actual Congress/public-image contradiction, source portrait, real construction/football/detail, Congress. No Spanish campaign slogan, uncertain-person isolation or fabricated evidence.
-32.20–48.29s:intact fear audio, credited image cutaway, distinct-source question beats, contemporary city clearly labeled; no prison, escape/death or payoff headline.
-48.29–53.83s:both actual original Escobar names readable at review-thumbnail scale; marker grows while letters stay fixed. Type resolves into PABLOESCOBARtitle. Intentional single-frame initial black and final0.18sfade, no accidental joining black frames seen.
- Encoded delivered loudness is loudnorm **input** measurement:**−16.02LUFS,−2.00dBTP,LRA5.70**. Do not quote target/output theoretical values as delivery measurements.
-55unit tests PASS; display/design/material/hash gates PASS. Tests and render success do **not** mean artistic approval.
- **No manual ear-listening or full real-time playback claimed.** Actual audio checks are encodedAACASR/full decode/levels; human ear judgement and user approval remain outstanding.

## Rejected research and source limits

- Initial ElPaisname crop actually showed cookie-consent prose despite a valid h1DOMbox. Rejected by pixel inspection. Recovered only by clicking the ordinary public ACCEPTANDCONTINUEbutton in a fresh anonymous browser; then viewed the unobscured original Escobar pixels. No hidden-overlay deletion, login, cookies export, subscription/paywall bypass.
- ABCYouTube bot-login block:never acquired, no workaround/cookies/fake voice. Forbesnew-webpageh1timeout:no usable screenshot. Original print scans remain actual source media.
- Campaign banner original acquired and inspected; source's naturally out-of-focus crowd crop/Spanish slogan unsuitable. Preserved as rejected research, **not in final film**. Moravia low-resolution composite/banner also excluded.
- Public accessibility is NOT publication permission. Internal review only; source-photo/archive rights remain uncleared.2.5Dincludes original-pixel planes and reconstructed hidden backgrounds, not recorded subject movement or surveyed3D. No watermark removed.

## Preservation and shared engine

- Revision3MP4 remains SHA256`37e5342b1745381dd41255eb332c9c3d0af33e1aa48134ff6711def650f32eb0`; original/revision2outputs unchanged.
- Common `film_runtime.py`, `photo_depth.py`, `speech_edit.py`, `encoded_review.py`; masks/crops/timeline/editorial choices are film data. Revision3authoring helper delegates to the same runtime, without regenerating/overwriting its delivered output.
- Source/review packet includes used originals, original narrator takes, real120ssource, mix/stems, profile/runtime/code, exact edits, final encoded review evidence and measured QC. MainMP4 delivered separately. No publication license implied.
