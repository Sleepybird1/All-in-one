"""100 mB migration layered on captured, installed material and semiconductor policies."""
import copy,json,re,shutil,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'progression/metal-units';STAGE=ROOT/'isolated-runtime/metal-units-01'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
old=read(ROOT/'processing/material_processing_catalog.json');cat=copy.deepcopy(old)
policy=cat['policy'];fluids=policy['fluidMetals']
for m,v in cat['metals'].items():v.update(ingot_mb=100,block_mb=900,nugget_mb=10)
for ref,v in policy['finishedValues'].items():
    v['amount']=10 if policy['nuggets'].get(ref) else v['amount']/10
    assert int(v['amount'])==v['amount'];v['amount']=int(v['amount'])
policy['steelFeedValues']={'minecraft:raw_iron':20,'create:crushed_raw_iron':20,'#c:dusts/iron':8}
def metal(v):
    ref=v.get('fluid',v.get('id',('#'+v['tag']) if 'tag' in v else ''))
    return fluids.get(ref) if isinstance(ref,str) else None
def scale(v,input_side=False):
    if isinstance(v,list):
        for x in v:scale(x,input_side)
    elif isinstance(v,dict):
        if metal(v) and 'amount' in v:
            n=v['amount']/10;v['amount']=max(1,math.ceil(n) if input_side else math.floor(n+.5))
        for k,x in v.items():
            if isinstance(x,(list,dict)):scale(x,input_side)
changes={}
for rid,recipe in cat['recipes'].items():
    before=copy.deepcopy(recipe)
    for k,v in recipe.items():
        if isinstance(v,(dict,list)):scale(v,k in ('fluid','ingredient','ingredients','input','inputs','fluid_input','fluid_inputs'))
    if '/foundry/' in rid and rid.endswith('/nugget'):recipe['result']['amount']=10
    if '/casting/' in rid and rid.endswith('/nugget'):recipe['fluid']['amount']=10
    if recipe!=before:changes[rid]={'before':before,'after':recipe}
# Preserve all nonmetal quantities, machine gates, heat and timing. Existing fractions
# expressed as item-to-item arc batches need no change: their ingot ratios are unchanged.
text=(SRC/'baseline/kubejs/server_scripts/zz_industrial_material_processing.js').read_text(encoding='utf-8')
text=re.sub(r'  const policy = .*',lambda _: '  const policy = '+json.dumps(policy,separators=(',',':')),text)
def replace_recipe(m):
    rid=json.loads(m.group(2));return '  event.custom('+json.dumps(cat['recipes'][rid],separators=(',',':'))+').id('+json.dumps(rid)+')'
text=re.sub(r'  event.custom\((\{[^\n]+\})\)\.id\(("[^\n]+")\)',replace_recipe,text)
text=text.replace('1000 / unit','100 / unit')
text=text.replace("{'minecraft:raw_iron':200,'create:crushed_raw_iron':200,'#c:dusts/iron':75}","{'minecraft:raw_iron':20,'create:crushed_raw_iron':20,'#c:dusts/iron':8}")
text='// 100 mB unit migration; authoritative generator: tools/build_metal_units.py\n'+text
(SRC/'candidate.material-processing.js').write_text(text,encoding='utf-8')
ownership=(SRC/'baseline/kubejs/server_scripts/zzz_industrial_ownership.js').read_text(encoding='utf-8')
ownership=ownership.replace("id:'bigreactors:yellorium',amount:2000","id:'bigreactors:yellorium',amount:200").replace("fluid:'bigreactors:yellorium',amount:1000","fluid:'bigreactors:yellorium',amount:100")
(SRC/'candidate.ownership.js').write_text(ownership,encoding='utf-8')
retired=read(ROOT/'progression/semiconductors/migration.json')['retired']
for rid in retired:cat['recipes'].pop(rid)
dump(SRC/'effective.material-catalog.json',cat)
dump(SRC/'migration.json',{'changed':changes,'ingotMb':100,'blockMb':900,'nuggetMb':10,'minimumTraceMb':1})
if not STAGE.exists():
    STAGE.mkdir();base=ROOT/'isolated-runtime/semiconductors-01'
    for name in ('mods','config','defaultconfigs','kubejs','kjsgen','offline-maven'):
        if (base/name).exists():shutil.copytree(base/name,STAGE/name)
    shutil.copy2(base/'offline-assets.properties',STAGE/'offline-assets.properties')
    (STAGE/'geology-smoke.init.gradle').write_text((base/'geology-smoke.init.gradle').read_text(encoding='utf-8').replace('semiconductors-01','metal-units-01'),encoding='utf-8')
for folder in ('kubejs/server_scripts','kjsgen/projects'):
    shutil.copytree(SRC/'baseline'/folder,STAGE/folder,dirs_exist_ok=True)
for src,dst in [('candidate.material-processing.js','zz_industrial_material_processing.js'),('candidate.ownership.js','zzz_industrial_ownership.js')]:shutil.copy2(SRC/src,STAGE/'kubejs/server_scripts'/dst)
for folder,target in [('ownership','ownership-migration.json'),('semiconductors','semiconductor-migration.json')]:shutil.copy2(ROOT/'progression'/folder/'migration.json',STAGE/target)
shutil.copy2(SRC/'migration.json',STAGE/'metal-unit-migration.json')
print('Prepared',len(changes),'owned metal recipe changes; retained',len(cat['recipes']),'material recipes')
