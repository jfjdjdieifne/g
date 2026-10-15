"""Technical gates only; not an aesthetic or legal approval certificate."""
import hashlib
import json
import sys
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import escobar_hook30 as h
from production_policy import display_errors,design_errors,enforce_editorial_review
from xyz_scene import Camera,World,cylinder


class HookGates(unittest.TestCase):
    def test_rejected_cut_is_blocked_before_render(self):
        with self.assertRaisesRegex(ValueError,'Editorial production blocked'):
            enforce_editorial_review(h.PROJECT)
        import contextlib,io
        with contextlib.redirect_stdout(io.StringIO()) as output:
            enforce_editorial_review(h.PROJECT,historical_rebuild=True)
        self.assertIn('REJECTED',output.getvalue())
    def test_explicit_approval_and_exact_take(self):
        meta=json.loads((h.PROJECT/'voice_preview.json').read_text())
        self.assertEqual(meta['approved_voice_id'],'voice-02')
        self.assertIn('approved by user',meta['approval'])
        self.assertEqual(hashlib.sha256((h.PROJECT/meta['approved_audio']).read_bytes()).hexdigest(),meta['sha256'])
    def test_policy(self):
        self.assertEqual(display_errors(h.MANIFEST),[])
        self.assertEqual(design_errors(h.MANIFEST['design']),[])
    def test_photo_has_modern_date_and_credit(self):
        with Image.open(h.PROJECT/'assets/la_catedral_site_2019.jpg') as im:
            self.assertEqual(im.size,(1919,886))
        self.assertIn('2019',h.TXT['site_date'])
        self.assertIn('Stefanomione',h.TXT['photo_credit'])
        self.assertIn('CC BY-SA 4.0',h.TXT['photo_credit'])
    def test_no_false_pbs_attribution_for_comfort(self):
        self.assertIn('AMUSING PLANET',h.TXT['comfort_credit'])
        self.assertNotIn('FRONTLINE',h.TXT['comfort_credit'])
    def test_camera_looks_at_center_at_various_resolutions(self):
        for width,height in [(1920,1080),(960,540),(640,480)]:
            cam=Camera((8,-10,12),(1,2,.5),43,width,height)
            np.testing.assert_allclose(cam.project([(1,2,.5)])[0,:2],[width/2,height/2],atol=1e-8)
    def test_height_parallax(self):
        cam=h.camera(6.5);p=cam.project([(0,0,0),(0,0,1)])
        self.assertGreater(np.linalg.norm(p[0,:2]-p[1,:2]),25)
    def test_paper_readable_inside_frame(self):
        for u in np.linspace(0,1,12):
            cam=Camera([.35-.2*u,-9.6+.25*u,13.6-.35*u],[0,0,0],41)
            # Full text-column extent, excluding deliberate paper-stack edge overlap.
            q=cam.project([(-4.4,2.9,.1),(4.4,2.9,.1),(4.4,-2.8,.1),(-4.4,-2.8,.1)])
            self.assertTrue(np.all(q[:,0]>25) and np.all(q[:,0]<h.W-25))
            self.assertTrue(np.all(q[:,1]>20) and np.all(q[:,1]<h.H-20))
    def test_continuous_camera_within_both_model_shots(self):
        for a,b in [(5.45,11.3),(15,29.95)]:
            prev=None
            for t in np.arange(a,b,1/24):
                cam=h.camera(t);p=cam.project([(0,-2,.5),(2.8,.4,.9)])[:,:2]
                self.assertTrue(np.isfinite(p).all())
                if prev is not None:self.assertLess(np.max(np.linalg.norm(p-prev,axis=1)),20)
                prev=p
    def test_gate_and_figure_actually_change_geometry(self):
        closed=h.world_scene(17);opened=h.world_scene(21)
        self.assertGreater(len(opened.faces),len(closed.faces))
        self.assertTrue(any(not np.allclose(a[0],b[0]) for a,b in zip(closed.lines,opened.lines)))
    def test_shared_oriented_cylinder_and_depth_render(self):
        w=World();cylinder(w,(0,0,0),(1,1,1),.1,(150,150,150))
        self.assertEqual(len(w.faces),14)
        im=Image.new('RGB',(400,300));cam=Camera((4,-5,4),(0,0,0),43,400,300)
        self.assertIs(w.render(im,cam),im)
        self.assertGreater(np.asarray(im).max(),0)

if __name__=='__main__':unittest.main()
