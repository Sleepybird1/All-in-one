# Cave exploration traces — 0.5.1

Small recoverable patches now form on air-exposed underground stone, including cave walls, floors and ceilings. This supplements the existing surface traces and regional deposits.

| Resource | Patch selection weight |
| --- | ---: |
| Coal | 35% |
| Hematite (iron) | 30% |
| Sphalerite (zinc) | 15% |
| Cassiterite (tin) | 15% |
| Chalcopyrite (copper) | 5% |

Defaults: 1–3 connected exposed blocks per patch; six candidate patch attempts per chunk, each with a 65% chance. Thirty-two sampled underground columns find exposed faces, rather than spending attempts on arbitrary buried blocks. A chunk with sufficient cave exposure averages roughly four patches before placement clipping; chunks without suitable caves produce none. At most 18 blocks can be added in a chunk. These are tuning defaults, not a guarantee for every cave.

Only natural stone/deepslate ore-replaceable blocks qualify, at Y -60 through 503, clipped to the actual world height and at least eight blocks below the sampled terrain surface. Dry cave faces and deep ravine faces qualify; fully submerged faces do not. Every placed block must touch air. Existing geological deposits, structures, fluids, air and bedrock are not replacement targets. A one-block chunk-edge margin keeps all terrain reads and writes in the owning chunk.

The four main resources account for 95% of patch selections. Zinc and tin use the approved low-yield geological rocks and their existing processing chains; no new recipe, texture, rich ore, or advanced-metal shortcut is added.

## Use and tuning

Restart Minecraft after installing. Explore **newly generated chunks**: already generated caves are not retroactively populated. This does not require deleting an existing world.

On first use the mod creates `config/industrial_colonies/worldgen/cave_traces.json`. Its separate file allows existing `settings.json` overrides to continue working. Edit it and restart to adjust density, patch sizes, resource weights or disable the feature. Do not infer block percentages from patch weights when clipping changes individual patch sizes.

## Validation

- Java 21 / NeoForge build passed.
- Production planner passed 2,000 synthetic cave cases: deterministic replay, negative chunk coordinates, all adjacency accesses contained within the owner, exposed and connected patches, placement limits, height/cover filtering, protected material, no-air caves and zero chance.
- Synthetic run: 7,845 patches / 15,724 blocks. Patch selections: coal 2,759; hematite 2,369; zinc 1,189; tin 1,126; copper 402. This is a controlled geometry test, not a natural-world density measurement.
- Comparing all archive entries against installed 0.5.0 found only the new cave classes/configuration, the one geology generation hook and version metadata changed. All recipes, textures and other class/resource entries are byte-identical.
- Native Minecraft tests: all six required tests passed in a fresh Lithosphere world, using the 235-JAR server-compatible test copy. The controlled native fixture placed nine exposed blocks. Eight sampled natural chunks contained 36 exposed starter-resource blocks: 15 coal, 12 hematite, five cassiterite and four sphalerite. Those counts include existing deposits and are not a trace-only density estimate. Evidence: `isolated-runtime/cave-traces-01/launch-r2.log`, with both `CAVE_*_PASS` markers and the six-test passing summary. Run completed in 3m34s. Existing unrelated recipe warnings remain outside this change.
- Initial launch used an incomplete dependency cache and stopped before Minecraft; its log is preserved as `launch-r1.log`. The successful run used the previous task's complete local cache without new downloads.
- Original trace-only candidate SHA-256: `F862E00264A5E695CA807267436B3C7839560BC432443037B7F4EFA7A0589CEA`, preserved as `isolated-runtime/cave-traces-01/trace-only-0.5.1.jar.evidence`.
- The combined cave-trace / collectible-surface-rock candidate has SHA-256 `C4BCAA9D8068B592A435AF18492A66E3C495BB3112A29C31796B5F25541E5BC2`. It passed all eight required tests in `launch-surface-r2.log`, including the repeated native cave fixture and fresh natural cave survey. See `SURFACE_ROCKS.md` for additional scope.
- Installed in All in one as 0.5.1 after the combined update's visual check. Final JAR SHA-256: `7219C29073CF45918E4BD8A64127E4D83147CC277120E334BE10242882078749`; see `SURFACE_ROCKS.md` for the display-name-only final-build audit and backup receipt. Design decision following the user clarification: rewarding exploration is the goal. Keep the installed exposed starter-resource patches and existing major-deposit generation. Major veins may intersect caves naturally; no mandatory cave/vein connection is implemented or pending.

The working source now lives in this project's `industrial-colonies` directory, copied from the previous task's source. The earlier source and historical evidence remain available at their original location.

September 9 follow-up, 0.5.2: the user selected a specific mineshaft-to-ore connection. See MINESHAFT_VEINS.md. This adds one attached working per new vanilla mineshaft while preserving mineshaft frequency and independent regional veins; it does not impose a connection on every cave.
