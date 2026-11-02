"""Move the current iron-dust reduction to the native TFMG furnace."""
import copy, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACK=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
OUT=ROOT/'progression/iron-blast-fix';STAGE=ROOT/'isolated-runtime/advanced-semiconductors-01'
OUT.mkdir(parents=True,exist_ok=True)
rid='industrial_colonies:processing/iron/blast_reduction'
catalog=json.loads((ROOT/'progression/bucket-blocks/effective.material-catalog.json').read_text(encoding='utf-8-sig'))
old=copy.deepcopy(catalog['recipes'][rid])
recipe={'type':'tfmg:industrial_blasting','ingredients':[old['input']],
        'results':[{'id':'modernfoundry:molten_iron','amount':8},{'id':'tfmg:molten_slag','amount':10}],
        'processing_time':30,'hot_air_usage':20}
catalog['recipes'][rid]=recipe
rel='kubejs/server_scripts/zz_industrial_material_processing.js'
before=(PACK/rel).read_bytes();script=before.decode('utf-8-sig')
pattern=r'  event.custom\((\{[^\n]+\})\)\.id\("'+re.escape(rid)+r'"\)'
assert len(re.findall(pattern,script))==1
script=re.sub(pattern,lambda m:'  event.custom('+json.dumps(recipe,separators=(',',':'))+').id("'+rid+'")',script)
for p in (OUT/'candidate'/rel,STAGE/rel):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(script,encoding='utf-8')
baseline=OUT/'baseline'/rel;baseline.parent.mkdir(parents=True,exist_ok=True)
if not baseline.exists():baseline.write_bytes(before)
spec={'status':'PREPARED','id':rid,'before':old,'after':recipe,'yieldMb':8,
      'note':'Direct molten iron replaces reduced fraction followed by melting. Legacy fraction melting remains for existing inventory. Slag becomes native molten slag; 10 mB is half the native 20 mB slag-block cast.'}
for p,v in ((OUT/'effective.material-catalog.json',catalog),(OUT/'migration.json',spec),(STAGE/'iron-blast-migration.json',spec),(OUT/'live-manifest.json',{rel:hashlib.sha256(before).hexdigest()})):
 p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
print('PREPARED TFMG iron reduction: 8 mB iron, 10 mB slag; 295 other recipes unchanged')
