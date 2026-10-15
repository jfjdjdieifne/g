"""Geometry / camera / text gates; cannot certify artistic quality."""
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import ww2demo_v3 as v

class DesignGates(unittest.TestCase):
    def test_geography(self):
        self.assertIn('BRA',v.WORLD)
        self.assertTrue(v.contains('COL',v.MED))
        self.assertTrue(v.contains('USA',v.MIA))
        self.assertFalse(v.contains('COL',(-83,16)))
        for start,control in [((-74.6,9.3),(-74.3,7.5)),((-76.4,5.2),(-76.5,6.4)),((-74.2,5.2),(-74.1,6.2))]:
            self.assertTrue(all(v.contains('COL',p) for p in v.bezier(start,v.MED,control)))
    def test_camera_no_resets(self):
        positions=[v.point_at(*v.MED,v.camera(n/v.FPS)) for n in range(v.DUR*v.FPS)]
        speed=[math.dist(a,b) for a,b in zip(positions,positions[1:])]
        self.assertLess(max(speed),15)
        for x,y in positions:
            self.assertTrue(60<x<v.W-60)
            self.assertTrue(100<y<v.H-100)
    def test_arabic_layer_not_empty(self):
        for s in ['ميديين','ميامي','من ميديين، امتدت الشبكة','١٩٩٣ · كولومبيا']:
            im=v.text_layer(s,48)
            box=im.getchannel('A').getbbox()
            self.assertIsNotNone(box)
            self.assertGreater(box[2]-box[0],50)
            self.assertLess(box[2],im.width)
    def test_atlas_inverse_projection(self):
        for n in range(v.DUR*v.FPS):
            cam=v.camera(n/v.FPS)
            lon,lat,span,_=cam
            ratio=v.AK/(v.W/span)
            ax,ay=v.atlas_xy(lon,lat)
            x,y=v.point_at(*v.MED,cam)
            self.assertAlmostEqual(ax+(x-v.W/2)*ratio,v.atlas_xy(*v.MED)[0])
            self.assertAlmostEqual(ay+(y-v.H/2)*ratio,v.atlas_xy(*v.MED)[1])

if __name__=='__main__': unittest.main()
