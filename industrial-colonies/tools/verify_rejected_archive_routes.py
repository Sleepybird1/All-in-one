"""Cross-check old rejected cards against installed static recipe producers."""
import json,re,zipfile
from pathlib import Path
from collections import defaultdict,Counter
from audit_full_rejected_archive import ROOT,LIVE,outputs

def result_ids(value):
    if isinstance(value,str): return {value} if ':' in value else set()
    if isinstance(value,list): return set().union(*(result_ids(v) for v in value))
    if isinstance(value,dict):
        found=set()
        for key in ('id','item'): found |= result_ids(value.get(key,[]))
        return found
    return set()

def recipe_outputs(value):
    if not isinstance(value,dict): return set()
    found=set()
    for key in ('result','results','output','outputs'): found |= result_ids(value.get(key,[]))
    return found

def main():
    audit=json.loads((ROOT/'progression/review-batches/20260904/full-rejected-archive-audit.json').read_text(encoding='utf8'))
    project=json.loads((LIVE/'projects/default.json').read_text(encoding='utf8'))
    removed={r.get('recipeId') for r in project.get('removals',[]) if r.get('recipeId')}
    producers=defaultdict(set)
    for jar in (LIVE.parent/'mods').glob('*.jar'):
        try:
            with zipfile.ZipFile(jar) as z:
                for name in z.namelist():
                    match=re.fullmatch(r'data/([^/]+)/recipes?/(.+)\.json',name)
                    if not match: continue
                    try: data=json.loads(z.read(name))
                    except (ValueError,UnicodeError): continue
                    rid=match[1]+':'+match[2]
                    for item in recipe_outputs(data): producers[item].add(rid)
        except zipfile.BadZipFile: continue
    for row in audit['recipes']:
        stock=set().union(*(producers[item] for item in row['outputs']))
        row['installedStaticProducerIds']=sorted(stock)
        row['notRemovedByProject']=sorted(stock-removed)
        if row['disposition']=='default_restoration_to_verify' and stock-removed:
            row['disposition']='default_static_route_present'
    target=ROOT/'progression/review-batches/20260904/rejected-archive-route-audit.json'
    target.write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(dict(Counter(r['disposition'] for r in audit['recipes'])))
    for row in audit['recipes']:
        if row['disposition'] in ('absent_recipe_needs_investigation','default_restoration_to_verify') or row['recipeId'] in ('industrial_colonies:electronics/rotor','industrial_colonies:v3_ae2/accumulation_processor'):
            print(row['recipeId'],row['installedStaticProducerIds'],row['notRemovedByProject'])

if __name__=='__main__':main()
