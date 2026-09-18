"""Synthetic source/plan fixtures shared by gate tests; never real approval evidence."""
import copy
import json
from fidelity import sha256


def install_fixture(root, slide):
    source = {'image_sha256': sha256(root / slide['design']['image']),
              'canvas': {'width': 1600, 'height': 900}, 'elements': [
                  {'id': 'background', 'kind': 'background', 'properties': {
                      'bounds': [0, 0, 1600, 900], 'fill': 'ivory', 'texture': 'paper'}},
                  {'id': 'label', 'kind': 'text', 'properties': {
                      'bounds': [50, 40, 300, 50], 'text': 'SYNTHETIC caption', 'size': 30}},
                  {'id': 'art', 'kind': 'artwork', 'properties': {
                      'bounds': [600, 200, 400, 200], 'appearance': 'original detail'}},
                  {'id': 'arrow', 'kind': 'connector', 'properties': {
                      'bounds': [350, 70, 300, 230], 'from': 'label', 'to': 'art',
                      'route': 'curved via right margin', 'arrowheads': 'target'}}]}
    source_path = root / 'source.json'
    source_path.write_text(json.dumps(source), encoding='utf-8')
    source_hash = sha256(source_path)
    plan = {k: copy.deepcopy(source[k]) for k in ('canvas', 'elements')}
    plan.update(source_sha256=source_hash, changes=[])
    (root / 'plan.json').write_text(json.dumps(plan), encoding='utf-8')
    slide['reconstruction'] = {'source': 'source.json', 'source_sha256': source_hash, 'plan': 'plan.json'}
    return source, plan
