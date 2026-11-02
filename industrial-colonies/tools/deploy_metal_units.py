"""Deploy the tested metal-unit scripts and matching client resource overrides."""
import argparse, hashlib, json, os, re, shutil, subprocess
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'progression/metal-units'
STAGE=ROOT/'isolated-runtime/metal-units-01'
PACK=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
def sha(data):return hashlib.sha256(data).hexdigest()
def readjson(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def require(value,message):
    if not value:raise RuntimeError(message)
def block(data):
    start=list(re.finditer(rb'(?m)^// kjsgen:start default\r?$',data));end=list(re.finditer(rb'(?m)^// kjsgen:end default\r?$',data))
    require(len(start)==len(end)==1 and start[0].start()<end[0].start(),'Ambiguous native export markers')
    return start[0].start(),end[0].end()
def running():
    script="@(Get-CimInstance Win32_Process -Filter \"Name = 'java.exe' OR Name = 'javaw.exe'\" -ErrorAction Stop | Where-Object { $_.CommandLine -like '*All in one*' }).Count"
    return int(subprocess.run(['powershell.exe','-NoProfile','-Command',script],capture_output=True,text=True,check=True).stdout.strip())
def safe_target(relative):
    target=PACK/relative
    require(target.resolve().is_relative_to(PACK.resolve()),'Target escapes named pack')
    for p in [target,*target.parents]:
        if p==PACK.parent:break
        require(not p.is_symlink() and not p.is_junction(),'Refusing linked installation path')
    return target
def main():
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--apply',action='store_true');parser.add_argument('--revision',default='r1');args=parser.parse_args()
    require(re.fullmatch(r'r[0-9]+',args.revision),'Invalid revision')
    log=(STAGE/f'launch-{args.revision}.log').read_text(encoding='utf-8',errors='replace')
    for marker in ('OWNERSHIP_ACCEPTANCE_PASS owned=41','SEMICONDUCTOR_ACCEPTANCE_PASS endpoints=4 retired=3 copperGates=PASS','METAL_UNIT_ACCEPTANCE_PASS','All 2 required tests passed','MATERIAL_PROCESSING_SMOKE PASS recipes=296','BUILD SUCCESSFUL'):
        require(marker in log,'Missing native acceptance: '+marker)
    report=readjson(STAGE/f'material-processing-report-{args.revision}.json')
    export=readjson(STAGE/f'material-processing-export-{args.revision}.json')
    require(report.get('status')=='PASS' and export.get('status')=='PASS','Native report not PASS')
    require(readjson(SRC/'source-validation.json')['status']=='PASS','Source validation missing')
    unit_check=readjson(SRC/'effective-unit-check.json')
    require(unit_check['status']=='PASS' and unit_check['dumpSha256']==sha((STAGE/'ownership-effective-recipes.json').read_bytes()),'Effective unit/consolidation check is missing or stale')
    project=(SRC/'baseline/kjsgen/projects/default.json').read_bytes()
    require(sha(project)==export['projectSha256'],'Tested project hash changed')
    require((PACK/'kjsgen/projects/default.json').read_bytes()==project,'Live project changed')
    require(sha((SRC/'effective.material-catalog.json').read_bytes())==report['catalogSha256'],'Tested catalog changed')
    jar=PACK/'mods/industrial_colonies-0.5.2.jar'
    require(sha(jar.read_bytes())==report['candidateSha256'],'Live IC JAR differs from tested 0.5.2')
    payloads={}
    for rel,name in {
      'kubejs/server_scripts/zz_industrial_material_processing.js':'candidate.material-processing.js',
      'kubejs/server_scripts/zzz_industrial_ownership.js':'candidate.ownership.js',
      'kubejs/server_scripts/zzzzz_industrial_metal_units.js':'unit_policy.js'}.items():
        before=SRC/'baseline'/rel;after=(SRC/name).read_bytes()
        require((STAGE/rel).read_bytes()==after,'Staged script changed: '+rel)
        payloads[rel]=(before.read_bytes() if before.exists() else None,after)
    for rel in readjson(SRC/'asset-files.json'):
        before=SRC/'baseline'/rel;after=(SRC/'candidate-assets'/rel).read_bytes()
        require((STAGE/rel).read_bytes()==after,'Staged asset changed: '+rel)
        payloads[rel]=(before.read_bytes() if before.exists() else None,after)
    for rel,expected in readjson(SRC/'live-manifest.json').items():
        require(sha((PACK/rel).read_bytes())==expected,'Concurrent live edit: '+rel)
    targets={key:safe_target(key) for key in payloads}
    def verify_before():
        for key,(before,after) in payloads.items():
            current=targets[key].read_bytes() if targets[key].exists() else None
            require(current==before,'Concurrent/unexpected live change: '+key)
    verify_before()
    live_running=running()
    plan=dict(status='READY',revision=args.revision,files={key:dict(before=sha(before) if before is not None else None,after=sha(after)) for key,(before,after) in payloads.items()},jarUnchanged=report['candidateSha256'],savesTouched=False,liveGameRunning=live_running>0,restartRequired=True)
    if not args.apply:print(json.dumps(plan,indent=2));return
    backup=PACK/'_industrial_colonies_backups'/('metal-units-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    require(backup.resolve().is_relative_to(PACK.resolve()),'Backup escapes named pack');backup.mkdir(parents=True,exist_ok=False)
    for key,(before,_) in payloads.items():
        if before is not None:
            p=backup/key;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(before);require(p.read_bytes()==before,'Backup mismatch')
    journal=backup/'deployment.json'
    plan.update(status='INSTALLING',backup=str(backup),written=[])
    journal.write_text(json.dumps(plan,indent=2),encoding='utf-8')
    # Install only atomic recipe/resource files. Never interrupt the user's game,
    # trigger a reload, replace a loaded JAR or write a save; restart applies them.
    verify_before()
    try:
        for key,(before,after) in payloads.items():
            target=targets[key];require((target.read_bytes() if target.exists() else None)==before,'Concurrent target edit: '+key)
            target.parent.mkdir(parents=True,exist_ok=True)
            temp=target.with_name(target.name+'.metal-units-tmp');require(not temp.exists(),'Unexpected temporary file')
            temp.write_bytes(after);os.replace(temp,target);plan['written'].append(key)
            require(target.read_bytes()==after,'Installed hash mismatch: '+key)
            journal.write_text(json.dumps(plan,indent=2),encoding='utf-8')
        plan['status']='APPLIED';plan['appliedAt']=datetime.now().astimezone().isoformat()
        journal.write_text(json.dumps(plan,indent=2),encoding='utf-8')
        (SRC/'deployment.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    except Exception:
        for key in reversed(plan['written']):
            before,after=payloads[key];target=targets[key]
            require(target.read_bytes()==after,'Concurrent change blocks rollback: '+key)
            if before is None:
                failed=backup/'failed-new'/key;failed.parent.mkdir(parents=True,exist_ok=True);target.rename(failed)
            else:target.write_bytes(before)
        plan['status']='ROLLED_BACK';journal.write_text(json.dumps(plan,indent=2),encoding='utf-8');raise
    print(json.dumps(plan,indent=2))
if __name__=='__main__':main()
