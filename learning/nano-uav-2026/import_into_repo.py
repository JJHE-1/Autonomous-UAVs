"""Dry-run-first importer for a clean, existing local Git checkout.

No network, commits, pushes or visibility changes. Existing study destinations
are never overwritten. Optional README edits are backed up before replacement.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile

DESTINATION = Path('learning/nano-uav-2026')
MARKER = '<!-- nano-uav-learning-2026 -->'
OLD_LINK = '[maplab](https://github.com/ethz-asl/mav_voxblox_planning)'
NEW_LINK = '[maplab](https://github.com/ethz-asl/maplab)'


def git(target: Path, *args: str) -> str:
    result = subprocess.run(['git', '-C', str(target), *args], text=True,
                            capture_output=True, check=False)
    if result.returncode:
        raise ValueError(f'Git check failed: {" ".join(args)}: {result.stderr.strip()}')
    return result.stdout.strip()


def payload_files(bundle: Path) -> list[Path]:
    manifest_path = bundle / 'BUNDLE_MANIFEST.json'
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    entries = data.get('files')
    if not isinstance(entries, dict) or not entries:
        raise ValueError('Bundle manifest has no files')
    paths = []
    for rel, expected in sorted(entries.items()):
        logical = PurePosixPath(rel)
        if logical.is_absolute() or '..' in logical.parts or '\\' in rel or ':' in rel:
            raise ValueError(f'Unsafe manifest path: {rel}')
        path = bundle.joinpath(*logical.parts)
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != bundle):
            raise ValueError(f'Symlink in bundle path: {rel}')
        if not path.is_file() or not path.resolve().is_relative_to(bundle.resolve()):
            raise ValueError(f'Missing or out-of-bundle file: {rel}')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Bundle checksum mismatch: {rel}')
        paths.append(Path(*logical.parts))
    return paths + [Path('BUNDLE_MANIFEST.json')]


def import_bundle(bundle: Path, target: Path, *, apply: bool = False,
                  update_readme: bool = False) -> dict:
    bundle = bundle.resolve()
    target = target.expanduser().absolute()
    if target.is_symlink():
        raise ValueError('Target must not be a symbolic link')
    target = target.resolve()
    if not target.is_dir():
        raise ValueError('Target directory does not exist')
    if Path(git(target, 'rev-parse', '--show-toplevel')).resolve() != target:
        raise ValueError('Target must be the Git checkout root')
    if git(target, 'status', '--porcelain'):
        raise ValueError('Target checkout is not clean; preserve or commit unrelated changes first')
    remote = subprocess.run(['git', '-C', str(target), 'remote', 'get-url', '--push', 'origin'],
                            text=True, capture_output=True, check=False)
    if remote.returncode == 0 and re.search(r'(?i)[:/]alexkoven/Autonomous-UAVs(?:\.git)?/?$',
                                           remote.stdout.strip()):
        raise ValueError('origin points to the original upstream; use your own fork checkout')
    destination = target / DESTINATION
    for affected in (target / 'learning', destination, target / 'README.md'):
        if affected.is_symlink():
            raise ValueError(f'Symbolic link in affected path: {affected.name}')
    if destination.exists():
        raise ValueError('Study destination already exists; no files were overwritten')
    if (target / 'learning').exists() and not (target / 'learning').is_dir():
        raise ValueError('learning exists but is not a directory')
    if target == bundle or target.is_relative_to(bundle):
        raise ValueError('Keep the bundle separate from the target checkout')
    files = payload_files(bundle)
    readme = target / 'README.md'
    original = readme.read_bytes() if update_readme and readme.exists() else None
    replacement = None
    corrected = False
    if update_readme:
        text = original.decode('utf-8') if original is not None else ''
        if MARKER in text:
            raise ValueError('README already contains the guide marker; review the existing import')
        corrected = OLD_LINK in text
        text = text.replace(OLD_LINK, NEW_LINK)
        prefix = (f'{MARKER}\n## English navigation and nano-edge learning update\n\n'
                  '[Open the learning guide](learning/nano-uav-2026/README.md). '
                  'Includes a method matrix, source audit, learning exercises and experiment templates. '
                  'This is documentation, not validated flight firmware.\n\n---\n\n')
        replacement = (prefix + text).encode('utf-8')
    report = {'applied': False, 'target': str(target), 'destination': str(DESTINATION),
              'files_to_import': len(files), 'root_readme_update': update_readme,
              'exact_maplab_link_correction': corrected,
              'original_readme_backup': bool(update_readme and original is not None),
              'git_commit_created': False, 'github_upload_performed': False}
    if not apply:
        return report
    parent = destination.parent
    parent_created = not parent.exists()
    parent.mkdir(exist_ok=True)
    staged_readme = None
    moved = False
    readme_changed = False
    try:
        with tempfile.TemporaryDirectory(prefix='.nano-uav-import-', dir=parent) as temp:
            stage = Path(temp) / 'guide'
            stage.mkdir()
            for relative in files:
                out = stage / relative
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(bundle / relative, out)
            if update_readme and original is not None:
                backup = stage / 'provenance/README.before-import.md'
                backup.parent.mkdir()
                backup.write_bytes(original)
            if replacement is not None:
                fd, temporary_name = tempfile.mkstemp(prefix='.readme-update-', dir=target)
                staged_readme = Path(temporary_name)
                with os.fdopen(fd, 'wb') as handle:
                    handle.write(replacement)
                if readme.exists():
                    os.chmod(staged_readme, readme.stat().st_mode)
            os.rename(stage, destination)
            moved = True
            if staged_readme is not None:
                os.replace(staged_readme, readme)
                staged_readme = None
                readme_changed = True
        report['applied'] = True
        return report
    except Exception:
        if readme_changed:
            if original is None:
                readme.unlink(missing_ok=True)
            else:
                readme.write_bytes(original)
        if moved:
            shutil.rmtree(destination)
        if parent_created and parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
        raise
    finally:
        if staged_readme is not None:
            staged_readme.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True, help='Existing clean local fork checkout')
    parser.add_argument('--apply', action='store_true', help='Write files; omitted means dry run')
    parser.add_argument('--update-readme', action='store_true', help='Back up and add a root README link')
    args = parser.parse_args()
    try:
        report = import_bundle(Path(__file__).resolve().parent, args.target,
                               apply=args.apply, update_readme=args.update_readme)
    except (ValueError, OSError, json.JSONDecodeError, UnicodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
