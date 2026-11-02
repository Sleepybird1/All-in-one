// Pure Node regression/mutation tests. No Minecraft, KubeJS, or live writes.
const fs = require('node:fs')
const path = require('node:path')
const vm = require('node:vm')
const assert = require('node:assert/strict')
const root = path.resolve(__dirname, '../..')
const policyPath = path.join(__dirname, 'policy.js')
const original = fs.readFileSync(policyPath, 'utf8')
const inventory = JSON.parse(fs.readFileSync(path.join(root, 'build/material-processing/installed-inventory.json'), 'utf8'))
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'processing/material_processing_catalog.json'), 'utf8'))
const policy = catalog.policy
const clone = x => JSON.parse(JSON.stringify(x))
function run(source, data, id = 'test:recipe', customPolicy = policy) {
  let removed = false, replacement = null, audit = null, merged = false
  const liveData = clone(data)
  const context = { console: { info() {} }, JsonIO: { write(_path, value) { audit = value } } }
  vm.createContext(context)
  vm.runInContext(source, context)
  const recipe = { getId: () => id, serialize() {}, json: JSON.stringify(data), remove() { removed = true },
    merge(partial) { Object.assign(liveData, clone(partial)); merged = true; return this } }
  const event = { forEachRecipe(_filter, fn) { fn(recipe) }, custom(value) { replacement = clone(value); return { id(found) { assert.equal(found, id) } } } }
  context.icProcessingPolicy(event, clone(customPolicy))
  return { removed: removed && !replacement, changed: !!replacement || merged, data: replacement || liveData, audit,
    merged, recreated: !!replacement }
}
const cases = []
const test = (name, fn) => cases.push({ name, fn })
test('Rhino compatibility uses no lexical declarations in the policy', source => {
  assert.doesNotMatch(source, /^\s*(?:const|let)\s+[A-Za-z_$]/m,
    'Use function-scoped var to avoid Rhino repeated-block const redeclarations')
})
const installed = id => { assert.ok(inventory.recipes[id], id); return clone(inventory.recipes[id].data) }
const amount = result => result.data.fluid.amount
const ironCast = (count = 1) => ({ type: 'modernfoundry:casting_table', fluid: { tag: 'c:molten_iron', amount: 90 }, result: { item: 'minecraft:iron_ingot', count } })
const melt = (ingredient, amount = 90) => ({ type: 'modernfoundry:melting', ingredient, result: { tag: 'c:molten_iron', amount }, time: 60, temperature: 800 })
test('iron ingot cast costs 1000', src => assert.equal(amount(run(src, ironCast())), 1000))
test('three iron ingots cost 3000', src => assert.equal(amount(run(src, ironCast(3))), 3000))
test('iron nugget cast costs 25 not 1000/9', src => assert.equal(amount(run(src, { ...ironCast(), result: { item: 'minecraft:iron_nugget' } })), 25))
test('gold nugget cast costs 10', src => assert.equal(amount(run(src, { type: 'modernfoundry:casting_table', fluid: { tag: 'c:molten_gold', amount: 10 }, result: { item: 'minecraft:gold_nugget' } })), 10))
test('iron block cast costs 9000', src => assert.equal(amount(run(src, { ...ironCast(), result: { item: 'minecraft:iron_block' } })), 9000))
test('ingot remelting is exact 1000', src => assert.equal(run(src, melt({ item: 'minecraft:iron_ingot' })).data.result.amount, 1000))
test('two sized ingots remelt to 2000', src => assert.equal(run(src, melt({ basePredicate: { item: 'minecraft:iron_ingot' }, count: 2 })).data.result.amount, 2000))
test('nugget remelting matches 25', src => assert.equal(run(src, melt({ item: 'minecraft:iron_nugget' }, 10)).data.result.amount, 25))
test('ingredient alternatives are not multiple physical ingots', src => assert.equal(run(src, melt([{ item: 'minecraft:iron_ingot' }, { tag: 'c:ingots/iron' }])).data.result.amount, 1000))
test('CreateMetallurgy nested two-output count costs 2000', src => {
  const d = installed('createmetallurgy:casting_in_table/iron/ingot'); d.result.item.count = 2
  assert.equal(run(src, d).data.ingredients[0].amount, 2000)
})
test('altered CM casting string output becomes native ItemStack', src => {
  const d = installed('createmetallurgy:casting_in_table/iron/ingot')
  d.result = {item:'minecraft:iron_ingot'}
  const r = run(src, d)
  assert.deepEqual(r.data.result, {item:{id:'minecraft:iron_ingot',count:1}})
  assert.equal(r.data.ingredients[0].amount,1000)
})
test('altered CM casting outer count moves into stack exactly once', src => {
  const d = installed('createmetallurgy:casting_in_table/iron/ingot')
  d.result = {item:'minecraft:iron_ingot',count:3}
  const r = run(src,d)
  assert.deepEqual(r.data.result, {item:{id:'minecraft:iron_ingot',count:3}})
  assert.equal(r.data.ingredients[0].amount,3000)
})
test('unrelated CM casting output shape is not rewritten', src => {
  const d = {type:'createmetallurgy:casting_in_table',ingredients:[{fluid:'minecraft:water',amount:250}],result:{item:'minecraft:stone'}}
  assert.deepEqual(run(src,d).data,d)
})
test('native CM entity melt keeps empty ingredients through existing recipe merge', src => {
  for(const id of ['createmetallurgy:entity_melting/iron_golem','createmetallurgy:entity_melting/piglin']) {
    const d=installed(id), r=run(src,d,id)
    assert.ok(r.merged); assert.equal(r.recreated,false); assert.equal(r.removed,false)
    assert.deepEqual(r.data.ingredients,[])
    assert.deepEqual(r.data.entity,d.entity)
    assert.equal(r.data.minHeatRequirement,d.minHeatRequirement)
    assert.equal(r.data.results[0].amount,Math.floor(d.results[0].amount*1000/90))
    const unchanged=clone(r.data);unchanged.results=clone(d.results)
    assert.deepEqual(unchanged,d)
  }
})
test('nonmetal entity melt is not marked changed or recreated', src => {
  const d={type:'createmetallurgy:entity_melting',entity:{type:'minecraft:cow',damage:1},ingredients:[],results:[{id:'minecraft:water',amount:50}]}
  const r=run(src,d);assert.equal(r.changed,false);assert.equal(r.merged,false);assert.deepEqual(r.data,d)
})
test('TFMG results array count costs 2000', src => {
  const d = installed('tfmg:casting/steel'); d.results[0].count = 2
  assert.equal(run(src, d).data.ingredients[0].amount, 2000)
})
test('NC multiple item outputs counted together', src => {
  const d = installed('nuclearcraft:ingot_former/iron'); d.item_outputs.push({ item: 'minecraft:iron_ingot' })
  assert.equal(run(src, d).data.fluid_inputs[0].amount, 2000)
})
test('NC sized ingot input counted', src => {
  const d = { type: 'nuclearcraft:melter', item_inputs: [{ item: 'minecraft:iron_ingot', count: 3 }], fluid_outputs: [{ fluid: 'nuclearcraft:molten_iron', amount: 270 }] }
  assert.equal(run(src, d).data.fluid_outputs[0].amount, 3000)
})
test('split molten inputs must not charge output total twice', src => {
  const d = { type: 'nuclearcraft:ingot_former', fluid_inputs: [{ fluid: 'nuclearcraft:molten_iron', amount: 45 }, { fluid: 'nuclearcraft:molten_iron', amount: 45 }], item_outputs: [{ item: 'minecraft:iron_ingot' }] }
  assert.equal(run(src, d).data.fluid_inputs.reduce((sum, x) => sum + x.amount, 0), 1000)
})
test('Foundry alloy universally removed including ATM', src => assert.ok(run(src, { type: 'modernfoundry:alloy', inputs: [], result: {} }, 'allthemodium:test_alloy').removed))
test('owned processing namespace retained', src => assert.equal(run(src, { type: 'modernfoundry:melting', ingredient: { item: 'minecraft:raw_iron' }, result: { fluid: 'modernfoundry:molten_iron', amount: 200 } }, 'industrial_colonies:processing/raw/iron').removed, false))
test('external raw iron smelting suppressed', src => assert.ok(run(src, { type: 'minecraft:smelting', ingredient: { item: 'minecraft:raw_iron' }, result: { id: 'minecraft:iron_ingot' } }).removed))
test('raw iron block cannot use native multiplied ore melting', src => assert.ok(run(src, installed('modernfoundry:smeltery/melting/metal/iron/raw_block'), 'modernfoundry:smeltery/melting/metal/iron/raw_block').removed))
test('generic raw-block item member is mapped', _src => assert.ok(policy.feedstocks['minecraft:raw_iron_block']))
test('nine iron nuggets cannot craft an ingot', src => assert.ok(run(src, { type: 'minecraft:crafting_shaped', key: { I: { item: 'minecraft:iron_nugget' } }, pattern: ['III','III','III'], result: { id: 'minecraft:iron_ingot' } }).removed))
test('raw crafting is not a furnace bypass', src => assert.ok(run(src, { type: 'minecraft:crafting_shapeless', ingredients: [{ item: 'minecraft:raw_iron' }], result: { id: 'minecraft:iron_ingot' } }).removed))
test('nine raw iron storage packing remains available', src => assert.equal(run(src, { type: 'minecraft:crafting_shaped', key: { I: { item: 'minecraft:raw_iron' } }, pattern: ['III','III','III'], result: { id: 'minecraft:raw_iron_block' } }).removed, false))
test('raw storage unpacking remains available', src => assert.equal(run(src, { type: 'minecraft:crafting_shapeless', ingredients: [{ item: 'minecraft:raw_iron_block' }], result: { id: 'minecraft:raw_iron', count: 9 } }).removed, false))
test('one ingot cannot become forty raw iron', src => assert.ok(run(src, { type: 'minecraft:crafting_shapeless', ingredients: [{ item: 'minecraft:iron_ingot' }], result: { id: 'minecraft:raw_iron', count: 40 } }).removed))
test('normal ingot/block conversion is preserved', src => assert.equal(run(src, { type: 'minecraft:crafting_shapeless', ingredients: [{ item: 'minecraft:iron_block' }], result: { id: 'minecraft:iron_ingot', count: 9 } }).removed, false))
test('unrelated shaped hardware is preserved', src => assert.equal(run(src, { type: 'minecraft:crafting_shaped', key: { I: { item: 'minecraft:iron_ingot' } }, pattern: ['I I','III'], result: { id: 'minecraft:hopper' } }).removed, false))
test('Create Mixer intentional brass is preserved', src => assert.equal(run(src, { type: 'create:mixing', ingredients: [{ item: 'minecraft:copper_ingot' }, { item: 'create:zinc_ingot' }], results: [{ id: 'create:brass_ingot' }] }).removed, false))
test('unrelated nonmetal TFMG fluid quantities are untouched', src => {
  const d = installed('tfmg:casting/plastic_sheet'); assert.deepEqual(run(src, d).data, d)
})
for (const [id, expected] of [['tfmg:industrial_blasting/steel', 200], ['tfmg:industrial_blasting/steel_from_dust', 75], ['tfmg:industrial_blasting/steel_from_raw_iron', 200]]) {
  test('normal steel retained with finite Fe cap: '+id, src => {
    const d = installed(id); const r = run(src, d, id)
    assert.equal(r.removed, false)
    assert.equal(r.data.results[0].amount, expected)
    assert.deepEqual(r.data.results.slice(1), d.results.slice(1))
    assert.equal(r.data.hot_air_usage, d.hot_air_usage); assert.equal(r.data.processing_time, d.processing_time)
  })
}
test('unverified Foundry scrap melting is removed', src => assert.ok(run(src, melt({ item: 'minecraft:iron_pickaxe' }, 270)).removed))
test('reagents never get scaled with a metal', src => {
  const d = { type: 'nuclearcraft:ingot_former', fluid_inputs: [{ fluid: 'nuclearcraft:molten_iron', amount: 90 }, { fluid: 'minecraft:water', amount: 250 }], item_outputs: [{ item: 'minecraft:iron_ingot' }], process_time: 123 }
  const r = run(src, d); assert.equal(r.data.fluid_inputs[1].amount, 250); assert.equal(r.data.process_time, 123)
})
test('unknown NC metal-fluid codec is unchanged and explicitly reviewed', src => {
  const d = { type: 'nuclearcraft:unclassified_future_codec', fluid_inputs: [{ fluid: 'nuclearcraft:molten_iron', amount: 90 }], fluid_outputs: [{ fluid: 'nuclearcraft:molten_steel', amount: 90 }] }
  const r = run(src, d); assert.deepEqual(r.data, d)
  assert.ok(r.audit.some(x => x.action === 'review-unclassified-metal-fluid'))
})
test('NC compound conversion scales only controlled metal density', src => {
  const id='nuclearcraft:chemical_reactor/beryllium_fluoride';const d=installed(id)
  const r=run(src,d,id)
  assert.equal(r.data.fluid_inputs[0].amount,2000)
  assert.deepEqual(r.data.fluid_inputs[1],d.fluid_inputs[1])
  assert.deepEqual(r.data.fluid_outputs,d.fluid_outputs)
  assert.equal(r.data.process_time,d.process_time);assert.equal(r.data.energy_per_tick,d.energy_per_tick)
})
test('NC 144 mB chemical metal input becomes 1600 not 1000', src => {
  const d={type:'nuclearcraft:chemical_reactor',fluid_inputs:[{fluid:'nuclearcraft:molten_iron',amount:144}],fluid_outputs:[{fluid:'nuclearcraft:molten_steel',amount:144}]}
  const r=run(src,d);assert.equal(r.data.fluid_inputs[0].amount,1600);assert.equal(r.data.fluid_outputs[0].amount,1600)
})
test('NC isotope/fuel fluids and irradiator quantities remain untouched', src => {
  const d={type:'nuclearcraft:irradiator',fluid_inputs:[{fluid:'nuclearcraft:uranium_hexafluoride',amount:144},{fluid:'nuclearcraft:thorium_fluoride',amount:90}],fluid_outputs:[{fluid:'nuclearcraft:plutonium_fluoride',amount:90}],item_inputs:[{item:'nuclearcraft:uranium_235',count:3}],item_outputs:[{item:'nuclearcraft:plutonium_239',count:2}],process_time:1600}
  assert.deepEqual(run(src,d).data,d)
})
const alloyPolicy = () => ({ ...clone(policy), alloyProducts: { 'nuclearcraft:bronze_ingot':true, 'mekanism:ingot_bronze':true, 'create:brass_ingot':true } })
test('native NC bronze alloy cannot bypass Mixer ownership', src => {
  const d = installed('nuclearcraft:alloy_smelter/bronze_ingots')
  assert.ok(run(src, d, 'nuclearcraft:alloy_smelter/bronze_ingots', alloyPolicy()).removed)
})
test('NC molten bronze chemical reactor cannot bypass Mixer ownership', src => {
  const id='nuclearcraft:chemical_reactor/bronze_molten'
  assert.ok(run(src,installed(id),id,alloyPolicy()).removed)
})
test('TFMG copper-zinc vat alloy cannot bypass Mixer ownership', src => {
  const d = { type:'tfmg:vat_machine_recipe', ingredients:[{item:'minecraft:copper_ingot'},{item:'create:zinc_ingot'}], results:[{id:'create:brass_ingot'}] }
  assert.ok(run(src, d, 'test:vat_brass', alloyPolicy()).removed)
})
test('existing bronze casting is not treated as alloying', src => {
  const d = { type:'modernfoundry:casting_table', fluid:{tag:'c:molten_bronze',amount:90}, result:{item:'mekanism:ingot_bronze'} }
  const r = run(src, d, 'test:cast_bronze', alloyPolicy()); assert.equal(r.removed,false); assert.equal(r.data.fluid.amount,1000)
})
test('existing Create Mixer alloy is not treated as forbidden alloying', src => {
  const d = { type:'create:mixing', ingredients:[{item:'minecraft:copper_ingot'},{item:'create:zinc_ingot'}], results:[{id:'create:brass_ingot'}] }
  assert.equal(run(src,d,'test:mixer_brass',alloyPolicy()).removed,false)
})
function execute(source, silent = false) {
  const failures = []
  for (const item of cases) { try { item.fn(source) } catch (e) { failures.push({ name: item.name, error: e.message }); if (!silent) console.log('FAIL '+item.name+': '+e.message) } }
  return { passed: cases.length - failures.length, total: cases.length, failures }
}
const report = execute(original)
if (process.argv.includes('--installed-audit')) {
  let audit=[]
  const context={console:{info(){}},JsonIO:{write(_p,value){audit=clone(value)}}}
  vm.createContext(context);vm.runInContext(original,context)
  const event={
    forEachRecipe(_filter,fn){for(const [id,entry] of Object.entries(inventory.recipes)) fn({getId:()=>id,serialize(){},json:JSON.stringify(entry.data),remove(){},merge(){return this}})},
    custom(_value){return{id(_id){}}}
  }
  context.icProcessingPolicy(event,clone(policy))
  const counts={};audit.forEach(entry=>{counts[entry.action]=(counts[entry.action]||0)+1})
  report.installedAudit={recipes:Object.keys(inventory.recipes).length,actions:counts,
    unclassifiedMetalFluids:audit.filter(entry=>entry.action==='review-unclassified-metal-fluid').map(entry=>entry.id)}
}
if (process.argv.includes('--mutations') && report.failures.length === 0) {
  // Each real safety branch must be detected if disabled. Mutation is in memory only.
  const mutations = [
    ['disable entire policy', 'function icProcessingPolicy(event, policy) {}'],
    ['erase nugget membership', original.replace('  var replacements = []', '  policy.nuggets = {}; var replacements = []')],
    ['erase finished value map', original.replace('  var replacements = []', '  policy.finishedValues = {}; var replacements = []')],
    ['restore Rhino-incompatible counts binding', original.replace('      var counts = {}', '      const counts = {}')],
    ['skip native casting stack repair', original.replace('        repairAlteredCastingStack(data)', '        /* removed casting repair */')],
    ['recreate entity melt via incompatible schema', original.replace('        recipe.merge({results:data.results})', '        recipe.remove(); replacements.push({id:id,data:data})')],
  ]
  report.mutations = mutations.map(([name, src]) => ({ name, killed: execute(src, true).failures.length > 0 }))
  if (report.mutations.some(x => !x.killed)) process.exitCode = 1
}
console.log(JSON.stringify(report, null, 2))
if (report.failures.length) process.exitCode = 1
