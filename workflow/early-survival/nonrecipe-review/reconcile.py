"""Pin bounded outcomes without completing any recipe-dependent master row."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent;W=H.parents[2]
m=json.loads((W/'industrial-colonies/MASTER_TASKS.json').read_text())
assert m['version']==382
storage=H.parent/'storage-charge-crafting/REVIEW-r3.json'
assert json.loads(storage.read_text())['status']=='PASS_BOUNDED_SNAPSHOT_API'
common=[str(H/'ALL_TASKS.json'),str(H/'FINDINGS.md')]
spec={
 'WORLD-15':([H.parent/'heightmap-diagnostic/REVIEW-r1.json',H.parent/'heightmap-diagnostic/REPORT.md'], 'Reuse the Quark/Zeta caller attribution and matching400chunk reserve; all-family clipping/other dynamic height-range warnings remain unproved. Deposit lifetime waits for final recipes and demand.'),
 'mm.ae-digital':([H/'ACQUISITION_REFERENCES.json',H/'STRUCTURE_EXCEPTIONS.json'], 'Static scan bounds missing addon data reference to the MegaCells radioactive-cell reactor-glass ingredient; nested archives/Java/runtime conditions remain outside scope. Await user recipe review; do not enable addon.'),
 'mm.legacy-factories':([H/'ACQUISITION_REFERENCES.json',H/'STRUCTURE_EXCEPTIONS.json'], 'Ten block-self-drop tables require existing blocks; scanned structures show no independent target source. Two CRC-unreadable structures, nested archives and dynamic code remain gaps. Final retirement activation and paid-operation behavior wait for settled recipe policy.'),
 'mm.power-storage':([storage,H.parent/'storage-charge-crafting/REPORT.md'], 'Reuse snapshot-only charged crafting evidence: three historical recipes accept charged native MechanicalCraftingInput and produce empty cubes. No charge-retention promise; current original-review registrations stay inactive. Final14-output recipe choices and full survival access await user review.')}
updates=[]
for key,(evidence,next_action) in spec.items():
    old=next(t for t in m['tasks'] if t['id']==key)
    update={'id':key,'from_status':old['status'],'status':old['status'],'evidence':common+[str(p) for p in evidence],'next_action':next_action}
    if key=='mm.power-storage':update['blocker']='Snapshot-only charged crafting and physical installer checks are bounded passes. Current generated recipes remain intentionally inactive; final14-output recipe choices and recursive survival access await user review.'
    updates.append(update)
out={'reason':'All237tasks reviewed for recipe-independent work; four bounded partial investigations completed without recipe edits or status inflation. Storage fixture failures preserved.','work_status':'ACTIVE','active_section':'progression','active_tasks':list(spec),'tasks':updates,'note':'2026-10-09: complete237row audit;280archive acquisition/dependency scan;400chunk heightmap caller diagnostic;three historical charged-cube native recipe API cases. No task newly complete, no production or recipe changes. Overall175/237(73.8%); progression31/79(39.2%).','next_actions':['User recipe review and six prepared playthrough checks remain prerequisites; preserve29explicit deferrals.','Reuse bounded diagnostic results; separate broad clipping/dynamic acquisition and future space expansion from accepted scopes.']}
(H/'MASTER_CHECKPOINT-v383.json').write_text(json.dumps(out,indent=2)+'\n')
