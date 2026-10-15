# Escobar — broader, spoiler-free documentary opening

## Active user correction
The opening is about **Escobar broadly**, not the prison or a deal. Build curiosity from real, surprising information about wealth, public image, intimidation and political power. Do not reveal escape, death, later outcomes, or the answers to the film's central questions. Execution is authorized without a30-second ceiling; this is **an opening, not a full documentary**.

Keep the praised depth direction, but actual subject material must carry the story. English picture text and speech only; captions/transcription default off. Genuine source voices must say relevant sentences. Conversational narrator connects and yields, rather than narrating continuously over decorative slides. Original approved recording and revision2 are immutable. Voice-02 identity approved; **these newly written/performed takes are not user-approved**.

## This implementation
63.25-second,24fps,1920×1080internal review cut. Industrial-scale cocaine archive→actual1987Forbes cover/entry→a contemporary broadcast description over an actual Escobar portrait→1983public-image photographs→actual congressional photograph→organization/fear archive→two questions→real printed-name match→title/Medellín.

**Zero prison images, zero escape/death resolutions.** The real cover's “richest man” headline is the issue theme, NOT a claim Escobar ranked first. Voice says list membership. The full cover shows Forbes branding; no Escobar portrait is fabricated onto the cover. The actual article follows.

Authentic interview excerpts are from the12November1992Charlie Rose program. The host's12.66–15.30s excerpt is **audio only**, because its original picture is an unrelated Vanity Fair cover. Do not misrepresent that picture as Escobar material.

## Visual truth
- Forbes1987original scan, Semana1983original photograph crop,1983football-field photograph, congressional photograph; source/date notes remain small and functional.
- Spanish Semana article copy and the Spanish Moravia banner are **excluded from the film**, not rewritten into fake English print. The original Moravia plate remains in the research collection.
- El Colombiano photo identifies the correct Cerro Nutibara/Medellín location, published31March2026, credited to Andrés Camilo Suárez Echeverry. It is labeled **contemporary**, not passed off as1980s footage. The search results for Bilbao/Spokane were rejected.
- Shared camera engine plus `photo_depth.py` uses original-pixel perspective planes, physical ruled-paper turn, and masked photo parallax. These are **editorial2.5D movements**, not recorded historical camera moves or surveyed3D. There are no generated historical faces/actions. Tiny newly exposed regions behind foreground cutouts use computational inpainting; those regions are unknown reconstruction, not evidence.
- Name montage uses only original printed **Escobar** pixels.1992page context is never legible or used as background: the background is derived from the isolated word, preventing escape-headline spoilers. No synthetic newspaper.
-1080p is the **composition resolution**. Historical sources are much smaller; no nativeHD archive claim.

## Audio and review limits
Four new voice-02takes plus three bounded authentic interview excerpts. No voice pitch/time modification. Original procedural underscore; SFX target9dB below local music. Constant-gain dialogue leveling and final loudness/true-peak measurement. ASR checks do not constitute manual listening or user approval.

Render success is not art approval. Inspect the actual encoded file every0.5seconds, physical page turn, all picture joins and press-word crops at subsecond intervals. Record real findings and repairs, not a checklist marked passed in advance. Publication licenses are **not obtained**; availability is not clearance.

## Reproduce
`python3 tools/archive_research_fetch.py --run 38732941054 --out /home/user/build/escobar_archive_official`

`python3 tools/escobar_intro3.py prepare`

`python3 tools/escobar_intro3.py audio`

`python3 tools/escobar_intro3.py stills`

`python3 tools/escobar_intro3.py finish`

Selected images/new takes live with this profile; full recovered archive and generated outputs/frame caches stay outside Git. Final review media must be archived externally rather than placed in the source tree.
