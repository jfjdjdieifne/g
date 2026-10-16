"""Full-film data gates. Not evidence of creative approval or naturalness."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'engine/projects/escobar_full'
sys.path.insert(0,str(ROOT/'tools'))
from production_policy import display_errors,design_errors
from documentary_materials import material_errors

class FullFilmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.plan=json.loads((P/'timeline.json').read_text())
    def test_contiguous_body_and_total_scope(self):
        p=self.plan;shots=p['shots'];self.assertEqual(shots[0]['first'],0)
        for a,b in zip(shots,shots[1:]):self.assertEqual(a['last'],b['first'])
        self.assertGreaterEqual(min(s['last']-s['first'] for s in shots),12)  # No accidental quote-return flash.
        self.assertEqual(shots[-1]['last'],p['frames']);self.assertTrue(240<=33.125+p['frames']/p['fps']<=540)
    def test_speech_does_not_overlap(self):
        clips=sorted(self.plan['audio'],key=lambda c:c['start'])
        for a,b in zip(clips,clips[1:]):self.assertLessEqual(a['end'],b['start']+.0001)
    def test_sources_and_display(self):
        j=json.loads((P/'display_manifest.json').read_text());self.assertFalse(display_errors(j));self.assertFalse(design_errors(j['design']))
        self.assertFalse(material_errors(json.loads((P/'MATERIALS.json').read_text())))
    def test_original_witness_clocks_match_picture(self):
        for a in self.plan['audio']:
            if a['kind']!='archive':continue
            shot=next(s for s in self.plan['shots']if s['first']/24<=a['start']<s['last']/24)
            self.assertTrue(shot['speaker']);original=4191.35 if a['id']=='murphy' else 4877.43
            # Timeline quantization can differ by up to one half-frame.
            picture_source=shot['original_source_in']+a['start']-shot['first']/24
            self.assertAlmostEqual(picture_source,original,delta=1/48+.001)
        self.assertFalse(self.plan['archive_witnesses_retimed'])
    def test_later_film_approval_has_explicit_user_evidence(self):
        j=json.loads((P/'USER_FEEDBACK.json').read_text());self.assertTrue(j['pace_approved']);self.assertFalse(j['whole_film_work_paused_for_pace_review']);self.assertTrue(j['full_body_user_approved']);self.assertEqual(j['full_film_approval']['date'],'2026-10-16');self.assertEqual(j['full_film_approval']['style_id'],'pure_documentary')
    def test_word_partition_keeps_all_detected_words(self):
        for a in json.loads((P/'narration_pacing.json').read_text()).values():
            self.assertEqual([i for r in a['regions']for i in range(r['word_first'],r['word_last_exclusive'])],list(range(a['recognized_words'])))
            self.assertTrue(any(r['emphasis']for r in a['regions']));self.assertFalse(a['manual_listening_claimed'])
    def test_andean_routes_branch_instead_of_false_peru_bolivia_chain(self):
        s=next(s for s in self.plan['shots']if s.get('stage')=='andes');self.assertEqual(s['edges'],[[0,2],[1,2]])
    def test_known_native_cut_guards_and_motivated_quote_exit(self):
        shots=self.plan['shots']
        self.assertTrue(any(s.get('original_source_in')==3949.5 for s in shots))
        self.assertTrue(any(s.get('original_source_in')==4369.3 for s in shots))
        a=next(a for a in self.plan['audio'] if a['id']=='murphy')
        q=next(s for s in shots if s.get('speaker') and s['start']<=a['start']<s['end'])
        # The source cuts to a party photograph at about4195.50. Exit before it;
        # leave the original audio intact over the genuine prison-office return.
        self.assertLess(q['original_source_in']+(q['last']-q['first'])/24,4195.46)
        self.assertLess(q['end'],a['end'])
        nxt=shots[shots.index(q)+1]
        self.assertEqual(nxt['first'],q['last'])
        self.assertEqual(nxt['original_source_in'],4249)
        self.assertGreaterEqual(nxt['last']-nxt['first'],12)

    def test_no_invented_scene_or_uniform_video_speedup(self):
        self.assertFalse(self.plan['native_footage_retimed']);self.assertTrue(self.plan['intro_prefix_external_locked'])
        self.assertEqual({s['kind'] for s in self.plan['shots']},{'video','image','depth','route'})

if __name__=='__main__':unittest.main()
