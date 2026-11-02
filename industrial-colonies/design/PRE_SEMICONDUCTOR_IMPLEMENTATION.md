# Pre-semiconductor progression implementation

Status: installed in All in one on September 10, 2026 after native run `r7` passed. The application JAR remains 0.5.2; this is a recipe/progression update.

Scope: Basic Create, the Weathered/TFMG structural transition, Copper equipment needed to enter the existing semiconductor chain, and removal of early competing processing routes. Semiconductor/electronics recipes are preserved. Brass, Train, Industrial Iron and exotic machine recipes are not redesigned.

The authoring source is `tools/build_ownership_progression.py` against the exact captured live project in `progression/ownership/baseline.default.json`. This avoids regenerating the pack from the missing historical seed. The candidate preserves existing card UUIDs, project options and all removal cards. In-game edits must be merged into a fresh baseline before reapplying this migration.

## Implemented recipes

41 recipe cards change or are added: 26 Mechanical Crafter recipes, six compacting recipes, four pressing recipes and five sequenced component recipes. Two competing machine cards are retired. 642 unrelated original cards remain identical, including every electronics/semiconductor card. The resulting default project has 683 cards.

- Weathered Press starts from ordinary iron and Basic Create hardware. It requires neither steel nor its own products. Weathered Deployer then uses press-made heavy plate without requiring deployer-made frames. The remaining Weathered machines use structural frames and mechanisms, with no circuits, transistors, plastic or motors.
- Weathered Press owns cast-iron sheets, steel plates, heavy plate, industrial pipes and refractory forming. Weathered Deployer assembles steel frames, steel casing, steel mechanisms and heavy machinery casing. Existing registered parts and intermediate items are reused.
- Copper's six selected machines use 5×5 Mechanical Crafter layouts and Weathered-made structures. They do not consume semiconductors or capacitors. Copper Press/Deployer crafting-table shortcuts are removed.
- TFMG vats, tanks, industrial mixer, distillation output, selected valves and ducts use Mechanical Crafters for final assembly. Cast-iron tank/valve/pipe construction is reachable before steel and circuits. The ordinary refinery/distillation processing recipes remain unchanged.
- The rolling mill's legacy 5×2 dimensions excluded its third row. Its corrected 3×3 grid uses all eight intended inputs. All current Mechanical Crafter grids stay within 7×7.

## Machine ownership

Mekanism Crusher and its crushing factories, IE Crusher, NuclearCraft Manufactory/Rock Crusher and the Foundry Scorched Alloyer lose acquisition recipes. The corresponding generic crushing/grinding routes are removed; existing placed crushers no longer have their processing recipes.

65 surviving NuclearCraft manufacturing operations move to Create. Single-input recipes use Crushing Wheels; the two multi-input leather/bioplastic conversions use exact-count compacting, preserving their inputs and outputs. Raw ore bypasses are filtered by the earlier material policy before this transfer. Explicit coal, charcoal and coke grinding keep chemical and electrode feeds available.

Ordinary Create Metallurgy melting/casting/alloying/grinding, IE alloying, Mekanism slurry washing, TFMG casting and Diesel Generators casting are retired. Modern Foundry alloying remains disabled. Insulating glass is available from a heated Create Mixer. Existing approved material-specific arc-furnace, chemical and PGM bootstrap routes remain.

KubeJS separates original recipes from pending script additions. The policy checks both collections; ordinary `event.remove` alone does not remove those pending additions in the installed version. The material normalizer also rejects retired serializers before generating replacements, preventing a later reload from restoring them.

## Boundary safeguards

Native NuclearCraft Alloy Smelter/Melter/Ingot Former recipes were reachable without semiconductors. Their original construction ingredients are retained inside 5×5 crafter assemblies requiring existing circuit boards and frames. They now sit beyond this task's boundary. Their later nuclear processing recipes remain for a subsequent nuclear-specific ownership audit; this update does not claim complete enforcement across all later nuclear machinery.

Retiring Create Metallurgy would otherwise strand the existing Yellorium construction-metal endpoint. It now uses the existing Industrial Iron Mixer capability and Modern Foundry casting: one lead ingot plus one gold ingot yields 2,000 mB alloy, and 1,000 mB casts one Yellorium ingot. Its compound recipe remains unchanged. This does not add or redesign nuclear fuel, semiconductor manufacturing or an exotic machine tier.

## Validation and deployment

`tools/test_ownership_progression.py` verifies unchanged unrelated cards/UUIDs/options, exact electronics preservation, grid bounds, pressing input slots, and an acyclic dependency graph among changed components/machines. External native material sources are separately inspected; this is not a full survival-playthrough proof.

The isolated native harness uses the actual KJSGen exporter, loaded recipe manager and machine binding logic. It checks every changed recipe, rejected processors, retired machine outputs, semiconductor endpoints, downstream Yellorium availability and Weathered-only steel pressing. The existing 299-recipe material suite includes codec, fan-tier/cache, chemistry and value checks. Logs preserve unsuccessful intermediate runs rather than relabeling them as passes.

Installation is limited to the default KJSGen project, its native-exported default script block, the updated material policy script and the new ownership policy script. The Industrial Colonies 0.5.2 JAR, saves, other projects and other scripts are outside the deployment transaction. `tools/deploy_ownership_progression.py` requires passing native reports and exact tested hashes, refuses concurrent live edits or an open game, verifies backups and supports rollback on a write failure.

Final acceptance: both required native tests passed in 2m38s. The loaded manager contained all 41 changed recipes among 26,439 recipes, all four semiconductor endpoints, both retained Yellorium endpoints, and no prohibited serializers/machine outputs checked by the harness. Steel pressing accepted Weathered Iron and rejected normal/Copper presses. The material suite passed all 299 recipes and 145,355 assertions. The final ownership script removed 359 additional conflicts and migrated 65 NC operations; this count excludes removals performed earlier by the material normalizer.

Evidence: `isolated-runtime/ownership-01/launch-r7.log`, `material-processing-report-r7.json`, `material-processing-export-r7.json`, and `ownership-effective-recipes.json`; source checks and installation receipt are in `progression/ownership/`. Backup: `_industrial_colonies_backups/ownership-20260910-191354/` inside All in one. Four files were installed and verified. Restart Minecraft to load the updated recipes; existing worlds can use them without generating new chunks.
