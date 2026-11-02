"""Merge the pink semiconductor generation into the captured live KJSGen project."""
import copy,json,shutil,uuid,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'progression/advanced-semiconductors';STAGE=ROOT/'isolated-runtime/advanced-semiconductors-01'
PACK=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one');NS='industrial_colonies:'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
SRC.mkdir(parents=True,exist_ok=True)
if not (SRC/'baseline').exists():
    for rel in ('kjsgen/projects','kubejs/server_scripts','kubejs/assets'):
        shutil.copytree(PACK/rel,SRC/'baseline'/rel)
    dump(SRC/'live-manifest.json',{str(p.relative_to(SRC/'baseline')).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SRC/'baseline').rglob('*') if p.is_file()})
old=read(SRC/'baseline/kjsgen/projects/default.json');new=copy.deepcopy(old);cards={c['recipeId']:c for c in new['recipes']};changed={}
def item(i,n=1):return dict(kind='ITEM',id=i,**({'count':n} if n!=1 else {}))
def fluid(i,n):return dict(kind='FLUID',id=i,amount=n)
def card(path,typ,slots,params,comment):
    rid=NS+'electronics/'+path
    c=cards.get(rid)
    if c is None:
        c={'uid':str(uuid.uuid5(uuid.NAMESPACE_URL,rid)),'recipeId':rid,'replaceRecipe':False};new['recipes'].append(c);cards[rid]=c
    c.update(type=typ,slots=slots,params=params,comment=comment);changed[rid]=c;return c
def seq(path,source,out,steps,tier='brass',count=1,loops=1,comment=''):
    slots={'input':item(source),'transitional':item(source),'output0':item(out,count)};params={'loops':str(loops),'__seqLen':str(len(steps))}
    for n,(kind,feed) in enumerate(steps):
        suffix={'cutting':'mechanical_saw','pressing':'press','deploying':'deployer','filling':'spout'}[kind]
        slots[f'__machine_step_{n}_{kind}']=item('create:spout' if kind=='filling' else 'createcasing:'+tier+'_'+suffix)
        params['seq'+str(n)]=kind
        if feed:slots[('seqFluid' if feed['kind']=='FLUID' else 'seqItem')+str(n)]=feed
    return card(path,'kjsgen:create_sequenced_assembly',slots,params,comment)
seq('precision_wafer_mask','minecraft:glass_pane',NS+'precision_wafer_mask',[
    ('deploying',item('create:iron_sheet')),('deploying',item('minecraft:black_dye')),('cutting',None),('pressing',None)],tier='copper',count=4,
    comment='[Advanced semiconductors] Copper tooling patterns four consumable glass-and-metal masks. No finished semiconductor is required.')
seq('copper_contact_frame','create:copper_sheet',NS+'copper_contact_frame',[('cutting',None),('pressing',None)],tier='copper',count=2,
    comment='[Advanced semiconductors] Cut and form two contact frames from a copper sheet. Frames serve packaged semiconductor pairs.')
seq('gold_bonding_wire','create:golden_sheet',NS+'gold_bonding_wire',[('cutting',None),('pressing',None)],count=4,
    comment='[Advanced semiconductors] Brass precision tooling forms four fine gold bonding wires from one gold sheet.')
seq('patterned_silicon_wafer',NS+'etched_silicon_wafer',NS+'patterned_silicon_wafer',[
    ('deploying',item('tfmg:plastic_sheet')),('deploying',item(NS+'precision_wafer_mask')),('pressing',None),
    ('filling',fluid('tfmg:sulfuric_acid',250)),('filling',fluid('minecraft:water',250))],loops=2,
    comment='[Advanced semiconductors] Two fine-pattern layers on the same wafer: resist film, consumable mask, Brass alignment, acid etch and rinse. Game-scale abstraction of denser fabrication; two masks, two films and 500 mB acid per wafer.')
card('annealed_silicon_wafer','industrial_colonies:tfmg_chemical_vat',
    {'ingredients0':item(NS+'patterned_silicon_wafer'),'ingredients1':fluid(NS+'phosphoric_acid',200),'ingredients2':fluid('tfmg:hydrogen',250),'results0':item(NS+'annealed_silicon_wafer')},
    {'vatMode':'firebrick','machineMode':'mixing','heat':'superheated','minSize':'3','processingTime':'1200'},
    '[Advanced semiconductors] High-temperature dopant activation in a size-3 firebrick-lined vat: 200 mB phosphoric acid and 250 mB hydrogen, 1200 ticks. Requires the finely patterned wafer.')
seq('n_semiconductor',NS+'annealed_silicon_wafer','tfmg:n_semiconductor',[
    ('filling',fluid('minecraft:water',250)),('cutting',None),('deploying',item(NS+'copper_contact_frame')),
    ('deploying',item(NS+'gold_bonding_wire')),('deploying',item('tfmg:plastic_sheet')),('pressing',None)],count=2,
    comment='[Advanced pink semiconductor] Brass dicing, copper contact frame, fine gold bonds and insulation package two high-density parts from one annealed wafer. Same wafer size, finer fabrication. N/P names are legacy IDs, not technology-generation physics.')
# Starter transistor production must precede Brass tooling. Keep its existing output/operations.
c=cards[NS+'electronics/transistor'];c['slots']['seqItem1']=item('tfmg:p_semiconductor')
c['comment']='[Starter electronics] Two green starter semiconductor parts, copper leads and gate control packaged into four transistors with Copper tools. This route bootstraps Brass precision machinery without requiring advanced pink parts.';changed[c['recipeId']]=c
assert cards[NS+'electronics/p_semiconductor']==next(c for c in old['recipes'] if c['recipeId']==NS+'electronics/p_semiconductor')
untouched=[c for c in old['recipes'] if c['recipeId'] not in changed]
assert all(c==cards[c['recipeId']] for c in untouched)
dump(SRC/'candidate.default.json',new)
semi=read(ROOT/'progression/semiconductors/migration.json');owned=semi['owned'].copy()
for path in ('precision_wafer_mask','patterned_silicon_wafer','annealed_silicon_wafer','copper_contact_frame','gold_bonding_wire'):
    owned[NS+path]=NS+'electronics/'+path
policy=(SRC/'baseline/kubejs/server_scripts/zzzz_industrial_semiconductors.js').read_text(encoding='utf-8')
policy=re.sub(r'  var owned = .*;',lambda _: '  var owned = '+json.dumps(owned)+';',policy)
(SRC/'semiconductor_policy.js').write_text(policy,encoding='utf-8')
spec={'changed':list(changed),'owned':owned,'retired':semi['retired'],'untouchedCards':len(untouched),'starterUnchanged':True,'advancedOutput':'tfmg:n_semiconductor','starterOutput':'tfmg:p_semiconductor'}
dump(SRC/'migration.json',spec);dump(SRC/'source-validation.json',dict(status='PASS',**spec))
# Reuse existing model assets; every new intermediate remains a registered, selectable item.
models={'precision_wafer_mask':'minecraft:item/iron_trapdoor','patterned_silicon_wafer':'tfmg:item/etched_circuit_board','annealed_silicon_wafer':'tfmg:item/n_semiconductor','copper_contact_frame':'create:item/copper_sheet','gold_bonding_wire':'minecraft:item/gold_nugget'}
labels={'precision_wafer_mask':'Precision Wafer Mask','patterned_silicon_wafer':'Finely Patterned Silicon Wafer','annealed_silicon_wafer':'Annealed High-Density Wafer','copper_contact_frame':'Copper Contact Frame','gold_bonding_wire':'Fine Gold Bonding Wire'}
langpath=ROOT/'src/main/resources/assets/industrial_colonies/lang/en_us.json';lang=read(langpath)
for name,parent in models.items():
    dump(ROOT/f'src/main/resources/assets/industrial_colonies/models/item/{name}.json',{'parent':parent});lang['item.industrial_colonies.'+name]=labels[name]
dump(langpath,lang)
asset='kubejs/assets/industrial_colonies/lang/en_us.json';live_lang=read(SRC/'baseline'/asset)
live_lang.update({'item.industrial_colonies.'+n:t for n,t in labels.items()});dump(SRC/'candidate-assets'/asset,live_lang)
asset2='kubejs/assets/tfmg/lang/en_us.json';base=SRC/'baseline'/asset2;tfmg=read(base) if base.exists() else {}
tfmg.update({'item.tfmg.n_semiconductor':'High-Density Semiconductor','item.tfmg.p_semiconductor':'Starter Semiconductor'});dump(SRC/'candidate-assets'/asset2,tfmg)
dump(SRC/'asset-files.json',[asset,asset2])
if not STAGE.exists():
    STAGE.mkdir();base=ROOT/'isolated-runtime/bucket-blocks-01'
    for folder in ('mods','config','defaultconfigs','kubejs','kjsgen','offline-maven'):shutil.copytree(base/folder,STAGE/folder)
    shutil.copy2(base/'offline-assets.properties',STAGE/'offline-assets.properties')
    (STAGE/'geology-smoke.init.gradle').write_text((base/'geology-smoke.init.gradle').read_text(encoding='utf-8').replace('bucket-blocks-01','advanced-semiconductors-01'),encoding='utf-8')
for folder in ('kubejs/server_scripts','kubejs/assets','kjsgen/projects'):shutil.copytree(SRC/'baseline'/folder,STAGE/folder,dirs_exist_ok=True)
shutil.copy2(SRC/'candidate.default.json',STAGE/'kjsgen/projects/default.json')
shutil.copy2(SRC/'semiconductor_policy.js',STAGE/'kubejs/server_scripts/zzzz_industrial_semiconductors.js')
shutil.copytree(SRC/'candidate-assets',STAGE,dirs_exist_ok=True)
for folder,name in [('ownership','ownership-migration.json'),('metal-units','metal-unit-migration.json'),('bucket-blocks','block-unit-migration.json'),('advanced-semiconductors','semiconductor-migration.json')]:shutil.copy2(ROOT/'progression'/folder/'migration.json',STAGE/name)
shutil.copy2(SRC/'migration.json',STAGE/'advanced-semiconductor-migration.json')
shutil.copy2(ROOT/'progression/bucket-blocks/closure-policy.json',STAGE/'closure-policy.json')
print('PREPARED',len(changed),'cards;',len(untouched),'preserved; starter unchanged')
