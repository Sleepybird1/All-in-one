"""Verify installed artifacts and archive acceptance evidence."""
import json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'progression/advanced-semiconductors';STAGE=ROOT/'isolated-runtime/advanced-semiconductors-01';CLIENT=ROOT/'isolated-runtime/advanced-fluid-client-01'
PACK=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read(SRC/'deployment.json');assert r['status']=='APPLIED'
for rel,value in r['files'].items():
    if value['after'] is None:assert not (PACK/rel).exists(),rel
    else:assert sha(PACK/rel)==value['after'],rel
preserved=[]
for rel,digest in read(SRC/'live-manifest.json').items():
    if rel not in r['files']:assert sha(PACK/rel)==digest,rel;preserved.append(rel)
v={'status':'PASS','preservedFiles':preserved,'installedFiles':r['files']}
(SRC/'installation-verification.json').write_text(json.dumps(v,indent=2),encoding='utf-8')
out=ROOT.parent/'outputs/advanced-semiconductors-20260911';out.mkdir(parents=True,exist_ok=True)
for name in ('deployment.json','installation-verification.json','source-validation.json','effective-verification.json','migration.json'):shutil.copy2(SRC/name,out/name)
for name in (f"material-processing-report-{r['revision']}.json",f"material-processing-export-{r['revision']}.json",f"launch-{r['revision']}.log"):shutil.copy2(STAGE/name,out/name)
for name in ('client.log','fluid-slots.png'):shutil.copy2(CLIENT/name,out/name)
shutil.copy2(ROOT/'design/ADVANCED_SEMICONDUCTORS.md',out/'ADVANCED_SEMICONDUCTORS.md')
shutil.copy2(ROOT/'design/STRUCTURE_CLEANUP.md',out/'STRUCTURE_CLEANUP.md')
shutil.copy2(STAGE/'structure-cleanup-report.json',out/'structure-cleanup-report.json')
for name in ('source-validation.json','migration.json'):
    shutil.copy2(ROOT/'progression/structure-cleanup'/name,out/('structure-'+name))
print('INSTALLED_HASHES_PASS preserved=',len(preserved),' evidence=',out)
