# PROPOSED VISUAL GRAMMAR — original house style (deliverable 6)
Derived from the reference analysis (TECHNIQUES.md) + our no-music / exact-script /
authentic-evidence constraints. One studio voice across all strategies.

## Identity: "INK & ARCHIVE"
- **World rule:** the film is a physical research space — photographic paper, ink,
  tape, pushpins, filing-card edges, table surfaces — photographed materials, never
  flat vector decoration. Vector/SVG only for evidence annotations (arcs, measure
  lines, routes) drawn like an investigator's marker.
- **Palette (locked tokens):** ink `#14100C` · ivory `#EDE6D3` · gold `#DFA83E`
  (single emphasis) · oxblood `#7A2E2A` (danger/redaction) · map slate `#2E3A42` ·
  archival warm grade (teal-lifted shadows, amber highlights, unified 3% grain,
  consistent vignette) — one grade preset for the entire film.
- **Typography system (fonts already licensed in repo):**
  Display: Archivo Black (120–260px, chapter/emotion peaks, max one emphasis word in
  gold). Text: Inter 400/500/600 (32–56px). Numerals: Bebas Neue for dates/figures
  when monumental. Six-level hierarchy: Kicker(31/600/ls5) → Date(185) → Display(104)
  → Body(53) → Small(41) → Attribution(24/600). Line breaks are authored per phrase,
  never auto-wrapped mid-thought.
- **Camera language:** dolly/track always (never naked zoom); every move completes
  inside its narration sentence's duration; one hero move per scene max; static
  frames are allowed and are part of the rhythm.
- **Transition grammar (priority order):** shared-object carry > camera-path
  continuity > graphic shape match > typographic handoff > hard cut. Crossfade only
  between full-bleed environments of the same world. No glitch, no light-leak stock.
- **Sound:** narration is master; dry sparse SFX only on physical actions
  (paper, pin, camera shutter, distant city); silence is a beat. No music ever.
- **Pacing laws:** (1) never the same strategy 3 scenes in a row; (2) after two dense
  compositions (board/map/salvo) insert one restrained composition (hold/typographic);
  (3) open wide, end intimate; (4) list sentences get beats with 0.5s+ landing gaps;
  (5) peaks get T12 holds — quiet frames are the loudest frames.

## Strategy selection (narration type → technique bundle)
| Narration segment type (auto-classified) | Primary bundle |
|---|---|
| Person introduction / identity | T02 takeover → T03 parallax → T04 label |
| Relationship between people/events | T01 connection journey |
| Place / geography / movement | T06 map travel (+T14 if numbers) |
| Territory/control change | T07 shift map |
| Document / evidence quote | T08 document reveal / T13 quote card |
| Numbers / money / scale | T05 salvo (+T04 for the hero number) |
| Process acting-out (war-like sequences, deals) | T09 illustrative journey (tonally adapted) |
| Concept metaphor | T10 token system |
| Chapter turn | T11 zag reset |
| Emotional peak / death / verdict | T12 archival hold |

Selection rules: evidence-first (technique requires its real asset or is rejected at
Gate A — no placeholder downgrade); continuity-first (prefer continuing the previous
bundle when the subject persists); variety only when meaning changes.

# TECHNICAL IMPLEMENTATION PLAN (deliverable 7)
Builds on the existing verified engine (scene-model / camera / typography / qc /
runtime / storyboard CLI). No renderer rebuild.

- **M0 · Reference ingest (blocks nothing):** `tools/reference_ingest.py` (shipped)
  — ffmpeg shot-cut detection + contact sheets + shot-length CSV for any local
  reference file. Runs here when files arrive on Drive, or on user machine.
- **M1 · Typography vocabulary (T04/T05):** extend typography.mjs with entrance
  archetype registry (masked_rise, weight_shift, slide_mask, count_land) + emphasis
  budget check in qc.mjs (max 1 gold word/phrase; readable≤onset−60ms already
  enforced). Validates on existing scene 001 without new assets.
- **M2 · Connection & board system (T01/T08/T10):** world-space SVG connection
  layer (paths, pins, inklines) + board material pack (paper/table textures,
  generated-for-compositing) + camera path-follow util in camera.mjs
  (`cameraFollowPath(path, u)`). Gate B extended: path-dwell readability check.
- **M3 · Map adapter (T06/T07/T14):** offline vector basemap renderer — d3-geo +
  world-atlas (npm, no runtime network) baked to canvas textures; GeoJSON region
  masks for T07; label collision solver; route draw util. Sandbox-safe (tiles not
  required; local raster cache optional later).
- **M4 · Three validation tests (deliverable 8, DEMOS.md):** A/B/C scenes through
  the full gate pipeline (A→E), each 6–10s, Escobar script sentences, real assets.
  Only after tests pass visual review do we resume documentary production.

# THREE PROPOSED DEMONSTRATION SEQUENCES (deliverable 8)
All use real Escobar-script sentences (exact-word typography), verified assets, full
gate pipeline. ~6–10s each.

**TEST A — Connected investigative environment (T01+T08+T04+T02)**
Sentences 1–3: "In 1993, … house in Colombia. / He had billions of dollars. / He'd
bought politicians, built his own prison, and spent years making an entire country
afraid of him." One investigation table-world: mugshot (pinned, graded) → money
cluster → politicians/prison cluster, camera traveling an ink path between evidence
regions; date/typographic anchors hand off per phrase; ends on restrained hold.
Assets: mugshot ✅, bars ✅, needs: board/table material (generate-for-compositing),
document props without readable fabricated text (abstract ink marks only).

**TEST B — Advanced editorial typography (T04+T05+T13)**
Sentence 81: "Like the one about burning $2 million to keep his daughter warm."
(+"dollars" spoken) Typographic sequence: "$2 million" as monumental display beat
landing exactly on narration; ember/warm grade context; one emphasis word; quote-card
attribution grammar. Assets: none new required beyond fire/warm plate (optional
generated atmosphere — no faces, no fake evidence).

**TEST C — Cinematic mixed-media geo explainer (T06+T02+T01)**
Sentence 71: "On December 2nd, 1993, Colombian security forces tracked Escobar to a
house in Medellín." Offline vector map of Medellín → camera descends from country
scale to barrio scale → crossfade into the hillside photograph world → archival
anchor. Proves the map adapter + env takeover + handoff in one chain. Assets: needs
Medellín GeoJSON detail ( OSM extract via npm package at build time) + existing
hillside photo (full-res replacement still pending).

Acceptance per test: Gate A assets pass (no storyboard-only warnings), Gate B
layout clean, Gate C motion preview approved, Gate D word-sync verified from decoded
MP4 frames, Gate E representative frames reviewed against this grammar.
