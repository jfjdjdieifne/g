import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'studio/tools'))
import projectctl as ctl


class OnboardingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='studio_test_')
        cls.fixture = Path(cls.temp.name) / 'fixture'
        cls.fixture.mkdir()
        names = [e['path'] for e in ctl.load(ROOT, 'studio/FILE_CATALOG.json')['files']]
        names += ['studio/FILE_CATALOG.json', 'studio/INTEGRITY.json']
        for name in names:
            target = cls.fixture / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.saved = {}

    def tearDown(self):
        for path, data in self.saved.items():
            path.write_bytes(data)
        shutil.rmtree(self.fixture / 'studio/jobs', ignore_errors=True)

    def change(self, name, transform):
        path = self.fixture / name
        self.saved.setdefault(path, path.read_bytes())
        obj = json.loads(path.read_text())
        transform(obj)
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

    def reviewed_fixture_refresh(self):
        """TEST FIXTURE ONLY: update integrity after a simulated authorized status change."""
        name = 'studio/FILE_CATALOG.json'
        catalog = ctl.load(self.fixture, name)
        for entry in catalog['files']:
            path = self.fixture / entry['path']
            entry.update(sha256=ctl.digest(path), bytes=path.stat().st_size)
        self.change(name, lambda obj: obj.update(catalog))
        name = 'studio/INTEGRITY.json'
        self.change(name, lambda obj: obj.update(sha256={p: ctl.digest(self.fixture / p) for p in obj['sha256']}))

    def filled_job(self, allow_production=False):
        if allow_production:
            self.change('studio/CURRENT_STATE.json', lambda d: d.update(production_paused=False, active_task='SYNTHETIC TEST AUTHORIZATION ONLY'))
            self.reviewed_fixture_refresh()
        with contextlib.redirect_stdout(io.StringIO()):
            ctl.init_job(self.fixture, 'fixture_film', 'documentary_explainer', 'Synthetic fixture assignment, never a real video authorization.')
        path = self.fixture / 'studio/jobs/fixture_film/AGENT_ACK.json'
        ack = json.loads(path.read_text())
        for key in ('english_content', 'preserve_approved_history', 'shared_engine_only', 'tests_are_not_art_approval'):
            ack[key] = True
        ack['answers'] = {key: f'SYNTHETIC TEST ONLY: a sufficiently detailed answer for {key}, not proof of artistic comprehension.' for key in ctl.ANSWERS}
        path.write_text(json.dumps(ack))
        return path

    def run_gate(self, stage='planning'):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = ctl.gate(self.fixture, 'fixture_film', stage)
        return code, out.getvalue()

    def test_real_release_offline_doctor(self):
        self.assertEqual(ctl.verify(ROOT), [])

    def test_cold_copy_needs_no_git_or_renderer(self):
        self.assertFalse((self.fixture / '.git').exists())
        self.assertEqual(ctl.verify(self.fixture), [])

    def test_missing_authority_blocks(self):
        path = self.fixture / 'studio/USER_RULES.md'
        self.saved[path] = path.read_bytes()
        path.unlink()
        self.assertTrue(any('Missing' in e for e in ctl.verify(self.fixture)))

    def test_changed_approval_registry_blocks(self):
        self.change('studio/REFERENCE_INDEX.json', lambda d: d['references'][3].update(status='approved'))
        self.assertTrue(any('Modified release file' in e for e in ctl.verify(self.fixture)))

    def test_voice_bytes_not_just_local_number(self):
        path = self.fixture / 'youtube_documentary/engine/voices/approved_voice03/approved_reference.wav'
        self.saved[path] = path.read_bytes()
        path.write_bytes(b'not the approved identity')
        self.assertTrue(any('voice reference hash' in e for e in ctl.verify(self.fixture)))

    def test_existing_pause_blocks_even_filled_form(self):
        self.filled_job()
        code, out = self.run_gate()
        self.assertEqual(code, 1)
        self.assertIn('Production is paused', out)

    def test_unfilled_job_blocks_after_authorization(self):
        self.filled_job(allow_production=True)
        path = self.fixture / 'studio/jobs/fixture_film/AGENT_ACK.json'
        ack = json.loads(path.read_text())
        ack['answers']['causal_explanation'] = 'PASS'
        path.write_text(json.dumps(ack))
        code, out = self.run_gate()
        self.assertEqual(code, 1)
        self.assertIn('causal_explanation', out)

    def test_planning_not_voice_synthesis_permission(self):
        self.filled_job(allow_production=True)
        code, out = self.run_gate()
        self.assertEqual(code, 0, out)
        code, out = self.run_gate('synthesis')
        self.assertEqual(code, 1)
        self.assertIn('Synthesis blocked', out)

    def test_synthesis_requires_recorded_actual_binding_and_evidence(self):
        path = self.filled_job(allow_production=True)
        ack = json.loads(path.read_text())
        ack['voice_resolution'].update(status='resolved_exact_identity', actual_platform_binding='SYNTHETIC_TEST_ONLY', evidence='Synthetic fixture declaration; not real provider identity verification.')
        path.write_text(json.dumps(ack))
        code, out = self.run_gate('synthesis')
        self.assertEqual(code, 0, out)
        self.assertIn('not artistic', out)

    def test_reject_traversal_and_symlink_escape(self):
        for name in ('../escape', '/tmp/escape', 'x/../../escape', 'x\\..\\escape'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                ctl.safe_path(self.fixture, name)
        outside = self.fixture.parent / 'outside'
        outside.mkdir(exist_ok=True)
        link = self.fixture / 'escape_link'
        link.symlink_to(outside, target_is_directory=True)
        try:
            with self.assertRaises(ValueError):
                ctl.safe_path(self.fixture, 'escape_link/file')
        finally:
            link.unlink()

    def test_reject_bad_slug_and_style(self):
        with self.assertRaises(ValueError):
            ctl.job_dir(self.fixture, '../escape')
        with self.assertRaises(ValueError):
            ctl.init_job(self.fixture, 'film', 'last_film_style', 'Synthetic sufficiently specific assignment.')

    def test_do_not_overwrite_existing_job(self):
        self.filled_job()
        with self.assertRaises(FileExistsError):
            ctl.init_job(self.fixture, 'fixture_film', 'pure_explainer', 'Another synthetic assignment that must not overwrite.')

    def test_approval_scopes_and_recovery_gaps_preserved(self):
        refs = {r['id']: r for r in ctl.load(ROOT, 'studio/REFERENCE_INDEX.json')['references']}
        self.assertEqual(refs['escobar_full']['status'], 'approved_preserve')
        self.assertIn('rejected', refs['titan_warning']['status'])
        self.assertIn('unapproved', refs['black_hole']['status'])
        self.assertIn('topic_rejected', refs['phantom_traffic']['status'])
        state = ctl.load(ROOT, 'studio/CURRENT_STATE.json')['titan_v2']
        self.assertFalse(state['final_editable_recovery_verified'])
        self.assertEqual(state['film_bytes'], 95887992)

    def test_legacy_handoff_delegates_does_not_reintroduce_old_state(self):
        source = (ROOT / 'youtube_documentary/tools/handoff.py').read_text()
        self.assertIn('"projectctl.py"', source)
        state = ctl.load(ROOT, 'youtube_documentary/engine/HANDOFF_STATE.json')
        self.assertNotIn('active_new_production', state)
        self.assertEqual(state['authority'], '../../studio/CURRENT_STATE.json')

    def test_catalog_source_and_root_boundaries(self):
        entries = ctl.load(ROOT, 'studio/FILE_CATALOG.json')['files']
        names = {e['path'] for e in entries}
        self.assertIn('START_HERE.md', names)
        self.assertIn('studio/USER_RULES.md', names)
        self.assertFalse(any('trading_bot' in name or '/node_modules/' in name or name.startswith('.git/') for name in names))
        self.assertTrue(any(e['category'] == 'historical_snapshot_not_current_instructions' for e in entries))

    def test_external_audio_is_indexed_not_claimed_in_source_kit(self):
        files = ctl.load(ROOT, 'studio/EXTERNAL_DEPENDENCIES.json')['files']
        self.assertEqual(len(files), 15)
        catalog = {f['path'] for f in ctl.load(ROOT, 'studio/FILE_CATALOG.json')['files']}
        self.assertFalse(any(f['path'] in catalog for f in files))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = ctl.media_check(self.fixture, self.fixture)
        self.assertEqual(code, 1)
        self.assertIn('Missing external audio', out.getvalue())

    def test_package_refuses_tracked_tree_output(self):
        with self.assertRaises(ValueError):
            ctl.package(self.fixture, self.fixture / 'kit.zip')


if __name__ == '__main__':
    unittest.main()
