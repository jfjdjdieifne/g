"""Structural regression only. These tests cannot certify professional art."""
import inspect
import json
from pathlib import Path
import sys
import unittest
import numpy as np

TOOLS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TOOLS))
import escobar_hook30_revision2 as revision


class RevisedHookStructure(unittest.TestCase):
    def test_complete_contiguous_model_timeline(self):
        shots=revision.scene.SHOTS
        self.assertEqual(shots[0]['start'],7.6)
        self.assertEqual(shots[-1]['end'],30)
        for a,b in zip(shots,shots[1:]):self.assertEqual(a['end'],b['start'])
        for shot in shots:
            self.assertGreater(shot['end'],shot['start'])
            for t in [shot['start'],(shot['start']+shot['end'])/2,shot['end']]:
                cam=revision.scene.shot_camera(shot,t)
                self.assertTrue(np.isfinite(cam.eye).all())
                np.testing.assert_allclose(cam.R@cam.R.T,np.eye(3),atol=1e-10)

    def test_staging_contains_real_geometry_not_cards(self):
        world=revision.scene.build_world()
        self.assertGreater(len(world.faces),1500)
        self.assertGreater(len(world.lines),200)
        for pts,col,_,_ in world.faces:
            self.assertTrue(np.isfinite(pts).all())
            self.assertEqual(len(col),3)
            self.assertTrue(all(0<=v<=255 for v in col))

    def test_no_fabricated_escape_actor_animation(self):
        self.assertEqual(list(inspect.signature(revision.scene.build_world).parameters),['detail'])
        self.assertFalse(inspect.signature(revision.scene.build_world).parameters['detail'].default)
        review=json.loads((revision.PROFILE/'editorial_review.json').read_text())
        self.assertIn('not a surveyed floorplan',review['model_honesty'])
        self.assertFalse(review['user_approved'])
        self.assertFalse(review['publication_license_obtained'])
        self.assertEqual(review['voice_sha256'],'523220dab1465d8958a24345978de76982953396e05b9bcf7ed012da44c7485d')

    def test_legacy_rejected_cut_remains_blocked(self):
        parent=json.loads((revision.PROJECT/'editorial_review.json').read_text())
        self.assertTrue(parent['production_blocked'])
        self.assertEqual(parent['verdict'],'rejected_by_user')
        source=json.loads((revision.PROJECT/'archive_research/official_source_evidence.json').read_text())
        self.assertEqual(source['source']['original_air_date'],'1992-11-12')
        self.assertFalse(source['rights']['rights_cleared'])


if __name__=='__main__':unittest.main()
