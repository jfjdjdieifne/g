# v4 — English-only cartographic depth study

## Latest user decisions — 2026-10-15
- v3 is much stronger; generalize its scene-first design direction so the previous popup/PowerPoint mistake does not recur.
- ALL video content is English. Arabic stays in conversation/internal planning only. This supersedes the previous Arabic-primary screen treatment.
- Extend the same composition and connected sequence into 3D/depth.

## Implementation, not a new template
The reusable policy is `engine/PRODUCTION_POLICY.json`, the gate is `tools/production_policy.py`. The agent brief, continuity model, engine registry and director output now carry it. This is not a rule that every scene must be a map or every shot must be 3D.

`tools/ww2demo_v4_depth.py` keeps v3's 16s sequence and the same reference basis (WW2 P2 @2:04–2:15, previously seen cards). The 3D extension is requested by the user, not claimed to be observed in those flat reference frames. No new evidence-free technique card is inserted into the bank.

### Actual geometry
- Perspective look-at camera with focal length, XYZ world coordinates, continuous dolly plus gentle yaw/tilt. Poses are deterministic functions of time.
- Base map at Z=0, Colombia surface at Z=0.52, explicit vertical coastline/border side-wall quads, far-to-near ordering and a contact shadow.
- Elevated supply arc with height varying along its length. Start/end exactly meet the Medellin and Miami surface anchors; the arc also has a projected shadow.
- Convoy routes remain on land inside Colombia; small bevelled XYZ symbols follow them.
- Labels are upright billboards anchored via XYZ, not UI popup cards. Text size stays readable rather than tilting with the floor.
- Larger 7680×5760 atlas prevents missing-background corners during oblique shots.

### Scope / limitations
This is a stylized extruded cartographic stage, not a globe, measured terrain, photorealistic lighting, a general 3D scene graph or full mesh/z-buffer renderer. Plane homographies are derived from the perspective camera; wall quads use painter ordering. The tool remains `partial` in the engine registry because the sequence is Escobar-specific.

The old v3 Arabic MP4 stays historical. Future v3 source output has been translated to English and rejects non-Latin display strings. Legacy renderers are not all automatically wired into the new production gate: the brief explicitly requires calling the gate before any new render. Planning in Arabic is permitted, but it is not a caption fallback.

The gate checks writing system, not whether a sentence is semantically English. It validates declared scene/3D features, not professional aesthetics. Visual review remains mandatory.

### Narrative truth
The route, three convergence paths and country tint are symbolic design-study elements, not documented 1993 shipping/police paths or a claim of full-country occupation. No unsupported numeric statistics or archival-source claims are shown. Audio is the restrained synthetic bed from v3 with the same timed low-level cues, no VO.

## Reproduce
```
python3 -m pip install -r tools/requirements_ww2_v3.txt
python3 tools/production_policy.py engine/projects/ww2_demo/v4_depth/display.json
python3 -m unittest discover -s tools/tests -v
python3 tools/ww2demo_v4_depth.py --preview
python3 tools/ww2demo_v4_depth.py
```
Generated atlases/frames/videos stay in `/home/user/build/ww2_demo_v4_depth`, outside Git. Fonts and geometry remain in the repository. Do not promote a successful technical gate into a claim of reference-level professional art direction.
