"""Hand-authored corrections from the second September 4 recipe audit.

Grid symbols refer to the previous bill of materials in input/step order.
The layouts are explicit per machine, never generated borders or padding.
"""
from __future__ import annotations
import copy
import re
from recipe_design_v6_review_20260904 import _mechanical, _replace_process, _output

# A is the base; B onward are successive physical subassemblies of the old BOM.
# Repeated glyphs deliberately install paired hardware (rollers, ports, etc.).
LAYOUTS = {
    'grid/alternator_brushes': [' B ', 'DCD', 'AEA'],
    'high_voltage/transformer_core': [' EE ', 'ABCD', ' FF '],
    'high_voltage/current_transformer': [' B C', 'EAFE', ' DR '],
    'computercraft/computer/normal': [' EFE', 'BADC', 'GDDG', 'HIIH'],
    'computercraft/io/disk_drive': [' CCC', ' A B', 'GD EG', 'HFFH'],
    'computercraft/io/speaker': [' E ', 'BAB', 'CD '],
    'computercraft/io/redstone_relay': [' EF ', 'CBAD', ' BF '],
    'computercraft/computer/advanced_upgrade': [' F ', 'BAC', 'DED'],
    'digital_core/block_reader': [' BC ', ' A D', ' E  '],
    'digital_core/energy_detector': [' B ', 'CAD', ' E '],
    'digital_core/inventory_manager': [' D ', 'EAC', ' BF'],
    'digital_core/colony_integrator': [' CE', ' DA', ' B '],
    'computer_network_coverage/chat_box': [' DC ', ' B A', ' FE '],
    'computer_network_coverage/environment_detector': [' B ', 'CAD', ' EF'],
    'computer_network_coverage/nbt_storage': [' BB ', 'CAF', ' DE'],
    'tfmg_heavy_electrical/portable_energy_interface': [' BC ', 'BADC', ' EE '],
    'tfmg_heavy_electrical/digital_adapter': [' DE', 'BAF', ' CC'],
    'tfmg_heavy_electrical/transformer': [' B C ', 'DBACD', ' FEF '],
    'tfmg_heavy_electrical/voltage_observer': [' B ', 'CAD', ' FE'],
    'digital_core/energy_acceptor': [' B ', 'DACE', ' F  '],
    'digital_core/interface': [' A A', 'BCDB', 'FEHG', ' III'],
    'digital_core/molecular_assembler': [' B B ', ' CAD ', ' IEJ ', ' HFGH'],
    'digital_core/pattern_provider': [' C  ', 'DBAE', ' HG ', ' IF '],
    'mekanism/combiner': [' B  ', 'GCG ', 'EAD ', 'HFFH'],
    'mekanism_pre_nuclear/osmium_compressor': [' E  ', 'CBD ', 'GAF ', 'IHHI'],
    'mekanism_pre_nuclear/chemical_oxidizer': [' DC  ', 'EBAK ', ' FL  ', ' GIJ '],
    'mekanism_pre_nuclear/chemical_infuser': [' C C ', 'DBEA ', 'FLFK ', ' JIH ', '  G  '],
    'mekanism_pre_nuclear/pressurized_reaction_chamber': [' DEF ', 'GCG  ', 'KBLA ', 'HIMJ '],
    'mekanism_nuclear/purification_chamber': [' DC ', 'BAB ', ' EF '],
    'mekanism_nuclear/chemical_injection_chamber': [' B ', 'DCA', ' FE'],
    'mekanism_nuclear/chemical_dissolution_chamber': [' C D', 'EAE ', 'GBG ', ' FH '],
    'mekanism_nuclear/chemical_washer': [' A C', 'EDE ', ' B F', ' G  '],
    'mekanism_nuclear/chemical_crystallizer': [' C ', 'DBD', 'EAE', ' F '],
    'mekanism_nuclear/solar_neutron_activator': [' BBB ', ' C  ', 'DAE ', ' F  '],
    'mekanism_nuclear/sps_port': [' E ', 'FADF', ' BC '],
    'space/life_support/oxygen_sensor': [' A  ', 'CBDE', ' GF ', 'JHIJ'],
    'space/navigation/velocity_sensor': [' D ', 'BAC', 'GEG', ' F '],
    'space/navigation/gimbal_sensor': [' BC ', 'BAFH', ' GED'],
    'space/navigation/optical_sensor': [' CD ', 'BAEB', ' IHF', ' JG '],
    'planetary/outpost/nutritional_liquifier': [' B  ', 'ECD ', 'GAF ', ' HI '],
    'create_core/rotation_speed_controller': [' B ', 'ECD', 'FAH', ' IG'],
    'create_core/redstone_link_pair': [' B B', 'DC CD', ' EA E'],
    'create_core/display_link': [' B ', 'DAC', ' E '],
    'create_core/packager': [' B ', 'CAE', ' D '],
    'create_core/repackager': [' B ', 'CAE', ' D '],
    'create_core/stock_link': [' B ', 'DAC', ' E '],
    'create_core/stock_ticker': [' B ', 'CAD', ' E '],
    'create_core/factory_gauge': [' D ', 'BAC', ' E '],
    'create_addons/connected_dashboard': [' BD', ' CE', ' AA'],
    'create_addons/inventory_access_port_batch': [' B B', ' CAD', '  E '],
    'create_addons/inventory_bridge': [' C  ', 'ADBF', ' EE '],
    'create_addons/centrifugal_clutch': [' B ', 'CAD', ' E '],
    'create_addons/overstress_clutch': [' B ', 'CAE', ' D '],
    'create_addons/factory_controller': [' FBC', ' AED', ' GGG'],
    'create_addons/labeling_station': [' BC ', ' D  ', 'EAFE'],
    'create_addons/fuse_holder_batch': [' G H', 'BEFC', 'DAID'],
    'create_addons/cut_off_switch': [' D ', 'CBC', 'FAE'],
    'create_addons/electrical_relay': [' D ', 'EABE', ' C '],
    'create_addons/redstone_relay': [' D ', 'CABE', ' B  '],
    'create_addons/energy_meter': [' BF C', ' DA ', ' E  '],
    'create_addons/tri_polar_energy_meter': [' CDE ', ' B  ', 'FAHG'],
    'createaddition_coverage/rolling_mill': [' BB ', 'DAC ', 'EFF '],
    'mekanism/thermal_evaporation/controller': [' D ', 'FBF', 'CAG', ' E '],
    'mekanism/boiler/superheating_element': [' GGG', 'ECBE', ' FAG', ' D  '],
    'mekanism/laser/emitter': [' E ', 'CAD', 'GBG', ' F '],
    'simulated/altitude_sensor': [' BC ', ' DA ', 'GFEH'],
    'simulated/redstone_magnet': [' B ', 'CAD', ' B '],
    'simulated/directional_linked_receiver': [' B ', 'CAD', ' E '],
    'simulated/modulating_linked_receiver': [' B ', 'CAD', ' E '],
    'mekanism_utility/resistive_heater': [' DCD', ' BAG', ' EF '],
    'electroenergetics/grid_meter': [' E ', 'BAD', ' C '],
    'electroenergetics/variac': [' C ', 'BAD', ' EF'],
    'mekanism_pre_nuclear/modification_station': [' C  ', 'DBE ', 'FAGH', ' I  '],
    'mekanism_pre_nuclear/pigment_extractor': [' B  ', 'EDC ', 'IAF ', ' GH '],
    'mekanism_pre_nuclear/pigment_mixer': [' BCB ', 'DAE  ', ' FGH '],
    'mekanism_pre_nuclear/painting_machine': [' B C', ' FD ', 'GAE ', ' HI '],
    'mekanism_pre_nuclear/seismic_vibrator': [' C C ', ' DB  ', ' FAG ', 'EEEE ', ' HI  '],
    'manufacturing/industrial_iron/depot': ['BBBB', ' A I', 'GCF ', ' EDJ', 'HHHH'],
    'v3_ae2/crafting_unit': [' A ', 'DBE', 'CFG'],
    'v3_ae2/drive': [' C C ', ' C C ', ' DED ', 'HAFH ', ' JIG '],
    'v3_ae2/controller': [' B B ', ' ECE ', ' IFJ ', ' HAG ', ' KDK '],
    'ae2_high_energy/mega_crafting_unit': [' EF ', 'BDCG', ' JAK', ' IHI', ' LM '],
    'v3_ae2/quantum_unit': [' D  ', 'EJEE', 'CBAC', 'IKFI', ' GH '],
    'ae2_coverage/crafting_accelerator': [' D D ', ' BC  ', ' EAE ', ' HGF ', ' JIJ '],
    'ae2_coverage/crafting_monitor': [' I I', 'BCDB', 'FAF ', ' GEH'],
    'extendedae_coverage/ingredient_buffer': [' D E ', 'BCAB ', ' HG  ', ' IFJ ', ' KLM '],
    'extendedae_coverage/ex_drive': [' EEEE', ' CBF ', ' DAD ', ' IGHJ', ' K K '],
    'extendedae_coverage/ex_molecular_assembler': [' L E ', ' DC  ', ' MAM ', ' GBH ', ' IFJ ', '  K  '],
    'extendedae_coverage/ex_pattern_provider': [' E  ', 'GABD', ' IHC', ' F  '],
    'space_coverage/magnetic_stabilizer': [' B D ', ' FCA ', 'JEGH ', ' I I '],
}

def materials(recipe):
    if recipe.get('steps') is not None:
        return [recipe['input']] + [s['ingredient'] for s in recipe['steps'] if s.get('ingredient')]
    return list(recipe.get('inputs', []))

def single(value):
    if isinstance(value, str):
        return re.sub(r'^\d+x\s+', '', value)
    return value

def apply(data):
    recipes = {r['id']: r for r in data['recipes']}
    if 'industrial_colonies:grid/accumulator' not in recipes:
        r=dict(id='industrial_colonies:grid/accumulator',phase='Electrical Manufacturing',order=200,
               output='electroenergetics:accumulator',remove=['electroenergetics:crafting/accumulator'])
        data['recipes'].append(r)
        recipes[r['id']]=r
        data['exclude_outputs']=[x for x in data.get('exclude_outputs',[]) if x!='electroenergetics:accumulator']
        data['additional_removals']=[x for x in data.get('additional_removals',[]) if x!='electroenergetics:crafting/accumulator']
    for short_id, rows in LAYOUTS.items():
        recipe = recipes.get('industrial_colonies:' + short_id)
        if recipe is None: continue
        # Re-applying against the same already-converted recipe is a no-op.
        if recipe.get('review_revision') == '20260904-v7': continue
        bom = materials(recipe)
        key = {chr(65 + i): single(item) for i, item in enumerate(bom)}
        if short_id == 'high_voltage/current_transformer': key['R'] = 'tfmg:resistor'
        used = set(''.join(rows)) - {' '}
        if used - key.keys(): raise ValueError((short_id, used - key.keys()))
        width = max(map(len, rows))
        _mechanical(recipe, tuple(row.ljust(width) for row in rows), key,
            'Review correction: functional hardware now uses Mechanical Crafting. '
            'The working parts, connections and structural support are assembled in the shown layout; '
            'the former sequenced assembly is replaced, not added as an alternative.')
        recipe['review_revision'] = '20260904-v7'

    monitor = recipes['industrial_colonies:computercraft/monitor/normal']
    _mechanical(monitor, ('GGG', 'BCB', 'WPW'), {
        'G':'create:polished_rose_quartz', 'B':'tfmg:circuit_board',
        'C':'create:display_board', 'W':'tfmg:copper_wire', 'P':'tfmg:plastic_sheet'},
        'Review correction: a compact 3x3 monitor, with a pixel face, two circuit-board drivers and an insulated wiring strip. Produces two monitors.')
    radiance = recipes['industrial_colonies:nuclear/refined_radiance']
    radiance['inputs'] = ['4x create:chromatic_compound', '2x bigreactors:yellorium_ingot',
        '2x mekanism:alloy_atomic', '2x tfmg:magnetic_alloy_ingot', 'allthemodium:allthemodium_ingot']
    radiance['type'] = 'mixing'
    radiance['machine'] = 'createcasing:industrial_iron_mixer'
    radiance['heat'] = 'superheated'
    radiance['comment'] = 'Review correction: superheated material alloying, with no processors, capacitors or whole machines consumed. Chromatic compound, Yellorium and metallic alloys form the Radiance charge.'
    for short_id in ['appliedcreate/stress_storage_component_256k', 'digital_storage/ae2_crafting_storage_256k',
                     'v3_ae2/cell_component_64k', 'v3_ae2/cell_component_256k']:
        recipe = recipes['industrial_colonies:' + short_id]
        for step in recipe.get('steps', []):
            if 'megacells:accumulation_processor' in str(step.get('ingredient', '')):
                step['ingredient'] = '2x ae2:engineering_processor'
        for symbol, value in recipe.get('key', {}).items():
            if 'megacells:accumulation_processor' in str(value): recipe['key'][symbol] = 'ae2:engineering_processor'
        recipe['comment'] = 'Review correction: ordinary AE2/stress storage uses AE2 processors; Accumulation Processors are reserved for the later MEGA line.'

    precursor = recipes['industrial_colonies:outer_station/warp_charge_precursor']
    if precursor['input'] == 'industrial_colonies:gas_giant_condensate_bucket':
        precursor['input'] = precursor['transitional'] = 'ad_astra:mercury_iron_ore'
        precursor['steps'] = [s for s in precursor['steps'] if s.get('ingredient') not in
            ('7x industrial_colonies:gas_giant_condensate_bucket', 'ad_astra:mercury_iron_ore')]
        precursor['steps'].insert(0, {'op':'filling', 'machine':'create:spout', 'fluid':{'kind':'FLUID', 'id':'industrial_colonies:gas_giant_condensate', 'amount':8000}})
    precursor['comment'] = 'Review correction: a spout injects 8,000 mB of returned gas-giant condensate directly into the Mercury-seeded core. No bucket items are consumed. Containment and control parts are then fitted and pressed.'

    # Explicit batch families retain the same construction language as their
    # capacity grows; expensive internals sit in working rows, not an outer ring.
    for capacity in ('1k', '4k', '16k', '64k', '256k'):
        r = recipes['industrial_colonies:digital_storage/ae2_crafting_storage_' + capacity]
        _mechanical(r, ('GGGG', 'WSSW', 'BPBC', 'HUUH'), {
            'G':'ae2:quartz_glass', 'W':'tfmg:copper_wire',
            'S':'ae2:cell_component_' + capacity, 'B':'tfmg:coated_circuit_board',
            'P':('ae2:logic_processor' if capacity=='1k' else 'ae2:calculation_processor'), 'C':'tfmg:capacitor_item',
            'H':'tfmg:plastic_sheet', 'U':'ae2:crafting_unit'},
            'Review correction: Mechanical Crafting assembles a visible pair of storage planes above a controller backplane and the crafting-unit base. No Accumulation Processor is needed for ordinary AE2 crafting storage.')
    for index, capacity in enumerate(('1m', '4m', '16m', '64m', '256m')):
        # Components gain stacked addressing/insulation stages. Finished cells
        # retain their component dependency, so expensive internals aren't paid twice.
        component = recipes['industrial_colonies:v3_ae2/mega_cell_component_' + capacity]
        insert_steps(component, [('tfmg:capacitor_item', 2 + index),
                                 ('ae2:engineering_processor', 1 + index),
                                 ('tfmg:plastic_sheet', 2 + index)], 'railway')
        if index >= 3:
            insert_steps(component, [('allthemodium:allthemodium_ingot', index - 2)], 'railway')
        component['comment'] = 'Review correction: capacity planes receive additional address controllers, a capacitor bank and laminated dielectric layers. Later capacities require Allthemodium conductors; the smaller components remain the manufacturing foundation.'
        cell = recipes['industrial_colonies:v3_ae2/mega_item_storage_cell_' + capacity]
        insert_steps(cell, [('tfmg:rubber_sheet', 2), ('tfmg:copper_wire', 2 + index)], 'railway')
        cell['comment'] = 'Review correction: mount the expensive storage interior, install the wider contact bus, fit shock-isolation pads, then press the enclosure shut. The costly internal component already carries the new semiconductor/addressing work.'
        storage = recipes['industrial_colonies:v3_ae2/mega_crafting_storage_' + capacity]
        alloy = 'tfmg:magnetic_alloy_sheet' if index < 3 else 'allthemodium:allthemodium_ingot'
        _mechanical(storage, ('QSSSQ', 'WBBBW', 'CPAPC', 'HUFUH'), {
            'Q':'ae2:quartz_vibrant_glass', 'S':'megacells:cell_component_' + capacity,
            'W':'ae2:fluix_smart_dense_cable', 'B':'tfmg:coated_circuit_board',
            'C':'tfmg:capacitor_item', 'P':'ae2:engineering_processor',
            'A':'megacells:accumulation_processor', 'H':alloy,
            'U':'megacells:mega_crafting_unit', 'F':'tfmg:steel_frame'},
            'Review correction: three high-capacity storage banks sit above an addressing backplane and dual scheduling units. Mechanical Crafting builds the complete server block; its storage components remain process-manufactured.')

    # The scorched parts were liked; only change their requested manufacturing environment.
    for name in ('modern_scorched_basin', 'modern_scorched_drain', 'modern_scorched_table'):
        r = recipes['industrial_colonies:foundry_routes/' + name]
        r['machine'] = 'createcasing:weathered_iron_press'
        r['comment'] = 'Review correction: retain the scorched refractory construction and form it on the Weathered Iron press, as requested.'
    r = recipes['industrial_colonies:foundry_routes/create_metallurgy_foundry_mixer']
    for step in r['steps']:
        if step['op'] in ('pressing', 'deploying'):
            step['machine'] = 'createcasing:weathered_iron_' + ('press' if step['op'] == 'pressing' else 'deployer')
    r['comment'] = 'Review correction: build the foundry mixer on the Weathered Iron manufacturing line; retain the existing ingredients.'

    for name in ('advanced_bin', 'ultimate_bin'):
        r = recipes['industrial_colonies:mekanism_utility/' + name]
        _replace_process(r, dict(type='compacting', inputs=materials(r), output=_output(r),
            machine='createcasing:industrial_iron_press', heat='none',
            comment='Review correction: compact the upgraded storage shell and loading hardware around the previous bin; this storage exception does not require a whole-machine assembly line.'))
    r = recipes['industrial_colonies:petroleum/steel_distillation_output']
    _replace_process(r, dict(type='compacting', inputs=materials(r), output=_output(r),
        machine='createcasing:weathered_iron_press', heat='none',
        comment='Review correction: pressure-fit the tank, pipe manifold and valve into the output casing.'))

    for metal in ('aluminum', 'steel'):
        r = recipes['industrial_colonies:tfmg_coverage/' + metal + '_smart_fluid_pipe']
        _mechanical(r, (' B ', 'WVW', ' P '), {'B':'tfmg:circuit_board',
            'W':'tfmg:copper_wire', 'V':'tfmg:' + metal + '_fluid_valve',
            'P':'tfmg:plastic_sheet'},
            'Review correction: a compact valve assembly with its control board above and the conductive connections on either side, matching your explicit grid request.')

    r = recipes['industrial_colonies:create_addons/electro_converter']
    _mechanical(r, (' C ', 'RAR', ' M '), {'C':'tfmg:capacitor_item',
        'R':'electroenergetics:connector', 'A':'tfmg:industrial_aluminum_casing',
        'M':'tfmg:electric_motor'},
        'Review correction: cheaper Mechanical Crafting conversion unit. One motor supplies the electromechanical conversion; the duplicated standalone rotor and magnetic plate are removed.')
    r = recipes['industrial_colonies:create_core/display_board_batch']
    _mechanical(r, ('QQQ', 'TBT', 'WSW'), {'Q':'create:polished_rose_quartz',
        'T':'create:electron_tube', 'B':'tfmg:circuit_board', 'W':'tfmg:copper_wire',
        'S':'create:copper_casing'},
        'Review correction: three pixel segments above display drivers and a copper-casing structural support. Built with Mechanical Crafting.')

    semiconductor_chain(data, recipes)
    finish_cost_corrections(recipes)
    for rid, output, remove, pattern, key, comment in [
        ('auto/tfmg/cast_iron_frame','tfmg:cast_iron_frame','tfmg:crafting/materials/cast_iron_frame',
         ['ISI','S S','ISI'],dict(I='tfmg:cast_iron_ingot',S='tfmg:cast_iron_sheet'),
         'Review correction: a visibly load-bearing cast-iron frame. Solid corner castings join sheet-metal cross members; the center remains open because this is a frame.'),
        ('heavy_industry/foundry_controller','modernfoundry:foundry_controller','modernfoundry:smeltery/casting/scorched/foundry_controller',
         [' G ','BCB','FPF'],dict(G='minecraft:glass_pane',B='modernfoundry:scorched_brick',C='tfmg:circuit_board',F='minecraft:blast_furnace',P='modernfoundry:gold_platform'),
         'Review correction: a refractory control face over furnace hardware and a gold contact platform, rather than an expensive border around the stock recipe.'),
        ('heavy_industry/smeltery_controller','modernfoundry:smeltery_controller','modernfoundry:smeltery/casting/seared/smeltery_controller',
         [' G ','BCB','FPF'],dict(G='minecraft:glass_pane',B='minecraft:bricks',C='create:electron_tube',F='minecraft:furnace',P='create:iron_sheet'),
         'Review correction: a simple furnace-control face with an observation window, heat-resistant body and iron base; no late processor ring.'),
        ('steelworks/blast_furnace_output','tfmg:blast_furnace_output','tfmg:crafting/materials/blast_furnace_output',
         [' P ','BVB',' H '],dict(P='tfmg:cast_iron_pipe',B='tfmg:fireproof_bricks',V='minecraft:hopper',H='create:iron_sheet'),
         'Review correction: a refractory-lined outlet with a central drain and a load-bearing plate. Cast iron piping keeps the first blast furnace independent of its own steel output.')]:
        identity='industrial_colonies:'+rid
        if identity in recipes: continue
        spec=dict(id=identity,phase=('Electrical Manufacturing' if rid=='heavy_industry/foundry_controller' else 'Steel & Petroleum'),order=290,output=output,remove=[remove])
        _mechanical(spec,tuple(pattern),key,comment)
        data['recipes'].append(spec)
        data['exclude_outputs']=[x for x in data.get('exclude_outputs',[]) if x!=output]
        data['additional_removals']=[x for x in data.get('additional_removals',[]) if x!=remove]
        data['preserve_recipe_ids']=[x for x in data.get('preserve_recipe_ids',[]) if x!=remove]

def semiconductor_chain(data, recipes):
    preparation = dict(id='industrial_colonies:electronics/prepared_silicon_wafer',
        type='sequenced_assembly', phase='Electrical Manufacturing', order=478,
        input='tfmg:silicon_ingot', transitional='tfmg:silicon_ingot', loops=2,
        output='industrial_colonies:prepared_silicon_wafer', remove=[],
        comment='Wafer preparation: add conductive contacts and insulation, wash the surface, cut and press each layer. Two passes prepare the substrate before chemical etching.',
        steps=[dict(op='deploying', ingredient='tfmg:copper_wire', machine='createcasing:copper_deployer'),
               dict(op='deploying', ingredient='tfmg:plastic_sheet', machine='createcasing:copper_deployer'),
               dict(op='filling', fluid=dict(kind='FLUID',id='minecraft:water',amount=250),machine='create:spout'),
               dict(op='cutting',machine='createcasing:copper_mechanical_saw'),
               dict(op='pressing',machine='createcasing:copper_press')])
    etching = dict(id='industrial_colonies:electronics/etched_silicon_wafer', type='tfmg_vat',
        phase='Electrical Manufacturing',order=479,remove=[],vat_mode='steel',machine_mode='mixing',
        min_size=3,heat='heated',processing_time=600,
        ingredients=['industrial_colonies:prepared_silicon_wafer',
            dict(kind='FLUID',id='tfmg:sulfuric_acid',amount=500)],
        results=[dict(kind='ITEM',id='industrial_colonies:etched_silicon_wafer',count=1)],
        comment='Chemical Vat-only etching converts the prepared wafer into the substrate for both semiconductor types. This intermediate cannot be bypassed by directly processing silicon ingots.')
    for spec in (preparation, etching):
        if spec['id'] in recipes: recipes[spec['id']].update(spec)
        else: data['recipes'].append(spec)
    for kind, dopant in [('n','tfmg:sulfur_dust'),('p','minecraft:redstone')]:
        r = recipes['industrial_colonies:electronics/' + kind + '_semiconductor']
        _replace_process(r,dict(type='sequenced_assembly',input='industrial_colonies:etched_silicon_wafer',
            transitional='industrial_colonies:etched_silicon_wafer',loops=2,
            output=dict(kind='ITEM',id='tfmg:'+kind+'_semiconductor',count=2),
            steps=[dict(op='deploying',ingredient=dopant,machine='createcasing:copper_deployer'),
                dict(op='deploying',ingredient='tfmg:capacitor_item',machine='createcasing:copper_deployer'),
                dict(op='deploying',ingredient='tfmg:copper_wire',machine='createcasing:copper_deployer'),
                dict(op='filling',fluid=dict(kind='FLUID',id='minecraft:water',amount=250),machine='create:spout'),
                dict(op='cutting',machine='createcasing:copper_mechanical_saw'),
                dict(op='pressing',machine='createcasing:copper_press')],
            comment='Review correction: prepared wafer -> acid etching in the Chemical Vat -> two passes of dopant/contact assembly, washing, cutting and pressing. Produces two TFMG semiconductors; finished CPUs are not required to bootstrap them.'))

def finish_cost_corrections(recipes):
    def grid(short, pattern, key, note):
        r=recipes['industrial_colonies:'+short]
        width=max(map(len,pattern))
        _mechanical(r,tuple(s.ljust(width) for s in pattern),key,'Review correction: '+note)
    grid('extendedae/machine_frame', ['EQQE','WS W','ICCI','EIIE'],
         dict(E='extendedae:entro_ingot',Q='ae2:quartz_glass',W='ae2:fluix_smart_cable',
              S='tfmg:steel_frame',I='tfmg:heavy_plate',C='appliedcreate:advanced_stress_processor'),
         'a larger 4x4 frame, with a glazed inspection face, central steel structure, reinforced lower rails and dedicated controller mounts.')
    grid('grid/accumulator',['CLC','LBL','WPW'],dict(C='create:copper_sheet',L='tfmg:lithium_charge',
         B='tfmg:plastic_sheet',W='tfmg:copper_wire',P='tfmg:steel_casing'),
         'a cheaper lithium electrode stack, separated by plastic and supported by a steel casing. No processor bank is needed for this battery.')
    grid('extreme_grid/high_voltage_capacitor',['CCCC','LSSL','WTW ',' H H'],
         dict(C='tfmg:capacitor_item',L='tfmg:lithium_charge',S='tfmg:magnetic_alloy_sheet',
              W='electroenergetics:heavily_insulated_wire',T='electroenergetics:transformer_core',H='tfmg:steel_casing'),
         'Mechanical Crafting mounts the capacitor bank and insulated terminals above the transformer support.')
    grid('fluid_infrastructure/fireproof_chemical_vat',['B B','BVB','PMP','H H'],
         dict(B='tfmg:fireproof_bricks',V='tfmg:steel_chemical_vat',P='tfmg:steel_pipe',M='tfmg:steel_mechanism',H='tfmg:heavy_plate'),
         'Mechanically assemble the firebrick lining around the previous chemical vessel, then fit its service manifold and supports.')
    grid('extreme_grid/sulfur_hexafluoride_breaker',['I I','CVC','PBP',' H '],
         dict(I='electroenergetics:insulator',C='electroenergetics:connector',V='tfmg:steel_fluid_valve',
              P='tfmg:steel_pipe',B='electroenergetics:cut_off_switch',H='tfmg:heavy_machinery_casing'),
         'a simpler insulated disconnect with a sealed gas manifold, rather than the previous dense 5x5 electronics wall.')
    grid('high_voltage/voltage_regulator',[' T ','WCW',' EM',' H '],
         dict(T='tfmg:transformer',W='electroenergetics:heavily_insulated_wire',C='mekanism:advanced_control_circuit',
              E='tfmg:electric_motor',M='tfmg:potentiometer',H='tfmg:heavy_machinery_casing'),
         'Mechanical Crafting links the transformer to its variable control and motor-driven adjustment hardware.')
    grid('create_core/cart_assembler',[' P ','SCS','RBR',' A '],
         dict(P='create:mechanical_press',S='create:shaft',C='create:precision_mechanism',
              R='minecraft:rail',B='create:andesite_casing',A='create:andesite_alloy'),
         'a rail-mounted assembly platform with a real press head and kinetic linkage. This replaces the cheap hand-crafting route.')
    grid('v3_ae2/mega_interface',['QFFQ','WPBW','CAAC',' HHH'],dict(Q='ae2:quartz_vibrant_glass',
        F='ae2:formation_core',W='ae2:fluix_smart_dense_cable',P='megacells:accumulation_processor',
        B='tfmg:coated_circuit_board',C='tfmg:capacitor_item',A='ae2:interface',H='tfmg:heavy_plate'),
        'dual interface modules under a wide transfer backplane, with dedicated buffer electronics and formation hardware.')
    grid('v3_ae2/mega_pattern_provider',[' PP ','BTCB','WAAW',' HHH'],dict(P='ae2:blank_pattern',
        B='tfmg:coated_circuit_board',T='minecraft:crafting_table',C='extendedae:concurrent_processor',
        W='ae2:fluix_smart_dense_cable',A='ae2:pattern_provider',H='tfmg:heavy_plate'),
        'two pattern banks feed a crafting work surface and parallel scheduler, connected to paired providers.')
    grid('v3_ae2/mega_crafting_accelerator',[' M M ','CPAPC',' WBW ',' HUH '],dict(M='tfmg:electric_motor',
        C='tfmg:capacitor_item',P='extendedae:concurrent_processor',A='ae2:crafting_accelerator',
        W='ae2:fluix_smart_dense_cable',B='tfmg:coated_circuit_board',H='tfmg:heavy_plate',U='megacells:mega_crafting_unit'),
        'paired parallel processors and power buffers above a complete crafting-unit base; the actuator pair expresses the additional assembly throughput.')
    grid('v3_ae2/mega_crafting_monitor',['GGGG',' DMD','BCPB',' UWU'],dict(G='ae2:quartz_vibrant_glass',
        D='computercraft:monitor_normal',M='ae2:crafting_monitor',B='tfmg:coated_circuit_board',
        C='tfmg:capacitor_item',P='ae2:calculation_processor',U='megacells:mega_crafting_unit',W='ae2:fluix_smart_dense_cable'),
        'a wide monitoring face over a dedicated display driver and dual server base. The whole block is mechanically assembled.')
    grid('v3_ae2/quantum_core',[' GQG ','PABAP',' WTW ','HUFUH'],dict(G='ae2:quartz_vibrant_glass',
        Q='ae2:quantum_entangled_singularity',P='advanced_ae:quantum_processor',A='advanced_ae:quantum_alloy_plate',
        B='tfmg:coated_circuit_board',W='ae2:fluix_smart_dense_cable',T='tfmg:transformer',H='allthemodium:vibranium_ingot',
        U='mekanism:ultimate_control_circuit',F='tfmg:steel_frame'),
        'a contained quantum medium, two quantum controllers, dense data trunk and independent power stage. Vibranium bracing supports the late-game field assembly.')
    grid('world_loading/dimensional_stabilizer',[' Q Q ','FCPCF','WABAW',' HFH '],dict(Q='ae2:fluix_crystal',
        F='tfmg:steel_frame',C='tfmg:electromagnetic_coil',P='ae2:spatial_cell_component_128',
        W='ae2:fluix_smart_dense_cable',A='allthemodium:vibranium_ingot',B='advancedperipherals:chunk_controller',H='tfmg:heavy_plate'),
        'paired quantum field assemblies reference spatial capacity above a chunk-loader base. This is powered chunk management, with spatial materials serving its actual function.')
    grid('grid/alternator_rotor',[' WW ','WMSW','WASW',' WW '],dict(W='tfmg:copper_spool',
        M='tfmg:laminated_magnetic_alloy_block',S='create:shaft',A='tfmg:steel_mechanism'),
        'a laminated magnetic rotor and reinforced shaft enclosed in real windings, rather than paying for unrelated processors.')
    grid('space/dockyard/docking_connector',['P I P','WABAW','HMCMH',' F F '],dict(P='tfmg:steel_pipe',
        I='create:portable_storage_interface',W='ae2:fluix_smart_dense_cable',A='tfmg:steel_fluid_valve',
        B='rocketnautics:titanium_casing',H='tfmg:heavy_plate',M='tfmg:electric_motor',C='ae2:engineering_processor',F='tfmg:steel_frame'),
        'a central mating connector between two sealed service manifolds, driven by locking motors and a dedicated alignment controller.')
    grid('space_coverage/compressor',['TPT','MVM','BCB','F F'],dict(T='tfmg:steel_fluid_tank',
        P='create:mechanical_pump',M='tfmg:electric_motor',V='tfmg:steel_chemical_vat',
        B='tfmg:coated_circuit_board',C='ae2:engineering_processor',F='tfmg:steel_frame'),
        'paired receiver tanks and drive motors surround the pressure vessel; a proper electronic control backplane regulates it.')
    grid('planetary/outpost/gravity_normalizer',[' G G ','PQCQP',' BW B',' HFH '],dict(G='tfmg:electromagnetic_coil',
        P='ad_astra:desh_plate',Q='advanced_ae:quantum_processor',C='simulated:gyroscopic_mechanism',
        B='tfmg:coated_circuit_board',W='ae2:fluix_smart_dense_cable',H='rocketnautics:titanium_alloy_sheet',F='tfmg:steel_frame'),
        'two controlled field coils use gyroscopic feedback and quantum control, on planetary-metal supports.')
    grid('space/navigation/sputnik',[' A A ','PBCBP',' WD W',' HFH '],dict(A='create:transmitter',
        P='tfmg:heavy_plate',B='tfmg:coated_circuit_board',C='ae2:calculation_processor',
        W='tfmg:copper_wire',D='computercraft:computer_advanced',H='tfmg:plastic_sheet',F='tfmg:steel_frame'),
        'dual communications arrays feed dedicated navigation boards and an onboard computer, with insulated wiring and structural support.')
    for tier in ('railway','refined_radiance'):
        for machine in ('press','deployer','mixer','saw'):
            short=('v3_createcasing/railway_saw' if tier=='railway' and machine=='saw'
                   else 'manufacturing/'+tier+'/'+machine)
            prior='copper' if tier=='railway' else 'industrial_iron'
            suffix='mechanical_saw' if machine=='saw' else machine
            head='createcasing:'+prior+'_'+suffix
            casing='create:railway_casing' if tier=='railway' else 'create:refined_radiance_casing'
            alloy='tfmg:magnetic_alloy_sheet' if tier=='railway' else 'allthemodium:vibranium_ingot'
            pattern={'press':[' M  ','AHHA','CNPC','BFFB'],
                     'deployer':['  HM',' AH ','CNPC','BFFB'],
                     'mixer':[' M  ','CNPC','AHA ','BFFB'],
                     'saw':[' HH ','AM A','CNPC','BFFB']}[machine]
            grid(short,pattern,dict(M='tfmg:electric_motor',A=alloy,H=head,
                C='tfmg:coated_circuit_board',N='tfmg:n_semiconductor',P='tfmg:p_semiconductor',
                B=casing,F='tfmg:steel_frame'),
                'upgrade the working '+machine+' assembly with motor control, complementary semiconductor drivers, dual control boards and a reinforced support. The working head keeps the layout specific to this machine.')
    for machine in ('mixer','saw'):
        r=recipes['industrial_colonies:manufacturing/copper/'+machine]
        insert_steps(r,[('tfmg:copper_wire',2),('tfmg:capacitor_item',2),('tfmg:magnetic_alloy_sheet',1)],'copper')
        r['comment']='Review correction: an upgraded wired machine adds a conductive winding, capacitor pair and magnetic laminate before final closure. It does not require finished semiconductors to build their production machines.'
    for short, additions in {
        'computercraft/mobile/turtle':[('tfmg:coated_circuit_board',1),('tfmg:n_semiconductor',2),('tfmg:p_semiconductor',2)],
        'computercraft/monitor/advanced':[('tfmg:circuit_board',2),('tfmg:transistor_item',2),('tfmg:plastic_sheet',2)],
        'mekanism/ultimate_control_circuit':[('tfmg:n_semiconductor',2),('tfmg:p_semiconductor',2),('tfmg:capacitor_item',4)],
        'mekanism_components/upgrade_filter':[('tfmg:plastic_sheet',2),('tfmg:circuit_board',1),('mekanism:ingot_osmium',1)],
        'digital_storage/assembler_matrix_glass_batch':[('extendedae:entro_ingot',2),('tfmg:magnetic_alloy_sheet',2)],
        'v3_ae2/spatial_pylon_batch':[('ae2:engineering_processor',2),('tfmg:electromagnetic_coil',2)],
        'v3_ae2/quantum_processor':[('advanced_ae:quantum_alloy_plate',2),('tfmg:capacitor_item',4),('tfmg:p_semiconductor',2)],
        'space_coverage/rocket_thruster':[('rocketnautics:titanium_alloy_sheet',2),('tfmg:steel_fluid_valve',2),('tfmg:fireproof_bricks',4)],
        'interstellar/quantum_entangled_pair':[('mekanism:pellet_antimatter',2),('allthemodium:vibranium_ingot',2)],
        'interstellar/warp_charge':[('mekanism:pellet_antimatter',2),('rocketnautics:titanium_alloy_sheet',2)],
        'interstellar/unsigned_route_crystal':[('ae2:engineering_processor',2),('cosmowarp:moon_crystal',2)],
    }.items():
        r=recipes['industrial_colonies:'+short]
        tier=next((s['machine'].split(':')[1].removesuffix('_deployer') for s in r['steps'] if s['op']=='deploying'),'brass')
        insert_steps(r,additions,tier)
        r['comment']='Review correction: additional '+', '.join(str(n)+' '+i.split(':')[1].replace('_',' ') for i,n in additions)+' are installed before final closure. These additions strengthen the specific control, containment or structural function of this assembly.'

def insert_steps(recipe, ingredients, tier):
    """Add purpose-specific subassemblies before the final closure operation."""
    steps = recipe.get('steps')
    if steps is None: raise ValueError('Expected an assembly: ' + recipe['id'])
    at = len(steps) - 1 if steps[-1]['op'] == 'pressing' else len(steps)
    for item, count in ingredients:
        ingredient = (str(count) + 'x ' if count != 1 else '') + item
        steps.insert(at, dict(op='deploying', ingredient=ingredient, machine='createcasing:' + tier + '_deployer'))
        at += 1
