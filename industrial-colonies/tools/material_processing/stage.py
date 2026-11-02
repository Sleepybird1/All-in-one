"""Apply only this batch's recipe edits to a NEW workspace-only disposable stage.

Preserves every unrelated KJSGen card and project option. A full old seed merge
would broaden the request, so only the 19 audited machine cards are selected.
"""
import argparse
import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from upgrade_material_machine_tiers import WEATHERED, COPPER, INDUSTRIAL, NEW


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--stage', type=Path, required=True)
    args = parser.parse_args()
    stage = args.stage.resolve()
    if not stage.is_relative_to(ROOT / 'isolated-runtime') or stage == ROOT / 'isolated-runtime':
        raise SystemExit('Stage must be a child of project isolated-runtime')
    report = stage / 'material-stage-patch.json'
    if report.exists(): raise SystemExit('Refusing to overwrite a prepared stage patch')
    compiled = json.loads((ROOT / 'build/material-processing/default.managed.json').read_text(encoding='utf-8'))
    ids = {'industrial_colonies:' + name for name in WEATHERED + COPPER + INDUSTRIAL + NEW}
    cards = {r['recipeId']: r for r in compiled['recipes'] if r.get('recipeId') in ids}
    if set(cards) != ids:
        raise SystemExit('Compiled machine patch is incomplete: ' + ', '.join(sorted(ids - set(cards))))
    target = stage / 'kjsgen/projects/default.json'
    old = json.loads(target.read_text(encoding='utf-8-sig'))
    new = copy.deepcopy(old)
    preserved, replaced, removed = [], [], []
    seen = set()
    for index, card in enumerate(new['recipes']):
        ident = card.get('recipeId')
        if ident in cards:
            new['recipes'][index] = cards[ident]
            replaced.append(ident)
            seen.add(ident)
        elif ident == 'industrial_colonies:nuclear/refined_radiance':
            removed.append(ident)
        else:
            preserved.append(card)
    new['recipes'] = [r for r in new['recipes'] if r.get('recipeId') not in removed]
    for ident in sorted(ids - seen): new['recipes'].append(cards[ident])
    removals = {r.get('recipeId') for r in new.get('removals', [])}
    for removal in compiled['removals']:
        if removal.get('recipeId') in ('mekanism:metallurgic_infuser', 'mekanism:rotary_condensentrator',
                                      'tfmg:crafting/materials/industrial_mixer',
                                      'createcasing:crafting/roller/industrial_iron') and removal['recipeId'] not in removals:
            new['removals'].append(removal)
    # Verify all unrelated cards byte-for-field before writing any stage file.
    untouched = [r for r in new['recipes'] if r.get('recipeId') not in ids]
    if preserved != untouched: raise SystemExit('Unrelated project card changed')
    backup = stage / 'material-input-backups'
    backup.mkdir()
    shutil.copy2(target, backup / 'default.json')
    before_hash = sha(target)
    target.write_text(json.dumps(new, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    script = ROOT / 'pack-scripts/server_scripts/zz_industrial_material_processing.js'
    destination = stage / 'kubejs/server_scripts' / script.name
    if destination.exists(): raise SystemExit('Unexpected existing batch script')
    shutil.copy2(script, destination)
    catalog = ROOT / 'processing/material_processing_catalog.json'
    shutil.copy2(catalog, stage / 'material-processing-catalog.json')
    result = {'stage': str(stage), 'liveWrites': False, 'oldProjectSha256': before_hash,
              'newProjectSha256': sha(target), 'scriptSha256': sha(destination), 'catalogSha256': sha(catalog),
              'replacedMachineCards': replaced, 'addedMachineCards': sorted(ids - seen),
              'removedCapstoneCards': removed, 'unrelatedCardsPreserved': len(preserved),
              'note': 'Dedicated server must export this merged KJSGen project BEFORE server scripts load.'}
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
