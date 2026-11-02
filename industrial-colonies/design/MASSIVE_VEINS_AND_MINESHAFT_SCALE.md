# Vein and mineshaft scale — user clarification, September 21

This clarification supersedes interpreting the recent corridor-preservation repair as final acceptance of vein size. WORLD-15 remains NOT_VERIFIED. Overall completion remains 145/237 (61.2%); world mechanics 12/15 (80%).

## Required behavior

The ore deposit is a massive, noisy three-dimensional body within the existing rock. A normal-sized mineshaft should fit within such a deposit, encountering mineralized rock throughout its workings. Mining beyond tunnel walls must reveal substantial continuing depth of ore-bearing material, rather than a shell following the tunnels.

Preserve irregular boundaries, lobes, native stone/deepslate gaps and the existing distinction between ordinary mineralized host and rich ore. A massive vein does not mean every block is rich ore. Do not fill existing cave or tunnel air with ore.

Both deposits and mineshafts can vary from very small to very large. Deposit scale determines the supported mine scale; a mineshaft may influence the deposit's shape, but should not define a tunnel-shaped coating. UPDATE September22: mineshafts must become rarer and their extraction nodes extremely far apart; see MINESHAFT_EXTRACTION_NODES.md. This supersedes the former unchanged-occurrence rule. Standalone deposits still do not require a mineshaft.

## Current implementation is not final acceptance

The installed M78 repair prevents overly aggressive whole-piece pruning from turning a mine into a room with no corridors. It preserves paths to two existing galleries and admits further pieces by their centers. It does not implement the clarified massive-body scale.

Current family volumes, for example hematite's normalSizeMin=3000 and normalSizeMax=5000 before quality multipliers, are insufficient evidence of a body encompassing an ordinary mine. Passing three corridor/access tests establishes neither whole-mine coverage nor suitable supply scale.

## Next implementation and acceptance

1. Calibrate small, ordinary and massive deposit dimensions against actual unpruned vanilla mine footprints. Do not use increasingly severe mine pruning to compensate for undersized deposits.
2. Increase physical deposit scale to support ordinary whole-mine footprints while retaining smaller and larger variants. Preserve ore recovery recipes and rich-grade proportions; larger deposits necessarily alter total supply and must be measured explicitly.
3. Check generation cost before applying larger volumes. Current shape construction allocates a voxel frontier and full body maps; blindly multiplying block counts risks memory and generation-time regressions. Prefer bounded chunk work if required.
4. Verify mineralized volume away from corridors, noisy boundary shape, retained native-rock gaps, connected galleries and representative whole-mine coverage. Do not substitute a bounding-box-only coverage test for actual mineral distribution.
5. Verify deterministic save/reload, clipping at world limits, no replacement of air/fluids, and reasonable generation cost across small, ordinary and large cases.

New massive-scale code, calibration and native performance tests: NOT_RUN. No new production installation or save modification is implied by this recorded clarification. Existing generated terrain remains unchanged.
