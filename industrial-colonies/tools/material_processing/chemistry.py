"""Material-specific wet chemistry, reduction and reagent routes.

Only this batch's missing intermediates are registered. Existing TFMG solids/acid,
Mekanism gases and NuclearCraft compounds/isotope entry items remain canonical.
No worldgen, default TFMG refinery recipe, isotope or fuel recipe is authored here.
"""
from math import gcd
from common import F, I, O


def _liquid(fluid, amount):
    # Create processing RESULT codec uses id+amount, not its fluid-ingredient codec.
    return {'id': fluid, 'amount': amount}


def _sized(item, count=1):
    # Installed IE IngredientWithSize codec; an extra count beside item is not it.
    return I(item) if count == 1 else {'basePredicate': I(item), 'count': count}


def build(b):
    def value(key, default):
        return b.value('chemistry.' + key, default)

    def item(name, label=None):
        return b.item(name, label, 'minecraft:item/gunpowder')

    def fluid(name, color=0xFF788870, label=None):
        return b.fluid(name, color, label)

    def vat(path, inputs, outputs, stage='leaching', heat='none', machines=None,
            lining='both', size=1, comment=''):
        times = {'leaching': 480, 'separation': 400, 'precipitation': 320,
                 'reduction': 600, 'electrolysis': 1000, 'reagent': 300}
        b.vat(path, inputs, outputs, heat=heat,
              time=value('timing.' + stage, times[stage]), machines=machines,
              vat=lining, min_size=size, comment=comment)

    def roast(path, source, output, ticks=600, heat='lowheated', count=1,
              comment=''):
        # Actual Create Low Heated extension's basin heat level (root validates
        # the installed enum). No vanilla furnace acquisition is introduced.
        b.mix(path, [I(source)], [O(output, count)], heat=heat,
              time=value('timing.' + path.replace('/', '_'), ticks), comment=comment)

    def melt(path, source, metal, default, temperature=None, comment=''):
        b.melt(path, source, metal, value(metal + '.metal_mb', default),
               temp=temperature, comment=comment)

    def arc(path, source, output, count=1, additives=None, energy=102400,
            ticks=240, comment='', output_count=1):
        b.arc(path, _sized(source, count), [_sized(output, output_count)], additives=additives,
              energy=value('energy.' + path.replace('/', '_'), energy),
              time=value('timing.' + path.replace('/', '_'), ticks), comment=comment)

    def fraction_arc(path, source, metal, default_mb, energy, ticks, comment):
        # Preserve configured fractional value exactly when the available
        # Foundry fuel cannot reach a metal's final consolidation temperature.
        amount = value(metal + '.metal_mb', default_mb)
        if type(amount) is not int or amount <= 0:
            raise ValueError('Arc fraction value must be a positive integer mB: ' + metal)
        divisor = gcd(amount, 1000)
        inputs, outputs = 1000 // divisor, amount // divisor
        if max(inputs, outputs) > 64:
            raise ValueError('Arc fraction batch exceeds one stack; choose an exactly representable mB value: ' + metal)
        arc(path, source, b.metals[metal]['ingot'], count=inputs,
            output_count=outputs, energy=energy, ticks=ticks, comment=comment)

    acid = 'tfmg:sulfuric_acid'
    hydrogen = 'tfmg:hydrogen'
    oxygen = 'mekanism:oxygen'
    chlorine = 'mekanism:chlorine'
    hcl = 'mekanism:hydrogen_chloride'
    caustic = 'nuclearcraft:sodium_hydroxide_dust'
    carbon = 'tfmg:coal_coke_dust'
    slag = 'tfmg:slag'
    water = 'minecraft:water'
    electrodes = ['tfmg:electrode', 'tfmg:electrode']
    waste = fluid('spent_leach_liquor', 0xFF686650, 'Spent Leach Liquor')

    # ZINC: dissolution and precipitation, deliberately NOT fan-washing.
    sphalerite = item('sphalerite_dust')
    zinc_solution = fluid('zinc_bearing_solution', 0xFFA4BFC0)
    zinc_compound = item('zinc_precipitate')
    zinc_dust = 'nuclearcraft:zinc_dust'
    b.crush('zinc/crush_sphalerite', 'industrial_colonies:sphalerite', [O(sphalerite)])
    vat('zinc/leach', [I(sphalerite), F(acid, value('zinc.acid_mb', 100))],
        [_liquid(zinc_solution, 250)], comment='Sulfide dissolution owns Zinc recovery; no Copper-style washing shortcut.')
    vat('zinc/precipitate', [F(zinc_solution, 250), I(caustic)],
        [O(zinc_compound), _liquid(waste, 125)], stage='precipitation')
    vat('zinc/reduce', [I(zinc_compound), I(carbon)], [O(zinc_dust)],
        stage='reduction', heat='heated', lining='firebrick')
    melt('zinc/melt_recovered_dust', zinc_dust, 'zinc', 75, 550)
    b.melt('zinc/direct_sphalerite', 'industrial_colonies:sphalerite', 'zinc',
           value('zinc.direct_mb', 12), temp=420, comment='Brute-force recovery is substantially worse than leaching; its native Zinc temperature is reachable on early solid fuel.')

    # LEAD: roasting then carbon reduction; sulfur is only a trace byproduct.
    galena = item('galena_dust')
    roasted_lead = item('roasted_galena', 'Roasted Galena / Lead Oxide Fraction')
    crude_lead = item('crude_lead_granules')
    pure_lead = item('high_purity_lead')
    b.crush('lead/crush_galena', 'industrial_colonies:galena', [O(galena)])
    b.crush('lead/crush_rich_galena', 'industrial_colonies:rich_galena_ore',
            [O(galena, value('lead.rich_dust', 4))])
    b.mix('lead/roast', [I(galena)],
          [O(roasted_lead), O('tfmg:sulfur_dust', chance=value('lead.sulfur_chance', .015))],
          heat='lowheated', time=value('timing.lead_roasting', 700),
          comment='Oxidative roasting; sulfur recovery is trace-level, never a refinery substitute.')
    vat('lead/carbon_reduction', [I(roasted_lead), I(carbon)],
        [O(crude_lead), O(slag, chance=.2)], stage='reduction', heat='heated', lining='firebrick')
    melt('lead/melt_crude', crude_lead, 'lead', 75, 700)
    vat('lead/purify', [I(crude_lead), F(acid, value('lead.purification_acid_mb', 150))],
        [O(pure_lead), _liquid(waste, 150)], stage='electrolysis', machines=electrodes,
        comment='Optional controlled-grade Lead for shielding and chemical hardware, not another ore multiplier.')
    melt('lead/melt_high_purity', pure_lead, 'lead', 75, 700)
    b.melt('lead/direct_galena', 'industrial_colonies:galena', 'lead',
           value('lead.direct_mb', 15), temp=700)

    # NICKEL/COBALT: mixed feed stays linked through leach/clarification. The
    # mother liquor is consumed by one small cobalt roll; it is never recycled.
    pentlandite = item('pentlandite_dust')
    mixed_nico = fluid('mixed_nickel_cobalt_solution', 0xFF617763)
    clear_nico = fluid('clarified_nickel_cobalt_solution', 0xFF81976E)
    cobalt_mother = fluid('cobalt_bearing_mother_liquor', 0xFF64839F)
    nickel_solution = fluid('nickel_only_solution', 0xFF93A369)
    nickel_compound = item('nickel_precipitate')
    cobalt_compound = item('cobalt_precipitate')
    nickel_concentrate = item('nickel_only_concentrate', 'Nickel Concentrate (No Cobalt)')
    cobalt_concentrate = item('cobalt_rich_concentrate')
    b.crush('nickel/crush_pentlandite', 'industrial_colonies:pentlandite', [O(pentlandite)])
    vat('nickel/mixed_leach', [I(pentlandite), F(acid, value('nickel.acid_mb', 200))],
        [_liquid(mixed_nico, 250)], heat='heated')
    vat('nickel/remove_impurities', [F(mixed_nico, 250), I(caustic)],
        [_liquid(clear_nico, 250), O(slag, chance=.25)], stage='separation')
    vat('nickel/select_nickel', [F(clear_nico, 250), I(caustic)],
        [O(nickel_compound), _liquid(cobalt_mother, 250)], stage='precipitation',
        comment='Nickel precipitates first; the remaining dilute mother liquor is the only low-yield Cobalt branch.')
    vat('cobalt/dilute_recovery', [F(cobalt_mother, 250), F(hcl, 100)],
        [O(cobalt_compound, chance=value('cobalt.pentlandite_recovery_chance', .08)),
         _liquid(waste, 250)], stage='precipitation',
        comment='A single small chance, not guaranteed Cobalt from every Pentlandite and not a rerollable solution.')
    b.crush('nickel/crush_rich_nickel', 'industrial_colonies:rich_nickel_ore',
            [O(nickel_concentrate, value('nickel.rich_concentrates', 4))],
            comment='Intentionally nickel-only: no Cobalt item or mixed Ni/Co solution is produced.')
    vat('nickel/rich_nickel_leach', [I(nickel_concentrate), F(acid, 150)],
        [_liquid(nickel_solution, 250)], heat='heated')
    vat('nickel/precipitate_pure_feed', [F(nickel_solution, 250), I(caustic)],
        [O(nickel_compound), _liquid(waste, 150)], stage='precipitation')
    b.crush('cobalt/crush_rich_cobalt', 'industrial_colonies:cobalt_ore',
            [O(cobalt_concentrate, value('cobalt.rich_concentrates', 4)),
             O(nickel_concentrate, chance=value('cobalt.nickel_byproduct_chance', .25))],
            comment='The reverse asymmetry is intentional: Cobalt-rich ore can contain a smaller Nickel fraction.')
    vat('cobalt/rich_leach', [I(cobalt_concentrate), F(acid, 250), F(hcl, 100)],
        [O(cobalt_compound), _liquid(waste, 250)], heat='heated')
    for metal, compound, powder, amount in [('nickel', nickel_compound, 'immersiveengineering:dust_nickel', 75),
                                            ('cobalt', cobalt_compound, 'nuclearcraft:cobalt_dust', 100)]:
        oxide = item(metal + '_oxide')
        roast(metal + '/roast_precipitate', compound, oxide, heat='heated')
        vat(metal + '/hydrogen_reduce', [I(oxide), F(hydrogen, 250)], [O(powder)],
            stage='reduction', heat='heated', lining='firebrick')
        melt(metal + '/melt_powder', powder, metal, amount, 1400)
        b.claim_outputs.add(powder)

    # ALUMINUM: reuse TFMG Bauxite Powder; remove its direct-electrode shortcut.
    alumina_slurry = fluid('alumina_rich_slurry', 0xFFCBB9A8)
    alumina_solution = fluid('clarified_aluminate_solution', 0xFFE8D9C3)
    alumina = item('alumina')
    aluminum_granules = item('electrolytic_aluminum_granules')
    b.crush('aluminum/crush_bauxite', 'industrial_colonies:bauxite', [O('tfmg:bauxite_powder')])
    b.crush('aluminum/crush_rich_bauxite', 'industrial_colonies:rich_bauxite',
            [O('tfmg:bauxite_powder', value('aluminum.rich_powder', 4))])
    vat('aluminum/caustic_digest', [I('tfmg:bauxite_powder'), I(caustic), F(water, 250)],
        [_liquid(alumina_slurry, 250)], heat='heated')
    vat('aluminum/remove_red_mud', [F(alumina_slurry, 250)],
        [_liquid(alumina_solution, 250), O(slag)], stage='separation')
    vat('aluminum/precipitate_alumina', [F(alumina_solution, 250), F('tfmg:carbon_dioxide', 100)],
        [O(alumina), _liquid(waste, 125)], stage='precipitation')
    vat('aluminum/electrical_reduction', [I(alumina), I('nuclearcraft:graphite_dust')],
        [O(aluminum_granules), _liquid('tfmg:carbon_dioxide', 100)],
        stage='electrolysis', heat='heated', machines=electrodes, lining='firebrick',
        comment='Alumina requires powered vat electrodes. Bauxite cannot be directly melted into Aluminum.')
    melt('aluminum/melt_granules', aluminum_granules, 'aluminum', 75, 1000)
    b.remove_ids.add('tfmg:vat_machine_recipe/aluminum')

    # MAGNESIUM supplies the reusable reductant loop for Titanium.
    dolomite = item('dolomite_dust')
    calcined_mg = item('calcined_dolomite')
    mg_solution = fluid('magnesium_bearing_solution', 0xFFBDBAA8)
    mg_chloride = fluid('magnesium_chloride', 0xFFDEE0C9, 'Purified Magnesium Chloride')
    b.crush('magnesium/crush_dolomite', 'industrial_colonies:dolomite', [O(dolomite)])
    roast('magnesium/calcine', dolomite, calcined_mg, ticks=1000, heat='superheated')
    vat('magnesium/acid_separate', [I(calcined_mg), F(hcl, 250)],
        [_liquid(mg_solution, 250), O(slag, chance=.25)])
    vat('magnesium/purify_chloride', [F(mg_solution, 250), I(caustic)],
        [_liquid(mg_chloride, 250), _liquid(waste, 125)], stage='separation')
    vat('magnesium/electrolyze_chloride', [F(mg_chloride, 250)],
        [O('nuclearcraft:magnesium_dust'), _liquid(chlorine, 250)],
        stage='electrolysis', heat='heated', machines=electrodes, lining='firebrick',
        comment='Electrical recovery returns Magnesium and Chlorine; the Titanium loop returns only the MgCl2 it consumed as Magnesium.')
    melt('magnesium/melt_powder', 'nuclearcraft:magnesium_dust', 'magnesium', 75, 1000)

    # TITANIUM: chloride purification + Magnesium reduction, no direct melting.
    ilmenite = item('ilmenite_dust')
    titanium_concentrate = item('titanium_rich_concentrate')
    crude_ticl4 = fluid('crude_titanium_tetrachloride', 0xFFA59B78)
    pure_ticl4 = fluid('purified_titanium_tetrachloride', 0xFFCFD5D5)
    titanium_sponge = item('titanium_sponge')
    b.crush('titanium/crush_ilmenite', 'industrial_colonies:ilmenite', [O(ilmenite)])
    b.crush('titanium/crush_rich_ilmenite', 'industrial_colonies:rich_ilmenite_ore',
            [O(ilmenite, value('titanium.rich_dust', 4))])
    vat('titanium/remove_iron_impurities', [I(ilmenite), F(acid, 250)],
        [O(titanium_concentrate), O(slag)], heat='heated')
    vat('titanium/chlorinate', [I(titanium_concentrate), I(carbon), F(chlorine, 500)],
        [_liquid(crude_ticl4, 250)], heat='superheated', lining='firebrick')
    vat('titanium/purify_chloride', [F(crude_ticl4, 250)],
        [_liquid(pure_ticl4, 250), O(slag, chance=.1)], stage='separation',
        heat='heated', lining='firebrick')
    vat('titanium/magnesium_reduction', [F(pure_ticl4, 250),
        I('nuclearcraft:magnesium_dust'), I('nuclearcraft:magnesium_dust')],
        [O(titanium_sponge), _liquid(mg_chloride, 500)],
        stage='reduction', heat='superheated', lining='firebrick',
        comment='Two Magnesium units become two electrolyzer batches of MgCl2; recovery costs energy and never multiplies Magnesium.')
    arc('titanium/consolidate_sponge', titanium_sponge, 'nuclearcraft:titanium_ingot',
        count=value('titanium.sponge_per_ingot', 8), energy=204800, ticks=600,
        comment='Powered refractory consolidation is available before Industrial Iron, whose construction consumes Titanium.')

    # TUNGSTEN: tungstate precipitation, hydrogen reduction, electrical sintering.
    wolframite = item('wolframite_dust')
    tungstate = fluid('tungstate_solution', 0xFF829196)
    tungsten_precipitate = item('tungstate_precipitate')
    tungsten_oxide = item('tungsten_oxide')
    b.crush('tungsten/crush_wolframite', 'industrial_colonies:wolframite_rock', [O(wolframite)])
    b.crush('tungsten/crush_rich_wolframite', 'industrial_colonies:rich_wolframite_ore',
            [O(wolframite, value('tungsten.rich_dust', 4))])
    vat('tungsten/alkaline_leach', [I(wolframite), I(caustic), F(water, 250)],
        [_liquid(tungstate, 250), O(slag)], heat='heated')
    vat('tungsten/precipitate', [F(tungstate, 250), F(hcl, 150)],
        [O(tungsten_precipitate), _liquid(waste, 125)], stage='precipitation')
    roast('tungsten/oxide', tungsten_precipitate, tungsten_oxide, heat='heated')
    vat('tungsten/hydrogen_reduce', [I(tungsten_oxide), F(hydrogen, 500)],
        [O('nuclearcraft:tungsten_dust')], stage='reduction', heat='superheated', lining='firebrick')
    arc('tungsten/sinter', 'nuclearcraft:tungsten_dust', 'nuclearcraft:tungsten_ingot',
        count=value('tungsten.powder_per_ingot', 8), energy=409600, ticks=800,
        comment='Tungsten requires high-energy sintering; ordinary Foundry melting must not bypass this powder-consolidation stage.')

    # CHROMIUM: fan tier is a capability restriction, not just a JEI label.
    chromite = item('chromite_dust')
    conditioned_chromite = item('alkaline_roasted_chromite')
    chromium_fraction = item('chromium_bearing_fraction')
    chromium_compound = item('chromium_precipitate')
    b.crush('chromium/crush_chromite', 'industrial_colonies:chromite', [O(chromite)])
    b.crush('chromium/crush_rich_chromite', 'industrial_colonies:rich_chromium_ore',
            [O(chromite, value('chromium.rich_dust', 4))])
    b.mix('chromium/alkaline_roast', [I(chromite), I(caustic)], [O(conditioned_chromite)],
          heat='superheated', time=value('timing.chromium_conditioning', 800))
    b.add('chromium/industrial_iron_separation', {
        'type': 'industrial_colonies:industrial_iron_splashing',
        'ingredients': [I(conditioned_chromite)],
        'results': [O(chromium_fraction), O(slag, chance=.25)]},
        'ONLY the Industrial Iron encased fan can separate this conditioned feed; base and Weathered Iron fans must reject it. Native fan processing uses Create global timing, not a per-recipe duration field.')
    vat('chromium/purify', [I(chromium_fraction), F(acid, 250)],
        [O(chromium_compound), _liquid(waste, 125)], stage='precipitation', heat='heated')
    vat('chromium/reduce', [I(chromium_compound), F(hydrogen, 500)],
        [O('nuclearcraft:chromium_dust')], stage='reduction', heat='superheated', lining='firebrick')
    arc('chromium/consolidate', 'nuclearcraft:chromium_dust', 'nuclearcraft:chromium_ingot',
        count=value('chromium.powder_per_ingot', 8), energy=204800, ticks=500)

    # LITHIUM: thermal activation then wet chemistry and mandatory electrodes.
    spodumene = item('spodumene_dust')
    active_spodumene = item('activated_spodumene')
    lithium_solution = fluid('lithium_bearing_solution', 0xFFC4AECE)
    lithium_compound = item('lithium_precipitate')
    b.crush('lithium/crush_spodumene', 'industrial_colonies:spodumene_rock', [O(spodumene)])
    b.crush('lithium/crush_rich_spodumene', 'industrial_colonies:spodumene_ore',
            [O(spodumene, value('lithium.rich_dust', 4))])
    roast('lithium/activate', spodumene, active_spodumene, ticks=800, heat='heated')
    vat('lithium/leach', [I(active_spodumene), F(acid, 200)],
        [_liquid(lithium_solution, 250)])
    vat('lithium/precipitate', [F(lithium_solution, 250), I(caustic)],
        [O(lithium_compound), _liquid(waste, 150)], stage='precipitation')
    vat('lithium/electrical_reduction', [I(lithium_compound), F(hcl, 150)],
        [O('nuclearcraft:lithium_dust')], stage='electrolysis', heat='heated',
        machines=electrodes, lining='firebrick')
    melt('lithium/melt_powder', 'nuclearcraft:lithium_dust', 'lithium', 60, 700,
         'The molten endpoint casts canonical TFMG Lithium; the metal was electrically reduced before melting.')

    # SILVER: controlled roasting followed by leach and precipitation.
    argentite = item('argentite_dust')
    roasted_silver = item('roasted_argentite')
    silver_solution = fluid('silver_bearing_solution', 0xFFB6C2D1)
    b.crush('silver/crush_argentite', 'industrial_colonies:argentite', [O(argentite)])
    b.crush('silver/crush_rich_silver', 'industrial_colonies:rich_silver_ore',
            [O(argentite, value('silver.rich_dust', 4))])
    roast('silver/roast', argentite, roasted_silver, ticks=700)
    vat('silver/leach', [I(roasted_silver), F(acid, 150)], [_liquid(silver_solution, 250)])
    vat('silver/precipitate', [F(silver_solution, 250), I(caustic)],
        [O('nuclearcraft:silver_dust'), _liquid(waste, 125)], stage='precipitation')
    melt('silver/melt_powder', 'nuclearcraft:silver_dust', 'silver', 60, 1100)
    b.melt('silver/direct_argentite', 'industrial_colonies:argentite', 'silver',
           value('silver.direct_mb', 12), temp=1000)

    # PHOSPHATE is primarily an acid/compound feedstock, not immediate Phosphorus.
    phosphate = item('phosphate_dust')
    roasted_phosphate = item('conditioned_phosphate')
    phosphoric_acid = fluid('phosphoric_acid', 0xFFCDC398)
    purified_phosphate = item('purified_phosphate_compound')
    phosphorus = item('elemental_phosphorus', 'Elemental Phosphorus')
    b.crush('phosphate/crush', 'industrial_colonies:phosphate_rock', [O(phosphate)])
    roast('phosphate/condition', phosphate, roasted_phosphate, ticks=1200)
    vat('phosphate/acid_extract', [I(roasted_phosphate), F(acid, 250)],
        [_liquid(phosphoric_acid, 250), O(slag)], heat='heated')
    vat('phosphate/precipitate', [F(phosphoric_acid, 250), I(caustic)],
        [O(purified_phosphate), _liquid(waste, 125)], stage='precipitation')
    b.mix('phosphate/fertilizer', [I(purified_phosphate), I('tfmg:nitrate_dust'), I('minecraft:bone_meal')],
          [O('minecraft:bone_meal', value('phosphate.fertilizer_output', 6))],
          time=value('timing.fertilizer', 200), comment='A consumed phosphate/nitrate feed gives an early useful chemical product without elemental Phosphorus.')
    arc('phosphate/elemental_reduction', purified_phosphate, phosphorus,
        count=value('phosphate.compound_per_elemental', 4), additives=[_sized(carbon, 2)],
        energy=307200, ticks=800,
        comment='Elemental Phosphorus is a later high-temperature carbon reduction, not the first washing output.')

    # GRAPHITE: NC already owns Graphite Dust and a solid Graphite form; coal
    # is neither an output nor a substitute for the high-purity treatment here.
    graphite_concentrate = item('graphite_concentrate')
    pure_graphite = 'nuclearcraft:graphite_ingot'
    high_graphite = item('high_purity_graphite')
    b.crush('graphite/crush', 'industrial_colonies:graphite_rock', [O('nuclearcraft:graphite_dust')])
    b.mix('graphite/mechanical_separation', [I('nuclearcraft:graphite_dust'), F(water, 250)],
          [O(graphite_concentrate), O('minecraft:gravel', chance=.2)],
          time=value('timing.graphite_agitation', 400))
    vat('graphite/chemical_purification', [I(graphite_concentrate), F(acid, 250)],
        [O(pure_graphite), _liquid(waste, 250)], heat='heated')
    arc('graphite/high_temperature_purification', pure_graphite, high_graphite,
        energy=153600, ticks=600, comment='High-purity industrial Carbon is electrode/refractory feed, not fuel progression.')
    b.claim_outputs.update({'nuclearcraft:graphite_dust', pure_graphite})

    # BERYLLIUM: every grade passes precipitation, oxide formation and advanced
    # reduction. The dilute feed never directly melts to valuable metal.
    bertrandite = item('bertrandite_dust')
    beryllium_solution = fluid('beryllium_bearing_solution', 0xFFBCDCB9)
    beryllium_compound = item('beryllium_precipitate')
    beryllium_oxide = item('beryllium_oxide')
    b.crush('beryllium/crush', 'industrial_colonies:bertrandite', [O(bertrandite)])
    vat('beryllium/leach', [I(bertrandite), F(acid, 300)],
        [_liquid(beryllium_solution, 250)], heat='heated')
    vat('beryllium/precipitate', [F(beryllium_solution, 250), I(caustic)],
        [O(beryllium_compound), _liquid(waste, 250)], stage='precipitation')
    roast('beryllium/oxide', beryllium_compound, beryllium_oxide, ticks=1000, heat='superheated')
    vat('beryllium/electrochemical_reduce', [I(beryllium_oxide), F(hcl, 250)],
        [O('nuclearcraft:beryllium_dust')], stage='electrolysis', heat='superheated',
        machines=electrodes, lining='firebrick', size=9)
    melt('beryllium/melt_powder', 'nuclearcraft:beryllium_dust', 'beryllium', 40, 1400)

    # BORON: reuse the already registered Boric Acid fluid, no duplicate acid.
    borax = 'nuclearcraft:borax_dust'
    borate_solution = fluid('purified_borate_solution', 0xFFD7E0C0)
    boron_oxide = item('boron_oxide')
    b.crush('boron/crush', 'industrial_colonies:borax_rock', [O(borax)])
    vat('boron/dissolve', [I(borax), F(water, 250)],
        [_liquid(borate_solution, 250), O(slag, chance=.15)])
    vat('boron/acid_treat', [F(borate_solution, 250), F(acid, 150)],
        [_liquid('nuclearcraft:boric_acid', 250)], stage='precipitation')
    vat('boron/dehydrate', [F('nuclearcraft:boric_acid', 250)], [O(boron_oxide)],
        stage='separation', heat='heated', lining='firebrick')
    vat('boron/advanced_reduction', [I(boron_oxide), I('nuclearcraft:magnesium_dust'), F(hcl, 100)],
        [O('nuclearcraft:boron_dust'), _liquid(mg_chloride, 250)],
        stage='reduction', heat='superheated', lining='firebrick', size=9)
    fraction_arc('boron/consolidate_powder', 'nuclearcraft:boron_dust', 'boron', 60,
                 energy=409600, ticks=800,
                 comment='Fifty chemically reduced 60 mB Boron fractions consolidate into three 1000 mB ingots. Native Foundry fuel stops at 1500, so electrical consolidation replaces an unreachable 2000-degree melt.')

    # NUCLEAR HANDOFF: chemical concentrate -> refined feed -> NC dust entry.
    # Existing isotope separators/fuel fabrication retain ownership thereafter.
    for metal, source in [('uranium', 'uraninite'), ('thorium', 'thorium_ore')]:
        dust = item(metal + '_bearing_dust')
        concentrate = item(metal + '_concentrate')
        compound = item('refined_' + metal + '_compound')
        slurry = 'nuclearcraft:' + metal + '_slurry'
        b.crush(metal + '/physical_preparation', 'industrial_colonies:' + source, [O(dust)])
        vat(metal + '/leach', [I(dust), F(acid, value(metal + '.acid_mb', 400))],
            [_liquid(slurry, 250)], heat='heated')
        vat(metal + '/remove_impurities', [F(slurry, 250), I(caustic)],
            [O(concentrate), _liquid(waste, 250)], stage='precipitation')
        vat(metal + '/refine_compound', [I(concentrate), F(hcl, 250), F(oxygen, 100)],
            [O(compound)], stage='separation', heat='heated', lining='firebrick')
        vat(metal + '/nuclear_feed', [I(compound), F(hydrogen, 250)],
            [O('nuclearcraft:' + metal + '_dust')], stage='reduction', heat='superheated',
            lining='firebrick', comment='Refined feed enters existing NuclearCraft isotope separation; no direct ore-to-ingot or fuel recipe is introduced.')
        b.claim_outputs.update({slurry, 'nuclearcraft:' + metal + '_dust'})
        b.remove_ids.add('nuclearcraft:leacher/' + metal + '_slurry')

    # PGMs: three sequential selective recoveries, never a magic one-vat
    # output of all three metals. Separate rich ores remain single-metal feeds.
    ultramafic = item('ultramafic_dust')
    pgm_solution = fluid('mixed_pgm_solution', 0xFF606A78)
    ptir_solution = fluid('platinum_iridium_mother_liquor', 0xFF767088)
    ir_residue = item('iridium_bearing_refractory_residue')
    os_fraction = item('osmium_bearing_fraction')
    pt_fraction = item('platinum_bearing_fraction')
    ir_fraction = item('purified_iridium_fraction')
    b.crush('pgm/crush_ultramafic', 'industrial_colonies:ultramafic_rock', [O(ultramafic)])
    vat('pgm/aggressive_leach', [I(ultramafic), I(ultramafic), I(ultramafic), I(ultramafic),
        F(acid, 1000), F(hcl, 500)], [_liquid(pgm_solution, 1000)],
        heat='superheated', lining='firebrick', size=9)
    vat('pgm/osmium_first', [F(pgm_solution, 1000), F(oxygen, 250)],
        [O(os_fraction, value('pgm.osmium_fractions', 7)), _liquid(ptir_solution, 1000)],
        stage='separation', heat='heated', lining='firebrick', size=9)
    vat('pgm/platinum_second', [F(ptir_solution, 1000), F(hcl, 500), I(caustic)],
        [O(pt_fraction, value('pgm.platinum_fractions', 2)),
         O(pt_fraction, chance=value('pgm.platinum_extra_chance', .5)),
         O(ir_residue, chance=value('pgm.iridium_fraction_chance', .5)), _liquid(waste, 1000)],
        stage='precipitation', heat='heated', lining='firebrick', size=9,
        comment='Across a four-rock batch, expected small fractions retain the 70/25/5 bias; Iridium is a refractory residue, not a ready metal.')
    vat('pgm/iridium_harsh_purification', [I(ir_residue), F(acid, 750), F(chlorine, 500)],
        [O(ir_fraction), _liquid(waste, 750)], stage='separation', heat='superheated', lining='firebrick', size=9)
    for metal, block, fraction, powder in [
        ('osmium', 'rich_osmium_ore', os_fraction, 'mekanism:dust_osmium'),
        ('platinum', 'rich_platinum_ore', pt_fraction, 'nuclearcraft:platinum_dust'),
        ('iridium', 'rich_iridium_ore', ir_residue, 'nuclearcraft:iridium_dust')]:
        rich = item('rich_' + metal + '_concentrate')
        b.crush('pgm/crush_rich_' + metal, 'industrial_colonies:' + block,
                [O(rich, value('pgm.' + metal + '_rich_concentrates', 4))])
        vat('pgm/leach_rich_' + metal, [I(rich), F(acid, 400), F(hcl, 250)],
            [O(fraction), _liquid(waste, 250)], heat='superheated', lining='firebrick', size=9)
        feed = ir_fraction if metal == 'iridium' else fraction
        vat('pgm/reduce_' + metal, [I(feed), F(hydrogen, 500)], [O(powder)],
            stage='reduction', heat='superheated', lining='firebrick', size=9)
        if metal == 'iridium':
            arc('pgm/consolidate_iridium', powder, 'nuclearcraft:iridium_ingot',
                count=value('pgm.iridium_powder_per_ingot', 20), energy=819200, ticks=1200,
                comment='The rare refractory fraction needs the harshest purification and high-energy final consolidation.')
        else:
            fraction_arc('pgm/consolidate_' + metal, powder, metal, 50,
                         energy=204800 if metal == 'osmium' else 409600,
                         ticks=600 if metal == 'osmium' else 800,
                         comment='Twenty reduced 50 mB fractions consolidate into one 1000 mB ingot with native electrical equipment; no nonexistent high-temperature Foundry fuel is required.')
        b.claim_outputs.add(powder)

    # REAGENTS: Mekanism remains the gas producer; vats consume compatible
    # fluids. Existing TFMG acid remains the only player-facing acid fluid.
    b.add('reagents/hydrogen_rotary_bridge', {
        'type': 'mekanism:rotary',
        'chemical_input': {'amount': 1, 'chemical': 'mekanism:hydrogen'},
        'chemical_output': {'amount': 1, 'id': 'mekanism:hydrogen'},
        'fluid_input': {'amount': 1, 'fluid': hydrogen},
        'fluid_output': {'amount': 1, 'id': hydrogen}},
        'Mekanism hydrogen chemical supplies the existing TFMG hydrogen fluid instead of a duplicate custom gas.')
    b.remove_ids.add('mekanism:rotary/hydrogen')
    # This is the pre-Aluminum electrical bootstrap, not a free hydroxide
    # craft. Salt is an existing underwater mineral. Keep the native 15 mB /
    # salt conversion: a richer mixer output would duplicate salt through the
    # unchanged Mekanism rotary + crystallizer route.
    b.mix('reagents/dissolve_salt', [I('#c:dusts/salt'), F(water, 15)],
          [_liquid('mekanism:brine', 15)], time=value('timing.salt_dissolution', 300),
          comment='One existing Salt becomes 15 mB Brine, matching native Mekanism salt recovery exactly; no new sediment or free-salt route.')
    vat('reagents/bootstrap_brine_electrolysis',
        [F('mekanism:brine', 30), F(water, 250)],
        [O(caustic), _liquid(chlorine, 2), _liquid(hydrogen, 1)],
        stage='electrolysis', machines=electrodes,
        comment='Powered two-electrode TFMG vat supplies the first caustic before Aluminum-dependent electronics. Two mined Salt units per hydroxide; not hand-crafting or smelting.')
    vat('reagents/caustic_soda', [F('mekanism:sodium', 1), F(water, 250)],
        [O(caustic), _liquid(hydrogen, 1)], stage='reagent',
        comment='Reuse NuclearCraft sodium hydroxide. Later Mekanism brine electrolysis uses 10 mB Brine per Sodium and improves reagent recovery over the 30 mB bootstrap.')
    vat('reagents/contact_acid_hydration', [F('mekanism:sulfur_trioxide', 250), F(water, 250)],
        [_liquid(acid, 250)], stage='reagent',
        comment='Sulfur → Mekanism SO2 → SO3; final hydration still belongs to the Chemical Vat and outputs canonical TFMG acid.')

    # A SIDE STREAM, not a rewritten refinery: consume existing heavy oil with
    # Hydrogen, retain most of that heavy fraction and recover captured sulfide.
    desulfurized_oil = fluid('desulfurized_heavy_oil', 0xFF353323)
    sour_gas = fluid('captured_refinery_sulfide', 0xFFBBC379)
    vat('sulfur/refinery_side_stream', [F('tfmg:heavy_oil', 1000), F(hydrogen, 250)],
        [_liquid(desulfurized_oil, 900), _liquid(sour_gas, 500)],
        stage='reagent', heat='heated', lining='firebrick', size=9,
        comment='Optional finite-feed refinery desulfurization, leaving TFMG crude/heavy distillation recipes untouched.')
    vat('sulfur/recover_refinery_sulfur', [F(sour_gas, 500), F(oxygen, 250)],
        [O('tfmg:sulfur_dust', value('sulfur.refinery_dust_per_batch', 8)), _liquid(water, 250)],
        stage='reagent', heat='heated',
        comment='Oil is deliberately the bulk Sulfur source; sulfide-rock byproducts are only small chance traces.')
    # Preserve native heavy-oil distillation's exact 200 -> 100/25/50/20/5
    # composition. Its remaining heavy fraction stays DESULFURIZED: returning
    # native heavy_oil would permit repeated sulfur extraction from one feed.
    b.add('sulfur/desulfurized_oil_distillation', {
        'type': 'tfmg:distillation', 'ingredients': [F(desulfurized_oil, 200)],
        'results': [_liquid(desulfurized_oil, 100), _liquid('tfmg:lubrication_oil', 25),
                    _liquid('tfmg:diesel', 50), _liquid('tfmg:kerosene', 20),
                    _liquid('tfmg:naphtha', 5)],
        'processing_time': value('timing.desulfurized_oil_distillation', 100)},
        'Native heavy-oil product ratios are retained. The recirculated heavy fraction stays desulfurized and cannot return to the sulfur extractor; native refining is not overridden.')
    b.remove_ids.update({
        'industrial_colonies:sulfur/coal_gasification_blocks_coals',
        'industrial_colonies:sulfur/coal_gasification_coals',
        'industrial_colonies:sulfur/coal_gasification_dusts_coals',
        'industrial_colonies:sulfur/gunpowder_recovery',
        'mekanism:reaction/coal_gasification/blocks_coals',
        'mekanism:reaction/coal_gasification/coals',
        'mekanism:reaction/coal_gasification/dusts_coals',
        'mekanism:injecting/gunpowder_to_sulfur',
        'mekanism:chemical_infusing/sulfuric_acid',
        'mekanism:chemical_conversion/sulfur_to_sulfuric_acid',
        'nuclearcraft:chemical_reactor/sulfuric_acid',
    })
    b.claim_outputs.update({
        zinc_dust, 'tfmg:bauxite_powder', 'nuclearcraft:magnesium_dust',
        'nuclearcraft:lithium_dust', 'nuclearcraft:silver_dust',
        'nuclearcraft:tungsten_dust', 'nuclearcraft:chromium_dust',
        'nuclearcraft:beryllium_dust', 'nuclearcraft:boron_dust', borax,
    })
