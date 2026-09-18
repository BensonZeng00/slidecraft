"""Recheck PPTX, scene and render/review evidence before choosing delivery wording."""
import argparse
import json
import sys
import zipfile
from pathlib import Path
from xml.etree.ElementTree import ParseError
from delivery_evidence import assess
from pptx_audit import inspect_pptx
from fidelity import delivery_fidelity_errors
from validate_state import validate


def load(path):
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(value, dict):
        raise ValueError(f'Expected a JSON object: {path.name}')
    return value


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('pptx', type=Path)
    p.add_argument('--requirements', type=Path, required=True)
    p.add_argument('--scene', type=Path, required=True)
    p.add_argument('--evidence', type=Path)
    p.add_argument('--state', type=Path, required=True,
                   help='Project state with locked source inventories and reconstruction plans')
    args = p.parse_args()
    try:
        audit = inspect_pptx(args.pptx, load(args.requirements))
        evidence = load(args.evidence) if args.evidence else {}
        result = assess(audit, load(args.scene), evidence,
                        args.evidence.parent if args.evidence else args.pptx.parent)
        state = load(args.state)
        issues = validate(state, args.state.parent)
        if not issues:
            issues = delivery_fidelity_errors(state, audit, evidence, args.state.parent)
        result['issues'].extend(issues)
        result['delivery_status'] = 'draft' if result['issues'] else 'evidence_complete'
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['delivery_status'] == 'evidence_complete' else 1
    except (OSError, ValueError, KeyError, ParseError, zipfile.BadZipFile, RuntimeError) as exc:
        print(json.dumps({'delivery_status': 'draft', 'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
