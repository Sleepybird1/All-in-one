"""Stage the current rejected designs; keep every other live card byte-equivalent."""
import copy
import hashlib
import json
from pathlib import Path
from collections import Counter
import recipe_design_v7_review_20260904 as revision
from generate_managed_recipe_overhaul import compile_manifest
from recipe_review_feedback import design_hash

ROOT=Path(__file__).resolve().parents[1]
LIVE=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one\kjsgen')
STAGE=ROOT/'progression/review-batches/20260904/v7-staged'

def load(path): return json.loads(path.read_text(encoding='utf-8'))
def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def main():
    STAGE.mkdir(parents=True,exist_ok=True)
    sources={name:LIVE/path for name,path in {
        'default.json':'projects/default.json',
        'default.recipe_reviews.json':'industrial_colonies_sync/default.recipe_reviews.json',
        'default.managed.baseline.json':'industrial_colonies_sync/default.managed.baseline.json',
        'rejected_recipes.json':'projects/rejected_recipes.json',
        'approved_recipes.json':'projects/approved_recipes.json',
        'Deferred.json':'projects/Deferred.json',
        'disabled_recipes.json':'projects/disabled_recipes.json',
        'maybe_recipes.json':'projects/maybe_recipes.json'}.items()}
    documents={name:load(path) for name,path in sources.items()}
    hashes={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in sources.values()}
    project=copy.deepcopy(documents['default.json'])
    ledger=copy.deepcopy(documents['default.recipe_reviews.json'])
    by_id={r['recipeId']:r for r in project['recipes']}
    current_rejected={rid for rid,r in ledger['reviews'].items() if r['status']=='rejected'
        and rid in by_id and r['cardSha256']==design_hash(by_id[rid])}
    seed=load(ROOT/'progression/managed_recipe_overhaul.seed.json')
    before={r['id']:copy.deepcopy(r) for r in seed['recipes']}
    revision.apply(seed)
    changed=[r for r in seed['recipes'] if r!=before.get(r['id']) and
             (r['id'] in current_rejected or r['id'] not in before and r['id'] not in by_id)]
    for spec in changed:
        if not spec.get('remove'): spec.pop('exclusive_output',None)
    manifest={'schema_version':1,'project':'default','recipes':changed,'machine_families':[],
              'additional_removals':[], 'phase_order':seed.get('phase_order',[])}
    save(STAGE/'revisions.manifest.json',manifest)
    compiled=compile_manifest(STAGE/'revisions.manifest.json',STAGE/'revisions.managed.json')
    updates={r['recipeId']:r for r in compiled['recipes']}
    # These rejections asked for identification or reported duplicates, rather
    # than a new BOM. Requeue with findings instead of inventing another recipe.
    explanations={
        'industrial_colonies:create_addons/experience_lantern':'Review clarification: this is an experience collection/storage utility. See Recipe Help for its role; the ingredients are unchanged for an informed second review.',
        'industrial_colonies:mekanism_components/electrolytic_core':'Review clarification: the Electrolytic Core is the internal component used to build the Electrolytic Separator. It is not a functional machine by itself. Ingredients retained for a second review with this explanation.',
        'industrial_colonies:mekanism_tools/armored_free_runners':'Review clarification: powered footwear provides step assistance and fall protection while charged, with armor protection in this version. It is mobility equipment, not production machinery. Ingredients retained for a second review.',
        'industrial_colonies:electronics/rotor':'Duplicate audit: one managed recipe card is present for tfmg:rotor, and the installed stock mechanical-crafting recipe is already removed. Ingredients retained; a duplicate visible in JEI still needs its displayed recipe IDs to identify a runtime or category issue.',
        'industrial_colonies:v3_ae2/accumulation_processor':'Duplicate audit: one managed accumulation-processor card is present. Both the MEGA Cells inscriber and ExtendedAE assembler stock routes are removed. Ingredients retained; any remaining JEI duplicate needs runtime identification rather than another replacement recipe.'}
    for rid,comment in explanations.items():
        if rid in current_rejected:
            updates[rid]=copy.deepcopy(by_id[rid])
            updates[rid]['comment']=comment
    for rid,card in updates.items():
        if rid in by_id: card['uid']=by_id[rid]['uid']
    project['recipes']=[updates.get(r['recipeId'],r) for r in project['recipes']]
    project['recipes'].extend(r for rid,r in updates.items() if rid not in by_id)
    removal_uids={r['uid'] for r in project.get('removals',[])}
    project.setdefault('removals',[]).extend(r for r in compiled['removals'] if r['uid'] not in removal_uids)
    for rid,card in updates.items():
        old=ledger['reviews'].get(rid,{})
        ledger['reviews'][rid]=dict(uid=card['uid'],status='pending',reason='revised_for_review',
            note=old.get('note',''),cardSha256=design_hash(card))
    rejected=copy.deepcopy(documents['rejected_recipes.json'])
    rejected['recipes']=[r for r in rejected['recipes'] if r['recipeId'] not in updates]
    baseline=copy.deepcopy(documents['default.managed.baseline.json'])
    baseline['recipes']=[updates.get(r['recipeId'],r) for r in baseline['recipes']]
    baseline_ids={r['recipeId'] for r in baseline['recipes']}
    baseline['recipes'].extend(r for rid,r in updates.items() if rid not in baseline_ids)
    for card in project['recipes']:
        rid=card['recipeId']
        if rid in by_id and rid not in updates: assert card==by_id[rid],rid
    save(STAGE/'default.json',project)
    save(STAGE/'default.recipe_reviews.json',ledger)
    save(STAGE/'rejected_recipes.json',rejected)
    save(STAGE/'default.managed.baseline.json',baseline)
    save(STAGE/'deployment-input-hashes.json',hashes)
    save(STAGE/'report.json',dict(revised=len(compiled['recipes']),clarificationOnly=sum(rid in current_rejected for rid in explanations),new=sum(rid not in by_id for rid in updates),
        pendingReviewIds=sorted(updates),unchangedActiveRejections=sorted(current_rejected-set(updates)),
        protectedCards=len(by_id)-len(set(updates)&by_id.keys()),remainingArchivedRejections=len(rejected['recipes'])))
    print(json.dumps(load(STAGE/'report.json'),indent=2))

if __name__=='__main__': main()
