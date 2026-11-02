import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/material_processing'))
from inventory import inventory
inv=inventory(Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods'))
project=json.loads((ROOT/'progression/ownership/candidate.default.json').read_text())
migration=json.loads((ROOT/'progression/ownership/migration.json').read_text())
models=set(inv['item_models']);missing=[]
for c in project['recipes']:
    if c['recipeId'] not in migration['changed']:continue
    for key,value in c.get('slots',{}).items():
        if value.get('kind')=='ITEM' and not value.get('id','').startswith('minecraft:') and value.get('id') not in models:missing.append((c['recipeId'],key,value.get('id')))
print('New/changed item references without installed item models:',missing)
print('Native grinding/washing/melting serializers:',sorted({r['data'].get('type','') for r in inv['recipes'].values() if any(x in r['data'].get('type','') for x in ('crush','grind','washing','melting','casting'))}))
for key,r in inv['recipes'].items():
    if r['data'].get('type') in ('mekanism:crushing','immersiveengineering:crusher'):
        d=r['data'];text=json.dumps(d)
        if any(s in text for s in ('coke','graphite','sawdust','sulfur','coal')):print(key,json.dumps(d,separators=(',',':')))
(ROOT/'progression/ownership/native-inventory.json').write_text(json.dumps(inv),encoding='utf-8')
assert not missing
