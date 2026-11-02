"""Early mechanical metallurgy, fixed melt values, and intentional Mixer alloys."""
from math import gcd
from common import I, O, F, NS


METALS = {
    'iron': ('minecraft:iron_ingot', 'minecraft:iron_nugget', 'minecraft:iron_block'),
    'copper': ('minecraft:copper_ingot', 'create:copper_nugget', 'minecraft:copper_block'),
    'gold': ('minecraft:gold_ingot', 'minecraft:gold_nugget', 'minecraft:gold_block'),
    'zinc': ('create:zinc_ingot', 'create:zinc_nugget', 'create:zinc_block'),
    'tin': ('mekanism:ingot_tin', 'mekanism:nugget_tin', 'mekanism:block_tin'),
    'lead': ('tfmg:lead_ingot', 'tfmg:lead_nugget', 'tfmg:lead_block'),
    'nickel': ('tfmg:nickel_ingot', 'tfmg:nickel_nugget', 'tfmg:nickel_block'),
    'aluminum': ('tfmg:aluminum_ingot', 'tfmg:aluminum_nugget', 'tfmg:aluminum_block'),
    'lithium': ('tfmg:lithium_ingot', 'tfmg:lithium_nugget', 'tfmg:lithium_block'),
    'osmium': ('mekanism:ingot_osmium', 'mekanism:nugget_osmium', 'mekanism:block_osmium'),
    'silver': ('nuclearcraft:silver_ingot', None, 'nuclearcraft:silver_block'),
    'magnesium': ('nuclearcraft:magnesium_ingot', None, 'nuclearcraft:magnesium_block'),
    'cobalt': ('nuclearcraft:cobalt_ingot', None, 'nuclearcraft:cobalt_block'),
    'chromium': ('nuclearcraft:chromium_ingot', None, None),
    'titanium': ('nuclearcraft:titanium_ingot', None, 'rocketnautics:titanium_block'),
    'tungsten': ('nuclearcraft:tungsten_ingot', 'createmetallurgy:tungsten_nugget', 'createmetallurgy:tungsten_block'),
    'beryllium': ('nuclearcraft:beryllium_ingot', None, 'nuclearcraft:beryllium_block'),
    'boron': ('nuclearcraft:boron_ingot', None, 'nuclearcraft:boron_block'),
    'platinum': ('nuclearcraft:platinum_ingot', None, 'nuclearcraft:platinum_block'),
    'iridium': ('nuclearcraft:iridium_ingot', None, None),
    'steel': ('tfmg:steel_ingot', 'tfmg:steel_nugget', 'tfmg:steel_block'),
    'brass': ('create:brass_ingot', 'create:brass_nugget', 'create:brass_block'),
    'bronze': ('mekanism:ingot_bronze', 'mekanism:nugget_bronze', 'mekanism:block_bronze'),
}


def register_metals(b, inventory):
    tags = inventory['tags']
    for metal, (ingot, nugget, block) in METALS.items():
        if tags.get('fluid/modernfoundry:molten_' + metal):
            fluid = 'modernfoundry:molten_' + metal
        elif tags.get('fluid/c:molten_' + metal):
            fluid = 'nuclearcraft:molten_' + metal
        else:
            fluid = b.fluid('molten_' + metal, 0xFFDDD3C0, 'Molten ' + metal.title())
        if metal in ('iron', 'gold'):
            # Brief-fixed values, not user balance knobs. Normalize legacy
            # generated 100s as well; dict.get's eager default previously
            # serialized a misleading unused value even when the fixed value won.
            nugget_value = {'iron': 25, 'gold': 10}[metal]
            b.config.setdefault('metals', {}).setdefault(metal, {})['nugget'] = nugget_value
        else:
            nugget_value = b.value('metals.' + metal + '.nugget', 100)
        b.metals[metal] = {'ingot': ingot, 'nugget': nugget, 'block': block, 'fluid': fluid,
                           'ingot_mb': 1000, 'block_mb': 9000, 'nugget_mb': nugget_value}


def build(b):
    for metal, props in b.metals.items():
        for form, amount in [('ingot', 1000), ('block', 9000), ('nugget', props['nugget_mb'])]:
            output = props[form]
            if output is None:
                continue
            tag = {'ingot': 'ingots/', 'block': 'storage_blocks/', 'nugget': 'nuggets/'}[form] + metal
            b.melt(f'foundry/{metal}/{form}', '#' + 'c:' + tag, metal, amount,
                   temp=1500 if metal in ('titanium', 'tungsten', 'chromium', 'iridium') else None,
                   comment='Already-finished material remelts at reachable native fuel temperature with the same value as casting; this is not raw-ore reduction or ore_melting multiplication.')
            recipe = {'type': 'modernfoundry:casting_basin' if form == 'block' else 'modernfoundry:casting_table',
                      'fluid': {'fluid': props['fluid'], 'amount': amount},
                      'result': {'item': output}, 'cooling_time': 160 if form == 'block' else 40}
            if form != 'block':
                recipe['cast'] = {'tag': 'modernfoundry:casts/multi_use/' + form}
            b.add(f'casting/{metal}/{form}', recipe)
    # Raw reserves do NOT count as a finished ingot and do not use MF machine ore multipliers.
    for metal, item, amount in [('iron', 'minecraft:raw_iron', 200), ('copper', 'minecraft:raw_copper', 125),
                               ('gold', 'minecraft:raw_gold', 100), ('zinc', 'create:raw_zinc', b.value('metals.zinc.raw', 125))]:
        b.melt(f'raw/{metal}', item, metal, amount)
        b.melt(f'raw/{metal}_block', '#c:storage_blocks/raw_' + metal, metal, 9 * amount)
    b.melt('gold/flake', NS + 'gold_flake', 'gold', 1)

    iron = b.item('reduced_iron_fraction', 'Reduced Iron Fraction (75 mB)', 'minecraft:item/iron_nugget')
    iron_dust = b.item('iron_bearing_dust')
    for rock in ('hematite', 'magnetite'):
        b.melt('iron/direct_' + rock, NS + rock, 'iron', 25)
        b.crush('iron/crush_' + rock, NS + rock, [O(iron_dust)])
    b.add('iron/blast_reduction', {'type': 'immersiveengineering:blast_furnace',
          'input': I(iron_dust), 'result': I(iron), 'slag': I('tfmg:slag'),
          'time': b.value('timing.iron_blast', 600)},
          'Carbon-fueled blast reduction leaves real slag; 75 mB is three 25 mB nuggets.')
    b.melt('iron/reduced', iron, 'iron', 75)

    crushed_copper = b.item('crushed_chalcopyrite', texture='create:item/crushed_raw_copper')
    b.melt('copper/direct', NS + 'chalcopyrite', 'copper', 20)
    b.crush('copper/crushing', NS + 'chalcopyrite', [O(crushed_copper)])
    b.add('copper/washing', {'type': 'create:splashing', 'ingredients': [I(crushed_copper)],
          'results': [O('mekanism:dust_copper')]}, 'Copper alone uses simple Fan + Water washing.')
    b.melt('copper/dust', 'mekanism:dust_copper', 'copper', 50)
    b.claim_outputs.add('mekanism:dust_copper')

    cassiterite = b.item('crushed_cassiterite')
    tin = b.item('heavy_cassiterite_concentrate')
    b.melt('tin/direct', NS + 'cassiterite', 'tin', b.value('metals.tin.direct', 20))
    b.crush('tin/crushing', NS + 'cassiterite', [O(cassiterite)])
    b.mix('tin/gravity_agitation', [I(cassiterite), F('minecraft:water', 250)],
          [O(tin), O('minecraft:sand')], time=b.value('timing.tin_agitation', 300),
          comment='Basin agitation separates dense cassiterite; intentionally NOT fan washing.')
    b.melt('tin/concentrate', tin, 'tin', b.value('metals.tin.concentrate', 75))
    b.crush('tin/rich_crushing', NS + 'rich_tin_ore', [O(tin, 4)])

    roasted = b.item('roasted_cinnabar', texture='minecraft:item/redstone')
    dust = b.item('cinnabar_dust', texture='minecraft:item/redstone')
    mercury = b.item('trace_mercury_residue', 'Trace Mercury Residue', 'minecraft:item/iron_nugget')
    b.crush('cinnabar/crushing', NS + 'cinnabar', [O(dust, 2)], time=200)
    b.mix('cinnabar/batch_redstone', [I(dust)] * 4,
          [O('minecraft:redstone', 8), O('tfmg:sulfur_dust', chance=0.10), O(mercury, chance=0.02)],
          heat='none', time=b.value('timing.cinnabar_batch', 300),
          comment='Unheated regular mixer, four dust batch; sulfur trace never competes with refining.')
    # Manual heating and damageable hammering are server-side real-player interactions,
    # not crafting/mixing recipes that FakePlayers, shift-crafting or deployers could batch.

    b.mix('alloys/brass', [I('#c:ingots/copper')] * 3 + [I('#c:ingots/zinc')],
          [O('create:brass_ingot', 4)], heat='heated', comment='Intentional alloys belong to the Mixer, not Foundry tanks.')
    b.mix('alloys/bronze', [I('#c:ingots/copper')] * 3 + [I('#c:ingots/tin')],
          [O('mekanism:ingot_bronze', 4)], heat='heated')

    b.add('pgm/crude_exclusive', {'type': 'industrial_colonies:exclusive_milling',
          'ingredients': [I(NS + 'ultramafic_rock')], 'processing_time': 500,
          'recovery_chance': b.value('pgm.crude_recovery_chance', 0.20),
          'results': [O('mekanism:nugget_osmium', chance=0.70),
                      O(b.item('platinum_trace_fragment', texture='minecraft:item/iron_nugget'), chance=0.25),
                      O(b.item('iridium_trace_fragment', texture='minecraft:item/iron_nugget'), chance=0.05)]},
          'ONE weighted result per successful crude roll, never three independent chances.')
    b.melt('pgm/platinum_fragment', NS + 'platinum_trace_fragment', 'platinum', b.value('metals.platinum.trace', 25))
    iridium_value = b.value('metals.iridium.trace', 25)
    if type(iridium_value) is not int or iridium_value <= 0:
        raise ValueError('Iridium trace value must be positive integer mB')
    iridium_divisor = gcd(iridium_value, 1000)
    iridium_inputs, iridium_outputs = 1000 // iridium_divisor, iridium_value // iridium_divisor
    if max(iridium_inputs, iridium_outputs) > 64:
        raise ValueError('Iridium trace arc batch must fit one stack without rounding its mB value')
    b.arc('pgm/iridium_fragment',
          {'basePredicate': I(NS + 'iridium_trace_fragment'), 'count': iridium_inputs},
          [{'basePredicate': I('nuclearcraft:iridium_ingot'), 'count': iridium_outputs}],
          energy=b.value('pgm.iridium_trace_consolidation_energy', 819200),
          time=b.value('pgm.iridium_trace_consolidation_ticks', 1200),
          comment='Forty rare 25 mB fragments electrically consolidate into one 1000 mB Iridium ingot; no unattainable 1800-degree Foundry melt and no value rounding.')
