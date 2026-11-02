"""Account for every archived rejection, including IDs retired from default."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = Path(r'C:\Users\GodPC\curseforge\minecraft\Instances\All in one\kjsgen')

def outputs(card):
    return {v.get('id') for k, v in card.get('slots', {}).items()
            if k.startswith(('output', 'result')) and isinstance(v, dict) and v.get('id')}

def main():
    load = lambda path: json.loads(path.read_text(encoding='utf-8'))
    active = load(LIVE / 'projects/default.json')['recipes']
    archive = load(LIVE / 'projects/rejected_recipes.json')['recipes']
    reviews = load(LIVE / 'industrial_colonies_sync/default.recipe_reviews.json')['reviews']
    active_ids = {r['recipeId'] for r in active}
    rows = []
    for card in archive:
        rid = card['recipeId']
        review = reviews.get(rid, {})
        matching = [r['recipeId'] for r in active if outputs(r) & outputs(card)]
        note = review.get('note', '')
        if rid in active_ids:
            disposition = 'active_recipe_to_review'
        elif matching:
            disposition = 'replacement_under_other_id_to_verify'
        elif any(word in note.lower() for word in ('default', 'doesnt make', 'doesn’t make', 'original recipe')):
            disposition = 'default_restoration_to_verify'
        elif any(word in note.lower() for word in ('disabled', 'tier installer', 'remove this', 'should not have recipes')):
            disposition = 'disabled_route_to_verify'
        else:
            disposition = 'absent_recipe_needs_investigation'
        rows.append(dict(recipeId=rid, outputs=sorted(outputs(card)), disposition=disposition,
                         replacementIds=matching, latestStatus=review.get('status'), note=note))
    archived_ids = {r['recipeId'] for r in archive}
    missing = [dict(recipeId=rid, **record) for rid, record in reviews.items()
               if record.get('status') == 'rejected' and rid not in archived_ids]
    report = dict(archiveCount=len(rows), counts=dict(Counter(r['disposition'] for r in rows)),
                  rejectedLedgerWithoutArchive=missing, recipes=rows)
    target = ROOT / 'progression/review-batches/20260904/full-rejected-archive-audit.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(dict(archiveCount=len(rows), counts=report['counts'], ledgerOnly=len(missing)), indent=2))
    for row in rows:
        if row['disposition'] == 'absent_recipe_needs_investigation': print(row['recipeId'], row['outputs'])

if __name__ == '__main__': main()
