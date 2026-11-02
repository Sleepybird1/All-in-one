import json
from pathlib import Path
from graphlib import TopologicalSorter
root=Path(__file__).resolve().parents[1]/'progression/ownership'
old=json.loads((root/'baseline.default.json').read_text(encoding='utf-8-sig'))
new=json.loads((root/'candidate.default.json').read_text(encoding='utf-8'))
change=json.loads((root/'migration.json').read_text(encoding='utf-8'))
before={c['recipeId']:c for c in old['recipes']};after={c['recipeId']:c for c in new['recipes']}
assert len(after)==len(new['recipes'])
assert len({c['uid'] for c in new['recipes']})==len(new['recipes'])
assert old['removals']==new['removals']
assert {k:v for k,v in old.items() if k!='recipes'}=={k:v for k,v in new.items() if k!='recipes'}
for rid,c in before.items():
    if rid not in change['changed'] and rid not in change['removed']:assert after[rid]==c,rid
    if rid in after:assert c['uid']==after[rid]['uid'],rid
legacy_bounds=[]
for rid,c in after.items():
    if c['type']=='kjsgen:create_mechanical_crafting':
        w,h=int(c['params']['gridW']),int(c['params']['gridH']);assert 1<=w<=7 and 1<=h<=7
        for key in c['slots']:
            if key.startswith('cell_'):
                y,x=map(int,key[5:].split('_'))
                if not (x<w and y<h):
                    assert rid not in change['changed'],(rid,key,w,h)
                    legacy_bounds.append(dict(id=rid,slot=key,width=w,height=h))
    if rid in change['changed'] and c['type']=='kjsgen:create_pressing':assert 'input' in c['slots']
    if '/electronics/' in rid:assert c==before[rid],'Semiconductor/electronics scope leaked: '+rid
owners={output:ids[0] for output,ids in change['ownedOutputs'].items()}
graph={rid:set() for rid in change['changed']}
for rid in graph:
    for key,slot in after[rid]['slots'].items():
        if key.startswith(('output','transitional')):continue
        if slot.get('id') in owners:graph[rid].add(owners[slot['id']])
order=list(TopologicalSorter(graph).static_order())
for rid in change['changed']:
    if '/manufacturing/weathered_iron/' in rid or '/manufacturing/copper' in rid:
        assert after[rid]['type']=='kjsgen:create_mechanical_crafting'
        refs={v.get('id') for v in after[rid]['slots'].values()}
        assert not refs & {'tfmg:circuit_board','tfmg:transistor_item','tfmg:n_semiconductor','tfmg:p_semiconductor','tfmg:electric_motor','minecraft:diamond','allthemodium:allthemodium_ingot'}
report=dict(status='PASS',changedCards=len(change['changed']),unrelatedPreserved=sum(r not in change['changed'] and r not in change['removed'] for r in before),scope='Changed component/machine dependency graph; external native material sources checked separately',topologicalOrder=order,unchangedLegacyOutOfBounds=legacy_bounds)
(root/'source-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('OWNERSHIP_SOURCE_PASS',report['changedCards'],'cards;',report['unrelatedPreserved'],'unrelated cards preserved; changed dependency graph acyclic; electronics unchanged')

