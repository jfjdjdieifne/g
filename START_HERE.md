# START HERE — English Documentary & Explainer Studio

**Release: `studio-2026-10-16-v1` · audited 2026-10-16**

This is the single entry point. Do not start from an old HANDOFF, the last film, a demo or whichever Drive ZIP has the newest name.

## What is this project?

A reusable production system for English documentary/explainer videos, with several selectable styles and **one common engine plus film profiles**. The user speaks Arabic; finished narration and authored display are English. It is not an Escobar-only or Titan-only engine.

**Current task: organize the project before further video edits. Production is paused.** Read the precise status in [CURRENT_STATE](studio/CURRENT_STATE.json). A full Titan V2 movie was located on Drive; the matching final editable recovery has **not** been verified. An earlier WIP ZIP is not its replacement.

## Read in this order (not the entire archive)

1. [USER_RULES](studio/USER_RULES.md) — current creative rules and corrections.
2. [CURRENT_STATE](studio/CURRENT_STATE.json) — actual task, availability, blockers and next action.
3. [REFERENCE_INDEX](studio/REFERENCE_INDEX.json) — what the user approved, rejected or never approved; voice reference.
4. [STYLE_PLAYBOOK](studio/STYLE_PLAYBOOK.md) and the selected entry of [STYLE_REGISTRY](youtube_documentary/engine/STYLE_REGISTRY.json).
5. [OPERATIONS](studio/OPERATIONS.md) — onboarding, recovery, scene review and durable handoff.
6. Only then: the relevant film profile, applicable reference studies and shared renderer documentation.

[PROJECT.json](studio/PROJECT.json) defines authority/precedence and storage ownership. [FILE_CATALOG](studio/FILE_CATALOG.json) classifies the source tree; [ASSET_REGISTRY](studio/ASSET_REGISTRY.json) locates large external media. Files in `studio/history/`, old numbered guides and old handoffs are **history**, not competing current instructions.

## Before producing anything

From the repository root, with Python 3.10+:

```bash
python3 studio/tools/projectctl.py doctor
python3 studio/tools/projectctl.py brief
```

Then summarize the specific assignment, selected style, approved/rejected references, voice identity/portability limits, material strategy and actual missing resources. Never invent a new film/topic as an onboarding exercise.

For a newly authorized job (not the currently paused production):

```bash
python3 studio/tools/projectctl.py init --job my_film --style documentary_explainer --task "The actual user assignment"
# Read and genuinely complete studio/jobs/my_film/AGENT_ACK.json; blanks fail.
python3 studio/tools/projectctl.py gate --job my_film
```

The gate checks recorded understanding and consistency, **not artistic quality**. Inspect real material and actual encoded scenes yourself. No form, test result or agent verdict confers user approval.

## Where to find things

| Location | Owns |
|---|---|
| GitHub, this release | Current rules, engine/tools, film profiles, small approved voice reference, registries/history |
| [Drive Studio home](https://drive.google.com/drive/folders/1wyEvNfgln5bvlquVQwKmhl2N0xEQepNp) | Labelled films, voice/recovery media, historical library, portable source/onboarding kit |
| `youtube_documentary/engine/runtime/` | Shared engine; extend it instead of creating per-film engines |
| `youtube_documentary/engine/projects/<slug>/` | Film-specific script, materials, timing, scene direction and provenance |
| `studio/jobs/<slug>/` | Assignment, comprehension record, current status and handoff |
| `/home/user/build` / caches | Disposable scratch; existence here is not durable saving |

**Branch trap:** the repository default `main` was not the current production branch at this audit. The published entry is [this exact branch link](https://github.com/jfjdjdieifne/g/blob/arena/b2ef2032-g/START_HERE.md). Do not assume an old/default clone is up to date. Respect platform-locked branches; never switch to a branch your environment forbids. See OPERATIONS for importing a reviewed release safely.

## Message to give any new agent

Copy the prompt from [NEW_AGENT_PROMPT_AR](studio/NEW_AGENT_PROMPT_AR.md), plus the actual task. Connecting apps alone does not choose the correct version, style or assignment.

No old film, source clip, raw voice, trading-bot ZIP or unrelated root file has been deleted by this organization. Drive links use original files or shortcuts, not destructive moves.
