"""Carbon/silicon quality grades culminate in a deliberately costly engineered Radiance."""
from common import I, O, F, NS


def S(item, count=1):
    return {'basePredicate': I(item), 'count': count}


def build(b):
    silica = b.item('fine_silica_dust', texture='minecraft:item/quartz')
    silicon = 'tfmg:silicon_ingot'  # Reuse the pack's metallurgical silicon, not a second silicon ingot.
    high = b.item('high_purity_silicon', texture='tfmg:item/silicon_ingot')
    refined_feed = b.item('purified_silicon_precursor', texture='minecraft:item/quartz')
    b.crush('silicon/sand', '#minecraft:sand', [O(silica)], time=400,
            comment='Abundant sand is a feedstock, not instantly usable semiconductor silicon.')
    b.vat('silicon/carbon_reduction', [I(silica)] * 3 + [I('tfmg:coal_coke_dust')],
          [O(silicon)], heat='superheated', time=b.value('timing.silicon_reduction', 1200),
          vat='firebrick', comment='High-temperature carbothermal reduction provides only metallurgical grade.')
    b.vat('silicon/chloride_purification', [I(silicon), F('mekanism:hydrogen_chloride', 500)],
          [O(refined_feed)], time=800, comment='Chemical cleanup is distinct from the high-temperature reduction.')
    b.vat('silicon/high_purity', [I(refined_feed), F('tfmg:hydrogen', 500)],
          [O(high)], heat='superheated', time=1000, vat='firebrick')
    b.claim_outputs.add(silicon)
    # Existing TFMG semiconductors and IC wafers remain the electronic identities.
    for polarity, dopant in [('n', F(NS + 'phosphoric_acid', 25)), ('p', I('nuclearcraft:boron_dust'))]:
        # Phosphate doping consumes the processed acid, not an invented free
        # elemental phosphorus dust. These are optional higher-grade routes.
        b.vat('silicon/' + polarity + '_semiconductor', [I(high), dopant],
              [O('tfmg:' + polarity + '_semiconductor', 2)], heat='heated', time=600,
              machines=['tfmg:electrode', 'tfmg:electrode'])
    b.add('silicon/wafer_cutting', {'type': 'create:cutting', 'ingredients': [I(high)],
          'results': [O('industrial_colonies:prepared_silicon_wafer', 2)], 'processing_time': 400},
          'High-purity silicon feeds the already-registered wafer; no duplicate wafer item.')
    # Keep lower-grade electronics/wafer routes for Weathered bootstrap. Industrial
    # machine construction independently consumes high_purity_silicon, so it cannot
    # evade its purity requirement through those existing electronic components.

    # Native IE coke -> hop graphite is kept as the furnace electrode bootstrap;
    # purified natural graphite is a second real carbon-electrode feed, not fuel.
    b.vat('graphite/electrode_feed', [I('nuclearcraft:graphite_ingot'), F('minecraft:water', 250)],
          [O('immersiveengineering:dust_hop_graphite', 2)], time=400)

    refractory = b.item('high_purity_refractory_lattice', texture='minecraft:item/netherite_ingot')
    matrix = b.item('rare_pgm_matrix', texture='minecraft:item/iron_ingot')
    substrate = b.item('radiant_silicon_substrate', texture='tfmg:item/p_semiconductor')
    precursor = b.item('radiant_precursor', texture='create:item/chromatic_compound_0')
    pressure = b.item('pressure_conditioned_radiant_composite', texture='create:item/chromatic_compound_0')
    b.arc('radiance/refractory_lattice', S('nuclearcraft:titanium_ingot', 16),
          [I(refractory)], additives=[S('nuclearcraft:tungsten_ingot', 16), S(NS + 'high_purity_graphite', 4)],
          energy=b.value('radiance.refractory_energy', 2000000), time=2400,
          comment='Sixteen Ti plus sixteen W form one refractory lattice; no electronics shortcut.')
    b.mix('radiance/pgm_matrix', [I('mekanism:ingot_osmium')] * 4 + [I('nuclearcraft:platinum_ingot')] * 2 +
          [I('nuclearcraft:iridium_ingot')], [O(matrix)], heat='superheated', tier='industrial_iron', time=1200,
          comment='Scarce iridium is mandatory; all three PGM industries feed the capstone.')
    b.arc('radiance/silicon_substrate', S(high, 8), [I(substrate)],
          additives=[S('tfmg:p_semiconductor', 2)], energy=1000000, time=1200)
    b.mix('radiance/composite', [I(refractory)] * 2 + [I(matrix)] * 2 + [I(substrate)] * 2 +
          [F('tfmg:sulfuric_acid', 1000)], [O(precursor)], heat='superheated', tier='industrial_iron', time=2400)
    b.add('radiance/pressure_treatment', {'type': 'mekanism:reaction',
          'item_input': {'item': precursor, 'count': 1},
          'fluid_input': {'fluid': 'nuclearcraft:boric_acid', 'amount': 1000},
          'chemical_input': {'chemical': 'mekanism:hydrogen_chloride', 'amount': 8192},
          'item_output': O(pressure), 'duration': b.value('radiance.pressure_ticks', 12500),
          'energy_required': b.value('radiance.pressure_extra_joules_per_tick', 1600)},
          'Native PRC energy_required is EXTRA JOULES PER TICK: 1600 x 12500 / installed 2.5 J per FE = 8 million extra FE before upgrades. Total 1605 J/t fits its native 2000 J buffer; machine upgrades retain their normal effects.')
    b.arc('radiance/stabilization', pressure, [I('create:refined_radiance')],
          additives=[S(NS + 'high_purity_graphite', 4)],
          energy=b.value('radiance.stabilization_energy', 16000000), time=6000,
          comment='One final Radiance from costly precursor; extreme electrical consolidation, no Allthemodium.')
    b.claim_outputs.add('create:refined_radiance')

    coal_tar = b.fluid('coal_tar', 0xFF252017, 'Coal Tar')
    b.crush('coal/pulverize', 'minecraft:coal', [O('mekanism:dust_coal')], time=200)
    b.add('coal/coke_dust', {'type': 'tfmg:coking', 'ingredients': [I('#c:dusts/coal')],
          'results': [O('tfmg:coal_coke'), {'id': coal_tar, 'amount': 100}, {'id': 'tfmg:hydrogen', 'amount': 20}],
          'processing_time': b.value('timing.pulverized_coal_coking', 1200)},
          'An additional coke-oven feed, not a rewrite of native Coal fuel, coking, oil or power.')
    b.add('coal/tar_fractionation', {'type': 'tfmg:distillation',
          'ingredients': [F(coal_tar, 1000)],
          'results': [{'id': 'tfmg:creosote', 'amount': 700}, {'id': 'tfmg:naphtha', 'amount': 150}],
          'processing_time': b.value('timing.coal_tar_fractionation', 100)},
          'Coal Tar is a finite chemical feedstock; no coal-derived sulfur farm.')
