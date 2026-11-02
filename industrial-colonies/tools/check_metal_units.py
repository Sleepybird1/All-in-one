"""Check the final native recipe dump, including ten-nugget consolidation."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'progression/metal-units';STAGE=ROOT/'isolated-runtime/metal-units-01'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
d=read(STAGE/'ownership-effective-recipes.json');p=read(SRC/'closure-policy.json')
def ref(v):
    if isinstance(v,str):return v
    if isinstance(v,dict):return v.get('fluid',v.get('id',v.get('item',('#'+v['tag']) if 'tag' in v else '')))
    return ''
castings=[];breakdowns=[];consolidations=[];melting=[]
for k,v in d.items():
    if v.get('type') in ('modernfoundry:casting_table','modernfoundry:casting_basin'):
        out=ref(v.get('result'));value=p['finishedValues'].get(out)
        if value and (p['ingots'].get(out) or p['nuggets'].get(out)) and p['fluidMetals'].get(ref(v.get('fluid',{})))==value['metal']:
            count=v['result'].get('count',1) if isinstance(v['result'],dict) else 1
            target=value['amount']*count;actual=v['fluid']['amount'];assert actual==target,(k,actual,target)
            castings.append(k)
    if v.get('type')=='minecraft:crafting_shapeless':
        ins=v.get('ingredients',[]);out=v.get('result',{})
        if len(ins)==1 and p['ingots'].get(ref(ins[0])) and p['nuggets'].get(ref(out)):
            assert out.get('count',1)==10,(k,out);breakdowns.append(k)
    if v.get('type') in ('modernfoundry:melting','nuclearcraft:melter'):
        ins=v.get('ingredient',v.get('item_inputs',[]));outs=v.get('result',v.get('fluid_outputs',[]))
        ins=ins if isinstance(ins,list) else [ins];outs=outs if isinstance(outs,list) else [outs]
        if len(ins)==1 and ref(ins[0]) in p['finishedValues']:
            value=p['finishedValues'][ref(ins[0])];count=ins[0].get('count',1) if isinstance(ins[0],dict) else 1
            amount=sum(x.get('amount',1000) for x in outs if isinstance(x,dict) and p['fluidMetals'].get(ref(x))==value['metal'])
            if amount:
                assert amount<=value['amount']*count,(k,amount,value,count)
                melting.append(k)
expected=[e['id'] for e in read(STAGE/'kubejs/industrial_metal_unit_audit.json') if e['action']=='ten-nugget-consolidation']
for name,forms in read(SRC/'effective.material-catalog.json')['metals'].items():
    if forms['nugget']:expected.append('industrial_colonies:units/'+name+'/ten_nuggets')
for rid in expected:
    v=d[rid];assert v['type']=='create:mechanical_crafting',rid
    assert v['pattern']==['AAAAA','AAAAA'] and v['result'].get('count',1)==1,rid
    source=ref(v['key']['A']);out=ref(v['result'])
    assert p['finishedValues'][source]['amount']*10==p['finishedValues'][out]['amount'],rid
    assert p['finishedValues'][source]['metal']==p['finishedValues'][out]['metal'],rid
    consolidations.append(rid)
assert len(castings)>60 and len(breakdowns)>20 and len(consolidations)>20 and len(melting)>20
report={'status':'PASS','nativeMetalCastingsChecked':len(castings),'nativeIngotBreakdownsChecked':len(breakdowns),'nativeConsolidationsChecked':len(consolidations),'nativeMeltingChecks':len(melting),'dumpSha256':hashlib.sha256((STAGE/'ownership-effective-recipes.json').read_bytes()).hexdigest(),'castings':castings,'breakdowns':breakdowns,'consolidations':consolidations,'melting':melting}
(SRC/'effective-unit-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('EFFECTIVE_UNIT_CHECK_PASS', {k:v for k,v in report.items() if isinstance(v,int)})
