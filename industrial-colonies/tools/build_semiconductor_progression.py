"""Scoped semiconductor migration from an immutable capture of the installed project."""
import copy, hashlib, json, shutil, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'progression/semiconductors'
PACK=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
STAGE=ROOT/'isolated-runtime/semiconductors-01'
NS='industrial_colonies:'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def item(s,count=1):return dict(kind='ITEM',id=s,**({'count':count} if count!=1 else {}))
def fluid(s,n):return dict(kind='FLUID',id=s,amount=n)
SRC.mkdir(parents=True,exist_ok=True)
for name,rel in {'baseline.default.json':'kjsgen/projects/default.json','baseline.kjsgen_recipes.js':'kubejs/server_scripts/kjsgen_recipes.js'}.items():
    if not (SRC/name).exists():shutil.copy2(PACK/rel,SRC/name)
old=read(SRC/'baseline.default.json');new=copy.deepcopy(old)
cards={c['recipeId']:c for c in new['recipes']};changed={}
def seq(path,source,out,steps,count=2):
    c=cards[NS+'electronics/'+path];changed[c['recipeId']]=out
    c['slots']={'input':item(source),'transitional':item(source),'output0':item(out,count)}
    c['params']={'loops':'2','__seqLen':str(len(steps))}
    for n,(kind,machine,feed) in enumerate(steps):
        c['params']['seq'+str(n)]=kind;c['slots'][f'__machine_step_{n}_{kind}']=item(machine)
        if feed:c['slots'][('seqFluid' if feed['kind']=='FLUID' else 'seqItem')+str(n)]=feed
    return c
C='createcasing:copper_'
c=seq('prepared_silicon_wafer',NS+'high_purity_silicon',NS+'prepared_silicon_wafer',[
    ('cutting',C+'mechanical_saw',None),('filling','create:spout',fluid('minecraft:water',250)),('pressing',C+'press',None)])
c['comment']='[Semiconductors] Purified silicon only. Two Copper cutting, rinsing and finishing passes produce two prepared wafers; contacts are added after etching.'
c=cards[NS+'electronics/etched_silicon_wafer'];changed[c['recipeId']]=NS+'etched_silicon_wafer'
c['comment']='[Semiconductors] Heated, size-3 steel Chemical Vat: one prepared wafer and 500 mB sulfuric acid produce one etched wafer in 600 ticks. Required before either doping sequence.'
for polarity,dopant in [('n',NS+'phosphoric_acid'),('p','nuclearcraft:boric_acid')]:
    c=seq(polarity+'_semiconductor',NS+'etched_silicon_wafer','tfmg:'+polarity+'_semiconductor',[
        ('filling','create:spout',fluid(dopant,100)),
        ('filling','create:spout',fluid('minecraft:water',250)),
        ('deploying',C+'deployer',item('tfmg:copper_wire')),
        ('deploying',C+'deployer',item('tfmg:plastic_sheet')),
        ('cutting',C+'mechanical_saw',None),('pressing',C+'press',None)])
    c['comment']='[Semiconductors] Two passes: processed '+('phosphorus' if polarity=='n' else 'boron')+' dopant solution, rinse, Copper contact/insulation assembly, dicing and pressing. Produces two parts; no capacitors, redstone or sulfur-dust dopant shortcut. Game-scale deposition abstraction.'
rid=NS+'electronics/bootstrap_hydrogen_chloride'
c=dict(uid=str(uuid.uuid5(uuid.NAMESPACE_URL,rid)),recipeId=rid,type='industrial_colonies:tfmg_chemical_vat',replaceRecipe=False,
       comment='[Semiconductor bootstrap] Heated size-3 steel vat combines 250 mB each of existing chlorine and hydrogen into 250 mB HCl. Existing powered brine electrolysis supplies chlorine; coke processing or electrolysis supplies hydrogen. Same 1:1 reagent consumption as Mekanism, without needing semiconductor-dependent chemical machinery first.',
       slots={'ingredients0':fluid('mekanism:chlorine',250),'ingredients1':fluid('tfmg:hydrogen',250),'results0':fluid('mekanism:hydrogen_chloride',250)},
       params={'vatMode':'steel','machineMode':'mixing','heat':'heated','minSize':'3','processingTime':'600'})
new['recipes'].append(c);changed[rid]='mekanism:hydrogen_chloride'
dump(SRC/'candidate.default.json',new)
retired=[NS+'processing/silicon/'+p for p in ('n_semiconductor','p_semiconductor','wafer_cutting')]
owned={v:k for k,v in changed.items() if k!=rid}
policy='''// priority: -1200
// Semiconductor ownership overlays the unchanged material/early-industry migrations.
ServerEvents.recipes(event => {
  var owned = OWNED;
  var retired = RETIRED;
  Object.keys(owned).forEach(out => event.remove({output:out,not:{id:owned[out]}}));
  retired.forEach(id => event.remove({id:id}));
  function refs(value, list) {
    if(!value || typeof value!=='object')return;
    if(Array.isArray(value)){value.forEach(v=>refs(v,list));return;}
    if(typeof value.id==='string')list.push(value.id);
    if(typeof value.item==='string')list.push(value.item);
    Object.keys(value).forEach(k=>{if(typeof value[k]==='object')refs(value[k],list);});
  }
  event.addedRecipes.removeIf(recipe => {
    var id=String(recipe.getId());
    if(retired.indexOf(id)>=0)return true;
    try{recipe.serialize();}catch(error){return false;}
    var data=JSON.parse(recipe.json.toString()),outputs=[];
    ['result','results','output','outputs','item_output','item_outputs'].forEach(k=>refs(data[k],outputs));
    return outputs.some(out=>owned[out] && owned[out]!==id);
  });
});
'''.replace('OWNED',json.dumps(owned)).replace('RETIRED',json.dumps(retired))
(SRC/'semiconductor_policy.js').write_text(policy,encoding='utf-8')
catalog=read(ROOT/'processing/material_processing_catalog.json')
for rid in retired:assert catalog['recipes'].pop(rid)
dump(SRC/'effective.material-catalog.json',catalog)
assert len(catalog['recipes'])==296
untouched=[c for c in old['recipes'] if c['recipeId'] not in changed]
assert all(c==cards[c['recipeId']] for c in untouched)
spec={'changed':changed,'owned':owned,'retired':retired,'untouchedCards':len(untouched),'materialRecipesRetained':296}
dump(SRC/'migration.json',spec)
if not STAGE.exists():
    STAGE.mkdir()
    base=ROOT/'isolated-runtime/ownership-01'
    for name in ('mods','config','defaultconfigs','kubejs','kjsgen','offline-maven'):
        if (base/name).exists():shutil.copytree(base/name,STAGE/name)
    shutil.copy2(base/'offline-assets.properties',STAGE/'offline-assets.properties')
    (STAGE/'geology-smoke.init.gradle').write_text((base/'geology-smoke.init.gradle').read_text(encoding='utf-8').replace('ownership-01','semiconductors-01'),encoding='utf-8')
shutil.copy2(SRC/'candidate.default.json',STAGE/'kjsgen/projects/default.json')
shutil.copy2(SRC/'baseline.kjsgen_recipes.js',STAGE/'kubejs/server_scripts/kjsgen_recipes.js')
shutil.copy2(SRC/'semiconductor_policy.js',STAGE/'kubejs/server_scripts/zzzz_industrial_semiconductors.js')
shutil.copy2(SRC/'migration.json',STAGE/'semiconductor-migration.json')
shutil.copy2(ROOT/'progression/ownership/migration.json',STAGE/'ownership-migration.json')
dump(SRC/'source-validation.json',dict(status='PASS',**spec))
print(json.dumps(spec,indent=2))
