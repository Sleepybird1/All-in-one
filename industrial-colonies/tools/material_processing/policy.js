// This file is prepended to the generated last-priority recipe script.
// It handles already-installed recipes too, including other KubeJS exporters.
// Rhino's lexical declarations inside repeatedly invoked/nested blocks can retain
// a const binding and throw on the next recipe. Use function-scoped var throughout
// this compatibility boundary. All iteration callbacks are synchronous; no block
// binding or asynchronous loop capture is required by this policy.
function icProcessingPolicy(event, policy) {
  var replacements = []
  var audit = []
  function refs(value, result) {
    if (value === null || value === undefined) return result
    if (typeof value === 'string') { result.push(value); return result }
    if (Array.isArray(value)) { value.forEach(v => refs(v, result)); return result }
    if (typeof value === 'object') {
      Object.keys(value).forEach(key => {
        if (key === 'item' || key === 'id' || key === 'tag') {
          if (typeof value[key] === 'string') result.push((key === 'tag' ? '#' : '') + value[key])
          else refs(value[key], result)
        } else if (key !== 'type') refs(value[key], result)
      })
    }
    return result
  }
  function inputs(data) {
    var result = []
    ;['ingredient','ingredients','input','inputs','item_input','item_inputs','primary_input','secondary_input','key'].forEach(key => refs(data[key], result))
    return result
  }
  function outputs(data) {
    var result = []
    ;['result','results','output','outputs','item_output','item_outputs','primary_output','secondary_output'].forEach(key => refs(data[key], result))
    return result
  }
  function includesAny(values, map) { return values.some(value => map[value] === true) }
  function metalFluid(obj) {
    if (!obj || typeof obj !== 'object') return null
    var id = obj.fluid || obj.id || (obj.tag ? '#' + obj.tag : '')
    return policy.fluidMetals[id] || null
  }
  // Stack counts can wrap their item (CreateMetallurgy result.item), or their
  // predicate (NeoForge IngredientWithSize). Never count an alternative as an
  // additional consumed item, and never multiply the same count twice.
  function stacks(value, multiplier, alternatives) {
    if (value === null || value === undefined) return []
    if (typeof value === 'string') return [{ref:value, count:multiplier}]
    if (Array.isArray(value)) {
      var branches = value.map(v => stacks(v, multiplier, false))
      if (alternatives) return branches.length ? branches[0].map(entry => {
        var known = policy.finishedValues[entry.ref]
        if (!known) return entry
        var lowest = entry.count * known.amount
        branches.forEach(branch => branch.forEach(other => {
          var amount = policy.finishedValues[other.ref]
          if (amount && amount.metal === known.metal) lowest = Math.min(lowest, other.count * amount.amount)
        }))
        return {ref:entry.ref, count:lowest / known.amount}
      }) : []
      return [].concat.apply([], branches)
    }
    if (typeof value !== 'object') return []
    var quantity = multiplier * (typeof value.count === 'number' ? value.count : 1)
    if (typeof value.item === 'string') return [{ref:value.item, count:quantity}]
    if (typeof value.id === 'string' && !metalFluid(value)) return [{ref:value.id, count:quantity}]
    if (typeof value.tag === 'string' && !metalFluid(value)) return [{ref:'#'+value.tag, count:quantity}]
    if (value.item && typeof value.item === 'object') return stacks(value.item, quantity, false)
    if (value.basePredicate) return stacks(value.basePredicate, quantity, true)
    if (value.ingredient) return stacks(value.ingredient, quantity, true)
    return []
  }
  function itemStacks(data, direction) {
    var result = []
    var fields = direction === 'in' ?
      ['ingredient','ingredients','input','inputs','item_input','item_inputs','primary_input','secondary_input'] :
      ['result','results','output','outputs','item_output','item_outputs','primary_output','secondary_output']
    fields.forEach(key => { result = result.concat(stacks(data[key], 1, direction === 'in' && (key === 'ingredient' || key === 'input'))) })
    if (direction === 'in' && data.key && data.pattern) {
      var counts = {}
      data.pattern.forEach(row => { String(row).split('').forEach(letter => { if (letter !== ' ') counts[letter]=(counts[letter] || 0)+1 }) })
      Object.keys(counts).forEach(letter => { result = result.concat(stacks(data.key[letter], counts[letter], true)) })
    }
    return result
  }
  function materialTotals(entries) {
    var totals = {}
    entries.forEach(entry => {
      var value = policy.finishedValues[entry.ref]
      if (value) totals[value.metal] = (totals[value.metal] || 0) + value.amount * entry.count
    })
    return totals
  }
  function inputMetal(ref) {
    if (policy.finishedValues[ref]) return policy.finishedValues[ref].metal
    var common = /^#c:(?:ingots|dusts|raw_materials|crushed_raw_materials)\/([a-z_]+)$/.exec(ref)
    if (common) return common[1]
    var named = /^[a-z_]+:(copper|zinc|tin)_(?:dust|ingot)$/.exec(ref) || /^[a-z_]+:(?:dust|ingot)_(copper|zinc|tin)$/.exec(ref)
    return named ? named[1] : null
  }
  function rawStorage(ref) {
    var match = /^#c:(?:storage_blocks\/raw_|raw_blocks\/)([a-z_]+)$/.exec(ref)
    if (match) return {metal:match[1], units:9}
    match = /^#c:raw_materials\/([a-z_]+)$/.exec(ref)
    if (match) return {metal:match[1], units:1}
    match = /^[a-z_]+:raw_([a-z_]+)_block$/.exec(ref) || /^[a-z_]+:block_raw_([a-z_]+)$/.exec(ref)
    if (match) return {metal:match[1], units:9}
    match = /^[a-z_]+:raw_([a-z_]+)$/.exec(ref)
    return match ? {metal:match[1], units:1} : null
  }
  function safeRawStorageCraft(inStacks, outStacks) {
    if (!inStacks.length || !outStacks.length) return false
    var metal = null, input = 0, output = 0, valid = true
    ;[inStacks,outStacks].forEach((list, side) => list.forEach(entry => {
      var raw = rawStorage(entry.ref)
      if (!raw || (metal && metal !== raw.metal)) { valid=false; return }
      metal=raw.metal
      if (side === 0) input += raw.units * entry.count
      else output += raw.units * entry.count
    }))
    return valid && input >= output
  }
  function fluidNodes(value, nodes) {
    if (!value || typeof value !== 'object') return
    if (Array.isArray(value)) { value.forEach(v => fluidNodes(v, nodes)); return }
    var metal=metalFluid(value)
    if (metal && typeof value.amount === 'number') { nodes.push({node:value, metal:metal}); return }
    Object.keys(value).forEach(key => { if (typeof value[key] === 'object') fluidNodes(value[key], nodes) })
  }
  function normalizeFluidFields(data, fields, factor, direction, exactTotals) {
    var grouped = {}
    fields.forEach(key => {
      var nodes=[]; fluidNodes(data[key], nodes)
      nodes.forEach(entry => { if (!grouped[entry.metal]) grouped[entry.metal]=[]; grouped[entry.metal].push(entry.node) })
    })
    var changed=false
    Object.keys(grouped).forEach(metal => {
      var nodes=grouped[metal]
      var nativeTotal=nodes.reduce((sum,node) => sum + node.amount, 0)
      var desired=exactTotals[metal]
      nodes.forEach(node => {
        var value=desired !== undefined && nativeTotal > 0 ? desired * node.amount / nativeTotal : node.amount * factor
        var amount=direction === 'in' ? Math.ceil(value) : Math.floor(value)
        if (amount !== node.amount) { node.amount=amount; changed=true }
      })
    })
    return changed
  }
  function repairAlteredCastingStack(data) {
    if (data.type !== 'createmetallurgy:casting_in_table' && data.type !== 'createmetallurgy:casting_in_basin') return
    if (!data.result || typeof data.result.item !== 'string') return
    // Almost Unified can leave item as a bare string. CM's StackOutput codec
    // requires ItemStack.CODEC under "item", so carry the existing count once.
    data.result.item = {id:data.result.item, count:data.result.count === undefined ? 1 : data.result.count}
    if (data.result.count !== undefined) delete data.result.count
  }
  event.forEachRecipe({}, recipe => {
    var id = String(recipe.getId())
    if (id.indexOf('industrial_colonies:processing/') === 0) return
    recipe.serialize()
    var data = JSON.parse(String(recipe.json))
    var type = data.type || ''
    // Ownership revision: never recreate a duplicate processor during value normalization.
    if (['mekanism:crushing','immersiveengineering:crusher','createmetallurgy:grinding','mekanism:washing',
         'modernfoundry:alloy','immersiveengineering:alloy','createmetallurgy:alloying','createmetallurgy:melting',
         'createmetallurgy:bulk_melting','createmetallurgy:entity_melting','createmetallurgy:casting_in_table',
         'createmetallurgy:casting_in_basin','createdieselgenerators:casting','tfmg:casting'].indexOf(type) >= 0) {
      recipe.remove(); audit.push({id:id,action:'remove',reason:'Assigned machine-family ownership'}); return
    }
    // The global Foundry no-alloy rule is universal, not a new supermetal chain.
    if (type !== 'modernfoundry:alloy' && (id.indexOf('allthemodium:') === 0 || id.indexOf('industrial_colonies:allthemodium/') === 0)) return
    var inRefs = inputs(data)
    var outRefs = outputs(data)
    var inStacks = itemStacks(data, 'in')
    var outStacks = itemStacks(data, 'out')
    var isCraft = type === 'minecraft:crafting_shaped' || type === 'minecraft:crafting_shapeless'
    var steelIds = ['tfmg:industrial_blasting/steel','tfmg:industrial_blasting/steel_from_dust','tfmg:industrial_blasting/steel_from_raw_iron']
    var steelFeeds = policy.steelFeedValues || {'minecraft:raw_iron':200,'create:crushed_raw_iron':200,'#c:dusts/iron':75}
    var steelValue = inStacks.reduce((sum,entry) => sum + (steelFeeds[entry.ref] || 0) * entry.count, 0)
    var steelBootstrap = type === 'tfmg:industrial_blasting' && steelIds.indexOf(id) >= 0 && steelValue > 0
    var copperAlloyFeed = inRefs.some(ref => inputMetal(ref) === 'copper')
    var secondAlloyFeed = inRefs.some(ref => inputMetal(ref) === 'zinc' || inputMetal(ref) === 'tin')
    var alloyFluidInputs=[], alloyFluidOutputs=[]
    fluidNodes(data.fluid_inputs, alloyFluidInputs); fluidNodes(data.fluid_outputs, alloyFluidOutputs)
    var moltenBrassBronze = type === 'nuclearcraft:chemical_reactor' &&
      alloyFluidInputs.some(entry => entry.metal === 'copper') &&
      alloyFluidInputs.some(entry => entry.metal === 'tin' || entry.metal === 'zinc') &&
      alloyFluidOutputs.some(entry => entry.metal === 'brass' || entry.metal === 'bronze')
    var reason = null
    if (type === 'modernfoundry:alloy') reason = 'Foundry is melt/cast only'
    else if (policy.removeIds[id]) reason = 'Exact conflicting progression recipe'
    else if (moltenBrassBronze) reason = 'Brass/Bronze molten alloying belongs to the owned Mixer'
    else if (includesAny(outRefs, policy.alloyProducts || {}) &&
             (type.indexOf('alloy') >= 0 || (type === 'tfmg:vat_machine_recipe' && copperAlloyFeed && secondAlloyFeed))) reason = 'Brass/Bronze alloying belongs to the owned Mixer'
    else if (!steelBootstrap && includesAny(inRefs, policy.feedstocks) && !(isCraft && safeRawStorageCraft(inStacks, outStacks))) reason = 'Raw feedstock must enter its owned processing chain'
    else if (outStacks.some(entry => rawStorage(entry.ref)) && includesAny(inRefs, policy.finishedForms)) reason = 'Finished metal cannot be converted back to raw reserves'
    else if (includesAny(outRefs, policy.claimedOutputs)) reason = 'Owned processing intermediate acquisition'
    else if (includesAny(inRefs, policy.nuggets) && includesAny(outRefs, policy.ingots)) reason = 'Nugget crafting violates fixed mB values; use Foundry'
    // Native ore_melting applies extra smeltery/foundry rates and byproducts.
    else if (type === 'modernfoundry:ore_melting' && includesAny(inRefs, policy.metalInputs)) reason = 'No machine-dependent ore multiplication'
    // Damageable scrap/tool returns assume vanilla nugget values, so cannot be
    // safely retained under the new 25/10 mB trace economy without a craft-cost audit.
    else if ((type === 'modernfoundry:damagable_melting' || type === 'modernfoundry:material_melting' || type === 'modernfoundry:melting') &&
             !includesAny(inRefs, policy.finishedForms) && metalFluid(data.result)) reason = 'Unverified scrap remelting under fixed metal values'
    if (reason) {
      recipe.remove(); audit.push({id:id, action:'remove', reason:reason}); return
    }
    if (steelBootstrap) {
      // Keep the native heat, flux, slag, furnace gas and machine. Only its
      // steel endpoint is capped at the approved finite Iron feed potential.
      var changed=false
      ;(data.results || []).forEach(result => {
        if (metalFluid(result) === 'steel' && result.amount !== steelValue) { result.amount=steelValue; changed=true }
      })
      if (changed) { recipe.remove(); replacements.push({id:id,data:data}); audit.push({id:id,action:'normalize-steel-feed',metalMb:steelValue}) }
      return
    }
    // Shared molten-fluid ecosystems must agree, including molds and TFMG blast outputs.
    // Only metal-fluid quantities change; reagents, fuels, timing and nonmetal fluids stay intact.
    // Installed NC ingot-former uses 90 mB per ingot of these exact shared
    // molten fluids. Chemical/irradiator metal fields use that same density;
    // 144 native mB therefore becomes 1600, never an assumed one-ingot 1000.
    // Only controlled metal fields participate: isotope/fuel compounds do not.
    var unit = type.indexOf('modernfoundry:') === 0 || type.indexOf('createmetallurgy:') === 0 ||
      type === 'nuclearcraft:melter' || type === 'nuclearcraft:ingot_former' ||
      type === 'nuclearcraft:chemical_reactor' || type === 'nuclearcraft:irradiator' ? 90 :
      type.indexOf('tfmg:') === 0 ? 144 : null
    if (!unit) {
      if (type.indexOf('nuclearcraft:') === 0) {
        var nodes=[]; fluidNodes(data,nodes)
        if (nodes.length) audit.push({id:id,action:'review-unclassified-metal-fluid',reason:'No blanket native unit assumption for this NuclearCraft codec'})
      }
      return
    }
    var changed = normalizeFluidFields(data, ['fluid','ingredient','ingredients','input','inputs','fluid_input','fluid_inputs'], 1000 / unit, 'in', materialTotals(outStacks))
    if (normalizeFluidFields(data, ['result','results','output','outputs','fluid_output','fluid_outputs'], 1000 / unit, 'out', materialTotals(inStacks))) changed=true
    if (changed) {
      if (type === 'createmetallurgy:entity_melting' && Array.isArray(data.ingredients) && data.ingredients.length === 0) {
        // KubeJS falls back to UnknownKubeRecipe for this native-valid shape.
        // Its merge() updates json, marks it changed and has no-op deserialize;
        // serialize is also a no-op. Preserve the original recipe/empty input
        // rather than re-entering event.custom's incompatible nonempty schema.
        recipe.merge({results:data.results})
        audit.push({id:id, action:'normalize-metal-fluid-in-place'})
      } else {
        repairAlteredCastingStack(data)
        recipe.remove(); replacements.push({id:id, data:data})
        audit.push({id:id, action:'normalize-metal-fluid'})
      }
    }
  })
  replacements.forEach(r => event.custom(r.data).id(r.id))
  // KubeJS creates its own root, but not an optional exported/ directory. A
  // diagnostic write must never abort the entire owned recipe installation.
  try { JsonIO.write('kubejs/industrial-material-processing-policy.json', audit) }
  catch (auditError) { console.warn('[Industrial Colonies] Could not save processing audit: ' + auditError) }
  console.info('[Industrial Colonies] Material processing policy: ' + audit.length + ' audited recipe changes.')
}
