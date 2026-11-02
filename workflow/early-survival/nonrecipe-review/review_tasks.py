"""Explicitly classify every fixed-register row without changing task statuses."""
from pathlib import Path
import json,hashlib,collections
H=Path(__file__).resolve().parent;W=H.parents[2]
master=W/'industrial-colonies/MASTER_TASKS.json';decisions=H.parent/'remaining-task-review/DECISIONS.json'
m=json.loads(master.read_text());d=json.loads(decisions.read_text())
deferred={r['task_id'] for r in d['tasks'] if r['review_status']=='DEFERRED'}
partial={
 'WORLD-15':'Completed warning attribution, scoped WWOO ore guard,400chunk galena regression and1302chunk/three-additional-family terrain survey. Current scoped measurements are ready; final supply/lifetime acceptance requires approved recipes and demand.',
 'mm.ae-digital':'Completed top-level, nested, embedded-pack and targeted acquisition-class reference scans without enabling addon or replacing recipes; MegaCells reactor-glass dependency retained for recipe review.',
 'mm.power-storage':'Unchanged historical charged cube recipe snapshots pass native matching/assembly checks, with zero-FE outputs; current recipes remain intentionally inactive. Final recipes and survival access await user review.',
}
play={'mm.log-free-axe','mm.low-heater-seed','mm.starter-metal-acquisition','mm.zinc-first-supply','mm.first-foundry-acquisition','A04'}
design={'mm.fusion-policy','mm.nuclear-owner'}
release={'A05','A06','A07','A08'}
rows=[]
for t in m['tasks']:
    key=t['id'];reason=t.get('blocker') or t.get('next_action') or t['acceptance']
    if t['status']=='COMPLETE':category='ACCEPTED_REUSE';reason='Existing bounded acceptance; no independent open deliverable is inferred from historical limitations.'
    elif key in deferred:category='EXPLICITLY_DEFERRED';reason='Preserve the user decision; this review does not silently reactivate the task.'
    elif key in partial:category='PARTIAL_EVIDENCE_PREREQUISITES_REMAIN';reason=partial[key]
    elif key in play:category='USER_PLAYTHROUGH';reason='Prepared checklist/evidence awaits the user playthrough; supplied materials cannot prove first acquisition.'
    elif key in design:category='DESIGN_DECISION';reason=t['blocker']
    elif key in release:category='RELEASE_PREREQUISITES';reason=t['blocker'] or t['next_action']
    elif key=='ASSET-06':category='TOOL_POLICY_BLOCK';reason=t['blocker']
    else:category='RECIPE_OR_FINAL_LOAD_DEPENDENCY'
    missing=[p for p in t['evidence'] if not Path(p).is_file()]
    rows.append({'id':key,'title':t['title'],'masterStatus':t['status'],'category':category,'reason':reason,
                 'evidenceReferences':len(t['evidence']),'missingEvidenceReferences':missing,
                 'acceptance':t['acceptance'],'existingLimits':t['limits']})
assert len(rows)==len({r['id'] for r in rows})==237
counts=dict(collections.Counter(r['category'] for r in rows))
result={'masterVersion':m['version'],'masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest(),
        'decisionSHA256':hashlib.sha256(decisions.read_bytes()).hexdigest(),'counts':counts,'rows':rows,
        'scope':'Every register row classified; evidence paths checked for availability, not independently revalidated. Completed scopes and explicit deferrals preserved. No master status or denominator changed.'}
(H/'ALL_TASKS.json').write_text(json.dumps(result,indent=2)+'\n')
progression=next(s for s in m['stages'] if s['id']=='progression');space=next(s for s in m['stages'] if s['id']=='space')
lines=['# Every task reviewed for recipe-independent work','',f"Master v{m['version']}: **{m['summary']['complete']}/237 ({m['summary']['percent']:.1f}%)** overall; progression **{progression['complete']}/{progression['total']} ({progression['percent']:.1f}%)**; space **{space['complete']}/{space['total']} ({space['percent']:.1f}%)**.",'',
       'All 237 rows are listed below. A blocked task can still contain useful partial work; partial evidence is not task completion. The proposed future enemy-ship expansion is outside the fixed register.','',
       '| Classification | Tasks |','| --- | ---: |']+[f'| {k} | {v} |' for k,v in counts.items()]
lines+=['','## Completed recipe-independent partial investigations','']+[f"- **{key}**: {value}" for key,value in partial.items()]
lines+=['','## Full register','', '| Task | Status | Assessment |','| --- | --- | --- |']
for r in rows:
    reason=r['reason'].replace('|','/').replace('\n',' ')
    lines.append(f"| {r['id']} — {r['title']} | {r['masterStatus']} | {r['category']}: {reason} |")
lines+=['','Evidence availability details are in ALL_TASKS.json. Missing paths are not silently replaced or counted as fresh proof.','']
(H/'ALL_TASKS.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'counts':counts,'missingReferences':sum(len(r['missingEvidenceReferences']) for r in rows)}))
