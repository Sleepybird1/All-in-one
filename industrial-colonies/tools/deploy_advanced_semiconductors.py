"""Install only the tested advanced recipe/UI project, policy, assets and mod."""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'progression/advanced-semiconductors';STAGE=ROOT/'isolated-runtime/advanced-semiconductors-01'
PACK=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
CLIENT=ROOT/'isolated-runtime/advanced-fluid-client-01'
STRUCTURES=ROOT/'progression/structure-cleanup'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
def require(ok,why):
    if not ok:raise RuntimeError(why)
def bounds(data):
    a=list(re.finditer(rb'(?m)^// kjsgen:start default\r?$',data));b=list(re.finditer(rb'(?m)^// kjsgen:end default\r?$',data))
    require(len(a)==len(b)==1 and a[0].start()<b[0].start(),'Ambiguous native export');return a[0].start(),b[0].end()
def running():
    # Launchers can hide the instance path in an argument file. Check JVM user.dir too.
    ps="@(Get-CimInstance Win32_Process -Filter \"Name = 'java.exe' OR Name = 'javaw.exe'\" -ErrorAction Stop | Select-Object ProcessId,CommandLine) | ConvertTo-Json -Compress"
    processes=json.loads(subprocess.run(['powershell.exe','-NoProfile','-Command',ps],capture_output=True,text=True,check=True).stdout or '[]')
    if isinstance(processes,dict):processes=[processes]
    count=0
    for process in processes:
        if 'All in one' in (process['CommandLine'] or ''):count+=1;continue
        jcmd=Path(r'C:\Users\GodPC\.gradle\jdks\eclipse_adoptium-21-amd64-windows.2\bin\jcmd.exe')
        result=subprocess.run([str(jcmd),str(process['ProcessId']),'VM.system_properties'],capture_output=True,text=True,timeout=20)
        if result.returncode!=0:
            # Exited processes are safe; unknown surviving JVMs require explicit resolution.
            alive=subprocess.run(['powershell.exe','-NoProfile','-Command',f"[bool](Get-Process -Id {int(process['ProcessId'])} -ErrorAction SilentlyContinue)"],capture_output=True,text=True,check=True).stdout.strip()
            require(alive=='False','Cannot determine active JVM working directory');continue
        directory=next((line for line in result.stdout.splitlines() if line.startswith('user.dir=')),'')
        if 'curseforge' in directory.lower() and 'All in one' in directory:count+=1
    return count
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--revision',default='r1');args=ap.parse_args()
    require(re.fullmatch(r'r[0-9]+',args.revision),'Invalid revision')
    log=(STAGE/f'launch-{args.revision}.log').read_text(encoding='utf-8',errors='replace')
    for marker in ('ADVANCED_SEMICONDUCTOR_PASS','STRUCTURE_CLEANUP_PASS','OWNERSHIP_ACCEPTANCE_PASS owned=41','BUCKET_BLOCK_ACCEPTANCE_PASS','All 2 required tests passed','MATERIAL_PROCESSING_SMOKE PASS recipes=296','BUILD SUCCESSFUL'):require(marker in log,'Missing native acceptance '+marker)
    require(read(STAGE/'structure-cleanup-report.json')['status']=='PASS' and read(STRUCTURES/'source-validation.json')['status']=='PASS','Structure acceptance missing')
    client=(CLIENT/'client.log').read_text(encoding='utf-8',errors='replace')
    require('FLUID_CLIENT_PASS' in client and 'FLUID_CLIENT_FAIL' not in client,'Client verification missing/failed')
    require((CLIENT/'fluid-slots.png').is_file(),'Client screenshot missing')
    require(read(SRC/'source-validation.json')['status']=='PASS','Source validation failed')
    effective=read(SRC/'effective-verification.json')
    require(effective['status']=='PASS' and effective['dumpSha256']==sha((STAGE/'ownership-effective-recipes.json').read_bytes()),'Effective recipe diff missing or stale')
    report=read(STAGE/f'material-processing-report-{args.revision}.json');export=read(STAGE/f'material-processing-export-{args.revision}.json')
    require(report['status']==export['status']=='PASS','Runtime/export not PASS')
    jar=(ROOT/'build/libs/industrial_colonies-0.5.3.jar').read_bytes()
    require(sha(jar)==report['candidateSha256'] and jar==(STAGE/'mods/industrial_colonies-0.5.3.jar').read_bytes(),'Untested JAR')
    require(jar==(CLIENT/'mods/industrial_colonies-0.5.3.jar').read_bytes(),'Client-tested JAR differs')
    project=(SRC/'candidate.default.json').read_bytes();require(sha(project)==export['projectSha256'],'Untested project')
    require(project==(STAGE/'kjsgen/projects/default.json').read_bytes(),'Stage project changed')
    require(sha((ROOT/'progression/bucket-blocks/effective.material-catalog.json').read_bytes())==report['catalogSha256'],'Catalog changed')
    baseline=SRC/'baseline';oldexport=(baseline/'kubejs/server_scripts/kjsgen_recipes.js').read_bytes();native=(STAGE/'kubejs/server_scripts/kjsgen_recipes.js').read_bytes()
    require(sha(native)==export['scripts'][0]['sha256'],'Export changed');a,b=bounds(oldexport);c,d=bounds(native)
    candidates={'kjsgen/projects/default.json':project,'kubejs/server_scripts/kjsgen_recipes.js':oldexport[:a]+native[c:d]+oldexport[b:],
      'kubejs/server_scripts/zzzz_industrial_semiconductors.js':(SRC/'semiconductor_policy.js').read_bytes()}
    require(candidates['kubejs/server_scripts/zzzz_industrial_semiconductors.js']==(STAGE/'kubejs/server_scripts/zzzz_industrial_semiconductors.js').read_bytes(),'Policy changed')
    for rel in read(SRC/'asset-files.json'):
        candidates[rel]=(SRC/'candidate-assets'/rel).read_bytes();require(candidates[rel]==(STAGE/rel).read_bytes() and candidates[rel]==(CLIENT/rel).read_bytes(),'Asset differs from client test')
    payload={rel:((baseline/rel).read_bytes() if (baseline/rel).exists() else None,data) for rel,data in candidates.items()}
    for rel in read(STRUCTURES/'migration.json')['files']:
        before=STRUCTURES/'baseline'/rel;after=(STRUCTURES/'candidate'/rel).read_bytes()
        require(after==(STAGE/rel).read_bytes(),'Untested structure/config resource '+rel)
        require(rel not in payload,'Duplicate installation target')
        payload[rel]=(before.read_bytes() if before.exists() else None,after)
    oldjar=(PACK/'mods/industrial_colonies-0.5.2.jar').read_bytes()
    require(sha(oldjar)=='d1a60ce6f8869b7c1197eae9d0d2879b8599a38bc34c064d878475e8594efa2e','Unexpected live JAR')
    payload['mods/industrial_colonies-0.5.2.jar']=(oldjar,None);payload['mods/industrial_colonies-0.5.3.jar']=(None,jar)
    for rel in payload:
        target=PACK/rel;require(target.resolve().is_relative_to(PACK.resolve()),'Target escapes pack')
        for p in [target,*target.parents]:
            if p==PACK.parent:break
            require(not p.is_symlink() and not p.is_junction(),'Linked target refused')
    manifest=read(SRC/'live-manifest.json')
    def verify():
        require(running()==0,'Close All in one Minecraft before installing the new mod JAR; no game was interrupted')
        for rel,digest in manifest.items():require(sha((PACK/rel).read_bytes())==digest,'Concurrent live edit '+rel)
        for rel,digest in read(STRUCTURES/'live-manifest.json').items():require((sha((PACK/rel).read_bytes()) if (PACK/rel).exists() else None)==digest,'Concurrent structure edit '+rel)
        for rel,(before,after) in payload.items():require(((PACK/rel).read_bytes() if (PACK/rel).exists() else None)==before,'Unexpected target '+rel)
    verify()
    plan={'status':'READY','revision':args.revision,'files':{rel:{'before':sha(b) if b is not None else None,'after':sha(a) if a is not None else None} for rel,(b,a) in payload.items()},'savesTouched':False,'restartRequired':True}
    if not args.apply:print(json.dumps(plan,indent=2));return
    backup=PACK/'_industrial_colonies_backups'/('advanced-semiconductors-'+datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,exist_ok=False)
    for rel,(before,_) in payload.items():
        if before is not None:
            dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(before);require(dest.read_bytes()==before,'Backup mismatch')
    plan.update(status='INSTALLING',backup=str(backup),written=[]);journal=backup/'deployment.json'
    def save():journal.write_text(json.dumps(plan,indent=2),encoding='utf-8')
    save();verify()
    try:
        for rel,(before,after) in payload.items():
            target=PACK/rel;require((target.read_bytes() if target.exists() else None)==before,'Concurrent target edit '+rel)
            if after is None:target.unlink() # Exact checked old JAR, already backed up.
            else:
                target.parent.mkdir(parents=True,exist_ok=True);temp=target.with_name(target.name+'.advanced-tmp');require(not temp.exists(),'Temporary file exists');temp.write_bytes(after);os.replace(temp,target)
            plan['written'].append(rel);save();require((target.read_bytes() if target.exists() else None)==after,'Installation mismatch '+rel)
        for rel,digest in manifest.items():
            if rel not in payload:require(sha((PACK/rel).read_bytes())==digest,'Preserved file changed '+rel)
        plan.update(status='APPLIED',appliedAt=datetime.now().astimezone().isoformat());save();(SRC/'deployment.json').write_text(json.dumps(plan,indent=2),encoding='utf-8');(STRUCTURES/'deployment.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    except Exception:
        for rel in reversed(plan['written']):
            before,after=payload[rel];target=PACK/rel;require((target.read_bytes() if target.exists() else None)==after,'Concurrent edit prevents rollback')
            if before is None:target.unlink()
            else:target.write_bytes(before)
        plan['status']='ROLLED_BACK';save();raise
    print(json.dumps(plan,indent=2))
if __name__=='__main__':main()
