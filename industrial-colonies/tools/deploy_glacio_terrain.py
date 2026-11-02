"""Scoped, tested Glacio resources and terrain-guard JAR installation."""
import argparse,hashlib,json,os,shutil,zipfile,subprocess
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACK=Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one')
SRC=ROOT/'progression/glacio-anglers'
STAGE=ROOT/'isolated-runtime/advanced-semiconductors-01'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest() if b is not None else None
def current(p):return p.read_bytes() if p.exists() else None
def require(ok,message):
    if not ok:raise RuntimeError(message)
def running():
    # Crash Assistant is a separate observer JVM, not the game's mod classloader.
    ps="@(Get-CimInstance Win32_Process -Filter \"Name = 'java.exe' OR Name = 'javaw.exe'\" -ErrorAction Stop | Select-Object ProcessId,CommandLine) | ConvertTo-Json -Compress"
    processes=json.loads(subprocess.run(['powershell.exe','-NoProfile','-Command',ps],capture_output=True,text=True,check=True).stdout or '[]')
    if isinstance(processes,dict):processes=[processes]
    count=0
    for process in processes:
        result=subprocess.run([r'C:\Users\GodPC\.gradle\jdks\eclipse_adoptium-21-amd64-windows.2\bin\jcmd.exe',str(process['ProcessId']),'VM.system_properties'],capture_output=True,text=True,timeout=20)
        if result.returncode!=0:
            alive=subprocess.run(['powershell.exe','-NoProfile','-Command',f"[bool](Get-Process -Id {int(process['ProcessId'])} -ErrorAction SilentlyContinue)"],capture_output=True,text=True,check=True).stdout.strip()
            require(alive=='False','Cannot determine active JVM working directory');continue
        props=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
        if props.get('sun.java.command','').split(' ')[0]=='dev.kostromdan.mods.crash_assistant.app.class_loading.Boot':continue
        directory=props.get('user.dir','')
        if 'All in one' in (process['CommandLine'] or '') or ('curseforge' in directory.lower() and 'All in one' in directory):count+=1
    return count

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--revision',required=True);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    require(args.revision.isalnum(),'Invalid revision')
    log=(STAGE/f'launch-{args.revision}.log').read_text(encoding='utf-8',errors='replace')
    for marker in ('ORE_RECOVERY_PASS','IRON_BLAST_PASS','GLOBAL_LANDMARKS_PASS','VILLAGE_DISTRIBUTION_PASS','GLACIO_ANGLERS_PASS','SURFACE_TERRAIN_PASS','STRUCTURE_CLEANUP_PASS','BUCKET_BLOCK_ACCEPTANCE_PASS','ADVANCED_SEMICONDUCTOR_PASS','OWNERSHIP_ACCEPTANCE_PASS owned=41','MATERIAL_PROCESSING_SMOKE PASS recipes=300','All 4 required tests passed','BUILD SUCCESSFUL'):
        require(marker in log,'Missing acceptance: '+marker)
    for name in ('ore-yields-report.json','global-landmarks-report.json','village-distribution-report.json','glacio-anglers-report.json','surface-terrain-report.json'):
        require(read(STAGE/name)['status']=='PASS','Failed runtime report')
    report=read(STAGE/f'material-processing-report-{args.revision}.json')
    jar=(ROOT/'build/libs/industrial_colonies-0.5.4.jar').read_bytes()
    require(sha(jar)==report['candidateSha256'] and jar==(STAGE/'mods/industrial_colonies-0.5.4.jar').read_bytes(),'Untested JAR')
    prior=read(ROOT/'progression/advanced-semiconductors/deployment.json')
    oldrel='mods/industrial_colonies-0.5.3.jar';old=current(PACK/oldrel)
    require(sha(old)==prior['files'][oldrel]['after'],'Unexpected existing JAR')
    with zipfile.ZipFile(PACK/oldrel) as a,zipfile.ZipFile(ROOT/'build/libs/industrial_colonies-0.5.4.jar') as b:
        changed=[n for n in set(a.namelist())|set(b.namelist()) if not n.endswith('/') and (n not in a.namelist() or n not in b.namelist() or a.read(n)!=b.read(n))]
        require(all(n in ('META-INF/neoforge.mods.toml','industrial_colonies.mixins.json','data/industrial_colonies/tags/worldgen/structure/terrain_fitting_exempt.json','dev/godpc/industrialcolonies/mixin/SurfaceStructureTerrainMixin.class') or n.startswith('dev/godpc/industrialcolonies/worldgen/SurfaceStructureTerrain') for n in changed),'Unrelated JAR code changed')
    payload={}
    for rel,digest in read(SRC/'live-manifest.json').items():
        before=current(PACK/rel);require(sha(before)==digest,'Concurrent live edit: '+rel)
        after=(SRC/'candidate'/rel).read_bytes();require(after==(STAGE/rel).read_bytes(),'Untested resource: '+rel)
        payload[rel]=(before,after)
    payload[oldrel]=(old,None);payload['mods/industrial_colonies-0.5.4.jar']=(None,jar)
    villages=ROOT/'progression/village-distribution'
    globalsrc=ROOT/'progression/global-landmarks';ironsrc=ROOT/'progression/ore-yields'
    require(report['catalogSha256']==sha((ironsrc/'effective.material-catalog.json').read_bytes()),'Untested iron catalog')
    for source in (villages,globalsrc,ironsrc):
        for rel,digest in read(source/'live-manifest.json').items():
            require(rel not in payload,'Duplicate target: '+rel)
            before=current(PACK/rel);require(sha(before)==digest,'Concurrent live edit: '+rel)
            after=(source/'candidate'/rel).read_bytes();require(after==(STAGE/rel).read_bytes(),'Untested resource: '+rel)
            payload[rel]=(before,after)
    preserved={}
    for receipt in (prior,read(ROOT/'progression/oil-well-removal/deployment.json')):
        for rel,value in receipt['files'].items():
            if rel not in payload:preserved[rel]=value['after']
    # Preserve all recipe/UI files except the explicitly balanced material script.
    for sub in ('kjsgen/projects','kubejs/server_scripts','kubejs/assets'):
        for file in (PACK/sub).rglob('*'):
            if file.is_file() and file.relative_to(PACK).as_posix() not in payload:preserved[file.relative_to(PACK).as_posix()]=sha(file.read_bytes())
    def verify():
        for rel,(before,_) in payload.items():
            target=PACK/rel
            require(target.resolve().is_relative_to(PACK.resolve()),'Target escapes instance')
            require(not any(p.is_symlink() or p.is_junction() for p in [target,*target.parents]),'Linked target')
            require(current(target)==before,'Concurrent target change: '+rel)
        for rel,digest in preserved.items():require(sha(current(PACK/rel))==digest,'Preserved file changed: '+rel)
    verify()
    plan={'status':'READY','revision':args.revision,'savesTouched':False,'files':{r:{'before':sha(b),'after':sha(a)} for r,(b,a) in payload.items()},'preservedFiles':preserved,'jarChanges':sorted(changed)}
    (SRC/'installation-plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    if not args.apply:print('READY: '+str(len(payload))+' targets; '+str(len(preserved))+' files preserved');return
    require(running()==0,'Close All in one Minecraft before installing the new terrain-guard JAR; the game was not interrupted')
    backup=PACK/'_industrial_colonies_backups'/('glacio-terrain-'+datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,exist_ok=False)
    for rel,(before,_) in payload.items():
        if before is not None:
            p=backup/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(before);require(p.read_bytes()==before,'Backup mismatch')
    plan.update(status='INSTALLING',backup=str(backup),written=[])
    journal=backup/'deployment.json'
    def save():journal.write_text(json.dumps(plan,indent=2),encoding='utf-8')
    save();verify();require(running()==0,'Minecraft reopened; installation deferred')
    try:
        for rel,(before,after) in payload.items():
            target=PACK/rel;require(current(target)==before,'Concurrent target change')
            if after is None:target.unlink()
            else:
                target.parent.mkdir(parents=True,exist_ok=True);temporary=target.with_name(target.name+'.glacio-tmp');require(not temporary.exists(),'Temporary target exists');temporary.write_bytes(after);os.replace(temporary,target)
            plan['written'].append(rel);save();require(current(target)==after,'Installed bytes differ')
        for rel,digest in preserved.items():require(sha(current(PACK/rel))==digest,'Preserved file changed')
        plan.update(status='APPLIED',appliedAt=datetime.now().astimezone().isoformat());save()
        (SRC/'deployment.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
        for source in (villages,globalsrc,ironsrc):
            (source/'deployment.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    except Exception:
        for rel in reversed(plan['written']):
            before,after=payload[rel];target=PACK/rel;require(current(target)==after,'Concurrent change prevents rollback')
            if before is None:target.unlink()
            else:target.write_bytes(before)
        plan['status']='ROLLED_BACK';save();raise
    evidence=ROOT.parent/'outputs/glacio-terrain-20260911';evidence.mkdir(parents=True,exist_ok=True)
    for name in ('deployment.json','migration.json','installation-plan.json'):shutil.copy2(SRC/name,evidence/name)
    for name in ('ore-yields-report.json','global-landmarks-report.json','village-distribution-report.json','glacio-anglers-report.json','surface-terrain-report.json',f'launch-{args.revision}.log',f'material-processing-report-{args.revision}.json'):shutil.copy2(STAGE/name,evidence/name)
    for source in (globalsrc,ironsrc):shutil.copy2(source/'migration.json',evidence/(source.name+'-migration.json'))
    shutil.copy2(villages/'migration.json',evidence/'village-migration.json')
    shutil.copy2(ROOT/'design/VILLAGE_DISTRIBUTION.md',evidence/'VILLAGE_DISTRIBUTION.md')
    shutil.copy2(ROOT/'design/GLACIO_ANGLERS_AND_TERRAIN.md',evidence/'GLACIO_ANGLERS_AND_TERRAIN.md')
    for name in ('GLOBAL_LANDMARK_DISTRIBUTION.md','ORE_RECOVERY_BALANCE.md'):shutil.copy2(ROOT/'design'/name,evidence/name)
    print('APPLIED and verified: '+str(len(payload))+' targets; '+str(len(preserved))+' files preserved; backup='+str(backup))
if __name__=='__main__':main()
