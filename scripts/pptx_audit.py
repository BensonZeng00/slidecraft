"""Read-only, backend-neutral PPTX inspection; not a renderer or OOXML validator."""
import hashlib
import posixpath
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

MAX_UNCOMPRESSED = 256 * 1024 * 1024


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def local(tag):
    return tag.rsplit('}', 1)[-1]


def attribute(element, name):
    return next((v for k, v in element.attrib.items()
                 if k.startswith('{') and local(k) == name), None)


def resolve_part(source, target):
    target = unquote(urlsplit(target).path)
    path = posixpath.normpath(posixpath.join(posixpath.dirname(source), target))
    if target.startswith('/'):
        path = target.lstrip('/')
    if path.startswith('../') or '\\' in path:
        raise ValueError('Relationship target escapes the package')
    return path


def xml(package, name):
    data = package.read(name)
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('DTD/entity declarations are not supported')
    return ET.fromstring(data)


def relationships(package, source):
    name = posixpath.join(posixpath.dirname(source), '_rels',
                         posixpath.basename(source) + '.rels')
    if name not in package.namelist():
        return {}
    return {item.attrib['Id']: item.attrib for item in xml(package, name)}


def required_texts(requirements):
    """Explicit per-slide inventory, never concatenate unrelated paragraphs."""
    if requirements is None:
        return []
    slides = requirements.get('slides') if isinstance(requirements, dict) else None
    if not isinstance(slides, list) or not slides:
        raise ValueError('requirements.slides must be a nonempty array')
    for slide in slides:
        if not isinstance(slide, dict):
            raise ValueError('Each required slide must be an object')
        values = slide.get('required_text')
        if not isinstance(values, list) or any(not isinstance(t, str) or not t for t in values):
            raise ValueError('Each slide needs required_text: array of nonempty strings')
    return slides


def inspect_pptx(path, requirements=None):
    expected = required_texts(requirements)
    errors, warnings, slides = [], [], []
    digest = sha256(path)
    with zipfile.ZipFile(path) as package:
        names = package.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate ZIP member names')
        if sum(i.file_size for i in package.infolist()) > MAX_UNCOMPRESSED:
            raise ValueError('Package exceeds inspection size limit')
        bad = package.testzip()
        if bad:
            raise ValueError(f'ZIP checksum failure: {bad}')
        presentation = xml(package, 'ppt/presentation.xml')
        rels = relationships(package, 'ppt/presentation.xml')
        dimensions = next((e.attrib for e in presentation if local(e.tag) == 'sldSz'), {})
        if any(int(dimensions.get(k, 0)) <= 0 for k in ('cx', 'cy')):
            errors.append('Missing or invalid slide dimensions')
        # Order comes from the presentation, not slide filenames.
        for index, item in enumerate(e for e in presentation.iter() if local(e.tag) == 'sldId'):
            relation = rels.get(attribute(item, 'id'))
            if not relation or relation.get('TargetMode') == 'External':
                raise ValueError('Missing or external slide relationship')
            part = resolve_part('ppt/presentation.xml', relation['Target'])
            root = xml(package, part)
            paragraphs = []
            for body in root.iter():
                if local(body.tag) != 'txBody':
                    continue
                for paragraph in body:
                    if local(paragraph.tag) == 'p':
                        paragraphs.append(''.join(
                            '\n' if local(e.tag) == 'br' else (e.text or '')
                            for e in paragraph.iter() if local(e.tag) in ('t', 'br')))
            missing = []
            if index < len(expected):
                missing = [t for t in expected[index]['required_text']
                           if not any(t in p for p in paragraphs)]
                if missing:
                    errors.append(f'Slide {index + 1}: missing required native text')
            slide_rels = relationships(package, part)
            media_parts = set()
            for rel in slide_rels.values():
                if rel.get('TargetMode') == 'External':
                    warnings.append(f'{part}: external relationship; not fetched')
                elif resolve_part(part, rel['Target']) not in names:
                    errors.append(f'{part}: missing relationship target {rel["Target"]}')
            for node in root.iter():
                embedded = attribute(node, 'embed')
                if embedded and embedded not in slide_rels:
                    errors.append(f'{part}: unresolved embedded asset {embedded}')
                elif embedded and local(node.tag) in ('blip', 'svgBlip'):
                    rel = slide_rels[embedded]
                    if rel.get('TargetMode') != 'External':
                        media_parts.add(resolve_part(part, rel['Target']))
            slides.append({'part': part, 'paragraphs': paragraphs,
                           'media_parts': sorted(media_parts),
                           'missing_text': missing,
                           'shape_count': sum(local(e.tag) == 'sp' for e in root.iter()),
                           'picture_count': sum(local(e.tag) == 'pic' for e in root.iter())})
        if not slides:
            errors.append('No slides in presentation order')
        if expected and len(expected) != len(slides):
            errors.append('Slide count differs from requirements')
        svg = [n for n in names if n.lower().endswith('.svg')]
        if svg:
            warnings.append('SVG assets present: inspect actual PPTX rendering; presence is not failure')
    if digest != sha256(path):
        raise ValueError('PPTX changed during inspection; retry after writing finishes')
    return {'schema_version': 1, 'pptx_sha256': digest,
            'structural_ok': not errors, 'coverage_checked': bool(expected),
            'visual_verified': False, 'dimensions_emu': dimensions,
            'slides': slides, 'svg_assets': svg, 'errors': errors, 'warnings': warnings}
