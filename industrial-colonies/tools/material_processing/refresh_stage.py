"""Refresh owned inputs in a stopped disposable stage, preserving prior evidence.

Never touches a live instance, world data, unrelated scripts, or user project cards.
The caller must have awaited the previous Minecraft process before invoking this.
"""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--stage', type=Path, required=True)
    parser.add_argument('--revision', required=True)
    args = parser.parse_args()
    stage = args.stage.resolve()
    if not stage.is_relative_to(ROOT / 'isolated-runtime') or stage == ROOT / 'isolated-runtime':
        raise SystemExit('Only an existing child of project isolated-runtime is allowed')
    if not re.fullmatch(r'[a-z0-9-]+', args.revision):
        raise SystemExit('Unsafe revision')
    report = stage / 'material-stage-patch.json'
    state = json.loads(report.read_text())
    project = stage / 'kjsgen/projects/default.json'
    if sha(project) != state['newProjectSha256']:
        raise SystemExit('Merged project changed; refusing to refresh over unreviewed edits')
    backup = stage / 'material-input-backups' / args.revision
    if backup.exists():
        raise SystemExit('Refusing to reuse a refresh revision')
    files = [
        (ROOT / 'pack-scripts/server_scripts/zz_industrial_material_processing.js',
         stage / 'kubejs/server_scripts/zz_industrial_material_processing.js', 'scriptSha256'),
        (ROOT / 'processing/material_processing_catalog.json',
         stage / 'material-processing-catalog.json', 'catalogSha256'),
    ]
    if not all(src.is_file() and dst.is_file() for src, dst, _ in files):
        raise SystemExit('Missing source or previously staged input')
    backup.mkdir()
    shutil.copy2(report, backup / report.name)
    for name in ('latest.log', 'debug.log'):
        log = stage / 'logs' / name
        if log.is_file():
            shutil.copy2(log, backup / name)
    for src, dst, field in files:
        shutil.copy2(dst, backup / dst.name)
        shutil.copy2(src, dst)
        state[field] = sha(dst)
    state['lastRefresh'] = args.revision
    state['priorInputBackup'] = str(backup)
    report.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'stage': str(stage), 'revision': args.revision,
                      'scriptSha256': state['scriptSha256'], 'catalogSha256': state['catalogSha256'],
                      'priorEvidence': str(backup), 'liveWrites': False}, indent=2))


if __name__ == '__main__':
    main()
