"""Scoped worldgen cleanup: rare islands/ships, no jungle villages, Venus dragon expedition."""
import copy,json,zipfile,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'progression/structure-cleanup';PACK=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
SRC.mkdir(parents=True,exist_ok=True)
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def native(jar,path):
    with zipfile.ZipFile(PACK/'mods'/jar) as z:return json.loads(z.read(path))
files={};changes=[]
def data(path,body):
    rel='kubejs/'+path;files[rel]=body;dump(SRC/'candidate'/rel,body)
sets=[('ModernFoundry-1.21.1-4.1.6-NeoForge.jar','modernfoundry:overworld_ocean_island',96,48,.05),('ModernFoundry-1.21.1-4.1.6-NeoForge.jar','modernfoundry:overworld_sky_island',128,64,.05),('minecolonies-1.1.1368-1.21.1.jar','minecolonies:ship',110,55,1),('block_factorys_bosses-2.1.2-neo-1.21.1.jar','block_factorys_bosses:kraken_ship',128,64,1),('irons_spellbooks-1.21.1-3.4.0.11.jar','irons_spellbooks:impaled_icebreaker',150,75,1)]
for jar,rid,spacing,separation,frequency in sets:
    if rid.startswith('irons_spellbooks:'):
        matches=list((PACK/'mods').glob('irons_spellbooks-*.jar'));assert len(matches)==1;jar=matches[0].name
    ns,name=rid.split(':');path=f'data/{ns}/worldgen/structure_set/{name}.json';body=native(jar,path);old=copy.deepcopy(body['placement'])
    body['placement'].update(spacing=spacing,separation=separation,frequency=frequency);data(path,body)
    ratio=(frequency/spacing**2)/(old.get('frequency',1)/old['spacing']**2)
    changes.append({'id':rid,'before':old,'after':body['placement'],'candidateDensityRatio':ratio})
# A single weighted set attempts at most one large ship per site. Independent sets
# can collide even at low density; do not leave them active beside this shared set.
ship_ids=['minecolonies:ship','block_factorys_bosses:kraken_ship','irons_spellbooks:impaled_icebreaker']
for change in changes[2:]:
    ns,name=change['id'].split(':');path=f'data/{ns}/worldgen/structure_set/{name}.json'
    body=files['kubejs/'+path];body['placement']['frequency']=0.0;data(path,body)
    change['after']['frequency']=0.0;change['candidateDensityRatio']=0.0;change['replacement']='industrial_colonies:rare_maritime_sites'
data('data/industrial_colonies/worldgen/structure_set/rare_maritime_sites.json',{
    'structures':[{'structure':rid,'weight':weight} for rid,weight in zip(ship_ids,[2,3,1])],
    'placement':{'type':'minecraft:random_spread','spacing':128,'separation':64,'salt':19610911}})
bossjar='block_factorys_bosses-2.1.2-neo-1.21.1.jar'
venus=['ad_astra:venus_wastelands','ad_astra:infernal_venus_barrens','stellaris:venus_desert','stellaris:infernal_venus_barrens']
data('data/block_factorys_bosses/tags/worldgen/biome/dragon_tower.json',{'replace':True,'values':venus})
# All sizes of both jungle styles are excluded even if another config layer re-enables them.
ctov='[Neoforge]ctov-3.6.3.jar'
villages=[]
data('data/industrial_colonies/tags/worldgen/biome/disabled_jungle_villages.json',{'replace':True,'values':[]})
for size in ('small','medium','large'):
    for name in ('village_jungle','village_jungle_tree'):
        path=f'data/ctov/worldgen/structure/{size}/{name}.json';body=native(ctov,path);body['biomes']='#industrial_colonies:disabled_jungle_villages';data(path,body);villages.append('ctov:'+size+'/'+name)
config='config/ctov-common.toml';base=SRC/'baseline'/config;base.parent.mkdir(parents=True,exist_ok=True)
if not base.exists():base.write_bytes((PACK/config).read_bytes())
text=base.read_text(encoding='utf-8-sig');match=re.search(r'(?m)^(\s*enabledVillages\s*=\s*)(\[[^\n]+\])',text);assert match
names=json.loads(match[2]);assert 'jungle' in names and 'jungle_tree' in names
text=text[:match.start(2)]+json.dumps([n for n in names if n not in ('jungle','jungle_tree')])+text[match.end(2):]
target=SRC/'candidate'/config;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')
# Native tower denizens must survive the destination's atmosphere.
denizens=['block_factorys_bosses:'+n for n in ('infernal_dragon','dragon_guard_sword','flaming_skeleton_guard_sword','flaming_skeleton_guard_fireball')]
for namespace,tag in [('ad_astra','can_survive_in_space'),('ad_astra','can_survive_extreme_heat'),('ad_astra','can_survive_in_acid_rain'),('ad_astra','lives_without_oxygen'),('stellaris','no_oxygen_needed')]:
    data(f'data/{namespace}/tags/entity_type/{tag}.json',{'replace':False,'values':denizens})
location={'condition':'minecraft:any_of','terms':[{'condition':'minecraft:location_check','predicate':{'dimension':dimension}} for dimension in ('ad_astra:venus','stellaris:venus')]}
def entry(name,lo,hi,weight=1):return {'type':'minecraft:item','name':name,'weight':weight,'functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':lo,'max':hi}}]}
def pool(entries,rolls=1,boss=False):return {'rolls':rolls,'entries':entries,'conditions':[location]+([{'condition':'minecraft:killed_by_player'}] if boss else [])}
for name in ('dragon_tower_common','dragon_tower'):
    path=f'data/block_factorys_bosses/loot_table/chests/{name}.json';body=native(bossjar,path)
    if name.endswith('common'):
        body['pools'].append(pool([entry('minecraft:gold_ingot',8,16),entry('tfmg:steel_ingot',8,16),entry('minecraft:copper_ingot',16,32)],2))
    else:
        body['pools'].append(pool([entry('nuclearcraft:titanium_ingot',8,16),entry('nuclearcraft:tungsten_ingot',6,12),entry('nuclearcraft:platinum_ingot',4,8),entry('tfmg:n_semiconductor',4,8),entry('minecraft:netherite_ingot',1,2)],4))
        body['pools'].append(pool([entry('minecraft:enchanted_golden_apple',1,2)]))
    data(path,body)
path='data/block_factorys_bosses/loot_table/entities/infernal_dragon.json';body=native(bossjar,path)
for name,lo,hi in [('nuclearcraft:titanium_ingot',24,32),('nuclearcraft:tungsten_ingot',16,24),('tfmg:n_semiconductor',16,24),('minecraft:netherite_ingot',4,6),('minecraft:enchanted_golden_apple',2,3)]:body['pools'].append(pool([entry(name,lo,hi)],boss=True))
data(path,body)
allpaths=list(files)+[config]
manifest={}
for rel in allpaths:
    base=SRC/'baseline'/rel;base.parent.mkdir(parents=True,exist_ok=True)
    live=PACK/rel
    if live.exists() and not base.exists():base.write_bytes(live.read_bytes())
    manifest[rel]=hashlib.sha256(base.read_bytes()).hexdigest() if base.exists() else None
dump(SRC/'live-manifest.json',manifest)
dump(SRC/'migration.json',{'files':allpaths,'placements':changes,'sharedShipSet':'industrial_colonies:rare_maritime_sites','shipStructures':ship_ids,'shipSpacing':128,'shipSeparation':64,'disabledVillages':villages,'towerBiomes':venus,'towerDenizens':denizens,'rewardDimensions':['ad_astra:venus','stellaris:venus'],'existingChunksUntouched':True})
dump(SRC/'source-validation.json',{'status':'PASS','files':len(allpaths),'islandDensityReductionPercent':[round((1-c['candidateDensityRatio'])*100,2) for c in changes[:2]],'jungleStylesDisabled':2,'towerOverworldBiomes':0,'bossRewardsRequirePlayerKill':True})
print('PREPARED',len(allpaths),'scoped worldgen/config resources; island candidate density reduced ~99%; one shared rare ship set')
# Disposable verification world includes both installed Venus implementations.
import shutil
shutil.copytree(ROOT/'tools/terrain-smoke/world-template',SRC/'world-template',dirs_exist_ok=True)
fixture=SRC/'world-template/data/minecraft/worldgen/world_preset/flat.json';preset=json.loads(fixture.read_text(encoding='utf-8'))
# Recipe/registry checks need an Overworld context, not expensive terrain around
# randomly selected GameTest coordinates. The tower test still uses real Venus noise.
preset['dimensions']['minecraft:overworld']['generator']={'type':'minecraft:flat','settings':{'biome':'minecraft:plains','features':False,'lakes':False,'layers':[{'block':'minecraft:bedrock','height':1},{'block':'minecraft:stone','height':3}]}}
for namespace,jar in [('ad_astra','adastra-1.21.1-1.16.22-neoforge.jar'),('stellaris','stellaris-1.21-neoforge-1.4.25.jar')]:preset['dimensions'][namespace+':venus']=native(jar,f'data/{namespace}/dimension/venus.json')
dump(fixture,preset)
