"""Validate local bundle contents. No external network links or hardware are tested."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'BUNDLE_MANIFEST.json'


def listed_files() -> list[Path]:
    result = []
    for path in ROOT.rglob('*'):
        rel = path.relative_to(ROOT)
        if any(part in {'.git', '__pycache__', '.venv', 'provenance'} for part in rel.parts):
            continue
        if path.is_file() and path.name != MANIFEST:
            result.append(path)
    return sorted(result)


def refresh_manifest() -> None:
    data = {'schema_version': 1, 'release_date': '2026-10-08',
            'hash_algorithm': 'sha256',
            'files': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in listed_files()}}
    (ROOT / MANIFEST).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def validate() -> dict:
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding='utf-8'))
    entries = manifest['files']
    errors = []
    actual_files = {p.relative_to(ROOT).as_posix() for p in listed_files()}
    for name in sorted(actual_files - set(entries)):
        errors.append(f'File omitted from manifest: {name}')
    for name in sorted(set(entries) - actual_files):
        errors.append(f'Manifest references untracked file: {name}')
    local_links = 0
    for name, expected in entries.items():
        logical = PurePosixPath(name)
        if logical.is_absolute() or '..' in logical.parts or '\\' in name or ':' in name:
            errors.append(f'Unsafe manifest path: {name}')
            continue
        p = ROOT / name
        if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(ROOT):
            errors.append(f'Missing or unsafe file: {name}')
            continue
        raw = p.read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            errors.append(f'Checksum mismatch: {name}')
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            errors.append(f'Non-UTF8 file: {name}')
            continue
        if re.search('[\u3400-\u4dbf\u4e00-\u9fff]', text):
            errors.append(f'Non-English CJK text in authored file: {name}')
        if p.suffix == '.json':
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f'Invalid JSON: {name}: {exc}')
        if p.suffix == '.md':
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
                parsed = urlsplit(link)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                referenced = (p.parent / unquote(parsed.path)).resolve()
                local_links += 1
                if not referenced.is_relative_to(ROOT) or not referenced.exists():
                    errors.append(f'Broken or out-of-bundle link: {name}: {link}')
                elif parsed.fragment and referenced.suffix == '.md':
                    body = referenced.read_text(encoding='utf-8')
                    if parsed.fragment.startswith('s') and parsed.fragment[1:].isdigit():
                        if f'id="{parsed.fragment}"' not in body:
                            errors.append(f'Missing source anchor: {name}: {link}')
    catalog = json.loads((ROOT / 'sources/catalog.json').read_text(encoding='utf-8'))
    source_ids = [item['id'] for item in catalog['sources']]
    if len(set(source_ids)) != len(source_ids):
        errors.append('Duplicate source IDs')
    for method in catalog['methods']:
        if method['local_validation'] != 'not_run':
            errors.append(f'Unexpected local external-stack validation claim: {method["id"]}')
        for source_id in method['source_ids']:
            if source_id not in source_ids:
                errors.append(f'Unknown source ID: {source_id}')
    return {'status': 'pass' if not errors else 'fail',
            'authored_files_verified': len(entries), 'local_links_checked': local_links,
            'method_entries': len(catalog['methods']), 'source_entries': len(source_ids),
            'external_links_network_tested': False, 'errors': errors}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-manifest', action='store_true',
                        help='Accept intentional edits and rewrite local hashes before validation')
    args = parser.parse_args()
    if args.refresh_manifest:
        refresh_manifest()
    try:
        report = validate()
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f'Validation failed: {exc}\n')
    print(json.dumps(report, indent=2))
    if report['status'] != 'pass':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
