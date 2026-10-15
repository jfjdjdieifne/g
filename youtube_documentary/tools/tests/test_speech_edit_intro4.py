import unittest,sys,importlib.util,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'engine/runtime'));sys.path.insert(0,str(ROOT/'tools'))
from speech_edit import tighten,map_time
from film_runtime import FilmVisuals
import escobar_intro4 as film

class SpeechEditingTests(unittest.TestCase):
    def test_quiet_gap_shortened_and_words_protected(self):
        x=np.zeros(16000);x[1000:4000]=.2;x[12000:15000]=-.2;words=[{'start':.07,'end':.4},{'start':1.2,'end':1.5}]
        y,a=tighten(x,words,sr=10000);self.assertLess(len(y),len(x));self.assertAlmostEqual(a['cuts'][0]['out']-a['cuts'][0]['in'],.54);self.assertEqual(y[1500],x[1500])
        self.assertIsNone(map_time(.8,a['mapping']));self.assertAlmostEqual(map_time(1.3,a['mapping']),.756)
    def test_nonquiet_gap_not_removed(self):
        x=np.full(16000,.1);y,a=tighten(x,[{'start':.1,'end':.4},{'start':1.2,'end':1.5}],sr=10000);self.assertEqual(len(y),len(x));self.assertEqual(a['cuts'],[])
    def test_short_natural_gap_untouched(self):
        x=np.zeros(10000);y,a=tighten(x,[{'start':.05,'end':.3},{'start':.6,'end':.9}],sr=10000);self.assertEqual(a['cuts'],[]);self.assertEqual(len(y),len(x))
    def test_explicit_phrase_cut_mapping(self):
        x=np.zeros(10000);y,a=tighten(x,[{'start':.05,'end':.3},{'start':.6,'end':.9}],sr=10000,explicit=[(.35,.55)]);self.assertEqual(len(y),7960);self.assertAlmostEqual(map_time(.7,a['mapping']),.496)
    def test_bad_bounds_and_nonmono_rejected(self):
        for kwargs in [{'explicit':[(-1,1)]},{'explicit':[(.1,2)]},{'sr':0}]:
            with self.assertRaises(ValueError):tighten(np.zeros(48000),[],**kwargs)
        with self.assertRaises(ValueError):tighten(np.zeros((2,4)),[])

class Revision4Tests(unittest.TestCase):
    def test_profile_preserves_voice_and_genuine_names(self):
        self.assertEqual(film.P.VOICE,'voice-02');self.assertEqual(film.P.ARCHIVE['name_host']['in'],11.36);self.assertEqual(film.P.ARCHIVE['name_guest']['in'],38.72)
    def test_timeline_all_gaps_small_no_voice_overlap(self):
        clips=film.timeline()['clips']
        for a,b in zip(clips,clips[1:]):self.assertGreaterEqual(b['start'],a['end']);self.assertLess(b['start']-a['end'],.121)
        self.assertLess(film.timeline()['duration'],55);self.assertGreater(film.timeline()['duration'],50)
    def test_shots_contiguous_and_readable_press(self):
        rows=film.shots();self.assertEqual(rows[0]['start'],0);self.assertAlmostEqual(rows[-1]['end'],film.timeline()['duration'])
        for a,b in zip(rows,rows[1:]):self.assertAlmostEqual(a['end'],b['start'])
        for s in rows:
            self.assertLessEqual(s['end']-s['start'],4.4)
            if s['kind']=='press':self.assertGreaterEqual(s['end']-s['start'],1.99)
        self.assertEqual(sum(s['kind']=='press'for s in rows),2)
    def test_word_scale_anchor_static_with_highlighter_visible(self):
        a=film.word_card('elpais_word.png',.5,'El Pais');b=film.word_card('elpais_word.png',.95,'El Pais');self.assertTrue(np.array_equal(a,b));self.assertEqual(a.shape,(1080,1920,3))
        self.assertGreater(film.image('elpais_word.png').shape[0],70);self.assertGreater(film.image('elpais_word.png').shape[1],300)
    def test_only_two_filler_phrases_removed_no_regeneration(self):
        a=json.loads((film.B/'voice_edits.json').read_text())
        for key,x in a.items():
            self.assertEqual(x['source_sha256'],hashlib.sha256((film.SRC/'voice'/f'broad_{key}.mp3').read_bytes()).hexdigest())
            for w in x['words']:
                if w['edited_start'] is not None and w['edited_end'] is not None:self.assertAlmostEqual(w['end']-w['start'],w['edited_end']-w['edited_start'],places=6)
    def test_modern_press_distinct_and_material_gate_passes(self):
        from documentary_materials import material_errors
        data=json.loads((film.PROJ/'MATERIALS.json').read_text());self.assertEqual(material_errors(data),[])
        self.assertEqual(sum(a['kind']=='press_webpage'for a in data['assets']),2);film.validate()
    def test_shared_runtime_is_not_film_specific(self):
        self.assertIsInstance(film.visuals,FilmVisuals)
        src=(ROOT/'engine/runtime/film_runtime.py').read_text();self.assertNotIn('football.jpg',src);self.assertNotIn('Escobar',src)

if __name__=='__main__':unittest.main()
