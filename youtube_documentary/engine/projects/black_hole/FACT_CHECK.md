# Factual basis and limits — What If You Fell Into a Black Hole?

Research date: 2026-10-16. These are physics explanations, not a historical crewed mission. No film archive or NASA simulation footage is used. No view counts or guaranteed audience performance are claimed.

## Actually retrieved and read

1. NASA, Francis Reddy, **New NASA Black Hole Visualization Takes Viewers Beyond the Brink**, 2024-05-06. Main article retrieved/read in fetch chunk3, including the small/supermassive tidal comparison, finite simulated infall versus distant view, inward spacetime description, and caveat about the center.
   https://science.nasa.gov/universe/black-holes/supermassive-black-holes/new-nasa-black-hole-visualization-takes-viewers-beyond-the-brink/
2. NASA Science, **Black Hole Anatomy**. Event Horizon, Accretion Disk, Event Horizon Shadow, Photon Sphere, Doppler Beaming and Singularity sections retrieved/read in fetch chunk3. Distinguishes a horizon from its larger apparent shadow; isolated black holes can lack a bright disk; singularity prediction may mark limits of relativity.
   https://science.nasa.gov/universe/black-holes/anatomy/
3. Astronomy, Don Lincoln (Fermilab), **Ask Astro: Can an observer ever see something fall into a black hole?** Main answer actually retrieved/read in fetch chunk0. Supports redder light, increasingly separated/dimmer received emissions and disappearance rather than an eternally clear frozen object.
   https://www.astronomy.com/science/ask-astro-can-an-observer-ever-see-something-fall-into-a-black-hole/

NASA's accompanying videos/images were NOT watched or borrowed. The body text and figure captions are the research used here. Search-result-only commercial summaries/blogs and Reddit discussions were not used as authority.

## Claim-to-source ledger

| Script claim | Basis / limitation |
|---|---|
| A sufficiently large, quiet black-hole horizon may be crossed without a sharp local impact or immediate lethal tides | 1, together with no-solid-surface causal boundary in 2; classical general relativity, not a promise that real accreting environments are survivable. |
| No outward message from inside reaches the outside | 2 Event Horizon; 1 inward spacetime discussion. A beacon emitted BEFORE crossing may still arrive much later: the narration does not claim otherwise. |
| A quiet isolated hole need not have a blazing disk | 2 Accretion Disk. The film deliberately has NO bright gas disk; painted background stars are fictional, not a star map. |
| Feet/head differential gravitational acceleration can stretch a person; at a supermassive horizon the gradient can be gentler | 1 tidal explanation. Small-hole and large-hole pictures are illustrative scale comparisons, not exact numerical mass/radius or human-tolerance calculations. |
| A distant receiver gets redder, fainter emissions at longer intervals and the image fades | 3. This is an observing effect, not the astronaut actually freezing or disappearing at that same event. Received-beacon timing is qualitative, not a numerical null-geodesic prediction. |
| A local carried clock keeps ordinary time; the horizon is crossed in finite proper time | 1 distinguishes finite infall from the outside image. Clock hands depict one-second local ticks, not coordinate time or a measured mission clock. |
| Inside a nonrotating hole every future-directed causal trajectory goes to smaller areal radius; even initially outward radial light cannot increase that radius | 1 inward spacetime description; also explicitly derived below in the specified Schwarzschild/PG idealization. This is not offered as a detailed interior model of a rotating/charged hole. |
| Deeper tides can become destructive; a classical singularity does not establish a portal or an observed interior | 1, 2 Singularity. The film does not assert that the classical infinite-density prediction is established physical reality. |

## Explicit mathematical consistency of the causal diagram

In nonrotating, uncharged Schwarzschild geometry expressed in ingoing Painleve–Gullstrand coordinates, set `c = r_s = 1`. The radial metric is

`ds² = -dT² + (dr + sqrt(1/r) dT)²`.

For radial light, `ds² = 0`, giving `dr/dT = ±1 - sqrt(1/r)`.

- Outside `r > 1`, the outward-directed radial ray has positive radial velocity.
- At `r = 1`, it is tangent to the horizon in these coordinates.
- Inside `r < 1`, even the largest permitted outward radial component is negative. Slower/nonradial future-directed causal motion cannot have a larger outward radial velocity.

Shared `engine/runtime/horizon_motion.mjs` integrates the radial rays with midpoint steps. The fan shows short local permissible directions, not a numerical solution of nonradial light geodesics. The plot's horizontal axis is areal radius (outward to the right); vertical is future PG coordinate time. Nonrotating geometry is disclosed in narration and on-screen. No axis numbers are presented as a measured result.

The optional tidal-ratio helper is only the relative weak-field radial gradient scaling `gradient ~ M/r³`, hence at fixed `r/r_s`, `gradient ~ 1/M²`. No absolute stress, survival interval or biomedical threshold is inferred from it or displayed.

## What is authored, simplified or unknown

- All geometry, blue horizon wires, background stars/nebula, apparent dark silhouette/lensing arcs, camera travel, suit deformation, signal colors/spacing, diagram scale and score are authored illustrations.
- The optical motif is NOT an accurate relativistic ray trace. Its apparent silhouette and the smaller schematic horizon are separate objects; the boundary is not a glowing material shell. The changing diagrams are NOT the literal sky experienced by an infalling person.
- Star backgrounds are seeded originals and imply no accurate constellation, location or real photograph.
- Space/clock/radius pictures are NOT to physical common scale. The same easily visible astronaut is retained for legibility.
- No accretion environment, spin/charge, exact black-hole mass, survival countdown or measured trip is asserted.
- No portal, wormhole, confirmed microscopic singularity structure, infinite view of the future universe, or signal relayed back out from inside is invented.
- The script says explicitly that these are diagrams, not a recording from inside.
