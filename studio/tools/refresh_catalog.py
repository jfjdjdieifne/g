#!/usr/bin/env python3
"""Explicit release-maintainer operation: classify source and refresh integrity after REVIEWED changes."""
from pathlib import Path
import json
import projectctl as ctl

ROOT = ctl.ROOT
EXCLUDED_PARTS = {'.git', 'node_modules', '__pycache__', '.venv', '.cache', 'build', 'dist', 'out', 'coverage', '.pytest_cache'}
EXCLUDED_FILES = {'studio/FILE_CATALOG.json', 'studio/INTEGRITY.json', 'studio/PUBLICATION.json'}
ENTRYPOINTS = ['START_HERE.md', 'README.md', 'AGENTS.md', '.gitignore', '.gitattributes', '.github/workflows/studio-checks.yml']


def category(name):
    if name.startswith('studio/history/'):
        return 'historical_snapshot_not_current_instructions'
    if name.startswith('studio/tools/') or name.startswith('studio/tests/'):
        return 'onboarding_tool_or_test'
    if name.startswith('studio/'):
        return 'current_authority_or_audit'
    if '/engine/voices/approved_voice03/' in name or name.endswith('/DEFAULT_VOICE.json'):
        return 'approved_voice_reference_not_executable_model'
    if '/engine/reference_lab/' in name:
        return 'historical_reference_observation_not_new_agent_viewing'
    if '/engine/projects/' in name:
        return 'film_specific_profile_or_historical_evidence_see_reference_index'
    if '/engine/runtime/' in name or '/tools/' in name:
        return 'shared_engine_or_tool'
    if '/assets_global/' in name:
        return 'shared_asset'
    if '/engine/' in name:
        return 'supporting_engine_contract_or_reference_current_rules_take_precedence'
    if name in ENTRYPOINTS or name.endswith('/AGENTS.md') or name.endswith('/START_HERE.md') or name.endswith('/README.md') or name.endswith('/HANDOFF.md'):
        return 'entrypoint_or_current_pointer'
    return 'historical_guide_or_supporting_project_file_not_current_policy'


def main():
    candidates = [ROOT / n for n in ENTRYPOINTS]
    for base in ('studio', 'youtube_documentary'):
        candidates.extend((ROOT / base).rglob('*'))
    files = []
    seen = set()
    for path in sorted(candidates):
        relative = path.relative_to(ROOT)
        name = relative.as_posix()
        if name in seen or name in EXCLUDED_FILES or any(p in EXCLUDED_PARTS for p in relative.parts):
            continue
        if name.startswith('studio/jobs/') or path.suffix in {'.pyc', '.pyo'}:
            continue
        if path.is_symlink():
            raise ValueError(f'List external dependencies in ASSET_REGISTRY, not source-kit symlinks: {name}')
        if not path.is_file():
            continue
        seen.add(name)
        files.append({'path': name, 'category': category(name), 'bytes': path.stat().st_size, 'sha256': ctl.digest(path)})
    catalog = {'schema': 1, 'release': ctl.RELEASE,
               'scope': 'Source/onboarding snapshot. Original media and final renders may be external. Root trading-bot ZIPs/demo and unrelated workflows are preserved but outside this documentary source kit.',
               'jobs': 'Active job records evolve separately; not a claim that future job files were reviewed by this release.',
               'files': files}
    (ROOT / 'studio/FILE_CATALOG.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    core = [f['path'] for f in files if f['category'] in {'current_authority_or_audit', 'entrypoint_or_current_pointer', 'onboarding_tool_or_test', 'approved_voice_reference_not_executable_model'}]
    core += ['studio/FILE_CATALOG.json', 'youtube_documentary/engine/STYLE_REGISTRY.json', 'youtube_documentary/engine/PRODUCTION_POLICY.json']
    manifest = {'schema': 1, 'release': ctl.RELEASE,
                'warning': 'Integrity/completeness within this source snapshot, not user approval, original-media availability or professional-art certification.',
                'sha256': {name: ctl.digest(ROOT / name) for name in sorted(set(core))}}
    (ROOT / 'studio/INTEGRITY.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'Refreshed {len(files)} source entries and {len(manifest["sha256"])} authority/tool hashes. Inspect git diff before publication.')


if __name__ == '__main__':
    main()
