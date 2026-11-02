"""Material-specific recovery rewards, layered on the TFMG iron correction."""
import copy,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'progression/ore-yields'
BASE=ROOT/'progression/iron-blast-fix';STAGE=ROOT/'isolated-runtime/advanced-semiconductors-01'
PACK=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
cat=read(BASE/'effective.material-catalog.json');before=copy.deepcopy(cat);ns='industrial_colonies:processing/'
amounts={'raw/iron':25,'raw/iron_block':225,'raw/copper':15,'raw/copper_block':135,
 'raw/zinc':12,'raw/zinc_block':108,'copper/direct':4,'copper/dust':25,
 'tin/direct':3,'tin/concentrate':20,'zinc/direct_sphalerite':2,'zinc/melt_recovered_dust':15,
 'lead/direct_galena':3,'lead/melt_crude':20,'lead/melt_high_purity':20,
 'nickel/melt_powder':25,'aluminum/melt_granules':25,'magnesium/melt_powder':20,
 'lithium/melt_powder':15,'silver/direct_argentite':2,'silver/melt_powder':10,'beryllium/melt_powder':10}
for key,amount in amounts.items():cat['recipes'][ns+key]['result']['amount']=amount
for key,count in {'titanium/consolidate_sponge':4,'tungsten/sinter':5,'chromium/consolidate':4,'boron/consolidate_powder':20,'pgm/consolidate_osmium':10}.items():
 cat['recipes'][ns+key]['input']['count']=count
for metal,amount in [('iron',100),('gold',25)]:
 recipe=copy.deepcopy(cat['recipes'][ns+'iron/blast_reduction'])
 recipe['ingredients']=[{'item':'minecraft:raw_'+metal}]
 recipe['results'][0]={'id':cat['metals'][metal]['fluid'],'amount':amount}
 cat['recipes'][ns+metal+'/blast_raw']=recipe
for metal,feed in [('copper','crushed_chalcopyrite'),('zinc','sphalerite_dust')]:
 cat['recipes'][ns+metal+'/crush_rich_raw']={'type':'create:crushing','ingredients':[{'item':('minecraft:raw_copper' if metal=='copper' else 'create:raw_zinc')}],
    'results':[{'id':'industrial_colonies:'+feed,'count':4}],'processing_time':250}
changed={k:v for k,v in cat['recipes'].items() if v!=before['recipes'].get(k)}
cat['notes'][ns+'iron/blast_reduction']={'family':'iron','comment':'Low-grade iron-bearing dust: native TFMG reduction yields 8 mB molten iron.'}
for rid in changed:cat['notes'][rid]={'family':rid.split('/')[1],'comment':'Material-specific ore recovery; see design/ORE_RECOVERY_BALANCE.md.'}
rel='kubejs/server_scripts/zz_industrial_material_processing.js'
script=(BASE/'candidate'/rel).read_text(encoding='utf-8')
def replace(m):
 rid=json.loads(m.group(2));return '  event.custom('+json.dumps(changed[rid],separators=(',',':'))+').id('+json.dumps(rid)+')' if rid in changed else m.group(0)
script=re.sub(r'  event.custom\((\{[^\n]+\})\)\.id\(("[^\n]+")\)',replace,script)
added={k:v for k,v in changed.items() if k not in before['recipes']}
anchor='  event.custom('+json.dumps(before['recipes'][ns+'iron/blast_reduction'],separators=(',',':'))+').id("'+ns+'iron/blast_reduction")'
assert script.count(anchor)==1
script=script.replace(anchor,anchor+'\n'+'\n'.join('  event.custom('+json.dumps(v,separators=(',',':'))+').id('+json.dumps(k)+')' for k,v in added.items()))
for p in (OUT/'candidate'/rel,STAGE/rel):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(script,encoding='utf-8')
baseline=OUT/'baseline'/rel;baseline.parent.mkdir(parents=True,exist_ok=True)
if not baseline.exists():baseline.write_bytes((PACK/rel).read_bytes())
spec={'status':'PREPARED','changed':list(changed),'added':list(added),'meltAmounts':amounts,'recipes':len(cat['recipes']),
 'richRawRecovery':{'iron':100,'copper':100,'zinc':60,'gold':25},
 'preserved':'Finished ingots=100 mB, blocks=1000 mB; reagent costs, machine gates, nonmetal products and trace rare-metal routes retained.'}
for p,v in ((OUT/'effective.material-catalog.json',cat),(OUT/'migration.json',spec),(STAGE/'ore-yields-migration.json',spec),(OUT/'live-manifest.json',{rel:hashlib.sha256((PACK/rel).read_bytes()).hexdigest()})):
 p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
assert len(cat['recipes'])==300
assert cat['policy']==before['policy'] and cat['metals']==before['metals']
print('PREPARED',len(changed),'ore recovery changes including',len(added),'new routes; 300 catalog recipes')
