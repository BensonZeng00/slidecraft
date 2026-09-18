"""Read-only renderer discovery; never launches an application or proves rendering."""
import argparse
import json
import os
import platform
import re
import shutil
from pathlib import Path


def executable_from_command(command):
    match = re.match(r'^\s*"([^"]+\.exe)"|^\s*(.+?\.exe)(?:\s|$)', command, re.I)
    return os.path.expandvars(next(v for v in match.groups() if v)) if match else None


def windows_powerpoint():
    import winreg
    evidence, candidates = [], []
    for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'PowerPoint.Application\CLSID', 0, winreg.KEY_READ | view) as key:
                clsid = winreg.QueryValue(key, None)
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, rf'CLSID\{clsid}\LocalServer32', 0, winreg.KEY_READ | view) as key:
                command = winreg.QueryValue(key, None)
            evidence.append({'source': 'COM registration', 'view': view, 'command': command})
            path = executable_from_command(command)
            if path:
                candidates.append(path)
        except OSError as exc:
            evidence.append({'source': 'COM registration', 'view': view, 'error': str(exc)})
    for var in ('ProgramFiles', 'ProgramFiles(x86)'):
        base = os.environ.get(var)
        if base:
            for suffix in ('Microsoft Office/Root/Office16/POWERPNT.EXE', 'Microsoft Office/Office16/POWERPNT.EXE'):
                candidates.append(str(Path(base) / suffix))
    return candidates, evidence


def discovery(extra_paths=()):
    candidates, evidence = [], []
    if platform.system() == 'Windows':
        pp, evidence = windows_powerpoint()
        candidates.extend(('PowerPoint', p) for p in pp)
        for var in ('ProgramFiles', 'ProgramFiles(x86)'):
            if os.environ.get(var):
                candidates.append(('LibreOffice', str(Path(os.environ[var]) / 'LibreOffice/program/soffice.exe')))
    if platform.system() == 'Darwin':
        candidates.extend([('PowerPoint', '/Applications/Microsoft PowerPoint.app/Contents/MacOS/Microsoft PowerPoint'),
                           ('LibreOffice', '/Applications/LibreOffice.app/Contents/MacOS/soffice')])
    for name in ('soffice', 'libreoffice'):
        found = shutil.which(name)
        if found:
            candidates.append(('LibreOffice', found))
    candidates.extend(('explicit candidate', str(p)) for p in extra_paths)
    found, seen = [], set()
    for name, path in candidates:
        key = os.path.normcase(os.path.abspath(path))
        if key in seen:
            continue
        seen.add(key)
        exists = Path(path).is_file()
        evidence.append({'source': 'file check', 'path': path, 'exists': exists})
        if exists:
            found.append({'name': name, 'path': path, 'status': 'detected_not_tested'})
    return {'schema_version': 1, 'os': platform.system(), 'renderers': found,
            'status': 'detected_not_tested' if found else 'not_detected', 'evidence': evidence,
            'note': 'Discovery only. Not detected does not mean not installed. Host render services are outside this local probe.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', action='append', default=[], type=Path)
    args = parser.parse_args()
    print(json.dumps(discovery(args.candidate), ensure_ascii=False, indent=2))
