"""Declared source/idea gate. Never certifies viewing, artistic quality or rights.

All newly planned documentary beats need a material choice, not just a motion.
The human/agent still has to inspect the original assets and encoded result.
"""

import math


def valid_bounds(bounds):
    return (isinstance(bounds, list) and len(bounds) == 2
            and all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in bounds)
            and 0 <= bounds[0] < bounds[1])


def material_errors(plan, expected_beats=None):
    if not isinstance(plan, dict):
        return ['Documentary material plan missing: source/idea planning must precede render readiness.']
    errors = []
    assets = plan.get('assets', [])
    beats = plan.get('beats', [])
    if not isinstance(assets, list) or not assets or not isinstance(beats, list) or not beats:
        return ['Documentary material plan needs non-empty assets and beats lists.']
    if any(not isinstance(a, dict) for a in assets) or any(not isinstance(b, dict) for b in beats):
        return ['Documentary assets and beats must be objects.']
    ids = [a.get('id') for a in assets]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        return ['Material IDs must be non-empty unique strings.']
    by_id = dict(zip(ids, assets))
    authentic = {'archive_video', 'real_photo', 'press_scan', 'press_webpage', 'interview'}
    generated = {'generated_from_photo', 'generated_illustration'}
    kinds = authentic | generated | {'original_model', 'graphic', 'typography'}
    for a in assets:
        name = a['id']
        if not isinstance(a.get('kind'), str) or a.get('kind') not in kinds:
            errors.append(f'{name}: unknown material kind; distinguish authentic media from illustration.')
            continue
        if not a.get('description'):
            errors.append(f'{name}: explain the material, not just its filename.')
        if a.get('kind') in authentic:
            if a.get('review_status') != 'inspected':
                errors.append(f'{name}: authentic material must be inspected, not merely a search lead.')
            for key in ['source', 'date_context', 'review_evidence', 'rights_status']:
                if not a.get(key):
                    errors.append(f'{name}: authentic material missing {key}.')
        if a.get('kind') in generated:
            if a.get('presented_as_archive') is not False or not a.get('disclosure'):
                errors.append(f'{name}: generated imagery must be disclosed and never presented as archive.')
            if a.get('kind') == 'generated_from_photo':
                ref_id = a.get('reference_id')
                ref = by_id.get(ref_id) if isinstance(ref_id, str) else None
                if not ref or not isinstance(ref.get('kind'), str) or ref.get('kind') not in {'real_photo', 'archive_video'} or not ref.get('review_evidence'):
                    errors.append(f'{name}: photo-derived generation requires an inspected authentic visual reference.')
                if not a.get('preserve') or not a.get('unknown_or_invented'):
                    errors.append(f'{name}: record preserved features and unknown/invented parts.')
    if errors:
        return errors
    beat_ids = [b.get('id') for b in beats]
    if any(not isinstance(i, (str, int)) or isinstance(i, bool) for i in beat_ids) or len(set(beat_ids)) != len(beat_ids):
        return errors + ['Material beat IDs must be unique strings or integers.']
    if expected_beats is not None and set(beat_ids) != set(expected_beats):
        errors.append('Material beats must cover every director beat exactly once.')
    for b in beats:
        name = str(b.get('id', '?'))
        for key in ['function', 'choice_reason', 'why_not_real']:
            if not b.get(key):
                errors.append(f'Beat {name}: missing {key}; explain the real-first choice, including deliberate illustration.')
        refs = b.get('material_ids')
        if not isinstance(refs, list) or not refs or any(not isinstance(i, str) or i not in by_id for i in refs):
            errors.append(f'Beat {name}: resolve all material_ids to actual manifest entries.')
            continue
        if b.get('type') == 'press_word_match':
            word = b.get('word')
            for aid in refs:
                a = by_id[aid]
                if a.get('kind') not in {'press_scan', 'press_webpage'} or not isinstance(word, str) or not word or word.casefold() not in str(a.get('verified_crop_text', '')).casefold():
                    errors.append(f'Beat {name}: word-match needs genuine inspected press crops containing the exact word.')
            if not b.get('semantic_reason'):
                errors.append(f'Beat {name}: word-match needs a semantic reason, not merely speed.')
        if b.get('narrative_owner') == 'archive':
            candidates = [by_id[i] for i in refs if by_id[i].get('kind') in {'archive_video', 'interview'}]
            if not any(a.get('exact_quote') and a.get('speaker') and valid_bounds(a.get('source_in_out')) and a.get('audio_review_method') for a in candidates):
                errors.append(f'Beat {name}: archive-led speech needs exact sourced words, speaker, bounds and audio-review method.')
    return errors
