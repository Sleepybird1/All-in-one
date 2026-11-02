"""Make finished metal blocks one bucket while keeping 100 mB ingots."""
import copy,hashlib,json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'progression/bucket-blocks';STAGE=ROOT/'isolated-runtime/bucket-blocks-01'
PACK=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
SRC.mkdir(parents=True,exist_ok=True)
manifest={}
for folder in ('kubejs/server_scripts','kjsgen/projects'):
    for path in (PACK/folder).rglob('*'):
        if not path.is_file():continue
        rel=path.relative_to(PACK);dest=SRC/'baseline'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():shutil.copy2(path,dest)
        manifest[str(rel)]=hashlib.sha256(dest.read_bytes()).hexdigest()
asset='kubejs/assets/modernfoundry/hilt/fluid_tooltips/metals.json'
dest=SRC/'baseline'/asset;dest.parent.mkdir(parents=True,exist_ok=True)
if not dest.exists():shutil.copy2(PACK/asset,dest)
manifest[asset]=hashlib.sha256(dest.read_bytes()).hexdigest();dump(SRC/'live-manifest.json',manifest)
old=read(ROOT/'progression/metal-units/effective.material-catalog.json');cat=copy.deepcopy(old)
def block_values(p):
    for ref,v in p['finishedValues'].items():
        if v['amount']==900:v['amount']=1000
block_values(cat['policy'])
for props in cat['metals'].values():props['block_mb']=1000
changed={}
for rid,v in cat['recipes'].items():
    if rid.endswith('/block') and ('processing/casting/' in rid or 'processing/foundry/' in rid):
        field='fluid' if '/casting/' in rid else 'result';assert v[field]['amount']==900
        v[field]['amount']=1000;changed[rid]=v
script=(SRC/'baseline/kubejs/server_scripts/zz_industrial_material_processing.js').read_text(encoding='utf-8')
script=re.sub(r'  const policy = .*',lambda _: '  const policy = '+json.dumps(cat['policy'],separators=(',',':')),script)
def replace(m):
    rid=json.loads(m.group(2))
    return '  event.custom('+json.dumps(changed[rid],separators=(',',':'))+').id('+json.dumps(rid)+')' if rid in changed else m.group(0)
script=re.sub(r'  event.custom\((\{[^\n]+\})\)\.id\(("[^\n]+")\)',replace,script)
(SRC/'candidate.material-processing.js').write_text(script,encoding='utf-8')
unit=(SRC/'baseline/kubejs/server_scripts/zzzzz_industrial_metal_units.js').read_text(encoding='utf-8')
policy=json.loads(re.search(r'  var policy = (.*);',unit).group(1));block_values(policy)
unit=re.sub(r'  var policy = .*;',lambda _: '  var policy = '+json.dumps(policy,separators=(',',':'))+';',unit)
unit=re.sub(r'  var coreForms = .*;',lambda _: '  var coreForms = '+json.dumps(cat['metals'],separators=(',',':'))+';',unit)
anchor='    // Nine-nugget legacy shortcuts are incompatible with ten-nugget ingots.'
addition='''    // A bucket-sized block represents ten ingots in both directions.
    function value(stack){return policy.finishedValues[stack.ref];}
    if(inStacks.length===1 && outStacks.length===1 && value(inStacks[0]) && value(outStacks[0]) &&
       value(inStacks[0]).amount===1000 && policy.ingots[outStacks[0].ref] && value(inStacks[0]).metal===value(outStacks[0]).metal) {
      var result=data.result || (data.results && data.results[0]) || data.output;
      if(result && typeof result==='object')result.count=inStacks[0].count*10;
      else throw new Error('Unsupported block breakdown result: '+id);
      audit.push({id:id,action:'ten-ingot-breakdown'});
    }
    if(inStacks.length && outStacks.length===1 && inStacks.every(s=>policy.ingots[s.ref]) && value(outStacks[0]) && value(outStacks[0]).amount===1000 &&
       inStacks.every(s=>value(s).metal===value(outStacks[0]).metal)) {
      var target=outStacks[0],source=inStacks[0];
      if(target.ref.charAt(0)==='#')throw new Error('Unsupported tagged block crafting result: '+id);
      replacements.push({id:id,data:{type:'create:mechanical_crafting',pattern:['AAAAA','AAAAA'],key:{A:source.ref.charAt(0)==='#'?{tag:source.ref.substring(1)}:{item:source.ref}},result:{id:target.ref,count:1},accept_mirrored:true}});
      audit.push({id:id,action:'ten-ingot-block'});return true;
    }
'''
assert unit.count(anchor)==1;unit=unit.replace(anchor,addition+anchor)
(SRC/'unit_policy.js').write_text(unit,encoding='utf-8')
assetdata=read(SRC/'baseline'/asset)
for entry in assetdata['units']:
    if entry['key']=='gui.modernfoundry.fluid.block':assert entry['needed']==900;entry['needed']=1000
dump(SRC/'candidate-assets'/asset,assetdata);dump(SRC/'asset-files.json',[asset])
dump(SRC/'effective.material-catalog.json',cat);dump(SRC/'closure-policy.json',policy)
dump(SRC/'migration.json',{'changed':list(changed),'blockMb':1000,'ingotMb':100,'nuggetMb':10})
assert len(cat['recipes'])==296 and len(changed)>30
for rid,v in cat['recipes'].items():
    if rid not in changed:assert v==old['recipes'][rid]
dump(SRC/'source-validation.json',{'status':'PASS','changedBlockRecipes':len(changed),'unchangedMaterialRecipes':296-len(changed),'oreYieldsUnchanged':True,'semiconductorsUnchanged':True})
if not STAGE.exists():
    STAGE.mkdir();base=ROOT/'isolated-runtime/metal-units-01'
    for folder in ('mods','config','defaultconfigs','kubejs','kjsgen','offline-maven'):
        if (base/folder).exists():shutil.copytree(base/folder,STAGE/folder)
    shutil.copy2(base/'offline-assets.properties',STAGE/'offline-assets.properties')
    (STAGE/'geology-smoke.init.gradle').write_text((base/'geology-smoke.init.gradle').read_text(encoding='utf-8').replace('metal-units-01','bucket-blocks-01'),encoding='utf-8')
for folder in ('kubejs/server_scripts','kjsgen/projects'):shutil.copytree(SRC/'baseline'/folder,STAGE/folder,dirs_exist_ok=True)
for name,rel in [('candidate.material-processing.js','kubejs/server_scripts/zz_industrial_material_processing.js'),('unit_policy.js','kubejs/server_scripts/zzzzz_industrial_metal_units.js')]:shutil.copy2(SRC/name,STAGE/rel)
shutil.copy2(SRC/'candidate-assets'/asset,STAGE/asset);shutil.copy2(SRC/'closure-policy.json',STAGE/'closure-policy.json')
for folder,dst in [('ownership','ownership-migration.json'),('semiconductors','semiconductor-migration.json'),('metal-units','metal-unit-migration.json')]:shutil.copy2(ROOT/'progression'/folder/'migration.json',STAGE/dst)
shutil.copy2(SRC/'migration.json',STAGE/'block-unit-migration.json')
print('Prepared',len(changed),'block melt/cast changes, conversion closure, and full-bucket tooltip.')
