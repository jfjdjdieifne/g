"""Math/policy gates; professional art direction is not machine-certified."""
import json
import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import ww2demo_v4_depth as v
from production_policy import display_errors, enforce_display, design_errors

class DepthGates(unittest.TestCase):
    def test_english_manifest(self):
        self.assertEqual([],display_errors(v.DISPLAY))
        for text in ['ميديين','COLOMBIA ١٩٩٣','COLOMBIA، 1993','Москва']:
            self.assertTrue(display_errors({'language':'en','texts':{'caption':text}}))
        self.assertEqual([],display_errors({'language':'en','texts':{'city':'MEDELLÍN / 1993'},'note':'ملاحظة داخلية'}))

    def test_general_scene_policy(self):
        self.assertEqual([],design_errors(v.DISPLAY['design']))
        self.assertTrue(design_errors({'unit_of_design':'popup_stack'}))
        self.assertTrue(design_errors({'unit_of_design':'scene','generic_popups':[{}]}))
        self.assertTrue(design_errors({'unit_of_design':'scene','claims_3d':True,'depth_features':['drop_shadow']}))

    def test_route_endpoints_meet_city_surfaces(self):
        demo=v.Demo()
        np.testing.assert_allclose(demo.route[0],v.world(*v.base.MED,v.LAND_Z),atol=1e-8)
        np.testing.assert_allclose(demo.route[-1],v.world(*v.base.MIA,.10),atol=1e-8)

    def test_perspective_plane_agrees_with_xyz(self):
        for t in [0,2.8,4,7.8,10,12,15]:
            cam=v.Camera(t)
            for z in [0,v.LAND_Z,2.9]:
                for loc in [v.base.MED,v.base.MIA,(-73,7)]:
                    uv=np.array([*v.base.atlas_xy(*loc),1])
                    projected=cam.plane_matrix(z)@uv
                    projected=projected[:2]/projected[2]
                    xyz=cam.project([v.world(*loc,z)])[0,:2]
                    np.testing.assert_allclose(projected,xyz,atol=1e-8)

    def test_height_creates_parallax(self):
        cam=v.Camera(1.8)
        lo=cam.project([v.world(*v.base.MED,0)])[0,:2]
        hi=cam.project([v.world(*v.base.MED,1)])[0,:2]
        self.assertGreater(np.linalg.norm(lo-hi),35)

    def test_no_camera_resets_or_atlas_edge_holes(self):
        prev=None
        for i in range(v.FPS*v.DUR):
            cam=v.Camera(i/v.FPS)
            xyz=cam.project([v.world(*v.base.MED,v.LAND_Z)])[0,:2]
            if prev is not None:self.assertLess(np.linalg.norm(xyz-prev),18)
            prev=xyz
            self.assertTrue(70<xyz[0]<v.W-70 and 70<xyz[1]<v.H-100)
            inv=np.linalg.inv(cam.plane_matrix(0))
            for x,y in [(0,0),(v.W,0),(0,v.H),(v.W,v.H)]:
                q=inv@[x,y,1];q=q[:2]/q[2]
                self.assertTrue(0<=q[0]<v.base.AW and 0<=q[1]<v.base.AH,(i,q))

    def test_director_propagates_policy_without_rendering_internal_text(self):
        import director
        script={'title':'Internal Arabic notes allowed','scenes':[{'id':'s1','sentences':[{'text':'كولومبيا','intent':['map']}]}]}
        report=director.plan(script,director.load_json(director.TECH_DB)['cards'],director.load_json(director.SOUND_DB),director.vocab_names())
        self.assertEqual(report['production_policy']['language']['on_screen'],'en')
        self.assertFalse(report['render_ready'])
        script['display_manifest']=v.DISPLAY
        report=director.plan(script,director.load_json(director.TECH_DB)['cards'],director.load_json(director.SOUND_DB),director.vocab_names())
        self.assertFalse(report['render_ready'])  # Display alone no longer supplies documentary materials.
        self.assertTrue(report['material_errors'])

if __name__=='__main__':unittest.main()
