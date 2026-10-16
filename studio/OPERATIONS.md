# Agent operations — repeatable onboarding and durable handoff

## 1. Acquire the correct source, not just connected apps

Open root `START_HERE.md` from the published branch linked in PROJECT.json or the versioned source/onboarding kit in the Drive Studio home. Connecting GitHub/Drive does not choose a branch, a task or a style.

Run `python3 studio/tools/projectctl.py doctor` and `brief` before production. Doctor needs only Python's standard library: no renderer installation or paid service. It checks the authority map, required files, integrity manifest, style IDs and approved reference bytes. It reports missing local Titan V2 source and exact voice-binding limits honestly; these known gaps are not silently treated as recovered.

If this checkout lacks START_HERE or has another release:

- Inspect GitHub's published branch read-only with `git fetch origin arena/b2ef2032-g`; inspect its tree/diff before importing anything.
- **Never override a platform-locked working branch**, delete .git or reset a colleague's changes. Save a working-tree patch/inventory first. Import reviewed files onto the permitted session branch, or start a session based on the correct source. Do not blindly overwrite newer source with a Drive ZIP.
- The Drive kit is a versioned **source/onboarding snapshot**, not a second live policy or a claim that all original media is inside it. Compare release and manifest with GitHub. If GitHub is unreachable, label the snapshot/version explicitly and work only within the known brief; do not invent newer approvals.

## 2. Demonstrate understanding before doing the film

The current job is organization; video production remains paused until the user's actual requested edits are known. After a genuine newer user authorization, record that assignment/evidence in CURRENT_STATE, set production_paused to false only within that scope, refresh the reviewed release catalog/manifest, then create the job below. Never unpause merely to make a test pass. For an authorized future film:

```bash
python3 studio/tools/projectctl.py init --job my_film --style documentary_explainer --task "Specific authorized assignment"
# Complete the generated AGENT_ACK.json with actual, task-specific answers.
python3 studio/tools/projectctl.py gate --job my_film
```

`init` creates records, not a film, voice, new engine or approval. It refuses to overwrite an existing job. The agent must state the task/style and why, what is approved/rejected, the planned authentic/illustrative material, causal explanation, camera/continuity, sound, actual review method, voice portability and recovery plan. A generic “PASS” is not understanding. Present a short Arabic summary to the user; do not make them re-explain already-recorded preferences. Resolve only genuine material ambiguities.

The gate checks completeness and recorded consistency, **not the truth of viewing claims, taste, professional quality or user consent**. It cannot certify artistic understanding. A task-specific visual approach must still be tested in actual encoded scenes. When the assignment remains paused, the gate refuses production jobs.

## 3. Restore only the media this task needs

Use ASSET_REGISTRY, not an old absolute build path. Fetch metadata through the authenticated Drive connector first. Verify size and MD5 against the registry; verify SHA256 when recorded. Preserve the original ZIP. List entries and reject absolute paths, parent traversal and unsafe links before extracting to a new staging directory. Never extract over current/newer source. Compare dates, scripts, raw audio, timing and hashes, then deliberately import the relevant profile/assets.

- **Titan V2:** existing full film is Drive `1RDoxZ7wIg_qboUKjvUnc2IYYe6mlmLj7`, 95,887,992 bytes, MD5 `b88f065891130e9ef4a9374ab03ef783`. The available 83,254,292-byte recovery is an EARLY WIP. It does not establish the final script/timing/repairs/evidence of that movie. No verified matching final editable recovery was located. Do not silently rerender the old WIP and overwrite the movie.
- **Voice:** approved WAV is in Git and its guide is in Drive. Validate its SHA256; preserve raw takes. `voice-03` only identifies a registration within its original session. Resolve that actual identity using available platform support. If the tool cannot restore it, state the limitation and stop replacement synthesis; no re-audition, assumed numeric mapping or speed/music concealment. Planning/research can continue when authorized, but not false claims of recovered voice synthesis.
- **Escobar:** use its profile README/source_retrieval and the source/review/recovery packages in ASSET_REGISTRY if genuinely needed. Approved historical film/opening and voice remain untouched. A source kit alone does not include all the original research clips.

Large files belong in Drive/external storage, not Git. Do not fetch every historical package for a new topic. An unavailable connector/tool is a specific blocker; never substitute fabricated material.

## 4. Produce scene-first using the existing common engine

Keep choices in `youtube_documentary/engine/projects/<slug>/`; shared capabilities belong in runtime/tools. Relevant technical tools already exist under `youtube_documentary/tools/`: style_contract, production_policy, renderer/profile/review/mix/package helpers. The Python/Chromium/Three.js/FFmpeg dependencies vary by profile; inspect engine/package.json, install_webgl_runtime.py, requirements and that profile before installation. Onboarding verification does not claim these renderers were executed.

Before each scene: specific claim/causal idea, source/timecode/rights, visual action, informative view/camera, connection to neighbors, narration timing, meaningful text if needed, and sound intention. See current USER_RULES and `engine/EDITORIAL_REVIEW_PROTOCOL.md`; use the latter as technical detail subordinate to current policy.

Encode one unit, review the actual encoded unit (all 0.5s samples plus finer motion/joins), inspect/readability/causality/materials/continuity, record what was actually opened/heard and fix failures. Preserve superseded versions. Only assemble after every required unit has genuine review evidence. Then review full encoded joins and actual final picture/audio; a prior scene receipt or source still does not prove the final mux.

Keep separate records for factual/source verification, technical tests, actual visual/aural review, user approval and publication rights. Do not label a raw/performance/script/style approved because some other component was praised.

## 5. Checkpoint before the session can disappear

At every meaningful phase (script/source plan, voice, accepted scene group, final encode), keep a job STATUS.json using the generated template. Distinguish:

- exact existing local files versus historically reported or missing files;
- current canonical file/hash versus superseded/rejected versions;
- actual reviewed media/time ranges versus planned work;
- published/verified copies versus pending uploads;
- next concrete command/action and blockers.

Before claiming “saved”:

1. Commit current rules/code/profile/job records on the permitted session branch and push that branch; record its commit ID. Never commit caches, tokens, large original media or scratch renders.
2. Put raw takes, media dependencies, actual scene-review evidence and encoded checkpoints in versioned Drive recovery parts below the connector's 100 MB/file limit. Do not call a WIP package final. Store original-source packs separately where needed.
3. List the uploaded files again and compare size/MD5; preserve manifest SHA256 for every part. Record IDs and checksums in the registry/job status.
4. Fresh-extract the parts to a separate directory; verify every manifest file/hash and required dependency. An old successful cold test does not certify a later edited package. Do not claim a cold render or listening check unless performed.
5. Update CURRENT_STATE with the **published reality** and known gaps. Regenerate the catalog/manifest, run doctor and tests, then publish matching Git/Drive navigation. A capsule and registry must reference each other without inventing unavailable assets.

Use `python3 studio/tools/refresh_catalog.py` after authorized source/policy changes, then `python3 -m unittest discover -s studio/tests -v`. Refresh is an explicit release-maintainer operation; don't use it to bless unknown modifications. `projectctl package --output /path/out.zip` builds and cold-verifies a portable source/onboarding kit (NOT all historical media). Keep it outside the tracked tree and upload it only after checks.

## Approval and conflict handling

Latest explicit user instruction wins over historical creative instructions. Platform safety/branch restrictions always remain in force. If a supposed newer approval contradicts the recorded scope, quote the specific discrepancy and ask only what materially changes the job. Never infer approval from a file/folder title such as “Full Film and Recovery”. No automation can guarantee that a new agent has identical artistic judgment; this system makes state, evidence, limits and decisions inspectable rather than relying on memory.
