"""Build and optionally install the user's scoped oil-well worldgen removal."""
import argparse
import hashlib
import json
import os
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
OUT = ROOT / 'progression/oil-well-removal'

def digest(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    jars = list((PACK / 'mods').glob('adastra-*.jar'))
    assert len(jars) == 1
    resource = 'data/ad_astra/worldgen/structure_set/oil_well.json'
    tag = 'data/ad_astra/tags/worldgen/biome/has_structure/oil_well.json'
    with zipfile.ZipFile(jars[0]) as jar:
        native = json.loads(jar.read(resource))
        structure = json.loads(jar.read('data/ad_astra/worldgen/structure/oil_well.json'))
        assert structure['biomes'] == '#ad_astra:has_structure/oil_well'
        assert native['structures'] == [{'structure': 'ad_astra:oil_well', 'weight': 1}]
    native['placement']['frequency'] = 0.0
    files = {'kubejs/' + resource: native, 'kubejs/' + tag: {'replace': True, 'values': []}}
    payload = {}
    for rel, body in files.items():
        data = (json.dumps(body, indent=2) + '\n').encode()
        candidate = OUT / 'candidate' / rel
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_bytes(data)
        target = PACK / rel
        assert target.resolve().is_relative_to(PACK.resolve())
        assert not any(p.is_symlink() or p.is_junction() for p in [target, *target.parents])
        payload[rel] = (target.read_bytes() if target.exists() else None, data)
    report = {'status': 'READY', 'sourceJar': jars[0].name, 'savesTouched': False,
              'files': {r: {'before': digest(b), 'after': digest(a)} for r, (b, a) in payload.items()}}
    (OUT / 'source-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    if args.apply:
        backup = PACK / '_industrial_colonies_backups' / ('oil-well-removal-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
        backup.mkdir(parents=True, exist_ok=False)
        for rel, (before, after) in payload.items():
            target = PACK / rel
            assert (target.read_bytes() if target.exists() else None) == before
            if before is not None:
                saved = backup / rel
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_bytes(before)
                assert saved.read_bytes() == before
        for rel, (before, after) in payload.items():
            target = PACK / rel
            assert (target.read_bytes() if target.exists() else None) == before
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + '.oil-well-tmp')
            assert not temporary.exists()
            temporary.write_bytes(after)
            os.replace(temporary, target)
            assert target.read_bytes() == after
        report.update(status='APPLIED', appliedAt=datetime.now().astimezone().isoformat(), backup=str(backup))
        for dest in (OUT / 'deployment.json', backup / 'deployment.json'):
            dest.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
