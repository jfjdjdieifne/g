import importlib.util
import sys
import unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'engine/runtime'))
from photo_depth import Camera,project_texture,view,page_turn,document,PhotoDepth
SPEC=importlib.util.spec_from_file_location('intro3_profile_tests',ROOT/'engine/projects/escobar_intro3/profile.py');P=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(P)

class SharedPhotoDepthTests(unittest.TestCase):
    def setUp(self):
        self.im=np.zeros((120,80,3),np.uint8);self.im[:]=[91,133,162];self.im[25:80,20:60]=[230,225,210]
    def test_view_and_document_dimensions(self):
        for x in [view(self.im,(40,60),80,(320,180)),document(self.im,220,(320,180))]:
            self.assertEqual(x.shape,(180,320,3));self.assertEqual(x.dtype,np.uint8)
    def test_full_document_has_edges_not_repeated_texture(self):
        x=document(self.im,220,(320,180));self.assertTrue(np.all(x[80,0]==[12,15,17]))
    def test_reject_near_plane(self):
        c=Camera((0,-1,0),(0,0,0),43,320,180)
        with self.assertRaises(ValueError):project_texture(self.im,[[-1,-2,1],[1,-2,1],[1,-2,-1],[-1,-2,-1]],c)
    def test_page_turn_all_phases_finite(self):
        for t in [0,.24,.49,.5,.51,.76,1]:
            x=page_turn(self.im,self.im,t,(320,180));self.assertEqual(x.shape,(180,320,3));self.assertTrue(np.isfinite(x).all())
    def test_layered_original_pixels(self):
        m=np.zeros((120,80),np.uint8);m[25:80,20:60]=255;s=PhotoDepth(self.im,m)
        for u in [0,.5,1]:self.assertEqual(s.render((40,60),80,u,(320,180)).shape,(180,320,3))

class BroadProfileTests(unittest.TestCase):
    def test_narration_has_no_event_resolution(self):
        text=' '.join(P.NARRATION.values()).lower()
        for word in ['prison','escaped','escape','died','death','killed','surrendered']:self.assertNotIn(word,text)
        self.assertIn('billionaire list',text);self.assertIn('football fields',text)
    def test_source_handoffs_do_not_overlap(self):
        duration={'ship':5.15,'wealth':15.487729,'wanted':2.64,'social':16.671938,'fear':5.51,'questions':11.087542,'close':4.260875}
        keys=list(P.STARTS)
        for a,b in zip(keys,keys[1:]):self.assertLessEqual(P.STARTS[a]+duration[a],P.STARTS[b])
        self.assertLess(P.STARTS['close']+duration['close'],P.DURATION)
    def test_identity_and_truthful_audio_only(self):
        self.assertEqual(P.VOICE,'voice-02');self.assertTrue(P.ARCHIVE['wanted']['audio_only'])
    def test_selected_assets_persist(self):
        for n in ['forbes_cover.png','forbes_entry.png','semana.jpg','football.jpg','congress.jpg','city.jpg','daily_page7.jpg']:
            self.assertTrue((ROOT/'engine/projects/escobar_intro3/assets'/n).is_file())
        for n in P.NARRATION:self.assertTrue((ROOT/'engine/projects/escobar_intro3/voice'/f'broad_{n}.mp3').is_file())

if __name__=='__main__':unittest.main()
