# 100 mB metal accounting

The later [full-bucket correction](BUCKET_BLOCK_MIGRATION.md) supersedes this document's 900 mB finished-block value: blocks now equal 1,000 mB and ten ingots. This document retains the original migration evidence; its ingot, nugget and ore balance still applies.

The user requested conversion of the original 1,000 mB ingot model to 100 mB. When asked how to handle fractional mB, the user delegated the balance decision: "Make the balance make sense." They subsequently authorized continued work without further replies.

Status: installed September 11, 2026 at 07:18 EDT, tested revision `r4`. Both required native tests passed, including all 296 material recipes and the earlier ownership/semiconductor gates. Final checks cover 168 same-material castings, 198 melting routes, 58 ingot breakdowns and 45 ten-nugget consolidations. Six files were installed and hash-verified. Backup: `All in one/_industrial_colonies_backups/metal-units-20260911-071858`. The mod JAR, default project, generated project export and saves were not changed.

## Consistent units

* Ingot: 100 mB.
* Nine-ingot storage block: 900 mB.
* Nugget: 10 mB for the metals covered by fluid conversion, replacing the old inconsistent iron/gold exceptions.
* Ingot breakdown: ten nuggets. Legacy nine-nugget-to-ingot shortcuts become ten-nugget Mechanical Crafter recipes (5 by 2); core metals also receive that consolidation route. Ten nuggets melt into one ingot's fluid value.

Only metal-fluid quantities are rescaled. Acids, water, gases, oils, plastics and other chemical quantities keep their existing values. Machine tiers, item recipes in the material catalog, heat, times, energy and ore drops remain unchanged. Item-to-item consolidation batches already express ingot ratios and do not need a volume change.

The 296-recipe material catalog has 143 changed metal-fluid fields. The policy also reconciles alternate native and pending KubeJS recipes. Ingot-tagged materials outside the original 23-metal catalog use their native metal-fluid units as the conversion baseline, not an indiscriminate division of every fluid by ten. Casting and melting of recognizable finished forms use their exact new item value. Existing later-tier recipes change units only; no new exotic progression is designed.

Native casting definitions supply fluid aliases that cannot be inferred from names, including molten debris for netherite scrap. Both melt and cast directions must use that alias so nugget breakdown cannot multiply fluid. Legacy recipe IDs are captured explicitly; newly authored pack recipes use the new 100 mB basis rather than being divided by ten again.

## Whole-mB balance decisions

Minecraft fluid quantities are integers. Owned ore outputs round to the nearest whole mB, with 0.5 rounded upward and a 1 mB minimum for recoverable traces. Other conversion inputs round upward and outputs downward to prevent rounding-created fluid. Finished ingot, block and nugget values are exact.

| Feed | Old mB | New mB | New feed per ingot |
|---|---:|---:|---:|
| Hematite or magnetite, directly melted | 25 | 3 | 34 pieces yield 102 mB |
| Reduced iron fraction | 75 | 8 | 13 pieces yield 104 mB |
| Raw iron | 200 | 20 | 5 |
| Raw copper or zinc | 125 | 13 | 8 pieces yield 104 mB |
| Processed copper dust | 50 | 5 | 20 |
| Gold flake | 1 | 1 | 100 |

These are deliberate small-yield balance adjustments, not mathematically exact division by ten. The minimum makes gold flakes worth ten times their former fraction of an ingot. Consistent nuggets also replace the earlier unusual per-metal nugget fractions. Those choices keep useful whole-mB trace outputs and understandable item conversions instead of adding batch-packaging items throughout early mining.

## Displays and saves

Modern Foundry ships fluid tooltip units separately from its recipes: its defaults are 90 mB per ingot and 810 mB per block. The KubeJS asset overrides change both the ingot-only display and the detailed metal display to 100/900/10. The Reduced Iron Fraction label changes from 75 mB to 8 mB.

No saves are rewritten. Existing tanks retain their stored numerical mB, so previously stockpiled molten metal can cast more ingots under the smaller unit system. Existing solid items retain their identities. This is a recipe/resource migration, not an automatic conversion of stored fluids. Restart Minecraft to load both server recipes and client tooltip resources.

## Sources and evidence

* `tools/build_metal_units.py` builds the material and ownership script candidates from the captured installed baseline and original material catalog.
* `tools/build_metal_unit_closure.py` builds the final native/pending recipe reconciliation layer.
* `progression/metal-units/effective.material-catalog.json` is the current 296-recipe validation catalog after installation.
* `progression/metal-units/source-validation.json` proves the owned recipe payload changes are restricted to positive integer fluid amounts.
* `isolated-runtime/metal-units-01` contains isolated native runtime reports and effective recipes.
* `progression/metal-units/deployment.json`, when `APPLIED`, identifies the installed hashes, tested revision and backup.

The original 1,000 mB catalog and prior migration receipts are historical source/reference data. Do not reinstall them over this migration. Native tests verify recipe loading and units; client tooltip JSON follows the installed Hilt schema but is not visually tested in a launched client.
