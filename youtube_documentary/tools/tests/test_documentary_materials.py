"""Declaration regression only, not media inspection or an artistic certificate."""
import copy
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from documentary_materials import material_errors


def photo():
    return {'id':'photo','kind':'real_photo','description':'Test fixture, not researched material',
            'source':'urn:test:photo','date_context':'Test date context','review_status':'inspected',
            'review_evidence':'Test fixture declaration only','rights_status':'Test/internal only'}


def plan():
    return {'assets':[photo()], 'beats':[{'id':1,'function':'Show the real subject',
        'material_ids':['photo'],'choice_reason':'Specific subject rather than generic model',
        'why_not_real':'The real photograph is used directly.'}]}


class MaterialDeclarations(unittest.TestCase):
    def test_missing_and_valid_material_plan(self):
        self.assertTrue(material_errors(None))
        self.assertEqual([], material_errors(plan(), [1]))
        self.assertTrue(material_errors(plan(), [1,2]))

    def test_search_lead_does_not_count_as_inspected(self):
        p=plan();p['assets'][0]['review_status']='search_only'
        self.assertTrue(material_errors(p))

    def test_photo_derivation_requires_real_reference_and_disclosure(self):
        p=plan();derived={'id':'derived','kind':'generated_from_photo','description':'Fixture',
            'reference_id':'photo','preserve':'Visible building edges','unknown_or_invented':'Unseen rear wall unknown',
            'presented_as_archive':False,'disclosure':'Illustrative reconstruction'}
        p['assets'].append(derived);p['beats'][0]['material_ids']=['derived']
        self.assertEqual([], material_errors(p))
        for field in ['reference_id','preserve','unknown_or_invented','disclosure']:
            bad=copy.deepcopy(p);bad['assets'][1].pop(field)
            self.assertTrue(material_errors(bad), field)
        p['assets'][1]['presented_as_archive']=True
        self.assertTrue(material_errors(p))

    def test_press_match_requires_real_words_not_generated_paper(self):
        p=plan();a=p['assets'][0];a.update(kind='press_scan',verified_crop_text='PABLO ESCOBAR')
        p['beats'][0].update(type='press_word_match',word='Escobar',semantic_reason='Repeated public identity')
        self.assertEqual([], material_errors(p))
        a['verified_crop_text']='Unrelated name'
        self.assertTrue(material_errors(p))
        a.update(kind='generated_illustration',presented_as_archive=False,disclosure='Generated fixture')
        self.assertTrue(material_errors(p))

    def test_archive_speech_needs_more_than_a_news_image(self):
        p=plan();p['assets'][0]['kind']='archive_video';p['beats'][0]['narrative_owner']='archive'
        self.assertTrue(material_errors(p))
        p['assets'][0].update(exact_quote='Test quote, not actual historical words',speaker='Fixture',
            source_in_out=[1,2],audio_review_method='Fixture method, not a listening claim')
        self.assertEqual([], material_errors(p))
        p['assets'][0]['source_in_out']=[2,1]
        self.assertTrue(material_errors(p))

    def test_no_arbitrary_asset_count_ceiling(self):
        p=plan()
        for i in range(1000):
            a=photo();a['id']=f'fixture{i}';p['assets'].append(a)
        self.assertEqual([], material_errors(p))

    def test_malformed_ids_and_unresolved_assets_fail_cleanly(self):
        for key,value in [('assets',[None]),('beats',[None])]:
            p=plan();p[key]=value;self.assertTrue(material_errors(p))
        p=plan();p['assets'][0]['kind']=[];self.assertTrue(material_errors(p))
        p=plan();p['beats'][0]['id']=[];self.assertTrue(material_errors(p,[1]))
        p=plan();p['assets'].append(copy.deepcopy(p['assets'][0]));self.assertTrue(material_errors(p))
        p=plan();p['beats'][0]['material_ids']=['missing'];self.assertTrue(material_errors(p))

    def test_director_does_not_promote_graphics_only_readiness(self):
        import director
        script={'title':'Fixture','display_manifest':{'language':'en','texts':{'title':'Test'}},
            'scenes':[{'id':'s','sentences':[{'text':'A real place','intent':['proof']}]}]}
        args=(director.load_json(director.TECH_DB)['cards'],director.load_json(director.SOUND_DB),director.vocab_names())
        self.assertFalse(director.plan(script,*args)['render_ready'])
        script['documentary_material_plan']=plan()
        self.assertFalse(director.plan(script,*args)['render_ready'])  # A style selection is required too.
        script['style_contract']={'schema':'film-style-contract/1','style_id':'pure_documentary','selection_evidence':'Test fixture instruction only'}
        script['documentary_material_plan']['beats'][0]['visual_driver']='archive'
        report=director.plan(script,*args)
        self.assertTrue(report['render_ready'])
        self.assertIn('not actual viewing',report['readiness_scope'])
        script['documentary_material_plan']['beats'][0]['material_ids']=['unknown']
        report=director.plan(script,*args)
        self.assertFalse(report['render_ready'])
        self.assertTrue(any('material_ids' in e for e in director.validate(report)[0]))

if __name__ == '__main__':unittest.main()
