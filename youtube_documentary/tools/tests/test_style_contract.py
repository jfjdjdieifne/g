"""Style declaration/onboarding regressions; NOT actual media/artistic review."""
import copy
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style_contract import (ROOT, SCENE_FIELDS, enforce_project_style, initialize,
                            registry, resolve_style, style_errors)
from documentary_materials import material_errors


def contract(name='pure_documentary'):
    return {'schema':'film-style-contract/1', 'style_id':name,
            'selection_evidence':'Test fixture instruction, not actual approval of a new film.'}


def fixture(explainer=False):
    asset={'id':'a','kind':'graphic' if explainer else 'real_photo',
           'description':'Synthetic declaration fixture; not an inspected production asset.'}
    if not explainer:
        asset.update(source='urn:fixture',date_context='Fixture date',review_status='inspected',
                     review_evidence='Fixture declaration only',rights_status='Fixture only')
    beat={'id':1,'function':'Demonstrate a connection','material_ids':['a'],
          'choice_reason':'Fixture choice','why_not_real':'Purposeful explanation' if explainer else 'Real photo',
          'visual_driver':'explanation' if explainer else 'archive'}
    if explainer:
        beat['scene_design']={key:'Fixture '+key for key in SCENE_FIELDS}
        beat['scene_design']['rendering_method']='meaningful_2d'
    return {'assets':[asset],'beats':[beat]}


def hybrid():
    a,b=fixture(),fixture(True)
    b['assets'][0]['id']='b';b['beats'][0].update(id=2,material_ids=['b'])
    return {'assets':a['assets']+b['assets'],'beats':a['beats']+b['beats']}


class StyleContracts(unittest.TestCase):
    def test_four_distinct_styles_no_default_or_invented_approvals(self):
        j=registry();self.assertIsNone(j['default_style']);self.assertEqual(len(j['styles']),4)
        approved=[s for s in j['styles'] if s['status']=='user_approved_film_reference']
        self.assertEqual([s['id'] for s in approved],['pure_documentary'])
        self.assertEqual(approved[0]['reference']['approved_on'],'2026-10-16')
        self.assertIn('three',approved[0]['reference']['scope'])

    def test_arabic_names_and_aliases_resolve_directly(self):
        for name,id_ in [(' وثائقي   بحت ','pure_documentary'),('بستايل وثائقي بحت','pure_documentary'),
                         ('وثائقي مع شرح','documentary_explainer'),('شرحي بحت','pure_explainer'),
                         ('شرحي مع أرشيف قليل','explainer_with_archive')]:
            self.assertEqual(resolve_style(name)['id'],id_)
        for bad in [None,True,{},'','unknown']:
            with self.assertRaises(ValueError):resolve_style(bad)

    def test_registry_aliases_are_unambiguous(self):
        from style_contract import normalized
        owners={}
        for s in registry()['styles']:
            for alias in [s['id'],s['name_ar'],*s['aliases']]:
                key=normalized(alias)
                self.assertIn(owners.get(key,s['id']),[s['id']]);owners[key]=s['id']

    def test_missing_selection_cannot_be_ready(self):
        self.assertTrue(style_errors(None,fixture()))
        c=contract();c['selection_evidence']='TODO'
        self.assertTrue(style_errors(c,fixture()))
        self.assertTrue(style_errors(contract(),None))

    def test_pure_documentary_real_material_and_no_silent_models(self):
        self.assertEqual(style_errors(contract(),fixture()),[])
        for kind in ['original_model','graphic','generated_from_photo','generated_illustration']:
            m=fixture();m['assets'][0]['kind']=kind
            self.assertTrue(style_errors(contract(),m),kind)
        self.assertTrue(style_errors(contract(),fixture(True)))

    def test_functional_title_is_not_a_slideshow_loophole(self):
        m=fixture();m['assets'].append({'id':'title','kind':'typography','description':'Fixture source title'})
        m['beats'].append({'id':2,'material_ids':['title'],'visual_driver':'support','support_purpose':'Identify source'})
        self.assertEqual(style_errors(contract(),m),[])
        m['beats'][1]['support_purpose']=''
        self.assertTrue(style_errors(contract(),m))
        m['assets'][1]['kind']='graphic';m['beats'][1]['support_purpose']='Decoration'
        self.assertTrue(style_errors(contract(),m))

    def test_pure_explainer_needs_no_screen_archive_but_research_allowed(self):
        m=fixture(True);c=contract('pure_explainer')
        self.assertEqual(style_errors(c,m),[]);self.assertEqual(material_errors(m),[])
        ref=fixture()['assets'][0];ref['id']='ref';ref['usage']='reference_only';m['assets'].append(ref)
        self.assertEqual(style_errors(c,m),[])
        m['beats'][0]['material_ids'].append('ref')
        self.assertTrue(style_errors(c,m))

    def test_real_archive_photo_on_an_explainer_board_still_counts_as_archive(self):
        m=fixture(True);m['assets'][0]=fixture()['assets'][0]
        self.assertTrue(style_errors(contract('pure_explainer'),m))

    def test_explanation_requires_meaning_camera_state_and_handoff(self):
        for key in [*SCENE_FIELDS,'rendering_method']:
            m=fixture(True);m['beats'][0]['scene_design'].pop(key)
            self.assertTrue(style_errors(contract('pure_explainer'),m),key)
        m=fixture(True);m['beats'][0]['scene_design']['rendering_method']='tilt_and_shadow'
        self.assertTrue(style_errors(contract('pure_explainer'),m))

    def test_mixed_styles_need_real_explanation_and_real_archive(self):
        c=contract('documentary_explainer')
        self.assertEqual(style_errors(c,hybrid()),[])
        self.assertTrue(style_errors(c,fixture()))
        self.assertTrue(style_errors(c,fixture(True)))

    def test_selective_archive_needs_insert_reason_not_percentage(self):
        c=contract('explainer_with_archive');m=hybrid()
        self.assertTrue(style_errors(c,m))
        m['beats'][0]['insert_reason']='Original evidence for this specific claim; return to the anchored board.'
        self.assertEqual(style_errors(c,m),[])

    def test_malformed_input_fails_with_errors_not_type_crash(self):
        for m in [None,[],{'assets':[None],'beats':[{}]}, {'assets':[{'id':[]}],'beats':[{}]}]:
            self.assertTrue(style_errors(contract(),m))
        for field,value in [('material_ids',[{}]),('visual_driver',{}),('scene_design',[])] :
            m=fixture(True);m['beats'][0][field]=value
            self.assertTrue(style_errors(contract('pure_explainer'),m))

    def test_init_is_draft_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            p=initialize(d,'وثائقي بحت');raw=p.read_bytes()
            self.assertTrue(style_errors(json.loads(raw),fixture()))
            with self.assertRaises(FileExistsError):initialize(d,'شرحي بحت')
            self.assertEqual(p.read_bytes(),raw)

    def test_shared_project_gate_and_explicit_legacy_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            with self.assertRaises(ValueError):enforce_project_style(p,fixture())
            with self.assertRaises(ValueError):enforce_project_style(p,fixture(),historical_rebuild=True)
            (p/'style_contract.json').write_text(json.dumps(contract()))
            self.assertEqual(enforce_project_style(p,fixture())['style_id'],'pure_documentary')
            with self.assertRaises(ValueError):enforce_project_style(p,fixture(True))
            (p/'delivery.json').write_text(json.dumps({'film':{'sha256':'a'*64}}))
            with contextlib.redirect_stdout(io.StringIO()) as log:
                self.assertIsNone(enforce_project_style(p,fixture(),historical_rebuild=True))
            self.assertIn('NOT a new-film',log.getvalue())

    def test_director_readiness_recomputes_style_not_trusted_label(self):
        import director
        def build(style=None):
            script={'sentences':['Show the actual subject.'],
                    'display_manifest':{'language':'en','texts':{'source':'Source / fixture'},'design':{'unit_of_design':'scene'}},
                    'documentary_material_plan':fixture()}
            if style is not None:script['style_contract']=style
            return director.plan(script,director.load_json(director.TECH_DB)['cards'],
                                 director.load_json(director.SOUND_DB),director.vocab_names())
        missing=build();self.assertFalse(missing['render_ready']);self.assertTrue(missing['style_errors'])
        good=build(contract());self.assertTrue(good['render_ready'])
        bad=build(contract('pure_explainer'));self.assertFalse(bad['render_ready'])
        # Validation of a stale/forged readiness boolean also checks the actual contract.
        bad['render_ready']=True
        errors,_=director.validate(bad)
        self.assertTrue(any('outside pure_explainer' in e for e in errors))

    def test_onboarding_discoverable_and_renderer_connected(self):
        self.assertTrue((ROOT.parent/'AGENTS.md').exists())
        for name in ['START_HERE.md','engine/STYLE_GUIDE.md','engine/STYLE_REGISTRY.json']:
            self.assertTrue((ROOT/name).exists(),name)
        renderer=(ROOT/'tools/render_film_profile.py').read_text()
        self.assertLess(renderer.index('enforce_project_style(P.PROJECT'),renderer.index('plan=P.prepare()'))


if __name__=='__main__':unittest.main()
