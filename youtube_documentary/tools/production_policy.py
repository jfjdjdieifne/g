#!/usr/bin/env python3
"""Validate display manifests, not Arabic internal planning notes.
Usage: python3 tools/production_policy.py path/to/display_manifest.json
Call enforce_display() before rendering any new display manifest.
"""
import argparse
import json
import unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/'engine/PRODUCTION_POLICY.json'


def display_errors(manifest):
    errors=[]
    if manifest.get('language')!='en':
        errors.append('Display manifest must explicitly declare language=en.')
    texts=manifest.get('texts')
    if not isinstance(texts,dict) or not texts:
        errors.append('Display manifest must contain a non-empty texts dictionary.')
        return errors
    for key,text in texts.items():
        if not isinstance(text,str):
            errors.append(f'{key}: display value must be a string.')
            continue
        for char in text:
            name=unicodedata.name(char,'')
            if 'ARABIC' in name:
                errors.append(f'{key}: Arabic display character {char!r}.')
                break
            if not (char.isalpha() or char.isdigit()):continue
            if char.isdigit() and char not in '0123456789':
                errors.append(f'{key}: non-Western digit {char!r}.')
                break
            if char.isalpha() and 'LATIN' not in name:
                errors.append(f'{key}: non-Latin display character {char!r}.')
                break
    return errors


def enforce_display(manifest):
    errors=display_errors(manifest)
    if errors:raise ValueError('Production policy: '+'; '.join(errors))
    return manifest


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('manifest',type=Path)
    args=parser.parse_args()
    manifest=json.loads(args.manifest.read_text())
    enforce_display(manifest)
    if 'design' in manifest:enforce_design(manifest['design'])
    print('PASS: display / declared design policy. Art direction still requires visual review.')



def design_errors(design):
    """Check declared scene intent, not aesthetic quality or renderer truthfulness."""
    errors=[]
    if design.get('unit_of_design')!='scene':
        errors.append('Design the scene, not a stack of per-sentence popups.')
    for popup in design.get('generic_popups',[]):
        if not popup.get('narrative_reason') or not popup.get('reference_evidence'):
            errors.append('Generic popup requires narrative_reason and reference_evidence.')
    if design.get('claims_3d'):
        required=set(json.loads(POLICY.read_text())['depth']['required_when_claiming_3d'])
        missing=required-set(design.get('depth_features',[]))
        if missing:errors.append('3D claim missing: '+', '.join(sorted(missing)))
    return errors


def enforce_design(design):
    errors=design_errors(design)
    if errors:raise ValueError('Production policy: '+'; '.join(errors))
    return design


if __name__=='__main__':main()
