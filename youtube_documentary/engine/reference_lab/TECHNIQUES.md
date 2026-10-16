# TECHNIQUE ANALYSIS & DATABASE (deliverables 4 + 5)
Evidence labels used throughout:
`[TRANSCRIPT]` = read from the actual narration. `[PIPELINE]` = channel's own declared
tools. `[STILL]` = verified key art. `[INFERRED]` = reasoned conclusion from the above,
not from watched frames. Frame-level confirmation is pending reference files (see
REFERENCE_ACCESS_REPORT §4) — the database is built so technique params can be
recalibrated once real shot data arrives.

## 1. Strongest techniques per channel (deliverable 4)

### MagnatesMedia (Vaping 27:27, PayPal 57:34)
- **Chapter architecture as pacing engine** `[TRANSCRIPT]`: hard chapter resets
  ("Chapter 2: Ploom" → "Chapter 3: The Perfect Product") every 2–5 min; within a
  chapter, narration runs in 2–6s idea-beats, each beat visually re-staged. Evidence:
  transcript cadence + chapter timestamps.
- **Rise/fall money arc with recurring money-visual motif** `[TRANSCRIPT]`: "$38
  billion company" → "plummeted 95%" — valuation language appears at setup and doom
  beats, implying a persistent valuation/scale graphic language that evolves
  (building → eroding) rather than one-off charts `[INFERRED]`.
- **Persona-driven cold opens with archive/news collage** `[TRANSCRIPT]`: opens with
  quoted TV/news lines ("the FDA calls it an epidemic") — archival-quote cards inside
  a branded frame language `[INFERRED from transcript + PIPELINE]`.
- **Cinematic warm grade + gold-brown identity** `[STILL from channel family art /
  INFERRED]`: consistent branded look across unrelated subjects (Juul/PayPal/Ponzi).

### James Jani (Crypto 54:18)
- **Thesis-first cold open over live-feel montage** `[TRANSCRIPT]`: 90 seconds of pure
  contradiction setup ("revolution… or the greatest Ponzi scheme in human history")
  before any explanation — visual language of juxtaposed extremes `[INFERRED]`.
- **Number-salvo sequences** `[TRANSCRIPT]`: "Nyan Cat 590,000… Charlie bit my finger
  760,999… Doge 4 million…" — rapid-fire sale prices; classic case for kinetic
  price-card typography where each number lands on its narration beat `[INFERRED,
  high confidence from narration structure]`.
- **Celebrity-quote stack** `[TRANSCRIPT]`: Snoop/Eminem/Curry list → wall-of-names
  composition opportunity (repeated identity cards forming a grid).
- Dark teal/green diagnostic palette, investigative desktop/terminal motifs
  `[INFERRED from channel identity]`.

### Moon (Apple 17:29, Dubai 3:01:42)
- **Economics-as-geography** `[TRANSCRIPT]`: Apple = price-comparison across countries
  ("$1,999… nearly $4,000 in Sweden… Turkey record $2,592") — price-by-country is
  inherently a map/bar hybrid sequence `[INFERRED, high confidence]`.
- **Product-as-monument shots** `[INFERRED from key art family + subject]`: devices
  treated as monumental objects with dramatic lighting, not flat catalog renders.
- **Long-form chapter diptych** `[TRANSCRIPT, Dubai 3h]`: city-as-character structure
  ("let's take a trip around the world") — a literal world-tour connective device:
  one map/spine the film keeps returning to `[INFERRED, high confidence from
  narration]`.

### RealLifeLore (Saudi 25:20)
- **Pipeline confirmed** `[PIPELINE]`: GEOlayers 3 + MapTiler/OSM basemaps, Getty/AP
  footage. This validates the exact map-production method our engine must replicate
  in code: real tile geography + animated zoom/pitch/rotate + drawn routes + labels.
- **Chokepoint geography as thriller** `[TRANSCRIPT]`: the whole film is two straits +
  a pipeline — geographic relationships ARE the narrative (Bab el-Mandeb ↔ Hormuz ↔
  East-West pipeline). Lesson: maps carry causality, not decoration.
- **Satellite before/after evidence** `[TRANSCRIPT]`: "before and after satellite
  images perfectly captured the aftermath" — paired imagery with synchronized reveal.
- **Stat-anchored map moments** `[TRANSCRIPT]`: "120,000 barrels/day → 4 million
  barrels/day (30×)" pinned to map regions — number + place fused `[INFERRED, high
  confidence]`.

### Kurzgesagt (AI Line 21:44)
- **Flat-vector identity with consistent metaphor system** `[STILL verified +
  PIPELINE: Illustrator→AE]`: every concept gets an icon-language token (agents =
  robots with hands; confinement = box) that recurs and evolves across scenes.
- **Metaphor escalation** `[TRANSCRIPT]`: solitary confinement → secret society →
  cyberattack, one metaphor world sustained for minutes — tokens recombine instead of
  new styles appearing.
- **Chapter cards as palette shifts** `[TRANSCRIPT — bold section headers in
  narration]`: "How Do You Grow an Intelligence?" — typographic full-screen pivot
  moments that reset attention `[INFERRED, high confidence]`.
- **Bold display type over image** `[STILL verified]`: oversized uppercase display
  type, high-contrast, integrated with illustration bursts (their "WE LOST CONTROL"
  art) — typography as the subject.

### OverSimplified (WW2 ×2)
- **Pipeline confirmed** `[PIPELINE]`: After Effects + Photoshop; **asset list is
  fully CC-attributed** (flags, archives, NASA Blue Marble world map) — proving the
  "drawn illustrative map + tokens" grammar.
- **Illustrative map journeys** `[INFERRED, very high confidence]`: cartoon map with
  moving unit tokens and arrows acting out the narration literally (Italy "tried to
  take British Somaliland… then Egypt… then Greece" = three arrow beats).
- **Comedic beat cutting** `[TRANSCRIPT]`: lists performed as rapid escalating beats
  with held reactions — rhythm: action → beat → punchline-hold; a pacing law our
  engine can adopt for list sentences (our version: restrained, dry SFX).
- **Recurring character mascots as continuity** `[INFERRED]`: same drawn figures
  return across eras — identity continuity device.

### Cross-channel conclusions `[INFERRED]`
1. Premium ≠ constant motion: every channel alternates dense compositions with
   restrained holds. Contrast is the grammar.
2. Money/number language is a first-class visual system everywhere (5 of 6 channels).
3. Maps appear wherever geography is causal (RLL, Moon, OverSimplified), always with
   real basemap data or consistent drawn geography.
4. Typography takes over the screen at chapter turns and emotional peaks.
5. Continuity devices (recurring tokens, motifs, mascots) make 50+ minutes feel like
   one film.

## 2. Reusable technique database (deliverable 5)
Machine-readable twin: `engine/database/techniques.json`. Format per technique:
Purpose / Inputs / Parameters / Outputs / Implementation / Complexity(1–5) /
Evidence / Anti-patterns. Summarized here; the JSON is canonical.

### T01 · camera_guided_evidence_connection
Purpose: reveal a relationship between 2+ subjects by traveling between them along a
designed path. Inputs: subject assets+rects, relationship label, narration word
timestamps. Params: path curve, dwell profile (ease ratios), connection style
(string/pin/paper-clip/none), subject scales, canvas material. Outputs: camera keys +
connection layer + typographic anchors. Implementation: Three.js plane canvas +
SVG path in world space; camera follows path tangent. C:4. Evidence: MagnatesMedia
board grammar `[INFERRED]`. Anti-patterns: thin floating rectangles, dark void canvas,
arrow-with-no-meaning.

### T02 · spatial_env_takeover
Full-bleed archival photograph becomes the world; UI-free. Params: grade preset,
drift vector+amount, scrim set (directional + bottom), entrance (fade-from-black
dur) / exit (crossfade to next env). C:2. Evidence: our verified bars frame +
documentary norm `[PIPELINE RLL Getty/AP]`. Anti-patterns: letterboxed floating photo,
slow-zoom-only.

### T03 · photo_2_5d_parallax
Depth from a still: separate fg subject plate / bg plate (+ optional mid), project
with controlled parallax ≤4% separation. Params: layer masks, depth budget, focus
pull between plates. Implementation: DOM layers or two textured planes; masks from
reference-guided generation when needed. C:3. Anti-patterns: cardboard cutout faces,
obvious extrusion `[directive]`.

### T04 · editorial_display_takeover
Typography becomes the subject: oversized display phrase, masked line reveals, one
gold/oxblood emphasis word. Params: type scale ramp, line-break map, entrance
archetype (rise/mask-slide/weight-shift), dwell, exit into next scene. C:2.
Evidence: Kurzgesagt display art `[STILL]`, Jani number salvos `[TRANSCRIPT]`.

### T05 · number_salvo / scale_reveal
Sequence of quantitative beats (prices, barrels, casualties) where each number lands
exactly on its narration onset; scale anchored by unit comparisons (barrels→pool,
dollars→brick stack). Params: rhythm (min 0.5s per landing), unit-anchor assets,
count-up restraint (no unreadable flicker). C:3. Evidence: Jani, RLL, Magnates
`[TRANSCRIPT]`. Anti-patterns: pie-slice icon kits, fake stats `[directive]`.

### T06 · map_geographic_travel
Real-tile geography (MapTiler/OSM-compatible), camera zoom/pitch/rotate keys,
drawn route with traveling head, label hierarchy (country/city/site) with
collision-safe anchoring. Offline engine path: GeoJSON+vector tiles rendered to
canvas texture (d3-geo + world-atlas npm package — no network needed at render).
Params: basemap style tokens (paper/ink/satellite), route style, label set,
height exaggeration. C:4. Evidence: RLL `[PIPELINE confirmed]`.

### T07 · territory_shift_map
Control/frontier change over time: region mask wipe between two states with date
stamp typography; palette swap per controlling power. Params: state keyframes
(dates+masks), palette map, wipe easing (linear with soft front). C:3.
Evidence: RLL Saudi front lines, WW2 fronts `[TRANSCRIPT]`.

### T08 · document_reveal
Authentic document/press clipping pinned in space; camera pushes to a detail crop
matched to narration; highlights sweep under key phrases (only real text — never
fabricated `[directive]`). Params: pin/shadow style, highlight tokens, crop targets.
C:3. Anti-patterns: invented documents; lorem text `[directive]`.

### T09 · illustrative_map_journey
Drawn consistent geography with unit tokens acting the narration (arrows, fronts,
capital moves) — OverSimplified grammar, restrained for our tone. Params: token
library, arrow beat timing (one per clause), hold-beat after each. C:3.
Evidence: OverSimplified `[PIPELINE + TRANSCRIPT]`.

### T10 · metaphor_token_system
A concept gets a recurring visual token that recombines across scenes (Kurzgesagt
grammar adapted: for us, photographic/physical tokens — keys, bars, bricks, files).
Params: token registry per film, recombination rules, consistency grading. C:3.
Evidence: Kurzgesagt `[STILL+TRANSCRIPT]`.

### T11 · chapter_zag_reset
Attention reset between chapters: palette/energy/composition-family all change
(typographic pivot card or environment swap); continuity kept only by one token.
Params: reset intensity levels, token carry-over. C:2. Evidence: all channels'
chapter structures `[TRANSCRIPT]`.

### T12 · archival_impact_hold
A single heavyweight archival still, full-bleed, near-still camera (≤2% push),
narration + silence carry it; entrance from black, exit via match-cut token.
Params: hold duration, grade, breath (fade) length. C:1. Anti-patterns: Ken-burns
every photo (reserve for peaks only).

### T13 · quote_card_editorial
Real quoted speech (news/archive/announcer) as designed type card with source
attribution line; enters with voice; hard cut in/out. Params: quote type style,
attribution treatment, background (photo blur/typographic field). C:2.
Evidence: Vaping/Magnates news quotes `[TRANSCRIPT]`.

### T14 · price_map_hybrid
Numbers pinned to geography (Apple pricing, oil flows): map camera + bar/price
tokens anchored to regions, one region highlighted at a time. C:4. Evidence:
Moon `[TRANSCRIPT]`, RLL barrels `[TRANSCRIPT]`.

Each technique's JSON entry also lists `requires` (assets/data), `pairs_with`
(natural neighbors), and `qc_checks` (gate hooks: e.g. T01 checks path dwell ≥
readable-time for its labels; T05 checks every number's readable≤onset−60ms).
