"""Read-only source/plan checks. Inventories and review claims still need human/agent inspection."""
import hashlib
import json
import math
from collections import Counter

from validate_state import safe_path


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_relative(root, value):
    if not safe_path(value):
        raise ValueError('fidelity paths must be project-relative')
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('fidelity file missing or outside project')
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(value, dict):
        raise ValueError('fidelity file must contain an object')
    return path, value


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def elements(data, label):
    """The same visual contract is used for the source and intended reconstruction."""
    items = data.get('elements')
    if not isinstance(items, list) or not items:
        raise ValueError(f'{label}: nonempty elements required')
    result = {}
    for item in items:
        if not isinstance(item, dict) or not nonempty(item.get('id')):
            raise ValueError(f'{label}: element ID required')
        key, kind, props = item['id'], item.get('kind'), item.get('properties')
        if key in result or kind not in {'text', 'connector', 'artwork', 'background', 'shape'}:
            raise ValueError(f'{label}: duplicate ID or invalid element kind: {key}')
        if not isinstance(props, dict) or not props:
            raise ValueError(f'{label}: properties required: {key}')
        bounds = props.get('bounds')
        if (not isinstance(bounds, list) or len(bounds) != 4
                or not all(type(v) in (int, float) and math.isfinite(v) for v in bounds)
                or min(bounds[2:]) < 0 or max(bounds[2:]) == 0
                or (kind not in {'connector', 'shape'} and min(bounds[2:]) == 0)):
            raise ValueError(f'{label}: finite [x,y,width,height] bounds required: {key}')
        if kind == 'text' and not nonempty(props.get('text')):
            raise ValueError(f'{label}: literal text required: {key}')
        if kind == 'connector' and not all(nonempty(props.get(p)) for p in ('from', 'to', 'route', 'arrowheads')):
            raise ValueError(f'{label}: connector endpoints, route and arrowheads required: {key}')
        result[key] = item
    if not any(item['kind'] == 'background' for item in items):
        raise ValueError(f'{label}: background must be inventoried')
    for item in items:
        if item['kind'] == 'connector':
            if any(item['properties'][end] not in result for end in ('from', 'to')):
                raise ValueError(f'{label}: connector references missing element: {item["id"]}')
    return result


def compare(source, plan):
    before, after = elements(source, 'source'), elements(plan, 'plan')
    if source.get('canvas') != plan.get('canvas'):
        return ['source canvas changed; preserve the source aspect ratio and coordinate system']
    changes = plan.get('changes', [])
    if not isinstance(changes, list):
        raise ValueError('plan changes must be an array (empty for faithful reconstruction)')
    allowed, errors = {}, []
    for change in changes:
        if not isinstance(change, dict) or not nonempty(change.get('element_id')):
            raise ValueError('change element_id required')
        key, authorization = change['element_id'], change.get('authorization')
        if key in allowed:
            errors.append(f'{key}: duplicate change authorization')
        allowed[key] = change
        if (not isinstance(authorization, dict)
                or authorization.get('kind') != 'explicit_change_request'
                or not all(nonempty(authorization.get(k)) for k in ('user_text', 'evidence'))):
            errors.append(f'{key}: explicit scoped user change request required; design approval is insufficient')
        if ('before' not in change or 'after' not in change
                or change.get('before') != before.get(key) or change.get('after') != after.get(key)):
            errors.append(f'{key}: change scope does not match exact source and planned element')
    for key in sorted(before.keys() | after.keys() | allowed.keys()):
        if before.get(key) != after.get(key):
            if key not in allowed:
                errors.append(f'{key}: unauthorized source change (addition, deletion or modified properties)')
        elif key in allowed:
            errors.append(f'{key}: unused change authorization')
    return errors


def inspect_fidelity(state, slide_id, root):
    """Return fingerprints plus plan for downstream coverage and source-comparison checks."""
    slide = next((s for s in state['slides'] if s['id'] == slide_id), None)
    if slide is None:
        raise ValueError('unknown slide')
    contract = slide.get('reconstruction')
    if not isinstance(contract, dict):
        raise ValueError('source inventory and reconstruction plan required; legacy states are not fidelity-verified')
    source_path, source = load_relative(root, contract.get('source'))
    plan_path, plan = load_relative(root, contract.get('plan'))
    source_hash = sha256(source_path)
    if contract.get('source_sha256') != source_hash:
        raise ValueError('source inventory lock missing or stale; do not rewrite the baseline to match output')
    design = slide.get('design')
    if not isinstance(design, dict) or not safe_path(design.get('image')):
        raise ValueError('source image required')
    image = (root / design['image']).resolve()
    if not image.is_relative_to(root.resolve()) or not image.is_file():
        raise ValueError('source image missing or outside project')
    image_hash = sha256(image)
    if source.get('image_sha256') != image_hash:
        raise ValueError('source inventory does not match current image')
    if plan.get('source_sha256') != source_hash:
        raise ValueError('plan references a missing/stale source inventory')
    canvas = source.get('canvas')
    if (not isinstance(canvas, dict)
            or not all(type(canvas.get(k)) in (int, float) and math.isfinite(canvas[k]) and canvas[k] > 0
                       for k in ('width', 'height'))):
        raise ValueError('source canvas width and height required')
    fingerprint = {'image_sha256': image_hash, 'source_sha256': source_hash,
                   'plan_sha256': sha256(plan_path)}
    return compare(source, plan), fingerprint, plan


def fidelity_errors(state, slide_id, root):
    try:
        return inspect_fidelity(state, slide_id, root)[0]
    except (ValueError, OSError, TypeError, KeyError) as exc:
        return [str(exc)]


def delivery_fidelity_errors(state, audit, evidence, root):
    """Require source-bound visual review and native source text, not only output-derived lists."""
    from workflow import design_approval_errors
    if len(state['slides']) != len(audit['slides']):
        return ['fidelity state must match delivered slide count and order']
    errors = []
    pages = evidence.get('pages', [])
    if not isinstance(pages, list):
        pages = []
    for index, slide in enumerate(state['slides'], 1):
        try:
            errors.extend(f'Slide {index}: {issue}' for issue in design_approval_errors(state, slide['id'], root))
            issues, fingerprint, plan = inspect_fidelity(state, slide['id'], root)
            errors.extend(f'Slide {index}: {issue}' for issue in issues)
            record = next((p for p in pages if isinstance(p, dict) and p.get('slide') == index), {})
            review = record.get('source_comparison')
            if (not isinstance(review, dict) or review.get('status') != 'passed'
                    or any(review.get(k) != v for k, v in fingerprint.items())
                    or review.get('preview_sha256') != record.get('preview_sha256')
                    or not all(nonempty(review.get(k)) for k in ('reviewer', 'reviewed_at', 'evidence'))):
                errors.append(f'Slide {index}: actual source-to-render comparison missing or stale')
            paragraphs = audit['slides'][index-1].get('paragraphs', [])
            expected_text = Counter()
            for item in plan['elements']:
                if item['kind'] == 'text':
                    for line in item['properties']['text'].splitlines():
                        if line.strip():
                            expected_text[line] += 1
            actual_text = Counter(line for paragraph in paragraphs for line in paragraph.splitlines() if line.strip())
            if expected_text - actual_text:
                errors.append(f'Slide {index}: source text missing or changed in native output: {dict(expected_text - actual_text)}')
            if actual_text - expected_text:
                errors.append(f'Slide {index}: unplanned native text or duplicate labels: {dict(actual_text - expected_text)}')
        except (ValueError, OSError, TypeError, KeyError) as exc:
            errors.append(f'Slide {index}: {exc}')
    return errors
