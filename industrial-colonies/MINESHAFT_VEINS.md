# Mineshaft ore connections — 0.5.2

Design: mineshafts retain their existing spawn rate. Each newly generated vanilla mineshaft receives one connected ore working. Standalone geological veins keep generating independently and do not create mineshafts.

The implementation appends a short excavated working and adjacent ore body to the central room after vanilla finishes generating and positioning its pieces. It preserves the original generation position, original pieces and vanilla random stream. Both ordinary and badlands mineshafts use this rule. No structure-set frequency, spacing, biome tag or locate rule is edited.

This adds a modest deposit at each mineshaft; it does not move a shaft to an existing regional deposit. Existing major-deposit frequency and spacing remain unchanged, so total ore increases by the attached workings. The ore body is an ellipsoid up to 11 × 9 × 7 blocks, with a four-block-long entrance. Original shaft volumes and world-height limits clip the result. Ore type uses the existing geological biome/depth weights, host blocks and normal rich-ore fraction. The attached body does not use regional deposit spacing or regional quality/size rolls.

The working is part of the structure: solid ore walls can occupy natural air or fluid. Placement protects the original mineshaft piece volumes, bedrock, barriers and block entities, and clips reads/writes to the owning chunk. Vanilla room/corridor placement still follows Minecraft's usual terrain restrictions. Disabling geological generation also disables the attachment.

Existing cave traces and collectible surface rocks remain. Surface clues continue to describe regional deposits; they do not gain a new detector for these attached workings.

Restart Minecraft and explore newly generated mineshafts. Existing saved structure starts are not retrofitted. No existing world needs to be deleted.

## Validation

Build passed. All six required native tests passed in 2m51s with the 235-JAR server-compatible modpack copy. Evidence: `build/mineshaft-build-final.log` and `isolated-runtime/mineshaft-01/launch-r1.log`. The native harness compared 128 ordinary/badlands generation plans against vanilla's original piece-building method: all 16,874 original pieces, generation positions and random streams matched. Twenty-one distinct host materials appeared. Serialization, translated structure movement and duplicate-attachment protection passed.

The controlled dry-stone fixture placed an actual central room and coal working: 243 new working blocks, 13 ore faces reachable from the room, spanning two chunks. Forward and reverse chunk order produced identical working blocks, and all original room/corridor blocks were preserved. The test also rejected reads/writes outside the owning chunk. These are connection and compatibility tests, not a natural-world frequency survey or visual review. Existing unrelated recipe warnings remain outside this update.

`build/mineshaft-archive-audit.json` compares the candidate with 0.5.1. Twenty-one surface loot tables differ only in JSON ordering. Six surface display labels also remove a duplicated “Rock”; pickup behavior, recipes and textures are unchanged.

## Installation

Installed into All in one on September 9, 2026. SHA-256: `D1A60CE6F8869B7C1197EAE9D0D2879B8599A38BC34C064D878475E8594EFA2E`. The hash-pinned installer replaced only the Industrial Colonies JAR after verifying that the live pack was closed. The prior 0.5.1 JAR is backed up under `_industrial_colonies_backups/mineshaft-veins-0.5.2-20260909-191716/` in the instance. Receipt: `build/mineshaft-deployment.json`. No saves or recipe scripts were modified.
