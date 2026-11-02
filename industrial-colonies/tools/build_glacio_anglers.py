"""Author the user's Glacio aquatic habitat and Deepling Angler relocation."""
import gzip, hashlib, json, shutil, struct, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACK=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
OUT=ROOT/'progression/glacio-anglers'
STAGE=ROOT/'isolated-runtime/advanced-semiconductors-01'
files={}
def data(path,value):
    files['kubejs/data/'+path]=(json.dumps(value,indent=2)+'\n').encode()
biomes=['ad_astra:glacio_ice_peaks','ad_astra:glacio_snowy_barrens']
data('industrial_colonies/neoforge/biome_modifier/remove_earth_anglers.json',{
    'type':'neoforge:remove_spawns','biomes':'#cataclysm:deeplings_spawn','entity_types':['cataclysm:deepling_angler']})
data('industrial_colonies/neoforge/biome_modifier/glacio_anglers.json',{
    'type':'neoforge:add_spawns','biomes':biomes,
    'spawners':[{'type':'cataclysm:deepling_angler','weight':2,'minCount':1,'maxCount':1}]})
data('ad_astra/tags/entity_type/can_survive_extreme_cold.json',{
    'replace':False,'values':['cataclysm:deepling_angler','cataclysm:lionfish']})
with zipfile.ZipFile(PACK/'mods/adastra-1.21.1-1.16.22-neoforge.jar') as jar:
    path='ad_astra/worldgen/noise_settings/glacio.json'
    noise=json.loads(jar.read('data/'+path))
    original=json.loads(json.dumps(noise))
    # Subsurface groundwater: preserve terrain density, surface rules, ores and biomes.
    # Retain the native uniform fluid picker: randomized aquifer pressure left
    # the sampled caves dry. A water table fills connected lower caverns.
    noise.update(sea_level=0,aquifers_enabled=False,default_fluid={'Name':'minecraft:water'})
    assert {k for k in noise if noise[k]!=original[k]}=={'sea_level','default_fluid'}
    data(path,noise)
    dimension=jar.read('data/ad_astra/dimension/glacio.json')
native=next((PACK/'mods').glob("L_Ender*Cataclysm*.jar"))
templates={}
old=b'deepling_angler';new=b'deepling'
old_string=struct.pack('>H',len(old))+old;new_string=struct.pack('>H',len(new))+new
with zipfile.ZipFile(native) as jar:
    for path in jar.namelist():
        if not path.endswith('.nbt'):continue
        raw=jar.read(path)
        unpacked=gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw
        count=unpacked.count(old)
        if not count:continue
        # NBT strings have unsigned-short byte lengths. Replace only whole exact
        # string payloads, preserving all positions, blocks, loot and other entities.
        assert unpacked.count(old_string)==count
        changed=unpacked.replace(old_string,new_string)
        assert old not in changed
        files['kubejs/'+path]=gzip.compress(changed,mtime=0)
        templates[path]=count
assert len(templates)==10
manifest={}
for rel,content in files.items():
    candidate=OUT/'candidate'/rel;candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_bytes(content)
    live=PACK/rel;baseline=OUT/'baseline'/rel
    if live.exists() and not baseline.exists():baseline.parent.mkdir(parents=True,exist_ok=True);baseline.write_bytes(live.read_bytes())
    manifest[rel]=hashlib.sha256(live.read_bytes()).hexdigest() if live.exists() else None
    staged=STAGE/rel;staged.parent.mkdir(parents=True,exist_ok=True);staged.write_bytes(content)
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'live-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
spec={'status':'PREPARED','biomes':biomes,'templates':templates,'files':list(files),
      'habitat':'Glacio water-filled lower caverns below Y=0; native ice/snow surface and terrain density retained',
      'existingEntitiesAndSpawnersUnchanged':True}
for target in (OUT/'migration.json',STAGE/'glacio-anglers-migration.json'):
    target.write_text(json.dumps(spec,indent=2),encoding='utf-8')
fixture=OUT/'world-template'
shutil.copytree(ROOT/'progression/structure-cleanup/world-template',fixture,dirs_exist_ok=True)
target=fixture/'data/ad_astra/dimension/glacio.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(dimension)
preset=fixture/'data/minecraft/worldgen/world_preset/flat.json'
world=json.loads(preset.read_text(encoding='utf-8'))
world['dimensions']['ad_astra:glacio']=json.loads(dimension)
preset.write_text(json.dumps(world,indent=2),encoding='utf-8')
# Include the separately installed oil-well follow-up in this combined validation.
for path in (ROOT/'progression/oil-well-removal/candidate').rglob('*.json'):
    target=STAGE/path.relative_to(ROOT/'progression/oil-well-removal/candidate');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
print(json.dumps(spec,indent=2))
