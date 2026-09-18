"""Synthetic behavioral checks for source preservation, not visual-understanding tests."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from fidelity import compare, delivery_fidelity_errors, fidelity_errors, inspect_fidelity
from fidelity_fixtures import install_fixture
from workflow import design_fingerprint, reconstruction_errors
from validate_state import generation_errors


class FidelityTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.state = json.loads((Path(__file__).parents[1] / 'assets/project-state.example.json').read_text())
        self.slide = self.state['slides'][0]
        self.sid = self.slide['id']
        (self.root / 'image.png').write_bytes(b'SYNTHETIC source image')
        (self.root / 'brief.json').write_text('{}')
        self.slide.update(status='reference-ready', design={
            'revision': 1, 'image': 'image.png', 'brief': 'brief.json', 'approval': None})
        self.source, self.plan = install_fixture(self.root, self.slide)
        self.slide['design']['approval'] = dict(design_fingerprint(self.state, self.sid, self.root),
                                               user_text='SYNTHETIC yes', evidence='SYNTHETIC design approval')

    def save_plan(self):
        (self.root / 'plan.json').write_text(json.dumps(self.plan), encoding='utf-8')

    def check(self):
        self.save_plan()
        return fidelity_errors(self.state, self.sid, self.root)

    def authorize(self, before, after):
        self.plan['changes'].append({'element_id': before['id'] if before else after['id'],
                                     'before': copy.deepcopy(before), 'after': copy.deepcopy(after),
                                     'authorization': {'kind': 'explicit_change_request',
                                                       'user_text': 'SYNTHETIC exact change request',
                                                       'evidence': 'SYNTHETIC test only'}})

    def test_faithful_plan_passes(self):
        self.assertEqual(self.check(), [])
        self.assertEqual(reconstruction_errors(self.state, self.sid, self.root), [])

    def test_source_suspicions_do_not_authorize_changes_or_block_copy(self):
        self.plan['observations'] = ['Arrow seems illogical; typo suspected']
        self.assertEqual(self.check(), [])
        self.plan['elements'][3]['properties']['route'] = 'straight horizontal rows'
        self.assertTrue(self.check())

    def test_unrequested_visual_and_text_changes_block(self):
        cases = [(1, 'text', 'Improved wording'), (1, 'size', 24),
                 (1, 'bounds', [70, 50, 300, 50]), (0, 'fill', 'white'),
                 (0, 'texture', 'none'), (2, 'appearance', 'simplified icon'),
                 (3, 'route', 'straight'), (3, 'arrowheads', 'source'), (3, 'to', 'background')]
        original = copy.deepcopy(self.plan)
        for index, prop, value in cases:
            with self.subTest(prop=prop):
                self.plan = copy.deepcopy(original)
                self.plan['elements'][index]['properties'][prop] = value
                self.assertTrue(self.check())

    def test_secondary_caption_removal_and_new_reading_label_block(self):
        caption = {'id': 'secondary', 'kind': 'text', 'properties': {'bounds': [20, 800, 500, 40], 'text': 'Generated decoration caption'}}
        self.plan['elements'].append(caption)
        self.assertTrue(self.check())
        self.plan['elements'].pop()
        self.plan['elements'].pop(3)
        self.assertTrue(self.check())

    def test_blank_artwork_bubble_is_not_text_preservation(self):
        self.plan['elements'][1]['properties']['text'] = ' '
        self.assertTrue(self.check())

    def test_explicit_exact_edit_passes(self):
        before = copy.deepcopy(self.plan['elements'][1])
        self.plan['elements'][1]['properties']['text'] = 'User replacement'
        self.authorize(before, self.plan['elements'][1])
        self.assertEqual(self.check(), [])

    def test_change_authorization_does_not_expand_scope(self):
        self.test_explicit_exact_edit_passes()
        self.plan['elements'][1]['properties']['bounds'][0] += 10
        self.assertTrue(self.check())

    def test_design_approval_is_not_change_authorization(self):
        before = copy.deepcopy(self.plan['elements'][1])
        self.plan['elements'][1]['properties']['text'] = 'Assistant correction'
        self.authorize(before, self.plan['elements'][1])
        self.plan['changes'][0]['authorization'] = self.slide['design']['approval']
        self.assertTrue(self.check())

    def test_explicit_addition_and_deletion(self):
        removed = self.plan['elements'].pop(3)
        self.authorize(removed, None)
        self.assertEqual(self.check(), [])
        added = {'id': 'new', 'kind': 'text', 'properties': {'bounds': [0, 0, 100, 30], 'text': 'User addition'}}
        self.plan['elements'].append(added)
        self.authorize(None, added)
        self.assertEqual(self.check(), [])

    def test_unrelated_or_unused_authorization_blocks(self):
        self.authorize(self.plan['elements'][1], self.plan['elements'][1])
        self.assertTrue(self.check())

    def test_duplicate_authorization_blocks(self):
        self.test_explicit_exact_edit_passes()
        self.plan['changes'].append(copy.deepcopy(self.plan['changes'][0]))
        self.assertTrue(self.check())

    def test_missing_inventory_blocks_existing_production_and_artwork_gates(self):
        del self.slide['reconstruction']
        self.assertTrue(reconstruction_errors(self.state, self.sid, self.root))
        self.assertTrue(generation_errors(self.state, self.sid, 'artwork', self.root))

    def test_changed_source_lock_blocks(self):
        self.source['elements'][1]['properties']['text'] = 'Rewritten baseline'
        (self.root / 'source.json').write_text(json.dumps(self.source))
        self.assertTrue(self.check())

    def test_changed_source_image_blocks(self):
        (self.root / 'image.png').write_bytes(b'Changed source')
        self.assertTrue(self.check())

    def test_stale_plan_source_hash_blocks(self):
        self.plan['source_sha256'] = 'old'
        self.assertTrue(self.check())

    def test_outside_inventory_paths_block(self):
        for value in ('../source.json', '/source.json', 'C:/source.json'):
            self.slide['reconstruction']['source'] = value
            self.assertTrue(self.check())

    def test_background_and_connector_contracts_are_required(self):
        for change in ('background', 'endpoint', 'route'):
            plan = copy.deepcopy(self.plan)
            if change == 'background':
                plan['elements'].pop(0)
            elif change == 'endpoint':
                plan['elements'][3]['properties']['to'] = 'missing'
            else:
                del plan['elements'][3]['properties']['route']
            with self.assertRaises(ValueError):
                compare(self.source, plan)

    def test_nonfinite_geometry_and_malformed_records_block(self):
        for value in (True, float('nan'), float('inf'), '10'):
            self.plan['elements'][0]['properties']['bounds'][0] = value
            self.assertTrue(self.check())
        self.plan['elements'] = [None]
        self.assertTrue(self.check())

    def test_canvas_cannot_be_silently_changed(self):
        self.plan['canvas']['width'] = 1200
        self.assertTrue(self.check())

    def delivery(self):
        _, fingerprint, _ = inspect_fidelity(self.state, self.sid, self.root)
        review = dict(fingerprint, status='passed', preview_sha256='SYNTHETIC preview',
                      reviewer='TEST', reviewed_at='TEST', evidence='SYNTHETIC comparison')
        evidence = {'pages': [{'slide': 1, 'preview_sha256': 'SYNTHETIC preview', 'source_comparison': review}]}
        audit = {'slides': [{'paragraphs': ['SYNTHETIC caption']}]}
        return audit, evidence

    def test_source_bound_delivery_comparison_passes(self):
        audit, evidence = self.delivery()
        self.assertEqual(delivery_fidelity_errors(self.state, audit, evidence, self.root), [])

    def test_source_comparison_cannot_replace_design_approval(self):
        audit, evidence = self.delivery()
        self.slide['design']['approval'] = None
        self.assertTrue(delivery_fidelity_errors(self.state, audit, evidence, self.root))

    def test_generic_visual_pass_does_not_prove_fidelity(self):
        audit, evidence = self.delivery()
        evidence['pages'][0]['visual_review'] = {'status': 'passed'}
        del evidence['pages'][0]['source_comparison']
        self.assertTrue(delivery_fidelity_errors(self.state, audit, evidence, self.root))

    def test_stale_source_comparison_or_preview_blocks(self):
        for key in ('image_sha256', 'source_sha256', 'plan_sha256', 'preview_sha256'):
            audit, evidence = self.delivery()
            evidence['pages'][0]['source_comparison'][key] = 'stale'
            self.assertTrue(delivery_fidelity_errors(self.state, audit, evidence, self.root))

    def test_delivery_checks_original_text_not_only_output_inventory(self):
        audit, evidence = self.delivery()
        audit['slides'][0]['paragraphs'] = ['Replacement looks good']
        self.assertTrue(delivery_fidelity_errors(self.state, audit, evidence, self.root))

    def test_delivery_count_mismatch_blocks(self):
        audit, evidence = self.delivery()
        audit['slides'].append({})
        self.assertTrue(delivery_fidelity_errors(self.state, audit, evidence, self.root))

    def test_added_or_duplicate_native_labels_block(self):
        for text in ('接上行', 'SYNTHETIC caption', 'SYNTHETIC caption corrected'):
            audit, evidence = self.delivery()
            audit['slides'][0]['paragraphs'].append(text)
            self.assertTrue(delivery_fidelity_errors(self.state, audit, evidence, self.root))

    def test_zero_height_horizontal_connector_is_valid(self):
        source = copy.deepcopy(self.source)
        plan = copy.deepcopy(self.plan)
        source['elements'][3]['properties']['bounds'] = [100, 100, 300, 0]
        plan['elements'][3]['properties']['bounds'] = [100, 100, 300, 0]
        self.assertEqual(compare(source, plan), [])

    def test_cli_is_readonly_and_existing_alias_cannot_bypass(self):
        state_path = self.root / 'state.json'
        state_path.write_text(json.dumps(self.state))
        original = state_path.read_bytes()
        scripts = Path(__file__).parent
        cmd = [sys.executable, str(scripts/'workflow.py'), 'fidelity-check', str(state_path), '--slide', self.sid]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('plan_sha256', json.loads(result.stdout)['fidelity'])
        self.plan['elements'][3]['properties']['route'] = 'assistant reroute'
        self.save_plan()
        for command in (cmd, [sys.executable, str(scripts/'validate_state.py'), str(state_path), '--allow-produce', self.sid]):
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(original, state_path.read_bytes())


if __name__ == '__main__':
    unittest.main()
