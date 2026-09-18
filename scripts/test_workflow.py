"""Synthetic gates/geometry tests, not evidence of real user approval."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from workflow import design_fingerprint, preflight, reconstruction_errors
from validate_state import generation_errors
from fidelity_fixtures import install_fixture


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.state = json.loads((Path(__file__).parents[1]/'assets/project-state.example.json').read_text())
        self.sid = self.state['slides'][0]['id']
        self.slide = self.state['slides'][0]
        (self.root/'design.png').write_bytes(b'SYNTHETIC image fixture')
        (self.root/'brief.json').write_text('{"title":"SYNTHETIC"}')
        self.slide.update(status='reference-ready', design={
            'revision':1, 'image':'design.png', 'brief':'brief.json', 'approval':None})
        install_fixture(self.root, self.slide)

    def approve(self):
        self.slide['design']['approval'] = dict(
            design_fingerprint(self.state,self.sid,self.root),
            user_text='SYNTHETIC approval', evidence='TEST ONLY')

    def check(self):
        return reconstruction_errors(self.state,self.sid,self.root)

    def test_unapproved_blocks(self):
        self.assertTrue(self.check())

    def test_matching_approval_passes(self):
        self.approve()
        self.assertEqual(self.check(), [])

    def test_image_change_blocks(self):
        self.approve()
        (self.root/'design.png').write_bytes(b'changed')
        self.assertTrue(self.check())

    def test_brief_change_blocks(self):
        self.approve()
        (self.root/'brief.json').write_text('{}')
        self.assertTrue(self.check())

    def test_revision_change_blocks(self):
        self.approve()
        self.slide['design']['revision'] = 2
        self.assertTrue(self.check())

    def test_no_evidence_blocks(self):
        self.approve()
        self.slide['design']['approval']['evidence'] = ' '
        self.assertTrue(self.check())

    def test_legacy_blocks(self):
        del self.slide['design']
        self.assertTrue(self.check())

    def test_path_escape_blocks(self):
        self.approve()
        for value in ('../design.png','C:/design.png','/design.png'):
            self.slide['design']['image'] = value
            self.assertTrue(self.check())

    def test_resume_waits(self):
        restored = json.loads(json.dumps(self.state))
        self.assertTrue(reconstruction_errors(restored,self.sid,self.root))

    def test_missing_file_blocks(self):
        self.approve()
        (self.root/'design.png').unlink()
        self.assertTrue(self.check())

    def test_artwork_requires_approval(self):
        self.assertTrue(generation_errors(self.state,self.sid,'artwork',self.root))

    def test_artwork_does_not_reset_budget(self):
        self.approve()
        attempts=self.state['generation']['attempts']
        attempts.append({'id':'a','slide_id':self.sid,'outcome':'succeeded','usable':True})
        self.assertEqual(generation_errors(self.state,self.sid,'artwork',self.root),[])
        self.assertTrue(generation_errors(self.state,self.sid))
        for aid in ('b','c'):
            attempts.append({'id':aid,'slide_id':self.sid,'outcome':'failed'})
        self.assertTrue(generation_errors(self.state,self.sid,'artwork',self.root))

    def metrics(self):
        return {'measurement_source':'SYNTHETIC fixture','canvas':{'width':1600,'height':900},
                'texts':[{'id':'title','box':[40,20,500,100], 'measured_width':400,'measured_height':80}]}

    def test_fit(self):
        self.assertEqual(preflight(self.metrics()),[])

    def test_overflow(self):
        data=self.metrics()
        data['texts'][0]['measured_height']=101
        self.assertTrue(preflight(data))

    def test_bounds(self):
        data=self.metrics()
        data['texts'][0]['box'][0]=1500
        self.assertTrue(preflight(data))

    def test_invalid_measurements(self):
        for value in (None,True,float('nan'),-1):
            data=self.metrics()
            data['texts'][0]['measured_width']=value
            with self.assertRaises(ValueError):
                preflight(data)

    def test_empty_metrics_not_pass(self):
        data=self.metrics()
        data['texts']=[]
        with self.assertRaises(ValueError):
            preflight(data)

    def test_duplicate_ids(self):
        data=self.metrics()
        data['texts'].append(copy.deepcopy(data['texts'][0]))
        with self.assertRaises(ValueError):
            preflight(data)

    def test_cli_readonly_and_exit_codes(self):
        state_path=self.root/'state.json'
        state_path.write_text(json.dumps(self.state))
        original=state_path.read_bytes()
        script=str(Path(__file__).with_name('workflow.py'))
        for command, expected in (('fingerprint',0),('reconstruct-check',1)):
            result=subprocess.run([sys.executable,script,command,str(state_path),'--slide',self.sid],capture_output=True,text=True)
            self.assertEqual(result.returncode,expected,result.stderr)
            json.loads(result.stdout)
        self.assertEqual(state_path.read_bytes(),original)
        legacy_cli=str(Path(__file__).with_name('validate_state.py'))
        result=subprocess.run([sys.executable,legacy_cli,str(state_path),'--allow-produce',self.sid],capture_output=True,text=True)
        self.assertEqual(result.returncode,1,result.stderr)
        state_path.write_text('not json')
        result=subprocess.run([sys.executable,script,'fingerprint',str(state_path),'--slide',self.sid],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)


if __name__ == '__main__':
    unittest.main()
