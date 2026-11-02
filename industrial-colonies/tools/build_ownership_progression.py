"""Deterministic pre-semiconductor migration of the captured current live cards.
Writes workspace candidates only; unrelated cards, UUIDs and semiconductor recipes stay intact.
"""
import copy, hashlib, json, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'progression/ownership'
def dump(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def item(s,count=1): return dict(kind='ITEM_TAG' if s.startswith('#') else 'ITEM',id=s.lstrip('#'),**({'count':count} if count!=1 else {}))
old=json.loads((DIR/'baseline.default.json').read_text(encoding='utf-8-sig'))
new=copy.deepcopy(old); cards={c['recipeId']:c for c in new['recipes']}; changes={}; owned={}
NS='industrial_colonies:'
def output(c): return next(v for k,v in c['slots'].items() if k.startswith('output'))
def card(path,out):
    rid=path if ':' in path else NS+path
    if rid not in cards:
        cards[rid]=dict(uid=str(uuid.uuid5(uuid.NAMESPACE_URL,rid)),recipeId=rid,replaceRecipe=False)
        new['recipes'].append(cards[rid])
    c=cards[rid]; changes[rid]=out; owned.setdefault(out,[]).append(rid)
    c['comment']='[Pre-semiconductor ownership] Mechanical components precede final factory assembly.'
    return c
def grid(path,out,rows,key,count=1):
    assert len(rows)<=7 and len({len(r) for r in rows})==1 and len(rows[0])<=7
    c=card(path,out); c['type']='kjsgen:create_mechanical_crafting'
    c['slots']={f'cell_{y}_{x}':item(key[ch]) for y,row in enumerate(rows) for x,ch in enumerate(row) if ch!=' '}
    c['slots']['output']=item(out,count);c['params']={'gridW':str(len(rows[0])),'gridH':str(len(rows))}
def seq(path,out,source,transitional,steps,loops=1):
    c=card(path,out);c['type']='kjsgen:create_sequenced_assembly'
    c['slots']={'input':item(source),'transitional':item(transitional),'output0':item(out)}
    c['params']={'loops':str(loops),'__seqLen':str(len(steps))}
    for n,(kind,machine,feed) in enumerate(steps):
        c['params']['seq'+str(n)]=kind;c['slots'][f'__machine_step_{n}_{kind}']=item(machine)
        if feed:c['slots']['seqItem'+str(n)]=item(feed)
W='createcasing:weathered_iron_'; C='createcasing:copper_'
# First press is assembled from pre-industrial iron/Create parts. No steel or own output.
grid('manufacturing/weathered_iron/press',W+'press',['ISGI','AP A','A RA','IBBI'],dict(I='minecraft:iron_block',S='create:shaft',G='create:large_cogwheel',A='create:andesite_alloy',P='create:mechanical_press',R='create:iron_sheet',B='create:andesite_casing'))
# First deployer can use press-made heavy plate; it does not require a deployer-made frame.
grid('manufacturing/weathered_iron/deployer',W+'deployer',['ISGI','AP A','A HA','IBBI'],dict(I='minecraft:iron_block',S='create:shaft',G='create:large_cogwheel',A='create:andesite_alloy',P='create:deployer',H='create:brass_hand',B='tfmg:heavy_plate'))
roles={'depot':('create:depot','create:chute'),'fan':('create:encased_fan','create:propeller'),'mixer':('create:mechanical_mixer','create:whisk'),'saw':('create:mechanical_saw','minecraft:iron_block')}
for role,(base,head) in roles.items():
    grid('manufacturing/weathered_iron/'+role,output(cards[NS+'manufacturing/weathered_iron/'+role])['id'],['FS SF','P G P','S M S','P H P','FS SF'],dict(F='tfmg:steel_frame',S='create:shaft',P='tfmg:heavy_plate',G='tfmg:steel_mechanism',M=base,H=head))
# Structural subassemblies belong to the Weathered deployer. Existing registered intermediates are reused.
seq('ownership/steel_frame','tfmg:steel_frame','tfmg:steel_ingot','tfmg:steel_ingot',[('deploying',W+'deployer','tfmg:rebar'),('deploying',W+'deployer','tfmg:rebar'),('pressing',W+'press',None)])
seq('ownership/steel_casing','tfmg:steel_casing','tfmg:hardened_planks','tfmg:hardened_planks',[('deploying',W+'deployer','tfmg:steel_ingot'),('deploying',W+'deployer','tfmg:screw'),('pressing',W+'press',None)])
seq('ownership/steel_mechanism','tfmg:steel_mechanism','tfmg:heavy_plate','tfmg:unfinished_steel_mechanism',[('deploying',W+'deployer',s) for s in ('tfmg:steel_cogwheel','tfmg:nickel_sheet','tfmg:large_steel_cogwheel','tfmg:lead_sheet','tfmg:screw')]+[('pressing',W+'press',None)],2)
seq('tfmg_core/heavy_machinery_casing','tfmg:heavy_machinery_casing','tfmg:steel_casing','tfmg:steel_casing',[('deploying',W+'deployer',s) for s in ('tfmg:steel_frame','tfmg:heavy_plate','tfmg:heavy_plate','tfmg:heavy_plate','tfmg:heavy_plate','tfmg:rebar','tfmg:rebar')]+[('pressing',W+'press',None)])
c=cards[NS+'tfmg_core/heavy_plate'];c['comment']='[Weathered Iron] Three heavy press reductions form a structural plate.';changes[c['recipeId']]='tfmg:heavy_plate';owned['tfmg:heavy_plate']=[c['recipeId']]
# Steel sheets are formed on the heavy press; cast-iron sheets remain a basic bootstrap.
for path,out in [('steel_sheet','immersiveengineering:plate_steel'),('nuclearcraft_steel_plate','nuclearcraft:steel_plate'),('ad_astra_steel_plate','ad_astra:steel_plate')]:
    c=card('ownership/'+path,out);c['type']='kjsgen:create_pressing';c['slots']={'input':item('#c:ingots/steel'),'output':item(out),'__machine_process_pressing':item(W+'press')};c['params']={}
# Initial cast-iron hardware establishes TFMG before steel and semiconductors.
c=card('ownership/cast_iron_sheet','tfmg:cast_iron_sheet');c['type']='kjsgen:create_pressing';c['slots']={'input':item('#c:ingots/cast_iron'),'output':item('tfmg:cast_iron_sheet'),'__machine_process_pressing':item(W+'press')};c['params']={}
grid('ownership/cast_iron_fluid_tank','tfmg:cast_iron_fluid_tank',[' P ',' B ',' P '],dict(P='tfmg:cast_iron_sheet',B='minecraft:barrel'))
grid('ownership/cast_iron_fluid_valve','tfmg:cast_iron_fluid_valve',[' S ',' P ','   '],dict(S='create:iron_sheet',P='tfmg:cast_iron_pipe'))
c=card('ownership/cast_iron_pipe','tfmg:cast_iron_pipe');c['type']='kjsgen:create_compacting';c['slots']={'in0':item('tfmg:cast_iron_ingot'),'in1':item('tfmg:cast_iron_sheet',2),'output':item('tfmg:cast_iron_pipe',4),'__machine_process_compacting':item(W+'press')};c['params']={'heat':'none'}
# Copper capability is the gateway to existing semiconductor recipes, not dependent on them.
for role in ('press','deployer','depot','fan','mixer','saw'):
    path='manufacturing/copper_'+role if role in ('press','deployer') else 'manufacturing/copper/'+role
    out=output(cards[NS+path])['id'];base=W+{'fan':'encased_fan','saw':'mechanical_saw'}.get(role,role)
    head={'press':'minecraft:copper_block','deployer':'create:brass_hand','depot':'create:chute','fan':'create:propeller','mixer':'create:whisk','saw':'minecraft:iron_block'}[role]
    grid(path,out,['FS SF','P G P','S M S','P H P','FPCPF'],dict(F='tfmg:steel_frame',S='create:shaft',P='create:copper_sheet',G='tfmg:steel_mechanism',M=base,H=head,C='create:copper_casing'))
# Move early structure-forming operations off Brass/Train; keep material quantities.
for path in ('fluid_infrastructure/steel_pipe','fluid_infrastructure/industrial_pipe','steelworks/fireproof_bricks','steelworks/fireproof_brick_reinforcement','steelworks/blast_furnace_reinforcement'):
    c=cards[NS+path]
    for k,v in c['slots'].items():
        if k.startswith('__machine'):v['id']=W+'press'
    c['comment']='[Weathered Iron] Structural forming for the first industrial plant.'
    out=output(c)['id'];changes[c['recipeId']]=out;owned.setdefault(out,[]).append(c['recipeId'])
# Final equipment uses visible structural assemblies, not basin compression or sequenced machine outputs.
equipment={
 'fluid_infrastructure/steel_fluid_tank':('tfmg:steel_fluid_tank','minecraft:barrel','tfmg:steel_pipe'),
 'fluid_infrastructure/steel_chemical_vat':('tfmg:steel_chemical_vat','tfmg:cast_iron_chemical_vat','tfmg:nickel_sheet'),
 'fluid_infrastructure/fireproof_chemical_vat':('tfmg:fireproof_chemical_vat','tfmg:steel_chemical_vat','tfmg:fireproof_bricks'),
 'petroleum/steel_distillation_output':('tfmg:steel_distillation_output','tfmg:steel_fluid_tank','tfmg:steel_fluid_valve'),
 'heavy_industry/industrial_mixer':('tfmg:industrial_mixer','tfmg:steel_casing','tfmg:mixer_blade'),
}
# Use actual recorded output IDs, including the firebrick vat's registry spelling.
for path,(_,center,head) in equipment.items():
    out=output(cards[NS+path])['id']
    grid(path,out,['FS SF','P G P','S M S','P H P','FPTPF'],dict(F='tfmg:steel_frame',S='tfmg:screw',P='tfmg:heavy_plate',G='tfmg:steel_mechanism',M=center,H=head,T='tfmg:steel_pipe'))
# The early factory's valve/duct blocks are final functional blocks; retain their exact ingredients.
for path in ('tfmg_coverage/steel_fluid_valve','tfmg_coverage/plastic_fluid_valve','chemical_processing/cable_tube'):
    c=cards[NS+path]
    if c['type']=='kjsgen:shaped':
        out=output(c)['id']; oldslots=copy.deepcopy(c['slots']);count=output(c).get('count',1)
        c=card(path,out);c['type']='kjsgen:create_mechanical_crafting';c['slots']={f'cell_{int(k[2:])//3}_{int(k[2:])%3}':v for k,v in oldslots.items() if k.startswith('in') and k[2:].isdigit()};c['slots']['output']=item(out,count);c['params']={'gridW':'3','gridH':'3'}
# Its legacy 5x2 dimensions silently excluded the third row of structural parts.
c=card('createaddition_coverage/rolling_mill','createaddition:rolling_mill');c['params']={'gridW':'3','gridH':'3'}
c['comment']='[Copper Manufacturing] Assemble the rollers, geared Copper press and full three-row structural base.'
# Remove explicitly disallowed machines, without touching later nuclear/semiconductor cards.
# Native NC alloy/casting machinery was craftable before electronics. Keep those
# later nuclear systems behind the existing circuit-board boundary, preserving
# their native construction ingredients instead of redesigning nuclear chemistry.
inventory=json.loads((DIR/'native-inventory.json').read_text(encoding='utf-8'))
for name in ('alloy_smelter','melter','ingot_former'):
    native=inventory['recipes']['nuclearcraft:'+name]['data']
    mapping={ch:(value.get('item') or '#'+value['tag']) for ch,value in native['key'].items()}
    # Allocate boundary symbols that cannot collide with the native keys.
    mapping.update({'@':'tfmg:steel_frame','!':'tfmg:circuit_board'})
    rows=['@ ! @']+[' '+row+' ' for row in native['pattern']]+['@ ! @']
    grid('ownership/nuclear_boundary/'+name,'nuclearcraft:'+name,rows,mapping)
retired={'mekanism:crusher','modernfoundry:scorched_alloyer','nuclearcraft:manufactory','nuclearcraft:rock_crusher'}
new['recipes']=[c for c in new['recipes'] if not any(v.get('id') in retired for k,v in c.get('slots',{}).items() if k.startswith('output'))]
# Assert scope closure and persist the exact authority used for this migration.
after={c['recipeId']:c for c in new['recipes']}
removed=[c['recipeId'] for c in old['recipes'] if c['recipeId'] not in after]
for c in old['recipes']:
    if c['recipeId'] not in changes and c['recipeId'] not in removed: assert c==after[c['recipeId']],c['recipeId']
for c in new['recipes']:
    if c['type']=='kjsgen:create_mechanical_crafting':assert 1<=int(c['params']['gridW'])<=7 and 1<=int(c['params']['gridH'])<=7
dump(DIR/'candidate.default.json',new)
dump(DIR/'migration.json',dict(baselineSha256=hashlib.sha256((DIR/'baseline.default.json').read_bytes()).hexdigest(),changed=changes,removed=removed,ownedOutputs=owned,retiredOutputs=sorted(retired),scope='Before semiconductor recipes; later tiers unchanged'))
policy='''// priority: -1100
// Generated ownership policy; source: tools/build_ownership_progression.py.
// Run after material reconciliation so neither stock recipes nor exporters regain bypasses.
ServerEvents.recipes(event => {
  var owned = OWNED;
  var retired = RETIRED;
  var removed = 0;
  var transfers = [];
  Object.keys(owned).forEach(output => {
    event.forEachRecipe({output: output}, recipe => {
      if (owned[output].indexOf(String(recipe.id)) < 0) { recipe.remove(); removed++; }
    });
  });
  retired.forEach(output => event.remove({output: output}));
  // Empty the duplicate crushers, including already placed machines and factory upgrades.
  var blockedTypes = ['mekanism:crushing','immersiveengineering:crusher','createmetallurgy:grinding','mekanism:washing','nuclearcraft:rock_crusher',
  // Modern Foundry exclusively supplies ordinary molten-metal casting/melting.
   'modernfoundry:alloy','immersiveengineering:alloy','createmetallurgy:alloying','createmetallurgy:melting',
   'createmetallurgy:bulk_melting','createmetallurgy:entity_melting',
   'createmetallurgy:casting_in_table','createmetallurgy:casting_in_basin','createdieselgenerators:casting','tfmg:casting'];
  // Several serializers share Create's runtime RecipeType. Inspect serialized identity.
  event.forEachRecipe({}, recipe => {
    recipe.serialize();
    var data=JSON.parse(recipe.json.toString());
    // Preserve surviving non-ore NC grinding operations on Create. Raw-ore bypasses
    // have already been removed by the material policy. Multi-input conversion
    // (leather/bioplastic) uses exact-count compacting, not a probabilistic yield.
    if(data.type==='nuclearcraft:manufactory') {
      var inputs=[]; var results=[];
      (data.item_inputs || []).forEach(stack => {
        for(var n=0;n<(stack.count || 1);n++) {
          if(stack.item) inputs.push({item:stack.item});
          else if(stack.tag) inputs.push({tag:stack.tag});
          else throw new Error('Unsupported NC manufacturing input: '+recipe.getId());
        }
      });
      (data.item_outputs || []).forEach(stack => {
        if(!stack.item) throw new Error('Unsupported NC manufacturing output: '+recipe.getId());
        var result={id:stack.item,count:stack.count || 1};
        if(stack.chance!==undefined) result.chance=stack.chance;
        results.push(result);
      });
      if(inputs.length===0 || inputs.length>9 || results.length===0 || results.length>9) throw new Error('Unsupported NC manufacturing dimensions: '+recipe.getId());
      transfers.push({id:'industrial_colonies:ownership/nc/'+String(recipe.getId()).split(':')[1],data:{type:inputs.length===1?'create:crushing':'create:compacting',ingredients:inputs,results:results,processing_time:data.process_time || 200}});
      recipe.remove();removed++;return;
    }
    if(blockedTypes.indexOf(data.type)>=0) {recipe.remove();removed++;}
  });
  // KubeJS 2101 keeps added recipes separate: forEachRecipe/remove only visit
  // originalRecipes. Reconcile its public pending collection before final encoding.
  function refs(value,result) {
    if(!value || typeof value!=='object') return result;
    if(Array.isArray(value)){value.forEach(v=>refs(v,result));return result;}
    if(typeof value.id==='string')result.push(value.id);
    if(typeof value.item==='string')result.push(value.item);
    Object.keys(value).forEach(k=>{if(typeof value[k]==='object')refs(value[k],result);});
    return result;
  }
  event.addedRecipes.removeIf(recipe => {
    try {recipe.serialize();} catch(error) {return false;}
    var data=JSON.parse(recipe.json.toString());
    var values=[];
    ['result','results','output','outputs','item_output','item_outputs'].forEach(k=>refs(data[k],values));
    var id=String(recipe.getId());
    var reject=blockedTypes.indexOf(data.type)>=0 || values.some(v=>retired.indexOf(v)>=0 || (owned[v] && owned[v].indexOf(id)<0));
    if(reject)removed++;
    return reject;
  });
  transfers.forEach(entry => event.custom(entry.data).id(entry.id));
  // Keep the established coke-dust electrode feed available through the designated grinder.
  event.custom({type:'create:crushing',ingredients:[{tag:'c:coal_coke'}],results:[{id:'tfmg:coal_coke_dust'}],processing_time:250}).id('industrial_colonies:ownership/coke_grinding');
  event.custom({type:'create:crushing',ingredients:[{item:'minecraft:coal'}],results:[{id:'mekanism:dust_coal'}],processing_time:250}).id('industrial_colonies:ownership/coal_grinding');
  event.custom({type:'create:crushing',ingredients:[{item:'minecraft:charcoal'}],results:[{id:'mekanism:dust_charcoal'}],processing_time:250}).id('industrial_colonies:ownership/charcoal_grinding');
  event.custom({type:'create:mixing',ingredients:[{tag:'c:glass_blocks'},{tag:'c:glass_blocks'},{tag:'c:dusts/iron'}],results:[{id:'immersiveengineering:insulating_glass',count:2}],heat_requirement:'heated'}).id('industrial_colonies:ownership/insulating_glass');
  // Preserve this existing downstream construction-metal endpoint when retiring
  // CM's legacy cast/alloy serializers. This is not a new nuclear fuel recipe.
  event.custom({type:'industrial_colonies:industrial_iron_mixing',ingredients:[{tag:'c:ingots/lead'},{tag:'c:ingots/gold'}],results:[{id:'bigreactors:yellorium',amount:2000}],heat_requirement:'heated',processing_time:160}).id('industrial_colonies:materials/yellorium/molten_alloy');
  event.custom({id:'industrial_colonies:materials/yellorium/ingot_casting',type:'modernfoundry:casting_table',fluid:{fluid:'bigreactors:yellorium',amount:1000},cast:{tag:'modernfoundry:casts/multi_use/ingot'},result:{item:'bigreactors:yellorium_ingot'},cooling_time:60}).id('industrial_colonies:materials/yellorium/ingot_casting');
  console.info('[Industrial Colonies] Pre-semiconductor ownership reconciled '+removed+' alternate component/machine recipes; migrated '+transfers.length+' NC manufacturing operations.');
});
'''.replace('OWNED',json.dumps(owned)).replace('RETIRED',json.dumps(sorted(retired | {'mekanism:'+tier+'_crushing_factory' for tier in ('basic','advanced','elite','ultimate')} | {'immersiveengineering:crusher'})))
(DIR/'ownership_policy.js').write_text(policy,encoding='utf-8')
old_policy=(DIR/'baseline.material-policy.js').read_text(encoding='utf-8-sig')
material=(DIR/'baseline.material-processing.js').read_text(encoding='utf-8-sig')
assert material.count(old_policy)==1,'Material script differs from captured authoring policy'
material=material.replace(old_policy,(ROOT/'tools/material_processing/policy.js').read_text(encoding='utf-8'),1)
(DIR/'candidate.material-processing.js').write_text(material,encoding='utf-8')
print(f'Prepared {len(changes)} owned cards; removed {len(removed)} competing machine cards; {len(new["recipes"])} total.')


