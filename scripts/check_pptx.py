"""Inspect native text and references, or check whether saved evidence is stale."""
import argparse
import json
import sys
import zipfile
from pathlib import Path
from xml.etree.ElementTree import ParseError

from pptx_audit import inspect_pptx, sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pptx', type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--requirements', type=Path)
    mode.add_argument('--check-report', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        # Reports must never overwrite input artifacts.
        inputs = [p.resolve() for p in (args.pptx, args.requirements, args.check_report) if p]
        if args.output and args.output.resolve() in inputs:
            raise ValueError('Report output must differ from input files')
        if args.check_report:
            prior = json.loads(args.check_report.read_text(encoding='utf-8-sig'))
            digest = prior.get('pptx_sha256') if isinstance(prior, dict) else None
            current = sha256(args.pptx)
            result = {'matches_pptx': digest == current, 'pptx_sha256': current,
                      'visual_verified': False,
                      'note': 'Hash equality detects changes, not authenticity or visual correctness'}
            code = 0 if result['matches_pptx'] else 1
        else:
            requirements = json.loads(args.requirements.read_text(encoding='utf-8-sig')) if args.requirements else None
            result = inspect_pptx(args.pptx, requirements)
            if args.requirements:
                result['requirements_sha256'] = sha256(args.requirements)
            code = 0 if result['structural_ok'] else 1
        rendered = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            args.output.write_text(rendered + '\n', encoding='utf-8')
        print(rendered)
        return code
    except (OSError, ValueError, KeyError, ParseError, zipfile.BadZipFile, RuntimeError) as exc:
        print(json.dumps({'error': str(exc), 'visual_verified': False}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
