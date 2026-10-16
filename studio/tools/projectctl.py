#!/usr/bin/env python3
"""Offline onboarding/integrity tools. Declaration checks are NOT artistic certification."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
RELEASE = 'studio-2026-10-16-v1'
SLUG = re.compile(r'^[a-z][a-z0-9_]{0,63}$')
ANSWERS = ('assignment_and_style', 'approval_boundaries', 'material_strategy',
           'causal_explanation', 'camera_and_continuity', 'contextual_sound',
           'encoded_review_method', 'voice_portability', 'durable_recovery')


def load(root: Path, path: str):
    return json.loads((root / path).read_text(encoding='utf-8'))


def digest(path: Path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def safe_path(root: Path, name: str) -> Path:
    p = PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name:
        raise ValueError(f'Unsafe relative path: {name!r}')
    result = root / name
    if not result.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes root: {name!r}')
    return result


def verify(root: Path):
    errors = []
    try:
        project = load(root, 'studio/PROJECT.json')
        manifest = load(root, 'studio/INTEGRITY.json')
        if project['release'] != RELEASE or manifest['release'] != RELEASE:
            errors.append('Wrong/unknown release. Read the published START_HERE before proceeding.')
        for name in project['authority'].values():
            if not safe_path(root, name).is_file():
                errors.append(f'Missing authority file: {name}')
        for name, expected in manifest['sha256'].items():
            path = safe_path(root, name)
            if not path.is_file():
                errors.append(f'Missing release file: {name}')
            elif digest(path) != expected:
                errors.append(f'Modified release file: {name}; inspect changes, do not blindly refresh hashes.')
        refs = load(root, 'studio/REFERENCE_INDEX.json')
        voice = refs['voice']
        if digest(safe_path(root, voice['reference'])) != voice['sha256']:
            errors.append('Approved voice reference hash does not match.')
        profile = load(root, voice['profile'])
        if profile['reference_sha256'] != voice['sha256']:
            errors.append('Voice profile disagrees with approval registry.')
        default = load(root, 'youtube_documentary/engine/DEFAULT_VOICE.json')
        if default['authoritative_profile'] != 'voices/approved_voice03/VOICE_PROFILE.json':
            errors.append('DEFAULT_VOICE is not the approved voice03 profile.')
        styles = load(root, 'youtube_documentary/engine/STYLE_REGISTRY.json')
        ids = [s['id'] for s in styles['styles']]
        if len(ids) != len(set(ids)) or set(ids) != {'pure_documentary', 'documentary_explainer', 'pure_explainer', 'explainer_with_archive'}:
            errors.append('Style registry missing/duplicated/unknown family.')
        if styles.get('default_style') is not None:
            errors.append('Do not silently make the last film a universal default style.')
        state = load(root, 'studio/CURRENT_STATE.json')
        if state['release'] != project['release']:
            errors.append('Current state belongs to another release.')
        assets = load(root, 'studio/ASSET_REGISTRY.json')['assets']
        if len({a['id'] for a in assets}) != len(assets):
            errors.append('Duplicate external asset key.')
        for asset in assets:
            if not asset.get('drive_id') or not asset.get('scope') or not asset.get('verification'):
                errors.append(f'Asset missing identity/scope/verification: {asset.get("id")}')
        # Catalog is a complete snapshot of release files, not a guarantee of external media.
        catalog = load(root, 'studio/FILE_CATALOG.json')
        for entry in catalog['files']:
            path = safe_path(root, entry['path'])
            if not path.is_file():
                errors.append(f'Catalog file missing: {entry["path"]}')
            elif digest(path) != entry['sha256']:
                errors.append(f'Catalog file changed: {entry["path"]}')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'Incomplete/invalid studio release: {exc}')
    return errors


def doctor(root: Path):
    errors = verify(root)
    for error in errors:
        print('ERROR:', error)
    if errors:
        return 1
    state = load(root, 'studio/CURRENT_STATE.json')
    catalog = load(root, 'studio/FILE_CATALOG.json')
    print(f'PASS: {RELEASE}; {len(catalog["files"])} catalogued source files; authority/style/voice integrity verified.')
    print('TASK:', state['active_task'])
    print('PRODUCTION PAUSED:', state['production_paused'])
    for gap in state.get('known_gaps', []):
        print('KNOWN GAP:', gap)
    print('LIMIT: offline source/integrity check only; no renderer, Drive download, media viewing/listening or artistic certification.')
    return 0


def brief(root: Path):
    project = load(root, 'studio/PROJECT.json')
    state = load(root, 'studio/CURRENT_STATE.json')
    refs = load(root, 'studio/REFERENCE_INDEX.json')
    print(project['project'], '/', project['release'])
    print('ASSIGNMENT:', state['active_task'])
    print('NEXT:', state['next_action'])
    print('STYLES: pure_documentary / documentary_explainer / pure_explainer / explainer_with_archive; no default.')
    for ref in refs['references']:
        print(f'REFERENCE: {ref["id"]}: {ref["status"]}. {ref["scope"]}')
    print('VOICE:', refs['voice']['status'], '|', refs['voice']['warning'])
    print('RULES: English content; causal explanation; meaningful motion/camera across all styles; connected scenes; contextual sound; actual encoded review before assembly.')
    print('READ:', ', '.join(project['authority'].values()))
    return 0


def job_dir(root: Path, slug: str):
    if not SLUG.fullmatch(slug):
        raise ValueError('Job must be a lowercase letter followed by lowercase letters, digits or underscores (max64).')
    return root / 'studio/jobs' / slug


def init_job(root: Path, slug: str, style: str, task: str):
    errors = verify(root)
    if errors:
        raise ValueError('Release failed verification: ' + '; '.join(errors))
    valid = {s['id'] for s in load(root, 'youtube_documentary/engine/STYLE_REGISTRY.json')['styles']}
    if style not in valid or len(task.strip()) < 15:
        raise ValueError('A registered style and a specific real user assignment are required.')
    dest = job_dir(root, slug)
    dest.mkdir(parents=True, exist_ok=False)
    ack = {'release': RELEASE, 'job': slug, 'style': style, 'user_task': task,
           'english_content': None, 'preserve_approved_history': None,
           'shared_engine_only': None, 'tests_are_not_art_approval': None,
           'answers': {name: '' for name in ANSWERS},
           'voice_resolution': {'status': 'unresolved', 'approved_reference_sha256': load(root, 'studio/REFERENCE_INDEX.json')['voice']['sha256'], 'actual_platform_binding': None, 'evidence': None}}
    status = {'job': slug, 'phase': 'onboarding_not_approved_for_production', 'source_commit': None,
              'existing_local_assets': [], 'historically_reported_or_missing_assets': [],
              'actually_reviewed_encoded_units': [], 'user_approval_evidence': [],
              'durable_drive_copies': [], 'uploads_verified': False,
              'blockers': ['Complete truthful task-specific AGENT_ACK; resolve current pause/authorization and media availability.'],
              'next_action': 'Read current policy, inspect actual resources and write understanding; do not render.'}
    for name, obj in [('AGENT_ACK.json', ack), ('STATUS.json', status)]:
        (dest / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Created', dest.relative_to(root), '— unfilled declarations, NOT production permission.')
    return 0


def gate(root: Path, slug: str, stage='planning'):
    errors = verify(root)
    try:
        state = load(root, 'studio/CURRENT_STATE.json')
        ack = json.loads((job_dir(root, slug) / 'AGENT_ACK.json').read_text(encoding='utf-8'))
        if state['production_paused']:
            errors.append('Production is paused. Record a newer explicit user assignment/current state before authorizing a video job.')
        if ack.get('release') != RELEASE or ack.get('job') != slug:
            errors.append('Onboarding belongs to another job/release.')
        styles = {s['id'] for s in load(root, 'youtube_documentary/engine/STYLE_REGISTRY.json')['styles']}
        if ack.get('style') not in styles or len(ack.get('user_task', '').strip()) < 15:
            errors.append('Missing specific user task/registered style.')
        for key in ('english_content', 'preserve_approved_history', 'shared_engine_only', 'tests_are_not_art_approval'):
            if ack.get(key) is not True:
                errors.append(f'Explicit acknowledgment required: {key}')
        for key in ANSWERS:
            answer = ack.get('answers', {}).get(key, '')
            if not isinstance(answer, str) or len(answer.strip()) < 50:
                errors.append(f'Write a task-specific answer (not PASS): {key}')
        voice = ack.get('voice_resolution', {})
        if voice.get('approved_reference_sha256') != load(root, 'studio/REFERENCE_INDEX.json')['voice']['sha256']:
            errors.append('Voice acknowledgment refers to the wrong approved reference.')
        if voice.get('status') not in ('unresolved', 'resolved_exact_identity'):
            errors.append('Unknown voice resolution; do not treat a new numeric label as the same identity.')
        if stage == 'synthesis' and (voice.get('status') != 'resolved_exact_identity' or not voice.get('actual_platform_binding') or not voice.get('evidence')):
            errors.append('Synthesis blocked: exact approved identity lacks an actual backend binding/evidence; no silent substitute or re-audition.')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'Job record invalid/missing: {exc}')
    for error in errors:
        print('BLOCK:', error)
    if errors:
        return 1
    print(f'PASS: {slug} / {stage}: recorded understanding complete; not artistic, rights, listening or user-approval certification.')
    if stage == 'planning':
        print('New synthesis still requires gate --stage synthesis; unresolved voice does not authorize replacement.')
    return 0


def package(root: Path, output: Path):
    errors = verify(root)
    if errors:
        raise ValueError('Cannot package an unverified release: ' + '; '.join(errors))
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError('Keep generated kits outside the repository (e.g. /home/user/build).')
    if output.exists():
        raise FileExistsError('Refusing to overwrite an existing versioned kit.')
    entries = [f['path'] for f in load(root, 'studio/FILE_CATALOG.json')['files']]
    entries += ['studio/FILE_CATALOG.json', 'studio/INTEGRITY.json']
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in sorted(set(entries)):
            z.write(safe_path(root, name), name)
    # ZIP generated here contains only safe regular paths. Extract separately and verify all bytes.
    with tempfile.TemporaryDirectory(prefix='studio_cold_') as temp:
        target = Path(temp)
        with zipfile.ZipFile(output) as z:
            for entry in z.infolist():
                safe_path(target, entry.filename)
                if ((entry.external_attr >> 16) & 0o170000) == 0o120000:
                    raise ValueError('Unsafe ZIP symlink')
            z.extractall(target)
        errors = verify(target)
        if errors:
            raise ValueError('Cold extraction failed: ' + '; '.join(errors))
    print(json.dumps({'file': str(output), 'bytes': output.stat().st_size, 'md5': digest(output, 'md5'),
                      'sha256': digest(output), 'cold_source_integrity': 'PASS',
                      'scope': 'Source/onboarding kit; NOT all original media, final Titan recovery, a render or an artistic/listening test.'}, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    sub.add_parser('brief')
    init = sub.add_parser('init')
    init.add_argument('--job', required=True)
    init.add_argument('--style', required=True)
    init.add_argument('--task', required=True)
    check = sub.add_parser('gate')
    check.add_argument('--job', required=True)
    check.add_argument('--stage', choices=['planning', 'synthesis'], default='planning')
    pack = sub.add_parser('package')
    pack.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'doctor': return doctor(ROOT)
        if args.command == 'brief': return brief(ROOT)
        if args.command == 'init': return init_job(ROOT, args.job, args.style, args.task)
        if args.command == 'gate': return gate(ROOT, args.job, args.stage)
        if args.command == 'package': return package(ROOT, args.output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 1
    return 2


if __name__ == '__main__':
    sys.exit(main())
