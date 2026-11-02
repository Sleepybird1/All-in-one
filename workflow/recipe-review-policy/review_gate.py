"""Read-only authoring gate for PROPOSALS rows, not complete stored projects.

Comments, labels, UIDs and recipe-ID renaming cannot turn a reviewed design into
a new recipe. This script never changes the game ledger or review status.
"""
from pathlib import Path
import argparse,hashlib,json,re,sys
HERE=Path(__file__).resolve().parent
PACK=Path('C:/Users/GodPC/curseforge/minecraft/Instances/All in one')
JUDGED={'approved','rejected','maybe','deferred','disabled'}
ACTIVE={'Progression_Review.json','Material_Processing_Review.json','Exotic_Material_Review.json'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def digest(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')).hexdigest()
def normalize(value):
 if isinstance(value,list):return [normalize(x)for x in value]
 if not isinstance(value,dict):return value
 return {k:normalize(v)for k,v in value.items()if not(k=='count'and v==1)and not(k=='amount'and v==1000)}
def signature(card):
 # Keep real shape, tool, quantities, order and output. Ignore identity/cosmetics.
 return digest(normalize({k:card.get(k,{})for k in ('type','slots','params')}))
def native_hash(card):return 'sha256:'+digest({k:card.get(k,{})for k in ('type','recipeId','slots','params')})
def live_evidence(pack):
 ledger=read(pack/'kjsgen/industrial_colonies_sync/default.recipe_reviews.json')['reviews']
 projects={p.name:read(p)for p in (pack/'kjsgen/projects').glob('*.json')}
 by_id={}
 for n,p in projects.items():
  for c in p.get('recipes',[]):
   if c.get('recipeId'):by_id.setdefault(c['recipeId'],[]).append((n,c))
 records=[]
 for rid,d in ledger.items():
  if d['status']not in JUDGED:continue
  for n,c in by_id.get(rid,[]):
   if native_hash(c)==d['cardSha256']:
    records.append({'recipeId':rid,'designSha256':d['cardSha256'],'semanticSha256':signature(c),'status':d['status']})
 return ledger,projects,records
def check(proposals,ledger,projects,history,exotic_authorization=None):
 assert isinstance(proposals,list),'Pass only proposed review rows, never an entire stored project'
 known={r['semanticSha256']:r for r in history};seen=set();results=[]
 for row in proposals:
  c=row['card'];rid=c['recipeId'];target=row['target'];key=signature(c);reasons=[];decision=ledger.get(rid,{})
  if key in seen:reasons.append('duplicate design inside this proposal batch')
  seen.add(key)
  if key in known:reasons.append('same already-reviewed design; comments/UID/ID do not justify another review')
  if target=='Exotic_Material_Review.json'and not exotic_authorization:reasons.append('use the single Material Processing Review queue unless explicitly recreated by the user')
  auth=row.get('requeueAuthorization','').strip()
  if decision.get('status')=='approved'and not auth:reasons.append('already approved; preserve it unless the user explicitly requests this change')
  if decision.get('status')in {'maybe','deferred','disabled'}and not auth:reasons.append('keep the decision parked; a default Maybe note is not a request to reset it')
  for n,p in projects.items():
   if n in ACTIVE and n!=target and any(x['recipeId']==rid for x in p.get('recipes',[])):
    reasons.append('same recipe ID in another active queue; move its canonical row instead of copying')
  results.append({'recipeId':rid,'target':target,'semanticSha256':key,'status':'BLOCKED'if reasons else'PASS','reasons':reasons})
 return results
def main():
 ap=argparse.ArgumentParser();ap.add_argument('proposals');ap.add_argument('--pack',type=Path,default=PACK);ap.add_argument('--report',type=Path);args=ap.parse_args()
 ledger,projects,current=live_evidence(args.pack)
 history=read(HERE/'REVIEWED_DESIGNS.json')if(HERE/'REVIEWED_DESIGNS.json').exists()else[]
 policy=read(HERE/'QUEUE_POLICY.json')if(HERE/'QUEUE_POLICY.json').exists()else{}
 exotic=policy.get('exoticMaterialReview',{})
 authorization=exotic.get('authorization')if exotic.get('enabled')else None
 rows=check(read(args.proposals),ledger,projects,history+current,authorization)
 out={'status':'BLOCKED'if any(x['status']=='BLOCKED'for x in rows)else'PASS','proposals':len(rows),'blocked':sum(x['status']=='BLOCKED'for x in rows),'results':rows,'ledgerWrites':0,'recipeWrites':0}
 if args.report:args.report.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in out.items()if k!='results'}))
 return 1 if out['status']=='BLOCKED'else 0
if __name__=='__main__':sys.exit(main())
