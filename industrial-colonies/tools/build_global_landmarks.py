"""One sparse Overworld landmark roll, then weighted biome-compatible selection."""
import copy,hashlib,json,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PACK=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
OUT=ROOT/'progression/global-landmarks';STAGE=ROOT/'isolated-runtime/advanced-semiconductors-01'
def parse(b):return json.loads(re.sub(r'(?m)^\s*//.*$','',b.decode('utf-8-sig')))
catalog={};sets={}
archives=list((PACK/'mods').glob('*.jar'))+[Path(r'C:\Users\GodPC\Documents\Codex\2026-08-16\ok\work\gradle-user-home/caches/neoformruntime/intermediate_results/extractServer_3708c41639d60b56739a2bf9df29858932d3099a_output.jar')]
for jar in archives:
    with zipfile.ZipFile(jar) as z:
        for path in z.namelist():
            if not(path.startswith('data/') and '/tags/' not in path and path.endswith('.json')):continue
            if '/worldgen/structure/' not in path and '/worldgen/structure_set/' not in path:continue
            try:body=parse(z.read(path))
            except (ValueError,UnicodeDecodeError):continue
            (sets if '/structure_set/' in path else catalog)[path]=body
# Preserve previously installed resource customizations before disabling old rolls.
for live in (PACK/'kubejs/data').rglob('*.json'):
    path=live.relative_to(PACK/'kubejs').as_posix()
    if '/worldgen/structure_set/' in path and '/tags/' not in path:sets[path]=parse(live.read_bytes())
normal='''minecraft:desert_pyramid minecraft:jungle_pyramid minecraft:igloo minecraft:swamp_hut minecraft:ocean_ruin_cold minecraft:ocean_ruin_warm minecraft:pillager_outpost minecraft:ruined_portal minecraft:ruined_portal_desert minecraft:ruined_portal_jungle minecraft:ruined_portal_mountain minecraft:ruined_portal_ocean minecraft:ruined_portal_swamp
apotheosis:tower_leaf apotheosis:tower_main apotheosis:tower_sand apotheosis:tower_spruce block_factorys_bosses:sandworm_nest block_factorys_bosses:yeti_hideout bosses_of_mass_destruction:lich_tower bosses_of_mass_destruction:void_blossom friendsandfoes:iceologer_cabin friendsandfoes:illusioner_shack friendsandfoes:illusioner_training_grounds irons_spellbooks:mangrove_hut irons_spellbooks:mountain_tower cataclysm:abandoned_spire cataclysm:abandoned_temple cataclysm:desert_site cataclysm:desert_temple cataclysm:amethyst_nest mowziesmobs:frostmaw_spawn mowziesmobs:umvuthana_grove mowziesmobs:wrought_chamber betterdungeons:small_dungeon'''.split()
large='''minecraft:mansion minecraft:monument minecraft:ancient_city dungeoncrawl:dungeon dungeonnowloading:temple_of_duality dungeonnowloading:labyrinth irons_spellbooks:catacombs irons_spellbooks:evoker_fort irons_spellbooks:ice_spider_den cataclysm:acropolis cataclysm:ancient_factory cataclysm:cursed_pyramid cataclysm:frosted_prison cataclysm:sunken_city mowziesmobs:monastery betterdungeons:skeleton_dungeon betterdungeons:spider_dungeon betterdungeons:zombie_dungeon'''.split()
normal.extend(['stellaris:earth_satellite','stellaris:earth_operation_base'])
ships='''minecraft:shipwreck minecraft:shipwreck_beached minecolonies:ship block_factorys_bosses:kraken_ship irons_spellbooks:impaled_icebreaker supplementaries:galleon'''.split()
islands=['modernfoundry:'+n for n in ('clay_island','earth_slime_island','ocean_skyslime_island','sky_slime_island')]
for path in catalog:
    if path.startswith('data/ctov/worldgen/structure/pillager_outpost_'):normal.append('ctov:'+path.split('/structure/')[1][:-5])
village=json.loads((ROOT/'progression/village-distribution/migration.json').read_text(encoding='utf-8'))
weights={e['structure']:e['weight'] for e in village['sharedPool']}
for names,weight in ((normal,150),(large,10),(ships,300)):
    for rid in names:assert rid not in weights;weights[rid]=weight
weights['minecraft:mansion']=20
weights.update({'ae2:meteorite':30,'supplementaries:road_sign':5})
meteor_path='data/industrial_colonies/worldgen/structure/stellaris_overworld_meteor.json'
meteor_source=PACK/'kubejs'/meteor_path
if not meteor_source.exists():meteor_source=ROOT/'progression/mountain-surface/candidate/kubejs'/meteor_path
if meteor_source.exists():
    catalog[meteor_path]=parse(meteor_source.read_bytes())
    weights['industrial_colonies:stellaris_overworld_meteor']=30
files={};disabled=[];mixed=[]
def data(path,body):files['kubejs/'+path]=(json.dumps(body,indent=2)+'\n').encode()
for rid in weights:
    ns,name=rid.split(':');path=f'data/{ns}/worldgen/structure/{name}.json';assert path in catalog,rid
    if rid in {e['structure'] for e in village['sharedPool']}:continue
    body=copy.deepcopy(catalog[path]);live=PACK/'kubejs'/path
    if live.exists():body=parse(live.read_bytes())
    body['biomes']={'type':'neoforge:and','values':[body['biomes'],'#minecraft:is_overworld']}
    data(path,body)
targets=set(weights)|set(islands)
for path,body in sets.items():
    if not any(e['structure'] in targets for e in body.get('structures',[])):continue
    value=copy.deepcopy(body);remaining=[e for e in body['structures'] if e['structure'] not in targets]
    if remaining:value['structures']=remaining;mixed.append(path)
    else:value['placement']['frequency']=0.0;disabled.append(path)
    data(path,value)
placement={'type':'minecraft:random_spread','salt':19610912,'spacing':384,'separation':256,'frequency':0.5}
data('data/industrial_colonies/worldgen/structure_set/global_landmarks.json',{'structures':[{'structure':k,'weight':v} for k,v in sorted(weights.items())],'placement':placement})
manifest={}
for rel,content in files.items():
    p=OUT/'candidate'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
    live=PACK/rel;baseline=OUT/'baseline'/rel
    if live.exists() and not baseline.exists():baseline.parent.mkdir(parents=True,exist_ok=True);baseline.write_bytes(live.read_bytes())
    manifest[rel]=hashlib.sha256(live.read_bytes()).hexdigest() if live.exists() else None
    dest=STAGE/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
spec={'status':'PREPARED','placement':placement,'weights':weights,'ordinary':normal,'massive':large,'ships':ships,'disabledIslands':islands,'disabledSets':disabled,'mixedSets':mixed,'files':list(files),'villageSitePolicy':'Global grid supersedes earlier separate vanilla village/mansion site grids; biome preferences retained','exceptions':'Mineshafts, strongholds, buried treasure/fossils and separately configured off-world structures retain their established placement'}
for p in (OUT/'migration.json',STAGE/'global-landmarks-migration.json'):p.write_text(json.dumps(spec,indent=2),encoding='utf-8')
(OUT/'live-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('PREPARED global pool',len(weights),'entries;',len(disabled),'disabled independent sets;',len(files),'resources')
