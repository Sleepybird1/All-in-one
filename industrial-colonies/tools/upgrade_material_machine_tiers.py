"""Narrow, repeatable seed patch for the approved material-processing bootstrap.

Default validates/plans in memory. --apply edits only the named recipes and two
missing user-owned output markers; no KubeJS export, live pack or launch occurs.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / 'progression/managed_recipe_overhaul.seed.json'
PREFIX = 'industrial_colonies:'
WEATHERED = (
    'mekanism_pre_nuclear/electrolytic_separator',
    'mekanism_pre_nuclear/chemical_oxidizer',
    'mekanism_pre_nuclear/chemical_infuser',
    'mekanism_components/electrolytic_core',
    'mekanism_components/basic_chemical_tank',
    'mekanism/thermal_evaporation/block_batch',
    'mekanism/thermal_evaporation/controller',
    'mekanism/thermal_evaporation/valve',
)
COPPER = ('tfmg_heavy_electrical/electrode_holder',
          'fluid_infrastructure/fireproof_chemical_vat',
          'heavy_industry/industrial_mixer')
INDUSTRIAL = tuple('manufacturing/industrial_iron/' + role
                   for role in ('press', 'deployer', 'mixer', 'saw', 'fan', 'roller'))
NEW = ('material_bootstrap/metallurgic_infuser',
       'material_bootstrap/rotary_condensentrator')
ADDED_INPUTS = ('nuclearcraft:titanium_ingot', 'nuclearcraft:tungsten_ingot',
                'industrial_colonies:high_purity_silicon')


def move_machines(recipe, before, after):
    if recipe.get('machine', '').startswith('createcasing:' + before + '_'):
        recipe['machine'] = recipe['machine'].replace(':' + before + '_', ':' + after + '_')
    for step in recipe.get('steps', []):
        if step.get('machine', '').startswith('createcasing:' + before + '_'):
            step['machine'] = step['machine'].replace(':' + before + '_', ':' + after + '_')


def upgraded(source):
    target = copy.deepcopy(source)
    recipes = {r['id']: r for r in target['recipes']}
    mixer = {
        'id': PREFIX + 'heavy_industry/industrial_mixer',
        'type': 'mechanical_crafting', 'phase': 'Steel & Petroleum', 'order': 205,
        'output': 'tfmg:industrial_mixer', 'pattern': ['KSK', 'FCF', 'KGK'],
        'key': {'K': 'tfmg:screw', 'S': 'create:shaft', 'F': 'tfmg:steel_frame',
                'C': 'tfmg:steel_casing', 'G': 'tfmg:large_steel_cogwheel'},
        'exclusive_output': True,
        'remove': ['tfmg:crafting/materials/industrial_mixer'],
        'comment': 'Material bootstrap: assemble the vat mixer on ordinary mechanical crafters before circuit boards. Four screws, one shaft, two steel frames, one ordinary steel casing and one large steel cogwheel retain a physical steel machine without heavy plates, steel mechanisms, heavy casings or electronics. This unlocks initial acid, silicon and brine mixing; vat heat and electrical operations remain separate requirements.'}
    if mixer['id'] in recipes:
        assert recipes[mixer['id']] == mixer, 'Existing bootstrap mixer changed'
    else:
        target['recipes'].append(mixer)
        recipes[mixer['id']] = mixer
    for short in WEATHERED:
        r = recipes[PREFIX + short]
        move_machines(r, 'industrial_iron', 'weathered_iron')
        if short == 'mekanism_components/basic_chemical_tank':
            r['phase'] = 'Mekanized Industry'
        suffix = ' Material bootstrap: Weathered Iron builds this reagent component before Titanium/Tungsten Industrial machinery.'
        if suffix not in r.get('comment', ''):
            r['comment'] = r.get('comment', '') + suffix
    for short in COPPER:
        r = recipes[PREFIX + short]
        if short == 'heavy_industry/industrial_mixer':
            continue
        move_machines(r, 'railway', 'copper')
        for field in ('input', 'transitional'):
            if r.get(field) == 'tfmg:heavy_machinery_casing':
                r[field] = 'tfmg:steel_casing'
        for step in r.get('steps', []):
            if step.get('ingredient') == 'tfmg:heavy_machinery_casing':
                step['ingredient'] = 'tfmg:steel_casing'
        suffix = ' Material bootstrap: the Copper line and ordinary steel casing avoid the Aluminum-capacitor/heavy-casing cycle; powered electrodes and heat remain mandatory.'
        if suffix not in r.get('comment', ''):
            r['comment'] = r.get('comment', '') + suffix
    for short in INDUSTRIAL:
        r = recipes[PREFIX + short]
        assert r['type'] == 'sequenced_assembly' and r['loops'] == 1
        for step in r['steps']:
            if step.get('ingredient') == 'mekanism:hdpe_sheet':
                step['ingredient'] = 'tfmg:plastic_sheet'
        present = {s.get('ingredient') for s in r['steps']}
        for ingredient in ADDED_INPUTS:
            if ingredient not in present:
                r['steps'].insert(-1, {'op': 'deploying', 'ingredient': ingredient,
                                      'machine': 'createcasing:weathered_iron_deployer'})
        suffix = ' Physical material gate: one Titanium ingot, one Tungsten ingot and one high-purity Silicon are installed on the Weathered line. Existing advanced control and calculation electronics remain; ordinary TFMG plastic replaces only the downstream HDPE insulation.'
        if suffix not in r.get('comment', ''):
            r['comment'] = r.get('comment', '') + suffix
    infuser = {
        'id': PREFIX + NEW[0], 'type': 'shaped', 'phase': 'Electrical Manufacturing',
        'order': 510, 'output': 'mekanism:metallurgic_infuser',
        'pattern': ['IFI', 'ROR', 'IFI'],
        'key': {'I': '#c:ingots/iron', 'F': 'minecraft:furnace',
                'R': '#c:dusts/redstone', 'O': '#c:ingots/osmium'},
        'exclusive_output': True, 'remove': ['mekanism:metallurgic_infuser'],
        'comment': 'Restore the missing early Infuser using the exact installed native material counts (four Iron, two Furnaces, two Redstone, one Osmium). Crude low-yield Ultramafic Osmium supplies the core before wet PGM chemistry; no basic circuit is required to build its own producer.'}
    rotary = {
        'id': PREFIX + NEW[1], 'type': 'sequenced_assembly',
        'phase': 'Mekanized Industry', 'order': 1220,
        'input': 'tfmg:steel_frame', 'transitional': 'tfmg:steel_frame', 'loops': 1,
        'output': 'mekanism:rotary_condensentrator', 'exclusive_output': True,
        'remove': ['mekanism:rotary_condensentrator'],
        'depends_on': [PREFIX + 'mekanism_components/basic_chemical_tank',
                       PREFIX + 'mekanism/advanced_control_circuit',
                       PREFIX + 'fluid_infrastructure/steel_chemical_vat'],
        'steps': [
            {'op': 'deploying', 'ingredient': item,
             'machine': 'createcasing:weathered_iron_deployer'}
            for item in ('tfmg:steel_chemical_vat', 'tfmg:steel_fluid_tank',
                         'mekanism:basic_chemical_tank', 'create:mechanical_pump',
                         'tfmg:electric_motor', 'tfmg:transformer',
                         'mekanism:basic_control_circuit', 'mekanism:advanced_control_circuit',
                         'tfmg:capacitor_item', 'tfmg:plastic_sheet')
        ] + [{'op': 'pressing', 'machine': 'createcasing:weathered_iron_press'}],
        'comment': 'Restore the missing Rotary as a real Weathered-built gas/fluid bridge: separate reservoirs, pump, motor, transformer and advanced control. Avoid the unavailable user Energy Tablet and downstream HDPE/Industrial machines; existing unrelated user cards remain untouched.'}
    for new in (infuser, rotary):
        if new['id'] in recipes:
            assert recipes[new['id']] == new, 'Existing bootstrap recipe changed: ' + new['id']
        else:
            target['recipes'].append(new)
    target['user_owned_outputs'] = [o for o in target.get('user_owned_outputs', [])
                                    if o not in ('mekanism:metallurgic_infuser',
                                                 'mekanism:rotary_condensentrator')]
    target['exclude_outputs'] = [o for o in target.get('exclude_outputs', [])
                                 if o != 'tfmg:industrial_mixer']
    target['preserve_recipe_ids'] = [o for o in target.get('preserve_recipe_ids', [])
                                    if o != 'tfmg:crafting/materials/industrial_mixer']
    return target


def validate(before, after):
    a = {r['id']: r for r in before['recipes']}
    b = {r['id']: r for r in after['recipes']}
    allowed = {PREFIX + x for x in WEATHERED + COPPER + INDUSTRIAL + NEW}
    assert len(b) == len(after['recipes']), 'Duplicate recipe IDs'
    assert not (set(a) - set(b)), 'No recipe may be removed'
    for rid in set(a) & set(b):
        assert rid in allowed or a[rid] == b[rid], 'Unrelated recipe changed: ' + rid
    for key in before:
        assert key in ('recipes', 'user_owned_outputs', 'exclude_outputs', 'preserve_recipe_ids') or before[key] == after[key], key
    assert after.get('exclude_outputs', []) == [o for o in before.get('exclude_outputs', [])
                                               if o != 'tfmg:industrial_mixer']
    assert after.get('preserve_recipe_ids', []) == [o for o in before.get('preserve_recipe_ids', [])
                                                  if o != 'tfmg:crafting/materials/industrial_mixer']
    for short in INDUSTRIAL:
        r = b[PREFIX + short]
        inputs = [s.get('ingredient') for s in r['steps']]
        assert all(inputs.count(x) == 1 for x in ADDED_INPUTS)
        assert 'mekanism:advanced_control_circuit' in inputs and 'ae2:calculation_processor' in inputs
        assert 'mekanism:hdpe_sheet' not in inputs
        assert all(s['machine'].startswith('createcasing:weathered_iron_') for s in r['steps'])
    for short in WEATHERED + NEW[1:]:
        r = b[PREFIX + short]
        machines = [r.get('machine', '')] + [s.get('machine', '') for s in r.get('steps', [])]
        assert not any('industrial_iron' in m or 'refined_radiance' in m for m in machines)
    for short in COPPER:
        r = b[PREFIX + short]
        assert 'tfmg:heavy_machinery_casing' not in json.dumps(r)
        assert all(s['machine'].startswith('createcasing:copper_') for s in r.get('steps', []))
    mixer = b[PREFIX + 'heavy_industry/industrial_mixer']
    assert mixer['type'] == 'mechanical_crafting' and mixer['pattern'] == ['KSK', 'FCF', 'KGK']
    assert not ({'tfmg:heavy_plate', 'tfmg:steel_mechanism', 'tfmg:circuit_board',
                 'tfmg:heavy_machinery_casing'} & set(mixer['key'].values()))
    assert upgraded(after) == after, 'Patch is not idempotent'
    return [rid for rid in b if rid not in a or a[rid] != b[rid]]


def restore_batch_roller(seed):
    """Apply the new approval only to this batch's assembled scratch manifest.

    The historical reviewed-default policy intentionally retires all rollers.
    Do not edit that policy or restore any of its other rejected cards.
    """
    path = ROOT / 'build/material-processing/managed_recipe_overhaul.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    rid = PREFIX + 'manufacturing/industrial_iron/roller'
    recipe = next(r for r in seed['recipes'] if r['id'] == rid)
    existing = [r for r in manifest['recipes'] if r['id'] == rid]
    assert len(existing) <= 1 and (not existing or existing[0] == recipe)
    if not existing:
        manifest['recipes'].append(copy.deepcopy(recipe))
    manifest['preserve_recipe_ids'] = [r for r in manifest.get('preserve_recipe_ids', [])
                                       if r != 'createcasing:crafting/roller/industrial_iron']
    manifest['disabled_recipe_ids'] = [r for r in manifest.get('disabled_recipe_ids', []) if r != rid]
    manifest['material_processing_overrides'] = {
        'recipes': [rid],
        'reason': 'New material-processing approval requires Ti, W and high-purity Silicon in all six Industrial machines. Restore only this seed roller after historical default-restoration assembly; the historical policy remains unchanged.'}
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n',
                    encoding='utf-8', newline='\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--backup-name', choices=('machine-tiers.seed.before.json',
                                              'machine-tiers-mixer.seed.before.json'),
                    default='machine-tiers.seed.before.json')
    ap.add_argument('--restore-batch-roller', action='store_true',
                    help='After normal assembly, restore only the newly approved Industrial roller in build/material-processing/managed_recipe_overhaul.json')
    args = ap.parse_args()
    raw = SEED.read_bytes()
    before = json.loads(raw)
    after = upgraded(before)
    changed = validate(before, after)
    if args.apply and changed:
        backup = ROOT / 'backups/material-processing-20260909' / args.backup_name
        if backup.exists():
            assert backup.read_bytes() == raw, 'Existing backup is from another baseline; do not overwrite'
        else:
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(raw)
        SEED.write_text(json.dumps(after, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    if args.restore_batch_roller:
        assert not changed, 'Apply the seed patch before restoring the batch roller'
        restore_batch_roller(after)
    print(json.dumps({'status': 'PASS', 'applied': args.apply, 'changed': changed,
                      'recipesBefore': len(before['recipes']), 'recipesAfter': len(after['recipes']),
                      'seedBeforeSha256': hashlib.sha256(raw).hexdigest().upper(),
                      'seedCurrentSha256': hashlib.sha256(SEED.read_bytes()).hexdigest().upper()}, indent=2))


if __name__ == '__main__':
    main()
