"""Mechanical regression checks. Passing cannot certify creative quality."""
import unittest,json,sys,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'engine/runtime'))
from production_policy import enforce_display,enforce_design
from documentary_materials import material_errors
from speech_edit import tighten
P=ROOT/'engine/projects/escobar_intro5';plan=json.loads((P/'edit_plan.json').read_text());materials=json.loads((P/'MATERIALS.json').read_text())
class NewSequenceTests(unittest.TestCase):
 def test_source_and_display_gates(self):
  d=json.loads((P/'display_manifest.json').read_text());enforce_display(d);enforce_design(d['design']);self.assertEqual(material_errors(materials),[])
 def test_timeline_contiguous(self):
  self.assertEqual(plan['shots'][0]['first'],0);self.assertEqual(plan['shots'][-1]['last'],plan['frames'])
  for a,b in zip(plan['shots'],plan['shots'][1:]):self.assertEqual(a['last'],b['first'])
 def test_speech_never_overlaps(self):
  for a,b in zip(plan['audio'],plan['audio'][1:]):self.assertGreaterEqual(b['start'],a['end']);self.assertLess(b['start']-a['end'],.08)
 def test_original_voice_preserved(self):
  original=ROOT/'engine/projects/escobar_hook30/assets/narrator_approved.mp3';self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(),'523220dab1465d8958a24345978de76982953396e05b9bcf7ed012da44c7485d')
 def test_new_takes_are_not_time_stretched(self):
  a=json.loads((P/'voice_edit_audit.json').read_text())
  for key,row in a.items():
   self.assertIn('no time stretching',row['method']);self.assertEqual(row['source_sha256'],hashlib.sha256((P/'voice'/f'{key}_take1.wav').read_bytes()).hexdigest())
   for word in row['words']:self.assertAlmostEqual(word['end']-word['start'],word['edited_end']-word['edited_start'],places=6)
  self.assertGreater(a['hook']['wpm'],175);self.assertLess(a['industry']['wpm'],155);self.assertGreater(a['close']['wpm'],180)
 def test_quiet_pause_target_cannot_silently_conflict_with_word_guards(self):
  with self.assertRaises(ValueError):tighten(np.zeros(48000),[],target=.13)
 def test_no_repeated_stills_or_failed_name_motif(self):
  still=[s['asset']for s in plan['shots']if s['kind'] in ['image','depth']];self.assertEqual(len(still),4);self.assertEqual(len(set(still)),4)
  self.assertFalse(any(s['kind']in ['press_word_match','word_card','press']for s in plan['shots']))
 def test_source_voice_provenance_not_invented_broadcasters(self):
  self.assertEqual(materials['source_programmes_used'],3);self.assertEqual(materials['source_voice_programmes_used'],1);self.assertEqual(materials['independent_interview_contexts'],2)
  self.assertEqual(len([a for a in materials['assets']if a['kind']=='interview']),2)
 def test_cash_reveal_is_prompt_and_synchronized(self):
  c=next(c for c in plan['audio']if c['id']=='cash');v=next(s for s in plan['shots']if s['id']=='cash_reveal');self.assertAlmostEqual(v['start']-c['start'],10/24,places=5);self.assertAlmostEqual(v['source_in'],10/24,places=5)
 def test_source_logos_not_pushed_or_removed(self):
  for s in plan['shots']:
   if s.get('watermark'):self.assertFalse(s.get('push'))
  self.assertTrue(next(s for s in plan['shots']if s['id']=='public_image')['freeze_tail'])
 def test_local_effects_under_music(self):
  for row in json.loads((P/'mix_audit.json').read_text())['per_event_effects']:self.assertLessEqual(row['relative_to_local_music_db'],-7)
 def test_no_automatic_approval_or_claimed_listening(self):
  a=json.loads((P/'encoded_review.json').read_text());self.assertFalse(a['manual_listening_claimed']);self.assertFalse(materials['source_rights_cleared']);self.assertEqual(a['frame_counts'],{'half':67,'join':49,'motion':107})
if __name__=='__main__':unittest.main()
