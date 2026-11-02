"""Compile the source-owned material progression; never writes the live pack.

Run from project root. --check performs a deterministic stale-output check.
The generated late script reconciles installed recipes after normal pack scripts.
"""
import argparse
import json
from pathlib import Path
from common import Builder, NS
from alloy_intermediates import register_items as register_alloy_intermediates
from physical import register_metals, build as physical

ROOT = Path(__file__).resolve().parents[2]


def dump(data):
    return json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + '\n'


def expand(tags, name, seen=None):
    seen = set() if seen is None else seen
    if name in seen:
        return set()
    seen.add(name)
    result = {'#' + name}
    for entry in tags.get('item/' + name, []):
        entry = entry.get('id') if isinstance(entry, dict) else entry
        if not isinstance(entry, str): continue
        result.update(expand(tags, entry[1:], seen) if entry.startswith('#') else [entry])
    return result


def policy_for(b, inv):
    tags = inv['tags']
    feedstocks, nug, ingots, forms, values, fluids = set(), set(), set(), set(), {}, {}
    for metal, props in b.metals.items():
        feedstocks.update(expand(tags, 'c:storage_blocks/raw_' + metal))
        feedstocks.update(model for model in inv['item_models']
                          if model.split(':', 1)[-1] in ('crushed_raw_' + metal, 'dirty_' + metal + '_dust'))
        for group in ('ores/', 'raw_materials/', 'raw_blocks/', 'crushed_raw_materials/', 'dusts/', 'dirty_dusts/', 'clumps/', 'shards/', 'crystals/'):
            feedstocks.update(expand(tags, 'c:' + group + metal))
        for form, group in [('ingot', 'ingots/'), ('block', 'storage_blocks/'), ('nugget', 'nuggets/')]:
            members = expand(tags, 'c:' + group + metal)
            if props[form]: members.add(props[form])
            forms.update(members)
            if form == 'ingot': ingots.update(members)
            if form == 'nugget': nug.update(members)
            for member in sorted(members):
                values[member] = {'metal': metal, 'amount': props[form + '_mb']}
        fluids[props['fluid']] = metal
        # Fluid common tags and nested aliases across the four installed metallurgical mods.
        for tag, entries in tags.items():
            if tag.startswith('fluid/') and (tag.endswith(':molten_' + metal) or tag.endswith('/molten_' + metal)):
                fluids['#' + tag[6:]] = metal
                for entry in entries:
                    entry = entry.get('id') if isinstance(entry, dict) else entry
                    if isinstance(entry, str): fluids[entry] = metal
        for ref in inv['fluid_references']:
            if ref.split(':')[-1] in ('molten_' + metal, 'flowing_molten_' + metal, 'liquid_' + metal):
                fluids[ref] = metal
    for name in ('hematite','magnetite','chalcopyrite','sphalerite','cassiterite','galena','pentlandite',
                 'bauxite','ilmenite','wolframite_rock','chromite','spodumene_rock','dolomite','argentite',
                 'phosphate_rock','graphite_rock','bertrandite','borax_rock','uraninite','thorium_ore','ultramafic_rock',
                 'rich_sphalerite','rich_copper_ore','rich_hematite','rich_magnetite','rich_galena_ore',
                 'rich_bauxite','rich_ilmenite_ore','rich_wolframite_ore','rich_chromium_ore','rich_nickel_ore',
                 'cobalt_ore','rich_silver_ore','spodumene_ore','rich_tin_ore','rich_osmium_ore','rich_platinum_ore','rich_iridium_ore'):
        feedstocks.add(NS + name)
    b.remove_ids.update(['industrial_colonies:nuclear/refined_radiance',
        'industrial_colonies:sulfur/gunpowder_recovery',
        'industrial_colonies:sulfur/coal_gasification_coals',
        'industrial_colonies:sulfur/coal_gasification_blocks_coals',
        'industrial_colonies:sulfur/coal_gasification_dusts_coals'])
    def flags(values): return dict.fromkeys(sorted(values), True)
    return {'removeIds': flags(b.remove_ids), 'feedstocks': flags(feedstocks),
            'steelFeedValues': {'minecraft:raw_iron': 200, 'create:crushed_raw_iron': 200, '#c:dusts/iron': 75},
            'alloyProducts': flags(expand(tags, 'c:ingots/brass') | expand(tags, 'c:ingots/bronze') |
                                   {'create:brass_ingot', 'mekanism:ingot_bronze'}),
            'claimedOutputs': flags(b.claim_outputs), 'nuggets': flags(nug), 'ingots': flags(ingots),
            'finishedForms': flags(forms), 'metalInputs': flags(feedstocks | forms),
            'finishedValues': values, 'fluidMetals': fluids}


def compile_batch(physical_only=False):
    config_file = ROOT / 'processing/material_processing_values.json'
    config = json.loads(config_file.read_text(encoding='utf-8')) if config_file.exists() else {}
    inv = json.loads((ROOT / 'build/material-processing/installed-inventory.json').read_text(encoding='utf-8'))
    b = Builder(config)
    register_metals(b, inv)
    physical(b)
    register_alloy_intermediates(b)
    if not physical_only:
        from chemistry import build as chemistry
        chemistry(b)
        from capstone import build as capstone
        capstone(b)
    policy = policy_for(b, inv)
    header = '// priority: -1000\n// Generated by tools/material_processing/build.py; edit source modules and central values.\n'
    text = header + (Path(__file__).parent / 'policy.js').read_text(encoding='utf-8')
    text += '\nServerEvents.recipes(event => {\n  const policy = ' + json.dumps(policy, separators=(',', ':')) + '\n'
    text += '  icProcessingPolicy(event, policy)\n'
    for ident, recipe in b.recipes.items():
        comment = b.notes[ident]['comment'].replace('\n', ' ')
        if comment: text += '  // ' + comment + '\n'
        text += '  event.custom(' + json.dumps(recipe, separators=(',', ':')) + ').id(' + json.dumps(ident) + ')\n'
    text += "  console.info('[Industrial Colonies] Installed " + str(len(b.recipes)) + " owned material-processing recipes.')\n})\n"
    # Canonical forms use installed tags and add only missing canonical membership.
    text += "\nServerEvents.tags('item', event => {\n"
    for metal, props in b.metals.items():
        for form, group in [('ingot', 'ingots/'), ('block', 'storage_blocks/'), ('nugget', 'nuggets/')]:
            if props[form]: text += f"  event.add('c:{group}{metal}', '{props[form]}')\n"
    text += "})\n"
    text += "\nServerEvents.tags('fluid', event => { event.add('c:hydrogen', 'tfmg:hydrogen') })\n"
    outputs = {
        config_file: dump(b.config),
        ROOT / 'src/main/resources/data/industrial_colonies/processing/content.json': dump({'items': b.items, 'fluids': b.fluids}),
        ROOT / 'processing/material_processing_catalog.json': dump({'metals': b.metals, 'recipes': b.recipes, 'notes': b.notes, 'policy': policy}),
        ROOT / 'pack-scripts/server_scripts/zz_industrial_material_processing.js': text,
    }
    # Only explicitly requested rich ores change drops. Chemical ores continue
    # to drop their owned concentrate-bearing block so they cannot skip chemistry.
    for rock, raw in [('rich_hematite', 'minecraft:raw_iron'), ('rich_magnetite', 'minecraft:raw_iron'),
                      ('rich_copper_ore', 'minecraft:raw_copper'), ('rich_sphalerite', 'create:raw_zinc')]:
        outputs[ROOT / f'src/main/resources/data/industrial_colonies/loot_table/blocks/{rock}.json'] = dump({
            'type': 'minecraft:block', 'pools': [{'rolls': 1, 'entries': [{
                'type': 'minecraft:alternatives', 'children': [
                    {'type': 'minecraft:item', 'name': NS + rock, 'conditions': [{
                        'condition': 'minecraft:match_tool', 'predicate': {'predicates': {
                            'minecraft:enchantments': [{'enchantments': 'minecraft:silk_touch', 'levels': {'min': 1}}]}}}]},
                    {'type': 'minecraft:item', 'name': raw}]}],
                'conditions': [{'condition': 'minecraft:survives_explosion'}]}]})
    language = {}
    for name, entry in b.items.items():
        outputs[ROOT / f'src/main/resources/assets/industrial_colonies/models/item/{name}.json'] = dump({
            'parent': 'minecraft:item/generated', 'textures': {'layer0': entry['texture']}})
        language['item.industrial_colonies.' + name] = entry['name']
    for name, entry in b.fluids.items():
        language['fluid.industrial_colonies.' + name] = entry['name']
    # Keep existing localization intact. Each generated key is unambiguously owned.
    langfile = ROOT / 'src/main/resources/assets/industrial_colonies/lang/en_us.json'
    existing = json.loads(langfile.read_text(encoding='utf-8'))
    existing.update(language)
    outputs[langfile] = dump(existing)
    return outputs, b, inv


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--physical-only', action='store_true', help='Development-only intermediate compilation; not a complete deliverable')
    args = parser.parse_args()
    outputs, b, inv = compile_batch(args.physical_only)
    stale = []
    for path, text in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != text: stale.append(str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8', newline='\n')
    if stale: raise SystemExit('Stale generated processing outputs:\n' + '\n'.join(stale))
    print(f'{len(b.recipes)} processing recipes; {len(b.items)} new intermediates; {len(b.fluids)} new tank-only fluids; {len(outputs)} generated files')
    models = set(inv['item_models'])
    missing = [props[form] for props in b.metals.values() for form in ('ingot','block','nugget')
               if props[form] and not props[form].startswith(('minecraft:', NS)) and props[form] not in models]
    if missing: print('REVIEW canonical IDs without standalone models: ' + ', '.join(missing))


if __name__ == '__main__': main()
