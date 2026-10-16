# Escobar opening, rhythm revision4

Revision3 was strongly praised, but its rhythm was explicitly called slow and the tiny4Hzclosing-name montage unreadable. This is a new internal-review cut, NOT declared user-approved. Revision2/revision3and the approved original narrator recording remain unchanged.

- Broad premise retained: Forbes/wealth, industrial cocaine, benefactor image/real housing and football, public office versus fear. No prison-led story, escape, death or event-resolution reveal.
- English-only film. Original voice-02identity/performance reused from revision3. No new generation, global speed-up or pitch shift. Delete two filler phrases and quiet pauses, not substantive facts. Exact source-to-output mappings are in research/voice_edits.json.
- Two real voices say Pablo Escobar, from ONE1992CharlieRoseprogramme, openly credited. No fabricated multi-newscast montage. ABC research failed and is excluded.
- The exact1983housing photograph newly acquired from ElPais shows the homes, not a generic city substituted for housing. Campaign photograph was acquired but rejected for this cut: its Spanish banner cannot be shown and its crowd crop is naturally soft.
- Genuine1987Forbes issue/entry, original photographs and modest shared-engine2.5D. Material changes and shot lengths vary with meaning, not a compulsory newspaper template or a speed multiplier.
- Wealth and question sections cut across distinct sources; avoid adjacent nearly identical6-secondprint-portrait holds discovered during the first encoded review.
- Press-name match uses real current-webpage headline pixels, not historical print scans. Each2-secondhold, matched ink anchor/static size and editorial multiply marker; no blur or retyped fake archive.
- New original110BPMprocedural score/pulse and restrained editorial shutter/paper sounds. SFX measured8dBbelow local musicRMS, never asserted as original historical production sound.
- Review every0.5seconds plus encoded joins and subsecond page-turn/marker phases. Full1292-frame decode and finalAACASR supplement, never replace, creative review or human listening.
- Public availability is not publication permission. Internal review; rights clearance still needed.

## Rebuild

From repository root, with existing source120sarchive at profile.ARCHIVE_FILE, installed NumPy/OpenCV/Pillow/imageio-ffmpeg and localVoskmodel:

```
python3 youtube_documentary/tools/escobar_intro4.py prepare
python3 youtube_documentary/tools/escobar_intro4.py audio
python3 youtube_documentary/tools/escobar_intro4.py stills
python3 youtube_documentary/tools/escobar_intro4.py finish
python3 youtube_documentary/tools/review_escobar_intro4.py
```

Shared engine: engine/runtime/photo_depth.py, film_runtime.py, speech_edit.py, encoded_review.py. Film-specific crop/subject/silhouette choices live in projects/profiles. No separate Escobar renderer engine.
