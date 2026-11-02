"""Verify installation and archive the full-bucket correction evidence."""
import hashlib,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
src=root/'progression/bucket-blocks'
stage=root/'isolated-runtime/bucket-blocks-01'
pack=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=read(src/'deployment.json')
assert receipt['status']=='APPLIED'
for rel,entry in receipt['files'].items():assert sha(pack/rel)==entry['after'],rel
manifest=read(src/'live-manifest.json')
preserved=[]
for rel,digest in manifest.items():
    rel=rel.replace('\\','/')
    if rel not in receipt['files']:
        assert sha(pack/rel)==digest,rel
        preserved.append(rel)
dump=read(stage/'ownership-effective-recipes.json')
basin=dump['modernfoundry:smeltery/seared/basin']
assert basin['pattern']==['# #','# #','###'] and 'modernfoundry:seared_brick' in json.dumps(basin)
verification={'status':'PASS','installedFiles':list(receipt['files']),'preservedFiles':preserved,'firstBasinRecipe':basin}
(src/'installation-verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
out=root.parent/'outputs/bucket-blocks-20260911'
out.mkdir(parents=True,exist_ok=True)
for name in ('deployment.json','installation-verification.json','effective-unit-check.json','source-validation.json','migration.json'):
    shutil.copy2(src/name,out/name)
for name in ('material-processing-report-r1.json','material-processing-export-r1.json','launch-r1.log'):
    shutil.copy2(stage/name,out/name)
shutil.copy2(root/'design/BUCKET_BLOCK_MIGRATION.md',out/'BUCKET_BLOCK_MIGRATION.md')
print('INSTALLATION_VERIFIED',len(receipt['files']),'changed;',len(preserved),'preserved; bootstrap basin PASS; evidence:',out)
