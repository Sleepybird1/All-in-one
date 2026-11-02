"""Read-only material-catalog contracts; no Minecraft, Gradle or output writes.

Run: python -B tools/material_processing/test_catalog.py [--mods PATH]
Resource evidence is deliberately labelled separately from live registry/codec
testing. The integration GameTests own actual codec/machine acceptance.
"""
import argparse
import json
import math
import re
import sys
import tomllib
import unittest
from pathlib import Path
from zipfile import ZipFile

from build import compile_batch, expand, ROOT
from common import Builder, NS
from physical import register_metals

DEFAULT_MODS = Path('C:/Users/GodPC/curseforge/minecraft/Instances/All in one/mods')
P = NS + 'processing/'
ARGS = None
ASSERTIONS = 0


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def references(value, parent=''):
    """Typed IDs in native recipe trees, avoiding recipe IDs and tag IDs."""
    if isinstance(value, dict):
        for key in ('item', 'fluid', 'chemical'):
            if isinstance(value.get(key), str):
                yield key, value[key]
        if isinstance(value.get('id'), str):
            if 'amount' in value:
                yield ('chemical' if 'chemical' in parent else 'fluid'), value['id']
            elif 'count' in value or parent in ('results', 'result', 'item_output', 'item_outputs'):
                yield 'item', value['id']
        for key, child in value.items():
            yield from references(child, key)
    elif isinstance(value, list):
        for child in value:
            yield from references(child, parent)


def recipe_outputs(recipe):
    for key in ('results', 'result', 'item_output', 'item_outputs', 'fluid_output', 'fluid_outputs', 'chemical_output'):
        yield from references(recipe.get(key), key)


def recipe_inputs(recipe):
    for key in ('ingredients', 'ingredient', 'input', 'additives', 'item_input',
                'fluid_input', 'chemical_input', 'fluid', 'cast'):
        yield from references(recipe.get(key), key)


def evidence(mods, inv):
    resources = set()
    jars = sorted(mods.glob('*.jar'))
    vanilla = Path('C:/Users/GodPC/.gradle/caches/neoformruntime/intermediate_results')
    jars += sorted(vanilla.glob('stripClient_*_resourcesOutput.jar'))
    for jar in jars:
        with ZipFile(jar) as archive:
            resources.update(name for name in archive.namelist() if name.startswith('assets/'))
    known = {'item': {'minecraft:air'}, 'fluid': {'minecraft:water', 'minecraft:lava'}, 'chemical': set()}
    for name in resources:
        match = re.fullmatch(r'assets/([^/]+)/models/item/(.+)\.json', name)
        if match:
            known['item'].add(':'.join(match.groups()))
    for key, entries in inv['tags'].items():
        if not key.startswith('fluid/'):
            continue
        for entry in entries:
            entry = entry.get('id') if isinstance(entry, dict) else entry
            if isinstance(entry, str) and not entry.startswith('#'):
                known['fluid'].add(entry)
    known['fluid'].update(inv['fluid_references'])
    for record in inv['recipes'].values():
        for obj in objects(record['data']):
            if isinstance(obj.get('chemical'), str):
                known['chemical'].add(obj['chemical'])
    # Actual source-owned fixed registrations, not possibly stale generated models.
    for rel in ('IndustrialItems.java', 'geology/GeologyBlocks.java'):
        src = (ROOT / 'src/main/java/dev/godpc/industrialcolonies' / rel).read_text(encoding='utf-8')
        known['item'].update(NS + name for name in re.findall(
            r'ITEMS\.register(?:SimpleItem|SimpleBlockItem)?\(\s*"([a-z0-9_]+)"', src))
        match = re.search(r'APPROVED_IDS\s*=\s*List\.of\((.*?)\);', src, re.S)
        if match:
            known['item'].update(NS + name for name in re.findall(r'"([a-z0-9_]+)"', match.group(1)))
    return known, resources, len(jars)


class CatalogContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs, cls.b, cls.inv = compile_batch()
        cls.r = cls.b.recipes
        cls.known, cls.resources, cls.jars = evidence(ARGS.mods, cls.inv)
        cls.known['item'].update(NS + name for name in cls.b.items)
        cls.known['fluid'].update(NS + name for name in cls.b.fluids)

    def check(self, condition, message):
        global ASSERTIONS
        ASSERTIONS += 1
        self.assertTrue(condition, message)

    def rcp(self, path):
        self.check(P + path in self.r, 'Missing recipe ' + path)
        return self.r[P + path]

    def test_01_deterministic_complete_catalog(self):
        outputs, b, _ = compile_batch()
        self.check(outputs == self.outputs, 'Fresh compile is nondeterministic')
        self.check(b.recipes == self.r, 'Fresh recipes differ')
        self.check(len(self.r) >= 299, 'Full batch unexpectedly missing recipes')
        json.dumps(self.r, allow_nan=False)
        for ident, recipe in self.r.items():
            with self.subTest(recipe=ident):
                self.check(ident.startswith(P), 'Recipe namespace outside this batch')
                self.check(not any(word in json.dumps(recipe).lower() for word in
                                   ('allthemodium', 'vibranium', 'unobtainium')), 'Future material leaked into batch')

    def test_02_item_fluid_chemical_references(self):
        for ident, recipe in self.r.items():
            for kind, value in references(recipe):
                with self.subTest(recipe=ident, kind=kind, reference=value):
                    self.check(value in self.known[kind], f'No source/resource evidence for {kind} {value}')
        self.check(self.jars > 200, 'Incomplete installed-resource scan')

    def test_03_texture_resources(self):
        for name, entry in self.b.items.items():
            with self.subTest(item=name):
                namespace, suffix = entry['texture'].split(':', 1)
                resource = f'assets/{namespace}/textures/{suffix}.png'
                self.check(resource in self.resources or (ROOT / 'src/main/resources' / resource).is_file(),
                           'Missing texture ' + resource)

    def test_04_native_shape_and_capacity_contracts(self):
        allowed = {'modernfoundry:melting', 'modernfoundry:casting_table', 'modernfoundry:casting_basin',
                   'create:crushing', 'create:mixing', 'create:splashing', 'create:cutting',
                   'tfmg:vat_machine_recipe', 'tfmg:distillation', 'tfmg:coking',
                   'immersiveengineering:blast_furnace', 'immersiveengineering:arc_furnace',
                   'mekanism:rotary', 'mekanism:reaction', NS + 'exclusive_milling',
                   NS + 'industrial_iron_mixing', NS + 'industrial_iron_splashing'}
        # TFMG 1.2.0 bytecode: Vat has 4 slots per item/fluid input/output;
        # Distillation 0/1/0/6; Coking 1/0/1/2. Counts are list entries,
        # so repeated item ingredients genuinely consume distinct allowance.
        limits = {'tfmg:vat_machine_recipe': (4, 4, 4, 4),
                  'tfmg:distillation': (0, 1, 0, 6), 'tfmg:coking': (1, 0, 1, 2)}
        for ident, recipe in self.r.items():
            with self.subTest(recipe=ident):
                typ = recipe['type']
                self.check(typ in allowed, 'Unexpected/unreviewed recipe type ' + typ)
                for obj in objects(recipe):
                    for key in ('count', 'amount', 'time', 'processing_time', 'duration', 'energy', 'energy_required', 'min_size'):
                        if key in obj:
                            number = obj[key]
                            self.check(type(number) is int and number > 0, f'Invalid integer {key}: {number}')
                    if 'chance' in obj:
                        chance = obj['chance']
                        self.check(isinstance(chance, (int, float)) and math.isfinite(chance) and 0 < chance <= 1,
                                   'Invalid chance')
                if typ in limits:
                    ins, outs = recipe.get('ingredients', []), recipe.get('results', [])
                    actual = (sum('amount' not in v for v in ins), sum('amount' in v for v in ins),
                              sum('amount' not in v for v in outs), sum('amount' in v for v in outs))
                    self.check(all(n <= limit for n, limit in zip(actual, limits[typ])),
                               f'TFMG list capacity exceeded: {actual} > {limits[typ]}')
                if typ.endswith('mixing'):
                    self.check(sum('amount' not in v for v in recipe['ingredients']) <= 9, 'Basin exceeds 9 item ingredient slots')
                if typ == 'immersiveengineering:arc_furnace':
                    self.check(len(recipe['additives']) <= 4, 'Arc additive slot count exceeded')
                    for entry in [recipe['input']] + recipe['additives'] + recipe['results']:
                        self.check('count' not in entry or 'basePredicate' in entry, 'IE sized ingredient missing basePredicate')
                        self.check(entry.get('count', 1) <= 64, 'Arc stack exceeds normal stack capacity')
                if typ == 'modernfoundry:melting':
                    self.check('fluid' in recipe['result'] and 'amount' in recipe['result'], 'Invalid MF fluid result')

    def test_05_owned_content_closure_and_duplicate_materials(self):
        products = {ref for recipe in self.r.values() for ref in recipe_outputs(recipe)}
        # Manual server-interaction ownership is intentionally not a fake recipe.
        manual = {('item', NS + 'roasted_cinnabar')}
        for name in self.b.items:
            with self.subTest(item=name):
                self.check(('item', NS + name) in products | manual, 'New item has no production path')
                collisions = [i for i in self.inv['item_models'] if i.split(':', 1)[-1] == name
                              and not i.startswith(NS)]
                self.check(not collisions, 'New item duplicates existing exact name: ' + str(collisions))
        for name in self.b.fluids:
            with self.subTest(fluid=name):
                self.check(('fluid', NS + name) in products, 'New fluid has no producer')
        for output in self.b.claim_outputs:
            with self.subTest(claimed=output):
                self.check(('item', output) in products or ('fluid', output) in products,
                           'Claimed output is retired without an owned replacement')
        self.check(self.rcp('graphite/electrode_feed')['ingredients'][0] == {'item': 'nuclearcraft:graphite_ingot'},
                   'Electrode feed must reuse the existing purified graphite tier')
        self.check(self.rcp('boron/crush')['results'][0]['id'] == 'nuclearcraft:borax_dust',
                   'Borax Dust must reuse the existing NC identity')
        self.check('nuclearcraft:borax_dust' in self.b.claim_outputs, 'Untreated Borax acquisition needs review coverage')

    def test_06_fixed_values_and_rich_drops(self):
        for metal, props in self.b.metals.items():
            self.check(props['ingot_mb'] == 1000, metal + ' ingot value')
            self.check(props['block_mb'] == 9000, metal + ' block value')
        for path, amount in {'raw/iron': 200, 'raw/copper': 125, 'raw/gold': 100,
                             'iron/direct_hematite': 25, 'iron/direct_magnetite': 25,
                             'iron/reduced': 75, 'copper/direct': 20, 'copper/dust': 50, 'gold/flake': 1}.items():
            self.check(self.rcp(path)['result']['amount'] == amount, path + ' fixed value drift')
        self.check(self.b.metals['iron']['nugget_mb'] == 25, 'Iron trace value')
        self.check(self.b.metals['gold']['nugget_mb'] == 10, 'Gold nugget value')
        self.check(self.b.config['metals']['iron']['nugget'] == 25, 'Misleading serialized Iron trace setting')
        self.check(self.b.config['metals']['gold']['nugget'] == 10, 'Misleading serialized Gold nugget setting')
        stale = Builder({'metals': {'iron': {'nugget': 100}, 'gold': {'nugget': 100}}})
        register_metals(stale, self.inv)
        self.check(stale.config['metals']['iron']['nugget'] == 25, 'Old Iron 100 knob was not normalized')
        self.check(stale.config['metals']['gold']['nugget'] == 10, 'Old Gold 100 knob was not normalized')
        for rock, raw in [('rich_hematite', 'minecraft:raw_iron'), ('rich_magnetite', 'minecraft:raw_iron'),
                          ('rich_copper_ore', 'minecraft:raw_copper'), ('rich_sphalerite', 'create:raw_zinc')]:
            path = ROOT / f'src/main/resources/data/industrial_colonies/loot_table/blocks/{rock}.json'
            data = json.loads(self.outputs[path])
            children = data['pools'][0]['entries'][0]['children']
            self.check(children[0]['name'] == NS + rock, rock + ' Silk Touch identity')
            self.check(children[1]['name'] == raw, rock + ' raw-drop handoff')

    def test_07_processing_identity_and_electrical_gates(self):
        self.check(self.rcp('copper/washing')['type'] == 'create:splashing', 'Copper fan identity')
        self.check(self.rcp('tin/gravity_agitation')['type'] == 'create:mixing', 'Tin gravity identity')
        self.check(self.rcp('chromium/industrial_iron_separation')['type'] == NS + 'industrial_iron_splashing', 'Cr fan tier')
        for path in ('aluminum/electrical_reduction', 'lithium/electrical_reduction',
                     'magnesium/electrolyze_chloride', 'beryllium/electrochemical_reduce',
                     'reagents/bootstrap_brine_electrolysis'):
            self.check(self.rcp(path)['machines'] == ['tfmg:electrode', 'tfmg:electrode'], path + ' lacks electricity gate')
        for metal in ('aluminum', 'titanium', 'tungsten', 'chromium', 'lithium', 'magnesium', 'beryllium', 'boron', 'uranium', 'thorium'):
            self.check(not any(i.startswith(P + metal + '/direct') for i in self.r), 'Forbidden direct ' + metal)
        for path in ('titanium/consolidate_sponge', 'tungsten/sinter'):
            self.check(self.rcp(path)['type'] == 'immersiveengineering:arc_furnace', 'Refractory consolidation bypass')
            self.check(self.rcp(path)['input']['count'] == 8, 'Refractory powder batch drift')

    def test_08_nickel_cobalt_and_pgm_asymmetry(self):
        for path in ('nickel/crush_rich_nickel', 'nickel/rich_nickel_leach', 'nickel/precipitate_pure_feed'):
            self.check('cobalt' not in json.dumps(self.rcp(path)), 'Rich Nickel leaked into Cobalt branch')
        self.check(self.rcp('cobalt/dilute_recovery')['results'][0]['chance'] == .08, 'Pentlandite Cobalt must be small chance')
        self.check(self.rcp('cobalt/crush_rich_cobalt')['results'][1]['id'] == NS + 'nickel_only_concentrate', 'Cobalt reverse byproduct')
        crude = self.rcp('pgm/crude_exclusive')
        self.check(crude['type'] == NS + 'exclusive_milling', 'Crude PGM independent-roll regression')
        self.check([v['chance'] for v in crude['results']] == [.7, .25, .05], 'Crude PGM distribution')
        stages = [self.rcp(p) for p in ('pgm/osmium_first', 'pgm/platinum_second', 'pgm/iridium_harsh_purification')]
        self.check(len({r['type'] for r in stages}) == 1, 'PGM stage schema')
        for stage in stages:
            metal_ids = {x['id'] for x in stage['results'] if x['id'] in
                         ('mekanism:dust_osmium', 'nuclearcraft:platinum_dust', 'nuclearcraft:iridium_dust')}
            self.check(not metal_ids, 'Separation improperly outputs finished PGM powder')

    def test_09_consumed_recovery_loops(self):
        ti = self.rcp('titanium/magnesium_reduction')
        mg = self.rcp('magnesium/electrolyze_chloride')
        used = sum(i.get('item') == 'nuclearcraft:magnesium_dust' for i in ti['ingredients'])
        returned = next(v['amount'] for v in ti['results'] if v['id'] == NS + 'magnesium_chloride')
        self.check(returned == used * mg['ingredients'][0]['amount'], 'MgCl2 recycle multiplies Mg')
        boron = self.rcp('boron/advanced_reduction')
        self.check(boron['results'][1]['amount'] == mg['ingredients'][0]['amount'], 'Boron Mg recovery mismatch')
        oil = self.rcp('sulfur/desulfurized_oil_distillation')
        self.check([x['amount'] for x in oil['results']] == [100, 25, 50, 20, 5], 'Native Heavy Oil ratios changed')
        self.check(oil['results'][0]['id'] == NS + 'desulfurized_heavy_oil', 'Sulfide extraction reroll')
        self.check(all(x['id'] != 'tfmg:heavy_oil' for x in oil['results']), 'Native Heavy Oil returned')
        self.check(sum(x['amount'] for x in oil['results']) == oil['ingredients'][0]['amount'], 'Distillation volume drift')
        self.check(not any(i.startswith('tfmg:distillation/') for i in self.b.remove_ids), 'Native refinery removed')
        salt = self.rcp('reagents/dissolve_salt')
        self.check(salt['results'][0]['amount'] == 15, 'Salt duplication via native crystallizer')
        self.check(salt['ingredients'][0] == {'tag': 'c:dusts/salt'}, 'Salt mineral input missing')

    def test_10_native_reagent_and_nuclear_handoffs(self):
        required = ('mekanism:oxidizing/sulfur_dioxide', 'mekanism:chemical_infusing/sulfur_trioxide',
                    'mekanism:rotary/sulfur_trioxide', 'mekanism:rotary/sodium',
                    'mekanism:rotary/hydrogen_chloride', 'tfmg:vat_machine_recipe/sulfuric_acid',
                    'nuclearcraft:isotope_separator/uranium', 'nuclearcraft:isotope_separator/thorium')
        for ident in required:
            self.check(ident in self.inv['recipes'], 'Missing native handoff ' + ident)
            self.check(ident not in self.b.remove_ids, 'Native handoff explicitly retired ' + ident)
        so2 = self.inv['recipes']['mekanism:oxidizing/sulfur_dioxide']['data']
        self.check(so2['input']['tag'] == 'c:dusts/sulfur', 'Sulfur oxidation input tag drift')
        self.check('tfmg:sulfur_dust' in self.inv['tags']['item/c:dusts/sulfur'], 'Canonical sulfur absent from common tag evidence')
        self.check(self.rcp('reagents/contact_acid_hydration')['ingredients'][0]['fluid'] == 'mekanism:sulfur_trioxide', 'SO3 fluid handoff')
        for metal in ('uranium', 'thorium'):
            self.check(self.rcp(metal + '/nuclear_feed')['results'][0]['id'] == 'nuclearcraft:' + metal + '_dust', 'NC feed handoff')
        self.check(self.rcp('silicon/n_semiconductor')['ingredients'][1]['fluid'] == NS + 'phosphoric_acid', 'Phosphate semiconductor handoff')

    def test_11_no_global_placer_recipe(self):
        for ident, recipe in self.r.items():
            ins = json.dumps(recipe.get('ingredients', []))
            outs = json.dumps(recipe.get('results', []))
            self.check(not ('gold' in outs and any(v in ins for v in ('gravel', 'silt', 'peat', 'sediment'))),
                       'Unqualified sediment-to-gold recipe ' + ident)

    def test_12_new_intermediate_graph_has_no_isolated_cycle(self):
        # Native and old geology items are boundary inputs here. This proves
        # new-intermediate data closure, NOT native machine survival access.
        new = {('item', NS + name) for name in self.b.items}
        new |= {('fluid', NS + name) for name in self.b.fluids}
        available = {(kind, value) for kind, values in self.known.items() for value in values} - new
        available.add(('item', NS + 'roasted_cinnabar'))  # explicit real-player manual process
        remaining = dict(self.r)
        while remaining:
            ready = [(ident, recipe) for ident, recipe in remaining.items()
                     if set(recipe_inputs(recipe)).issubset(available)]
            if not ready:
                break
            for ident, recipe in ready:
                available.update(recipe_outputs(recipe))
                del remaining[ident]
        for kind, value in sorted(new):
            with self.subTest(kind=kind, intermediate=value):
                self.check((kind, value) in available, 'Unreachable or cyclic new intermediate ' + value)
        self.check(not remaining, 'Recipes with unclosed typed dependencies: ' + ', '.join(remaining))

    def test_13_tag_inputs_have_registered_resource_candidates(self):
        tags = {obj['tag'] for recipe in self.r.values() for obj in objects(recipe)
                if isinstance(obj.get('tag'), str)}
        for tag in sorted(tags):
            with self.subTest(tag=tag):
                # Every tag in this revision is an item/cast input; exact-fluid
                # maps deliberately avoid unresolved fluid-tag ambiguity.
                candidates = expand(self.inv['tags'], tag)
                for metal, props in self.b.metals.items():
                    for form, folder in (('ingot', 'ingots'), ('block', 'storage_blocks'), ('nugget', 'nuggets')):
                        if props[form] and tag == 'c:' + folder + '/' + metal:
                            candidates.add(props[form])
                self.check(bool(candidates & self.known['item']), 'No item resource candidate in #' + tag)

    def test_14_native_foundry_fuel_ceiling_and_exact_arc_values(self):
        fuels = [record['data'] for record in self.inv['recipes'].values()
                 if record['data'].get('type') == 'modernfoundry:melting_fuel']
        maximum = max(recipe['temperature'] for recipe in fuels)
        self.check(maximum == 1500, 'Installed fuel ceiling changed; re-audit Foundry reachability')
        for ident, recipe in self.r.items():
            if recipe['type'] == 'modernfoundry:melting':
                with self.subTest(recipe=ident):
                    self.check(recipe['temperature'] <= maximum, 'Unreachable Foundry temperature')
        for path, count, output_count, value in (
                ('pgm/consolidate_osmium', 20, 1, 50),
                ('pgm/consolidate_platinum', 20, 1, 50),
                ('pgm/iridium_fragment', 40, 1, 25),
                ('boron/consolidate_powder', 50, 3, 60)):
            recipe = self.rcp(path)
            self.check(recipe['type'] == 'immersiveengineering:arc_furnace', 'Fraction consolidation must be electrical')
            self.check(recipe['input']['count'] == count, 'Fraction input batch drift')
            self.check(recipe['results'][0].get('count', 1) == output_count, 'Fraction output batch drift')
            self.check(count * value == output_count * 1000, 'Fraction mB value was rounded or multiplied')
        for old in ('pgm/melt_osmium', 'pgm/melt_platinum', 'boron/melt_powder'):
            self.check(P + old not in self.r, 'Unreachable old acquisition path retained')
        for metal in ('titanium', 'tungsten', 'chromium', 'iridium'):
            self.check(self.rcp('foundry/' + metal + '/ingot')['temperature'] == 1500,
                       'Finished refractory remelting should use reachable Blazing Blood')
        blaze_head = self.inv['recipes']['modernfoundry:smeltery/entity_melting/heads/blaze']['data']
        self.check(blaze_head['temperature'] == 1000, 'Blaze-head fuel bootstrap requires hotter-than-lava input')
        self.check(blaze_head['result']['fluid'] == 'modernfoundry:blazing_blood', 'Native high-fuel source disappeared')

    def test_15_first_metals_use_native_solid_fuel_temperatures(self):
        solid = self.inv['recipes']['modernfoundry:smeltery/melting/fuel/solid']['data']['temperature']
        self.check(solid == 800, 'Native solid-fuel ceiling changed; re-audit first-metal bootstrap')
        # Exact source-defined temperatures, independent of the builder's map.
        # A universal 1000 default would put the first iron behind a lava bucket.
        expected = {
            'iron/direct_hematite': (800, 25), 'iron/direct_magnetite': (800, 25),
            'iron/reduced': (800, 75), 'raw/iron': (800, 200), 'raw/iron_block': (800, 1800),
            'copper/direct': (500, 20), 'copper/dust': (500, 50),
            'raw/copper': (500, 125), 'raw/copper_block': (500, 1125),
            'zinc/direct_sphalerite': (420, 12), 'zinc/melt_recovered_dust': (550, 75),
            'raw/zinc': (420, 125), 'raw/zinc_block': (420, 1125),
            'tin/direct': (225, 20), 'tin/concentrate': (225, 75),
            'raw/gold': (700, 100), 'raw/gold_block': (700, 900), 'gold/flake': (700, 1),
        }
        for metal, temperature in (('iron', 800), ('copper', 500), ('gold', 700), ('zinc', 420), ('tin', 225)):
            native = self.inv['recipes']['modernfoundry:smeltery/melting/metal/' + metal + '/ingot']['data']
            self.check(native['temperature'] == temperature, 'Installed native temperature drift: ' + metal)
            for form, amount in (('ingot', 1000), ('block', 9000),
                                 ('nugget', {'iron': 25, 'gold': 10}.get(metal, 100))):
                expected['foundry/' + metal + '/' + form] = (temperature, amount)
        for path, (temperature, amount) in expected.items():
            with self.subTest(recipe=path):
                recipe = self.rcp(path)
                self.check(recipe['temperature'] == temperature, 'Early native temperature drift: ' + path)
                self.check(recipe['temperature'] <= solid, 'First-metal route incorrectly requires liquid fuel: ' + path)
                self.check(recipe['result']['amount'] == amount, 'Heat correction altered metal value: ' + path)
        # Explicit process overrides and unknown-metal fallback still work;
        # these helper-only recipes are not inserted into the real catalog.
        helper = Builder()
        helper.metals = {'iron': {'fluid': 'modernfoundry:molten_iron'},
                         'unlisted': {'fluid': NS + 'test_only_unlisted'}}
        explicit = helper.melt('test/explicit', 'minecraft:iron_ingot', 'iron', 1000, temp=1111)
        fallback = helper.melt('test/fallback', 'minecraft:iron_ingot', 'unlisted', 1000)
        self.check(helper.recipes[explicit]['temperature'] == 1111, 'Explicit thermal process override was ignored')
        self.check(helper.recipes[fallback]['temperature'] == 1000, 'Unknown-metal fallback drift')

    def test_16_config_values_are_finite_nonnegative_and_integer_when_required(self):
        for default in (10, .5):
            for invalid in (-1, -.01, math.nan, math.inf, -math.inf, True, False, '10', None, [], {}):
                with self.subTest(default=default, invalid=repr(invalid)):
                    try:
                        Builder({'checks': {'value': invalid}}).value('checks.value', default)
                    except ValueError as error:
                        self.check('checks.value' in str(error), 'Rejected value lacks its configuration path')
                    else:
                        self.check(False, 'Nonfinite/negative/nonnumeric configuration value was accepted')
        for invalid in (.5, 2.0):
            with self.subTest(integer_default=10, invalid=invalid):
                try:
                    Builder({'checks': {'value': invalid}}).value('checks.value', 10)
                except ValueError as error:
                    self.check('checks.value' in str(error), 'Rejected fractional/count setting lacks path')
                else:
                    self.check(False, 'Integer count/time/volume accepted a floating-point value')
        for default, accepted in ((10, 0), (10, 2), (.5, 0), (.5, 2), (.5, 0.0), (.5, .25)):
            builder = Builder({'checks': {'value': accepted}})
            actual = builder.value('checks.value', default)
            self.check(actual == accepted and type(actual) is type(accepted),
                       'Valid nonnegative numeric value was rejected, rounded or coerced')
        builder = Builder()
        self.check(builder.value('checks.default_integer', 12) == 12, 'Absent integer default was not inserted')
        self.check(builder.value('checks.default_fraction', .25) == .25, 'Absent fractional default was not inserted')
        self.check(builder.config == {'checks': {'default_integer': 12, 'default_fraction': .25}},
                   'Default insertion did not preserve the nested source structure')
        # Zero is valid at this generic config boundary. Recipe-specific
        # positivity/chance ceilings remain the separate catalog contracts.

    def test_17_prc_unupgraded_energy_fits_actual_native_capacity(self):
        # Installed Mekanism 10.7.19.85 bytecode: PRCEnergyContainer adds
        # recipe.energy_required to base J/t; CachedRecipe spends it EACH tick.
        # Read the actual companion instance settings, not assumed defaults.
        config_root = ARGS.mods.parent / 'config/Mekanism'
        configs = {}
        for name in ('machine-storage', 'machine-usage', 'general', 'tiers'):
            source = config_root / (name + '.toml')
            self.check(source.is_file(), 'Missing native PRC config provenance: ' + str(source))
            configs[name] = tomllib.loads(source.read_text(encoding='utf-8-sig'))
        storage = configs['machine-storage']['pressurizedReactionBase']
        base_usage = configs['machine-usage']['pressurizedReactionBase']
        conversion = configs['general']['energy_conversion']['feConversionRate']
        cube_output = configs['tiers']['energy_cubes']['basicOutput']
        self.check(storage == 2000, 'PRC buffer changed; re-audit native reachability')
        self.check(base_usage == 5, 'PRC baseline J/t changed; re-audit native energy accounting')
        self.check(conversion == 2.5, 'FE-to-Joule ratio changed; re-audit operation cost')
        self.check(cube_output == 4000, 'Basic Energy Cube output changed; re-audit ordinary supply')
        recipe = self.rcp('radiance/pressure_treatment')
        self.check(recipe['type'] == 'mekanism:reaction', 'Radiance pressure-treatment machine drift')
        self.check(recipe['duration'] == 12500, 'Radiance PRC duration drift')
        self.check(recipe['energy_required'] == 1600, 'Radiance extra energy must be native Joules PER TICK')
        per_tick = base_usage + recipe['energy_required']
        capacity = max(storage, base_usage)  # native AttributeEnergy.getStorage
        extra_fe = recipe['energy_required'] * recipe['duration'] / conversion
        total_fe = per_tick * recipe['duration'] / conversion
        self.check(per_tick == 1605 and per_tick / conversion == 642, 'Unupgraded input demand drift')
        self.check(per_tick <= capacity, 'Unupgraded PRC cannot store one processing tick of energy')
        self.check(per_tick <= cube_output, 'Ordinary native cube cannot supply the baseline tick demand')
        self.check(extra_fe == 8000000, 'Default extra PRC cost must total 8M FE before upgrades')
        self.check(total_fe == 8025000, 'PRC base overhead omitted or operation-total energy misinterpreted')
        self.check(self.b.config['radiance']['pressure_extra_joules_per_tick'] == 1600,
                   'Central config must name and match the per-tick Joule charge')
        self.check('pressure_energy' not in self.b.config['radiance'], 'Ambiguous obsolete total-energy knob remains')
        # Negative regression: even max ENERGY upgrades (with no SPEED) cannot
        # rescue the old 8M-per-tick setting. Actual upgrades also change total
        # cost/time, so this test does not promise an upgrade-invariant 8M FE.
        multiplier = configs['general']['maxUpgradeMultiplier']
        self.check(multiplier == 10, 'Mekanism upgrade scaling changed; re-audit capacity')
        self.check(math.ceil((base_usage + 8000000) / multiplier) > capacity * multiplier,
                   'Old PRC failure control no longer demonstrates the native buffer blocker')

    def test_18_distillation_has_explicit_configurable_native_timing(self):
        # Isolated native recipe encoding adds processing_time:100 when KubeJS
        # receives an omitted timing. Keep source/catalog explicit and equal.
        expected = {'sulfur/desulfurized_oil_distillation', 'coal/tar_fractionation'}
        actual = {ident.removeprefix(P) for ident, recipe in self.r.items()
                  if recipe['type'] == 'tfmg:distillation'}
        self.check(actual == expected, 'Owned distillation set changed; review explicit timing coverage')
        for path in expected:
            self.check(self.rcp(path)['processing_time'] == 100, 'Native distillation timing omitted or drifted')
        self.check(self.b.config['chemistry']['timing']['desulfurized_oil_distillation'] == 100,
                   'Sulfur distillation default missing from central values')
        self.check(self.b.config['timing']['coal_tar_fractionation'] == 100,
                   'Coal Tar distillation default missing from central values')
        from chemistry import build as build_chemistry
        from capstone import build as build_capstone
        tuned = Builder({'chemistry': {'timing': {'desulfurized_oil_distillation': 137}},
                         'timing': {'coal_tar_fractionation': 173}})
        register_metals(tuned, self.inv)
        build_chemistry(tuned)
        build_capstone(tuned)
        self.check(tuned.recipes[P + 'sulfur/desulfurized_oil_distillation']['processing_time'] == 137,
                   'Configured sulfur distillation timing ignored')
        self.check(tuned.recipes[P + 'coal/tar_fractionation']['processing_time'] == 173,
                   'Configured Coal Tar distillation timing ignored')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--mods', type=Path, default=DEFAULT_MODS)
    ARGS = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CatalogContracts)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f'CATALOG DATA CONTRACTS: {ASSERTIONS} assertions; {result.testsRun} groups; '
          f'{len(result.failures)} failures; {len(result.errors)} errors. '
          'This is resource/schema evidence, not a live registry or machine test.')
    sys.exit(0 if result.wasSuccessful() else 1)
