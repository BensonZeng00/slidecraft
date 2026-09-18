"""Synthetic package tests; these do not simulate PowerPoint rendering."""
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from pptx_audit import inspect_pptx, sha256

P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def fixture(path, missing=False, svg=False):
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('ppt/presentation.xml', f'<p:presentation xmlns:p="{P}" xmlns:r="{R}"><p:sldIdLst><p:sldId id="256" r:id="r2"/><p:sldId id="257" r:id="r1"/></p:sldIdLst><p:sldSz cx="120" cy="90"/></p:presentation>')
        z.writestr('ppt/_rels/presentation.xml.rels', '<Relationships><Relationship Id="r1" Target="slides/slide1.xml"/><Relationship Id="r2" Target="slides/slide2.xml"/></Relationships>')
        for n, body in [(1, '<a:p><a:r><a:t>第二页</a:t></a:r></a:p>'), (2, '<a:p><a:r><a:t>AI </a:t></a:r><a:r><a:t>发展史</a:t></a:r></a:p><a:p><a:r><a:t>独立段落</a:t></a:r></a:p>')]:
            z.writestr(f'ppt/slides/slide{n}.xml', f'<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:sp><p:txBody>{body}</p:txBody></p:sp></p:sld>')
        if missing:
            z.writestr('ppt/slides/_rels/slide2.xml.rels', '<Relationships><Relationship Id="img" Target="../media/missing.png"/></Relationships>')
        if svg:
            z.writestr('ppt/media/icon.svg', '<svg/>')


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / '中文 文件.pptx'
        fixture(self.path)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(Path(__file__).with_name('check_pptx.py')),
                               str(self.path), *map(str, args)], capture_output=True, encoding='utf-8')

    def test_slide_order_and_split_runs(self):
        result = inspect_pptx(self.path, {'slides': [{'required_text': ['AI 发展史']}, {'required_text': ['第二页']}]})
        self.assertTrue(result['structural_ok'])
        self.assertEqual(result['slides'][0]['part'], 'ppt/slides/slide2.xml')
        self.assertFalse(result['visual_verified'])

    def test_no_cross_paragraph_match(self):
        result = inspect_pptx(self.path, {'slides': [{'required_text': ['发展史独立段落']}, {'required_text': []}]})
        self.assertFalse(result['structural_ok'])

    def test_count_mismatch(self):
        self.assertFalse(inspect_pptx(self.path, {'slides': [{'required_text': []}]})['structural_ok'])

    def test_missing_relationship(self):
        fixture(self.path, missing=True)
        self.assertFalse(inspect_pptx(self.path)['structural_ok'])

    def test_svg_warning_not_failure(self):
        fixture(self.path, svg=True)
        result = inspect_pptx(self.path)
        self.assertTrue(result['structural_ok'])
        self.assertTrue(result['warnings'])
        self.assertFalse(result['coverage_checked'])

    def test_stale_report(self):
        report = self.path.with_suffix('.json')
        self.assertEqual(self.run_cli('--output', report).returncode, 0)
        self.assertEqual(self.run_cli('--check-report', report).returncode, 0)
        fixture(self.path, svg=True)
        self.assertEqual(self.run_cli('--check-report', report).returncode, 1)

    def test_source_cannot_be_overwritten(self):
        before = sha256(self.path)
        self.assertEqual(self.run_cli('--output', self.path).returncode, 2)
        self.assertEqual(sha256(self.path), before)

    def test_bad_package_json_error(self):
        self.path.write_bytes(b'not a zip')
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn('error', json.loads(result.stdout))

    def test_invalid_inventory(self):
        with self.assertRaises(ValueError):
            inspect_pptx(self.path, {'slides': 'invalid'})


if __name__ == '__main__':
    unittest.main()
