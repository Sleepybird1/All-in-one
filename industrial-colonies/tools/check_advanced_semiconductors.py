"""Verify native recipe diff and final UI cards against the installed baseline."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'progression/advanced-semiconductors';STAGE=ROOT/'isolated-runtime/advanced-semiconductors-01'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
old=read(ROOT/'isolated-runtime/bucket-blocks-01/ownership-effective-recipes.json');new=read(STAGE/'ownership-effective-recipes.json');spec=read(SRC/'migration.json')
# Foundry serializes entity-type sets in nondeterministic order. Only that set is unordered.
for recipes in (old,new):
    for recipe in recipes.values():
        if recipe.get('type') in ('modernfoundry:entity_melting','modernfoundry:severing') and isinstance(recipe.get('entity'),dict) and isinstance(recipe['entity'].get('types'),list):recipe['entity']['types'].sort()
changed={k for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}
assert changed==set(spec['changed']),(changed-set(spec['changed']),set(spec['changed'])-changed)
ui=read(SRC/'candidate.default.json');cards={c['recipeId']:c for c in ui['recipes']}
assert len(cards)==len(ui['recipes'])
for rid in spec['changed']:
    c=cards[rid];r=new[rid]
    if c['type']=='kjsgen:create_sequenced_assembly':
        assert r.get('loops',1)==int(c['params']['loops']) and len(r['sequence'])==int(c['params']['__seqLen']),rid
        assert r['ingredient']['item']==c['slots']['input']['id'],rid
        assert r['results'][0]['id']==c['slots']['output0']['id'] and r['results'][0].get('count',1)==c['slots']['output0'].get('count',1),rid
        for i,step in enumerate(r['sequence']):
            feed=c['slots'].get('seqFluid'+str(i),c['slots'].get('seqItem'+str(i)))
            if feed:
                actual=step['ingredients'][1];key='fluid' if feed['kind']=='FLUID' else 'item'
                assert actual[key]==feed['id'],(rid,i,actual)
                if key=='fluid':assert actual['amount']==feed['amount'],(rid,i)
    else:
        assert r['allowed_vat_types']==['tfmg:firebrick_lined_vat'] and r['min_size']==3,rid
report={'status':'PASS','exactNativeRecipeChanges':sorted(changed),'unrelatedNativeRecipesPreserved':len(old)-2,'uiCards':len(cards),'dumpSha256':hashlib.sha256((STAGE/'ownership-effective-recipes.json').read_bytes()).hexdigest()}
(SRC/'effective-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
