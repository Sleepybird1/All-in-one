import json, zipfile
from pathlib import Path
pack=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
wanted={'tfmg:'+s for s in ('steel_frame','steel_mechanism','steel_casing','screw','large_steel_cogwheel','fireproof_brick','steel_sheet','cast_iron_sheet','rebar')}
for jar in (pack/'mods').glob('*.jar'):
    if not jar.name.startswith(('tfmg-','createcasing-','Mekanism-')): continue
    with zipfile.ZipFile(jar) as z:
        for name in z.namelist():
            if '/recipe/' not in name or not name.endswith('.json'): continue
            try: d=json.loads(z.read(name))
            except ValueError: continue
            outputs=json.dumps({k:d[k] for k in ('result','results','output') if k in d})
            if any('"'+w+'"' in outputs for w in wanted): print(name,json.dumps(d,separators=(',',':')))
