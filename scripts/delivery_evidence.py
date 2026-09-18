"""Validate evidence consistency, never create or authenticate visual-review claims."""
from pathlib import Path
from pptx_audit import sha256


def scene_errors(audit, scene):
    errors = []
    declared = scene.get('image_only_assets')
    if not isinstance(declared, list):
        return ['Scene must declare image_only_assets (empty only when no embedded artwork exists)']
    expected = {(i, part) for i, slide in enumerate(audit['slides'], 1)
                for part in slide.get('media_parts', [])}
    mapped = set()
    for asset in declared:
        if (not isinstance(asset, dict) or type(asset.get('slide')) is not int
                or not isinstance(asset.get('part'), str) or not asset.get('role')):
            errors.append('Each image-only asset needs slide (1-based), package part and semantic role')
            continue
        pair = (asset['slide'], asset['part'])
        if pair in mapped:
            errors.append(f'Duplicate scene asset mapping: {pair}')
        mapped.add(pair)
    if expected - mapped:
        errors.append(f'Undeclared embedded artwork: {sorted(expected - mapped)}')
    if mapped - expected:
        errors.append(f'Scene artwork absent from output: {sorted(mapped - expected)}')
    return errors


def evidence_errors(audit, evidence, root):
    errors = []
    if evidence.get('pptx_sha256') != audit['pptx_sha256']:
        errors.append('Render evidence missing or stale PPTX hash')
    renderer = evidence.get('renderer', {})
    if (not isinstance(renderer, dict) or not renderer.get('name')
            or not renderer.get('version') or not renderer.get('operation_evidence')):
        errors.append('Renderer name, version (or unknown) and actual export evidence required')
    pages = evidence.get('pages')
    if not isinstance(pages, list):
        return errors + ['No page render/review records']
    seen = set()
    for record in pages:
        if not isinstance(record, dict):
            errors.append('Page record must be an object')
            continue
        index = record.get('slide')
        if type(index) is not int or index < 1 or index > len(audit['slides']) or index in seen:
            errors.append('Invalid or duplicate rendered slide number')
            continue
        seen.add(index)
        if record.get('render_status') != 'succeeded':
            errors.append(f'Slide {index}: render not successful')
        preview = record.get('preview')
        if not isinstance(preview, str) or not preview:
            errors.append(f'Slide {index}: missing preview path')
            continue
        path = (root / preview).resolve()
        if Path(preview).is_absolute() or not path.is_relative_to(root.resolve()) or not path.is_file():
            errors.append(f'Slide {index}: missing or out-of-project preview')
            continue
        digest = sha256(path)
        if path.stat().st_size == 0 or digest != record.get('preview_sha256'):
            errors.append(f'Slide {index}: empty or changed preview')
        review = record.get('visual_review', {})
        if (not isinstance(review, dict) or review.get('status') != 'passed'
                or review.get('preview_sha256') != digest
                or not review.get('evidence') or not review.get('reviewer')
                or not review.get('reviewed_at')):
            errors.append(f'Slide {index}: missing/stale actual visual review record')
    if seen != set(range(1, len(audit['slides']) + 1)):
        errors.append('Render/review records do not cover every slide')
    return errors


def assess(audit, scene, evidence, root):
    issues = list(audit['errors']) + scene_errors(audit, scene)
    if not audit['coverage_checked']:
        issues.append('Content inventory was not checked')
    issues.extend(evidence_errors(audit, evidence, root))
    return {'schema_version': 1, 'delivery_status': 'draft' if issues else 'evidence_complete',
            'pptx_sha256': audit['pptx_sha256'], 'issues': issues,
            'shape_count': sum(p['shape_count'] for p in audit['slides']),
            'picture_count': sum(p['picture_count'] for p in audit['slides']),
            'embedded_artwork_present': any(p.get('media_parts') for p in audit['slides']),
            'note': 'Checks evidence consistency only. Does not view images, certify visual quality or grant user approval.'}
