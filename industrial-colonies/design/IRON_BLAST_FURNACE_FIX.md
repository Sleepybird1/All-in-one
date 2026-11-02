# Iron dust reduction in TFMG

The iron-bearing dust reduction used immersiveengineering:blast_furnace. The candidate replaces that same recipe ID with tfmg:industrial_blasting. One iron-bearing dust produces 8 mB Modern Foundry molten iron and 10 mB TFMG molten slag, with processing_time 30 seconds (the prior 600 ticks) and hot_air_usage 20. Native furnace fuel and hot-air handling apply. No extra flux ingredient is imposed on this early iron route.

TFMG accepts fluid outputs only, so the molten iron replaces the former reduced-iron fraction followed by melting. The iron yield is unchanged. Existing reduced-iron fractions can still be melted for 8 mB. Slag now follows TFMG's native fluid handling. The 10 mB amount is based on half its native 20 mB slag-block recipe; the pack's existing casting-ownership policy remains unchanged. All other 295 material recipes and the 100 mB ingot / 1,000 mB block balance are preserved.

Authoring source: tools/build_iron_blast_fix.py. Current candidate catalog: progression/iron-blast-fix/effective.material-catalog.json. An APPLIED deployment receipt is required to claim installation. Earlier bucket/metal migration scripts are historical and must not overwrite this fix.

The subsequent ore/rock balance request supersedes this initial 296-recipe candidate. Use progression/ore-yields/ and design/ORE_RECOVERY_BALANCE.md for the final 300-recipe catalog, including the direct raw-iron 25/100 mB progression. The earlier candidate is retained as a layer, not a deployment target.
