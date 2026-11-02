"""Use vanilla village sites/biomes with compact vanilla and rare modded villages."""
import copy,hashlib,json,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PACK=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
OUT=ROOT/'progression/village-distribution';STAGE=ROOT/'isolated-runtime/advanced-semiconductors-01'
def parse(b):return json.loads(re.sub(r'(?m)^\s*//.*$','',b.decode('utf-8-sig')))
catalog={};sets={}
for jar in (PACK/'mods').glob('*.jar'):
    with zipfile.ZipFile(jar) as z:
        for path in z.namelist():
            if path.startswith('data/') and '/tags/' not in path and path.endswith('.json') and ('/worldgen/structure/' in path or '/worldgen/structure_set/' in path):
                try:body=parse(z.read(path))
                except (ValueError,UnicodeDecodeError):continue
                (sets if '/structure_set/' in path else catalog)[path]=body
vanilla=Path(r'C:\Users\GodPC\Documents\Codex\2026-08-16\ok\work\gradle-user-home/caches/neoformruntime/intermediate_results/extractServer_3708c41639d60b56739a2bf9df29858932d3099a_output.jar')
files={};pool=[];restricted=[];removed=[]
def data(path,body):files['kubejs/'+path]=(json.dumps(body,indent=2)+'\n').encode()
union='industrial_colonies:vanilla_village_biomes'
styles=['plains','desert','savanna','snowy','taiga']
data('data/industrial_colonies/tags/worldgen/biome/vanilla_village_biomes.json',{'replace':True,'values':['#minecraft:has_structure/village_'+s for s in styles]})
with zipfile.ZipFile(vanilla) as z:
    shared=parse(z.read('data/minecraft/worldgen/structure_set/villages.json'))
    original_placement=copy.deepcopy(shared['placement'])
    for style in styles:
        rid='minecraft:village_'+style;path='data/minecraft/worldgen/structure/village_'+style+'.json'
        body=parse(z.read(path));assert body['size']==6;body['size']=4;data(path,body)
        pool.append({'structure':rid,'weight':1000})
# Alien/nether settlements retain their separate progression context. All
# Overworld village styles and generated MineColonies settlements are included.
for path,body in catalog.items():
    namespace=path.split('/')[1];name=path.split('/worldgen/structure/')[1][:-5]
    is_ctov=namespace=='ctov' and '/village_' in name
    is_colony=namespace=='minecolonies' and (name.endswith('_colony') or name.endswith('_camp')) and name!='warpednetherlands_colony'
    is_other=namespace not in ('ad_astra','stellaris','allthemodium','ctov','minecolonies') and 'village' in name
    if not (is_ctov or is_colony or is_other):continue
    rid=namespace+':'+name;restricted.append(rid)
    live=PACK/'kubejs'/path
    value=parse(live.read_bytes()) if live.exists() else copy.deepcopy(body)
    value['biomes']={'type':'neoforge:and','values':[value['biomes'],'#'+union]}
    data(path,value)
    if not is_ctov:pool.append({'structure':rid,'weight':1})
for name in ('plains','desert','savanna','snowy_igloo','taiga'):
    pool.append({'structure':'ctov:small/village_'+name,'weight':20})
for path,body in sets.items():
    selected=[e for e in body.get('structures',[]) if e.get('structure') in restricted]
    if not selected:continue
    value=copy.deepcopy(body);remaining=[e for e in body['structures'] if e.get('structure') not in restricted]
    if remaining:
        value['structures']=remaining
        # Nether's sole eligible colony already wins after all incompatible
        # Overworld entries are retried; preserve that separate destination rate.
        if path!='data/minecolonies/worldgen/structure_set/empty_colony.json':
            value['placement']['frequency']=value['placement'].get('frequency',1)*sum(e['weight'] for e in remaining)/sum(e['weight'] for e in body['structures'])
    else:value['placement']['frequency']=0.0
    removed.append(path) # Final global-landmark generator owns all placement sets.
shared['structures']=pool;assert shared['placement']==original_placement
config=PACK/'config/ctov-common.toml';text=config.read_text(encoding='utf-8-sig')
for flag in ('generatesmallVillage','generatemediumVillage','generatelargeVillage','generatePillagerOutpost'):
    text,count=re.subn(r'(?m)^(\s*'+flag+r'\s*=\s*)true\s*$',r'\g<1>false',text);assert count==1
files['config/ctov-common.toml']=text.encode()
manifest={}
for rel,content in files.items():
    candidate=OUT/'candidate'/rel;candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_bytes(content)
    live=PACK/rel;baseline=OUT/'baseline'/rel
    if live.exists() and not baseline.exists():baseline.parent.mkdir(parents=True,exist_ok=True);baseline.write_bytes(live.read_bytes())
    manifest[rel]=hashlib.sha256(live.read_bytes()).hexdigest() if live.exists() else None
    stage=STAGE/rel;stage.parent.mkdir(parents=True,exist_ok=True);stage.write_bytes(content)
spec={'status':'PREPARED','restrictedStructures':restricted,'sharedPool':pool,'historicalVanillaPlacement':original_placement,'siteOwner':'industrial_colonies:global_landmarks','replacedSets':removed,'files':list(files),'vanillaSize':4,'ctov':'Only five small styles, weight 20 versus 1000 per vanilla style; original CTOV injection disabled'}
for dest in (OUT/'migration.json',STAGE/'village-distribution-migration.json'):dest.write_text(json.dumps(spec,indent=2),encoding='utf-8')
(OUT/'live-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('PREPARED',len(restricted),'village/settlement biome restrictions,',len(pool),'shared entries,',len(files),'files')
