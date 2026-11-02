# One-bucket metal blocks

Installed September 11, 2026 at 15:43 EDT, revision r1. Deployment receipt: `progression/bucket-blocks/deployment.json` (`APPLIED`). The three previous files are backed up in the live instance under `_industrial_colonies_backups/bucket-blocks-20260911-154319`.

The user corrected the block value to one full bucket, 1,000 mB. This supersedes the earlier 900 mB finished-block value. The resulting unit system is:

| Form | Molten metal |
|---|---:|
| Nugget | 10 mB |
| Ingot | 100 mB |
| Finished metal storage block | 1,000 mB |

One block therefore contains ten ingots (100 nuggets). A basin's required casting amount comes from its recipe; the full-bucket block amount is the chosen pack balance, not an inherent restriction that prevents smaller castings.

## Recipe changes

The 21 canonical finished metal blocks receive matching 1,000 mB melting and casting recipes: 42 changes in the 296-recipe material catalog. Native and script-added routes use the same block values through the final unit policy. Pure ingot-to-block recipes use ten ingots in a 5-by-2 Mechanical Crafter layout; matching block breakdowns yield ten ingots. This prevents nine ingots becoming a block that remelts into ten ingots' worth of fluid.

Ore yields, raw-ore storage quantities, ingot/nugget values, semiconductor recipes, machine ownership and nonmetal fluids remain unchanged. Hematite still yields 3 mB and Reduced Iron Fraction 8 mB. Ordinary raw-ore storage blocks retain their separate processing values; they are not finished metal storage blocks.

The early block path remains available: the native Seared Basin is made from seven Seared Bricks and can cast a full-bucket iron block before Mechanical Crafters or the first iron-block-dependent Create Press. This avoids making the first block require a crafter whose components need a press. Mechanical Crafter compression is an additional solid-item path.

The Modern Foundry detailed metal tooltip now displays blocks as 1,000 mB. Its ingot display remains 100 mB.

## Sources and verification

`tools/build_bucket_blocks.py` captures and merges the current installed scripts rather than reinstalling an older project. Candidates and the current material catalog are under `progression/bucket-blocks/`. `tools/check_bucket_blocks.py` verifies the effective native block castings, remelting, ten-ingot compression and breakdown paths alongside the previous ingot/nugget checks.

`progression/bucket-blocks/deployment.json`, when `APPLIED`, records the tested revision, backups and installed hashes. Installation changes only the material recipe script, final unit policy and detailed metal tooltip JSON. The project, semiconductor script, mod JAR and saves are preserved. Restart Minecraft to apply the recipe and client-resource changes; existing tanks retain their stored numerical mB.

Native verification passed all 296 material recipes (145,310 assertions), 41 ownership endpoints and semiconductor acceptance. The effective recipe check passed 52 block castings, 77 ten-ingot compression routes, 80 block breakdowns, 168 ingot/nugget castings, 198 finished-form melting checks, 58 ingot breakdowns and 45 nugget consolidation routes. Pre-existing empty uranium ingredient tags leave several uranium recipes unusable; those exact routes are recorded separately in `effective-unit-check.json` with baseline and current native-log evidence. Uranium tag repair is outside this unit correction.
