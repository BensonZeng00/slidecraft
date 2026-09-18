"""Synthetic evidence tests; no real visual-review claims."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from delivery_evidence import assess
from pptx_audit import sha256
from renderer_probe import discovery, executable_from_command


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        preview = self.root / 'page.png'
        preview.write_bytes(b'SYNTHETIC NOT A REAL RENDER')
        digest = sha256(preview)
        self.audit = {'errors': [], 'pptx_sha256': 'synthetic', 'coverage_checked': True,
                      'slides': [{'shape_count': 2, 'picture_count': 1, 'media_parts': ['ppt/media/a.svg']}]}
        self.scene = {'image_only_assets': [{'slide': 1, 'part': 'ppt/media/a.svg', 'role': 'arrow'}]}
        self.evidence = {'pptx_sha256': 'synthetic',
                         'renderer': {'name': 'synthetic', 'version': 'unknown', 'operation_evidence': 'test fixture'},
                         'pages': [{'slide': 1, 'render_status': 'succeeded', 'preview': 'page.png', 'preview_sha256': digest,
                                    'visual_review': {'status': 'passed', 'preview_sha256': digest,
                                                      'evidence': 'synthetic fixture only', 'reviewer': 'test', 'reviewed_at': 'test'}}]}

    def result(self):
        return assess(self.audit, self.scene, self.evidence, self.root)

    def test_complete_records(self):
        result = self.result()
        self.assertEqual(result['delivery_status'], 'evidence_complete')
        self.assertTrue(result['embedded_artwork_present'])

    def test_no_render_stays_draft(self):
        self.evidence = {}
        self.assertEqual(self.result()['delivery_status'], 'draft')

    def test_render_success_without_review(self):
        del self.evidence['pages'][0]['visual_review']
        self.assertEqual(self.result()['delivery_status'], 'draft')

    def test_changed_pptx(self):
        self.audit['pptx_sha256'] = 'changed'
        self.assertEqual(self.result()['delivery_status'], 'draft')

    def test_changed_preview(self):
        (self.root / 'page.png').write_bytes(b'changed')
        self.assertEqual(self.result()['delivery_status'], 'draft')

    def test_scene_undeclared_image(self):
        self.scene['image_only_assets'] = []
        self.assertIn('Undeclared embedded artwork', ' '.join(self.result()['issues']))

    def test_scene_nonexistent_image(self):
        self.scene['image_only_assets'][0]['part'] = 'ppt/media/other.svg'
        self.assertEqual(self.result()['delivery_status'], 'draft')

    def test_missing_page(self):
        self.audit['slides'].append(copy.deepcopy(self.audit['slides'][0]))
        self.assertEqual(self.result()['delivery_status'], 'draft')

    def test_preview_escape(self):
        self.evidence['pages'][0]['preview'] = '../outside.png'
        self.assertEqual(self.result()['delivery_status'], 'draft')

    def test_native_failure(self):
        self.audit['errors'] = ['missing required text']
        self.assertEqual(self.result()['delivery_status'], 'draft')

    def test_windows_command_paths(self):
        for command in ['"C:\\Program Files\\Office\\POWERPNT.EXE" /AUTOMATION', 'C:\\Program Files\\Office\\POWERPNT.EXE /AUTOMATION']:
            self.assertEqual(executable_from_command(command), r'C:\Program Files\Office\POWERPNT.EXE')

    def test_absent_is_not_detected_not_uninstalled(self):
        with patch('renderer_probe.platform.system', return_value='Linux'), patch('renderer_probe.shutil.which', return_value=None):
            self.assertEqual(discovery()['status'], 'not_detected')

    def test_discovery_does_not_claim_execution(self):
        with patch('renderer_probe.platform.system', return_value='Linux'), patch('renderer_probe.shutil.which', return_value=None):
            result = discovery([self.root / 'page.png'])
            self.assertEqual(result['status'], 'detected_not_tested')


if __name__ == '__main__':
    unittest.main()
