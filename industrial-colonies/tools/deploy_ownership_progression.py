"""Deploy only the tested pre-semiconductor project and three recipe scripts."""
import argparse, hashlib, json, os, re, shutil, subprocess
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'progression/ownership'
STAGE=ROOT/'isolated-runtime/ownership-01'
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
    parser=argparse.ArgumentParser(__doc__);parser.add_argument('--apply',action='store_true');parser.add_argument('--revision',default='r6');args=parser.parse_args()
    require(re.fullmatch(r'r[0-9]+',args.revision),'Invalid revision')
    log=(STAGE/f'launch-{args.revision}.log').read_text(encoding='utf-8',errors='replace')
    for marker in ('OWNERSHIP_ACCEPTANCE_PASS owned='+str(len(readjson(SRC/'migration.json')['changed'])),'All 2 required tests passed','MATERIAL_PROCESSING_SMOKE PASS recipes=299','BUILD SUCCESSFUL'):
        require(marker in log,'Missing native acceptance: '+marker)
    report=readjson(STAGE/f'material-processing-report-{args.revision}.json')
    export=readjson(STAGE/f'material-processing-export-{args.revision}.json')
    require(report.get('status')=='PASS' and export.get('status')=='PASS','Native report not PASS')
    require(readjson(SRC/'source-validation.json')['status']=='PASS','Source validation missing')
    project=(SRC/'candidate.default.json').read_bytes()
    require(sha(project)==export['projectSha256'],'Tested project hash changed')
    require((STAGE/'kjsgen/projects/default.json').read_bytes()==project,'Stage project differs')
    require((STAGE/'kubejs/server_scripts/zzz_industrial_ownership.js').read_bytes()==(SRC/'ownership_policy.js').read_bytes(),'Ownership policy differs from tested stage')
    require((STAGE/'kubejs/server_scripts/zz_industrial_material_processing.js').read_bytes()==(SRC/'candidate.material-processing.js').read_bytes(),'Material policy differs from tested stage')
    jar=PACK/'mods/industrial_colonies-0.5.2.jar'
    require(sha(jar.read_bytes())==report['candidateSha256'],'Live IC JAR differs from tested 0.5.2')
    old_export=(SRC/'baseline.kjsgen_recipes.js').read_bytes();native=(STAGE/'kubejs/server_scripts/kjsgen_recipes.js').read_bytes()
    require(sha(native)==export['scripts'][0]['sha256'],'Native export changed after test')
    a,b=block(old_export);c,d=block(native);merged=old_export[:a]+native[c:d]+old_export[b:]
    payloads={
      'kjsgen/projects/default.json':((SRC/'baseline.default.json').read_bytes(),project),
      'kubejs/server_scripts/kjsgen_recipes.js':(old_export,merged),
      'kubejs/server_scripts/zz_industrial_material_processing.js':((SRC/'baseline.material-processing.js').read_bytes(),(SRC/'candidate.material-processing.js').read_bytes()),
      'kubejs/server_scripts/zzz_industrial_ownership.js':(None,(SRC/'ownership_policy.js').read_bytes())}
    targets={key:safe_target(key) for key in payloads}
    def verify_before():
        for key,(before,after) in payloads.items():
            current=targets[key].read_bytes() if targets[key].exists() else None
            require(current==before,'Concurrent/unexpected live change: '+key)
    verify_before()
    require(running()==0,'Close the live All in one Minecraft instance before installation')
    plan=dict(status='READY',revision=args.revision,files={key:dict(before=sha(before) if before is not None else None,after=sha(after)) for key,(before,after) in payloads.items()},jarUnchanged=report['candidateSha256'],savesTouched=False)
    if not args.apply:print(json.dumps(plan,indent=2));return
    backup=PACK/'_industrial_colonies_backups'/('ownership-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    require(backup.resolve().is_relative_to(PACK.resolve()),'Backup escapes named pack');backup.mkdir(parents=True,exist_ok=False)
    for key,(before,_) in payloads.items():
        if before is not None:
            p=backup/key;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(before);require(p.read_bytes()==before,'Backup mismatch')
    journal=backup/'deployment.json'
    plan.update(status='INSTALLING',backup=str(backup),written=[])
    journal.write_text(json.dumps(plan,indent=2),encoding='utf-8')
    verify_before();require(running()==0,'Live pack started during preparation')
    try:
        for key,(before,after) in payloads.items():
            target=targets[key];require((target.read_bytes() if target.exists() else None)==before,'Concurrent target edit: '+key)
            temp=target.with_name(target.name+'.ownership-tmp');require(not temp.exists(),'Unexpected temporary file')
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
            if before is None:target.rename(backup/'failed-new-ownership.js')
            else:target.write_bytes(before)
        plan['status']='ROLLED_BACK';journal.write_text(json.dumps(plan,indent=2),encoding='utf-8');raise
    print(json.dumps(plan,indent=2))
if __name__=='__main__':main()
