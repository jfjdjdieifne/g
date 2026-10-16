#!/usr/bin/env python3
"""Shared style selection/declaration gate, NOT a creative quality certificate.
Pure explainer forbids archive on screen, not factual research/reference-only assets.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'engine/STYLE_REGISTRY.json'
AUTHENTIC = {'archive_video', 'interview', 'real_photo', 'press_scan', 'press_webpage'}
SCENE_FIELDS = ('viewer_learns', 'spatial_relationship', 'camera_motivation',
                'state_change', 'handoff', 'text_policy')
METHODS = {'xyz_3d', 'layered_2_5d', 'meaningful_2d'}


def registry():
    return json.loads(REGISTRY.read_text(encoding='utf-8'))


def normalized(value):
    return ' '.join(value.split()).casefold() if isinstance(value, str) else ''


def resolve_style(value):
    key = normalized(value)
    for style in registry()['styles']:
        if key and key in {normalized(x) for x in [style['id'], style['name_ar'], *style['aliases']]}:
            return style
    raise ValueError(f'Unknown or unspecified film style: {value!r}. Choose explicitly; no default style.')


def specified(value):
    return isinstance(value, str) and bool(value.strip()) and normalized(value) not in {
        'todo', 'tbd', 'pending', '...', 'fill me', 'n/a'}


def style_errors(contract, materials):
    """Check declared screen material/ownership, not actual pixels or listening."""
    if not isinstance(contract, dict):
        return ['Style contract missing: choose a named style before new production.']
    errors = []
    if contract.get('schema') != 'film-style-contract/1':
        errors.append('Style contract schema must be film-style-contract/1.')
    try:
        style = resolve_style(contract.get('style_id'))
    except ValueError as exc:
        return errors + [str(exc)]
    if not specified(contract.get('selection_evidence')):
        errors.append('Record the actual user instruction/decision in selection_evidence; init is only a draft.')
    if not isinstance(materials, dict):
        return errors + ['Style gate needs the actual material plan; a style name alone is not readiness.']
    assets, beats = materials.get('assets'), materials.get('beats')
    if not isinstance(assets, list) or not isinstance(beats, list) or not assets or not beats:
        return errors + ['Style gate needs non-empty assets and beats lists.']
    if any(not isinstance(a, dict) for a in assets) or any(not isinstance(b, dict) for b in beats):
        return errors + ['Style assets and beats must be objects.']
    ids = [a.get('id') for a in assets]
    if any(not specified(i) for i in ids) or len(set(ids)) != len(ids):
        return errors + ['Style material IDs must be unique non-empty strings.']
    by_id = dict(zip(ids, assets))
    seen_archive = seen_explanation = False
    for b in beats:
        name = str(b.get('id', '?'))
        refs = b.get('material_ids')
        if not isinstance(refs, list) or not refs or any(not isinstance(i, str) or i not in by_id for i in refs):
            errors.append(f'Beat {name}: unresolved screen material_ids.')
            continue
        used = [by_id[i] for i in refs]
        if any(a.get('usage') == 'reference_only' for a in used):
            errors.append(f'Beat {name}: reference_only assets cannot be referenced as screen material.')
        kinds = [a.get('kind') for a in used]
        for kind in kinds:
            if not isinstance(kind, str) or kind not in style['allowed_screen_kinds']:
                errors.append(f'Beat {name}: screen material {kind!r} is outside {style["id"]}; do not silently change styles.')
        has_archive = any(isinstance(k, str) and k in AUTHENTIC for k in kinds)
        seen_archive |= has_archive
        driver = b.get('visual_driver')
        if driver not in ('archive', 'explanation', 'support'):
            errors.append(f'Beat {name}: declare visual_driver archive/explanation/support (not the audio speaker).')
            continue
        if driver == 'support':
            if any(k != 'typography' for k in kinds) or not specified(b.get('support_purpose')):
                errors.append(f'Beat {name}: support is functional title/date/source typography, with support_purpose; not a loophole for illustrations.')
        if driver == 'archive' and not has_archive:
            errors.append(f'Beat {name}: archive visual_driver needs actual authentic screen material.')
        if driver == 'explanation':
            seen_explanation = True
            if style['id'] == 'pure_documentary':
                errors.append(f'Beat {name}: authored explanation requires a mixed style, not pure_documentary by default.')
            design = b.get('scene_design')
            if not isinstance(design, dict):
                errors.append(f'Beat {name}: explanation needs a scene_design, not decorative slides.')
            else:
                for field in SCENE_FIELDS:
                    if not specified(design.get(field)):
                        errors.append(f'Beat {name}: scene_design missing {field}.')
                if not isinstance(design.get('rendering_method'), str) or design['rendering_method'] not in METHODS:
                    errors.append(f'Beat {name}: choose xyz_3d/layered_2_5d/meaningful_2d; never label shadows as3D.')
        if style['id'] == 'explainer_with_archive' and has_archive and not specified(b.get('insert_reason')):
            errors.append(f'Beat {name}: selective archive needs insert_reason and a motivated return to explanation.')
    if style['archive_policy'] in ('required', 'selective_required') and not seen_archive:
        errors.append('Chosen documentary/hybrid style requires authentic on-screen material, not just an archive-style label.')
    if style['visual_driver'] in ('mixed', 'explanation') and not seen_explanation:
        errors.append('Chosen explanatory style needs an actual explanatory scene, not a renamed archive montage.')
    return errors


def enforce_project_style(project, materials, *, historical_rebuild=False):
    """Legacy reconstruction is explicit, never a new-film render-ready verdict."""
    project = Path(project)
    path = project / 'style_contract.json'
    if historical_rebuild:
        receipt = project / 'delivery.json'
        try:
            film = json.loads(receipt.read_text(encoding='utf-8'))['film']
            digest = film['sha256']
            known = isinstance(digest, str) and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest)
        except (OSError, ValueError, KeyError, TypeError):
            known = False
        if not known:
            raise ValueError('Historical rebuild requires an existing delivered-film receipt with SHA256, not a new-film bypass.')
        print('WARNING: historical reconstruction only; style gate bypass is NOT a new-film or artistic approval.')
        return None
    try:
        contract = json.loads(path.read_text(encoding='utf-8')) if path.exists() else None
    except (OSError, ValueError) as exc:
        raise ValueError(f'Invalid style contract: {exc}') from exc
    errors = style_errors(contract, materials)
    if errors:
        raise ValueError('Film style: ' + '; '.join(errors))
    return contract


def initialize(project, style_name):
    style = resolve_style(style_name)
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    path = project / 'style_contract.json'
    contract = {'schema': 'film-style-contract/1', 'style_id': style['id'],
                'selection_evidence': '', 'note': 'Draft only. Record the actual instruction and attach MATERIALS.json; no quality/approval claim.'}
    with path.open('x', encoding='utf-8') as f:
        json.dump(contract, f, ensure_ascii=False, indent=2)
        f.write('\n')
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    init = sub.add_parser('init')
    init.add_argument('--style', required=True)
    init.add_argument('--project', required=True, type=Path)
    check = sub.add_parser('check')
    check.add_argument('--project', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'list':
            for s in registry()['styles']:
                print(f'{s["id"]}: {s["name_ar"]} [{s["status"]}]')
        elif args.command == 'init':
            print('DRAFT, not render-ready:', initialize(args.project, args.style))
        else:
            materials = json.loads((args.project / 'MATERIALS.json').read_text(encoding='utf-8'))
            from documentary_materials import material_errors
            enforce_project_style(args.project, materials)
            errors = material_errors(materials)
            if errors:
                raise ValueError('; '.join(errors))
            print('PASS: declared style/material consistency ONLY. Actual encoded visual/audio review remains required.')
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f'{exc}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
