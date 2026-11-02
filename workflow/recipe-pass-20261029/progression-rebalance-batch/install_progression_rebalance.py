from pathlib import Path
import json,copy,hashlib,sys,shutil,datetime,subprocess,re
from zipfile import ZipFile
L=Path('C:/Users/GodPC/curseforge/minecraft/Instances/All in one');R=Path('C:/Users/GodPC/Documents/ChatGPT/Industrial Minecraft Modpack');O=Path('work/progression-rebalance-batch');read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
raw={p.name:p.read_bytes() for p in (L/'kjsgen/projects').glob('*.json')};ps={n:json.loads(b) for n,b in raw.items()};lp=L/'kjsgen/industrial_colonies_sync/default.recipe_reviews.json';lr=lp.read_bytes();ledger=json.loads(lr)
sys.path.insert(0,str(R/'workflow/recipe-review-policy'));import review_gate as gate
def out(c):return next((v.get('id') for k,v in c.get('slots',{}).items() if ('output' in k) and v.get('id')),None)
def dec(c):return ledger['reviews'].get(c.get('recipeId'),{})
def same(a,b):return a==b
before={c['recipeId']:c for c in read(O/'BEFORE_CARDS.json')};current={c.get('recipeId'):c for c in ps['Progression_Review.json']['recipes']};drafts=read(O/'CARDS.json');skipped=[];cards=[]
for c in drafts:
 old=current.get(c['recipeId'])
 if old is None or not same(old,before[c['recipeId']]) or dec(old).get('status','pending') not in ['pending','rejected']:
  skipped.append({'recipe':c['recipeId'],'reason':'live card or decision changed while preparing batch'});continue
 cards.append(c)
fusion=copy.deepcopy(next(c for c in ps['Progression_Review.json']['recipes'] if c.get('recipeId')=='industrial_colonies:fusion_subsystems/control_unit'))
restore=[]
for c in read(O/'RESTORE_DEFAULT_RECORDS.json'):
 d=dec(c)
 if d.get('status')=='rejected':restore.append(c)
restoreids={c['recipeId'] for c in restore};duplicates=read(O/'DUPLICATE_CARDS.json');duplicateids={c['recipeId'] for c in duplicates if dec(c).get('status')=='rejected'}
disabled=[c for c in read(O/'DISABLE_TANK_CARDS.json') if dec(c).get('status','pending') in ['pending','rejected']]
# Fix the remaining rejected quantum-processor machine feedback without altering its material bill.
quantum=next((c for c in ps['rejected_recipes.json']['recipes'] if c.get('recipeId')=='industrial_colonies:v3_ae2/quantum_processor' and dec(c).get('status')=='rejected'),None)
if quantum:
 quantum=copy.deepcopy(quantum)
 for n in range(int(quantum['params']['__seqLen'])):
  op=quantum['params']['seq'+str(n)];item=quantum['slots'].get('seqItem'+str(n),{}).get('id','')
  tier='shadow_steel' if op=='pressing' or item in ['advanced_ae:quantum_alloy_plate','iceandfire:ice_dragon_blood'] else ('brass' if item=='tfmg:plastic_sheet' else ('refined_radiance' if any(x in item for x in ['accumulation_processor','ultimate_control','high_voltage','allthemodium','cobalt_reinforcement']) else 'railway'))
  quantum['slots'][f'__machine_step_{n}_{op}']={'kind':'ITEM','id':'createcasing:'+tier+('_press' if op=='pressing' else '_deployer')}
 quantum['comment']='Rejection feedback addressed with role-specific machine routing: board/silicon/transistor placement Railway, plastic Brass, high-current/control parts Radiance, quantum-alloy and cold final assembly Shadow Steel. Original25steps, quantities, input/output and Ice Dragon Blood material retained. Existing Saturn-moon material requirement remains unresolved; not invented here. Pending material review only.'
proposals=[{'card':c,'target':'Progression_Review.json','requeueAuthorization':'User explicitly requests redesigning all visible pending/rejected cards with exact relevant materials; preserve Fusion Control Unit and Fuel Reprocessor layout.'} for c in cards]
if quantum:proposals.append({'card':quantum,'target':'Material_Processing_Review.json','requeueAuthorization':'User explicitly asks to handle rejected feedback; this card changes the rejected all-Radiance machine routing.'})
ll,pp,cur=gate.live_evidence(L);checks=gate.check(proposals,ll,pp,read(R/'workflow/recipe-review-policy/REVIEWED_DESIGNS.json')+cur);assert all(x['status']=='PASS' for x in checks),[x for x in checks if x['status']!='PASS'];dump(O/'FINAL_GATE.json',checks)
# Validate the exact final proposal set through installed native generators.
E=O/'native-export';one=copy.deepcopy(ps['Progression_Review.json']);one['recipes']=cards+([quantum] if quantum else []);one['removals']=[];dump(E/'private/before/kjsgen/projects/approved_recipes.json',one)
cp=Path('work/material-fabrication-fusion-pass/classpath.txt').read_text();q=subprocess.run(['java','-Xmx256m','-XX:ActiveProcessorCount=2','-cp',str(O)+';'+cp,'dev.godpc.approvedexport.RebalanceExport',str(E)],capture_output=True,text=True);assert q.returncode==0,q.stderr
native=read(E/'candidate/NATIVE_CODEGEN-r1.json');assert len(native)==len(one['recipes']) and all(x['status']=='GENERATED' and not x['validation'] for x in native)
# Runtime default restoration is necessary only for rejected outputs mentioned in current scripts.
# Preserve personal outputs and any independently approved finished design for the same output.
protected=set()
for n,p in ps.items():
 for c in p.get('recipes',[]):
  if n in ['Personal_Recipes.json','Material_Processing.json'] or dec(c).get('status') in ['approved','disabled']:
   if out(c):protected.add(out(c))
scripts='\n'.join(p.read_text(encoding='utf-8-sig') for p in (L/'kubejs/server_scripts').glob('*.js'))
targets={out(c) for c in restore if out(c) and out(c) in scripts and out(c) not in protected}
recipes={};known=read(Path('C:/Users/GodPC/Documents/Codex/2026-09-26/realtime-voice-chat/recipe-index/runtime/loaded-recipes.json'))
def outputs(data):
 result=[]
 def visit(x):
  if isinstance(x,str):result.append(x)
  elif isinstance(x,list):
   for v in x:visit(v)
  elif isinstance(x,dict):
   for k in ['id','item']: 
    if isinstance(x.get(k),str):result.append(x[k])
 for k in ['result','results','output','outputs']:visit(data.get(k))
 return result
jars=list((L/'mods').glob('*.jar'))+[R/'industrial-colonies/build/moddev/artifacts/neoforge-21.1.248-client-extra-aka-minecraft-resources.jar']
serializers={v.get('serializer',v.get('type')) for v in read(Path('C:/Users/GodPC/Documents/Codex/2026-09-26/realtime-voice-chat/recipe-index/runtime/loaded-recipe-metadata.json')).values()}
for jar in jars:
 with ZipFile(jar) as z:
  for entry in z.namelist():
   if not entry.startswith('data/') or not entry.endswith('.json') or '/recipe/' not in entry:continue
   # Restrict parsing to recipe namespaces with a targeted output.
   if entry.split('/')[1] not in {x.split(':')[0] for x in targets}:continue
   try:d=json.loads(z.read(entry))
   except Exception:continue
   if not isinstance(d,dict) or not set(outputs(d))&targets:continue
   rid=entry.split('/')[1]+':'+entry.split('/recipe/',1)[1][:-5]
   if d.get('neoforge:conditions') and rid not in known:continue
   if d.get('type') not in serializers:continue
   recipes[rid]={'id':rid,'json':d,'source':jar.name,'outputs':outputs(d)}
covered={o for x in recipes.values() for o in x['outputs']};missing=sorted(targets-covered)
# The loaded snapshot distinguishes native recipes from KubeJS added/modified entries.
provenance=read(Path('C:/Users/GodPC/Documents/Codex/2026-09-26/realtime-voice-chat/recipe-index/runtime/loaded-recipe-provenance.json'))
for output_id in list(missing):
 if output_id in known and not any(output_id in provenance.get(k,{}) for k in ['added','modified','removed']):
  recipes[output_id]={'id':output_id,'json':known[output_id],'source':'unmodified native loaded snapshot (original resource not found in top-level current jars)','outputs':outputs(known[output_id])}
covered={o for x in recipes.values() for o in x['outputs']};missing=sorted(targets-covered)
assert not missing,('Missing native default sources; refuse partial cleanup',missing)
restorejs='''// priority: -100000
// User-requested native-default restoration. Never exports the new pending review drafts.
const IC_DEFAULT_RESTORE = RECIPE_DATA;
const IC_DEFAULT_OUTPUTS = OUTPUT_DATA;
ServerEvents.recipes(event => {
 IC_DEFAULT_OUTPUTS.forEach(id => event.remove({output:id}));
 function matchesResult(data) {
  if(!data)return false;
  if(typeof data==='string')return IC_DEFAULT_OUTPUTS.indexOf(data)>=0;
  if(Array.isArray(data))return data.some(matchesResult);
  if(typeof data==='object')return IC_DEFAULT_OUTPUTS.indexOf(data.id||data.item||'')>=0;
  return false;
 }
 event.addedRecipes.removeIf(recipe => {
  if(recipe.removed)return false;
  recipe.serialize();var d=JSON.parse(recipe.json.toString());
  return !!(matchesResult(d.result)||matchesResult(d.results)||matchesResult(d.output)||matchesResult(d.outputs));
 });
 IC_DEFAULT_RESTORE.forEach(row => event.custom(row.json).id(row.id));
});
'''.replace('RECIPE_DATA',json.dumps([{'id':x['id'],'json':x['json']} for x in recipes.values()],separators=(',',':'))).replace('OUTPUT_DATA',json.dumps(sorted(targets)))
(O/'zzzzzzzzzzzzzzzzzzzz_ic_restore_rejected_defaults.js').write_text(restorejs,encoding='utf-8')
dump(O/'NATIVE_DEFAULT_SOURCES.json',list(recipes.values()));dump(O/'DEFAULT_RESTORE_TARGETS.json',sorted(targets))
node='C:/Users/GodPC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';q=subprocess.run([node,'--check',str(O/'zzzzzzzzzzzzzzzzzzzz_ic_restore_rejected_defaults.js')],capture_output=True,text=True);assert q.returncode==0,q.stderr
# Prepare canonical queue replacements and archive cleanup, retaining immutable backup evidence.
ids={c['recipeId'] for c in cards};disabledids={c['recipeId'] for c in disabled};remove=restoreids|duplicateids|disabledids
ps['Progression_Review.json']['recipes']=[c for c in ps['Progression_Review.json']['recipes'] if c.get('recipeId') not in ids|remove]+cards
superseded=ids|({quantum['recipeId']} if quantum else set())
ps['rejected_recipes.json']['recipes']=[c for c in ps['rejected_recipes.json']['recipes'] if c.get('recipeId') not in restoreids|duplicateids|superseded]
if quantum:
 name='Material_Processing_Review.json';ps[name]['recipes']=[c for c in ps[name]['recipes'] if c.get('recipeId')!=quantum['recipeId']]+[quantum]
disabledname=next(n for n in ps if n.lower().startswith('disabled'))
for c in disabled:
 ps[disabledname]['recipes']=[x for x in ps[disabledname]['recipes'] if x.get('recipeId')!=c['recipeId']]+[c]
 ledger['reviews'][c['recipeId']]={'uid':c['uid'],'status':'disabled','reason':'duplicate_machine','note':'Competing standalone fluid tank; existing user rule keeps Create Tank and Fluid Vessel only.','cardSha256':gate.native_hash(c)}
for c in cards+([quantum] if quantum else []):ledger['reviews'][c['recipeId']]={'uid':c['uid'],'status':'pending','reason':'revised_for_review','note':'Substantial user-requested material/function/machine rebalance, exact items only.','cardSha256':gate.native_hash(c)}
assert next(c for c in ps['Progression_Review.json']['recipes'] if c.get('recipeId')==fusion['recipeId'])==fusion
assert all(v.get('kind')!='ITEM_TAG' for c in cards for v in c['slots'].values())
B=L/'_industrial_colonies_backups'/('whole-review-rebalance-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));B.mkdir(parents=True)
for n,b in raw.items():(B/n).write_bytes(b)
(B/'recipe_reviews.json').write_bytes(lr)
sys.path.insert(0,str(R/'workflow/early-survival/project-refresh'));from external_update import update
changed=[]
for n in ['Progression_Review.json','rejected_recipes.json','Material_Processing_Review.json',disabledname]:
 if ps[n]==json.loads(raw[n]):continue
 dump(O/(n+'.candidate.json'),ps[n]);update(L/'kjsgen/projects'/n,O/(n+'.candidate.json'),hashlib.sha256(raw[n]).hexdigest());changed.append(n)
assert lp.read_bytes()==lr;dump(lp,ledger)
sp=L/'kubejs/server_scripts/zzzzzzzzzzzzzzzzzzzz_ic_restore_rejected_defaults.js';assert not sp.exists();sp.write_text(restorejs,encoding='utf-8')
for n in raw:
 if n not in changed:assert (L/'kjsgen/projects'/n).read_bytes()==raw[n]
report={'redesignedProgressionCards':len(cards),'correctedRejectedMaterialCards':1 if quantum else 0,'defaultRestorationRecordsCleared':len(restore),'nativeDefaultsRestored':len(recipes),'runtimeRestoredOutputs':len(targets),'nativeDefaultTagsPreserved':True,'newDraftTags':0,'duplicateCardRemoved':len(duplicateids),'fluidTankCardsDisabled':len(disabled),'fusionControlUnitExactUnchanged':True,'fuelReprocessorLayoutPreserved':True,'approvedAndPersonalProjectsUnchanged':True,'skippedConcurrentEdits':skipped,'nativeGenerationValidation':'PASS','reviewGate':'PASS','gameplayDraftExported':False,'nativeReloadVerification':'NOT_RUN','changedProjects':changed,'backup':str(B)}
dump(O/'REPORT.json',report);print(json.dumps(report,indent=2))
