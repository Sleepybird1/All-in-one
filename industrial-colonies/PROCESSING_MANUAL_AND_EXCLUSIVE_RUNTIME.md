# Material-processing runtime additions

Scope: attended manual Cinnabar, exact-machine fan cache correction, and mutually exclusive crude PGM recovery. No production entrypoint, mixin registry, item registry, live pack, or world was edited by this bounded implementation.

## Integration hooks (root-owned)

In `IndustrialColonies` construction, after registries are established, call:

```java
dev.godpc.industrialcolonies.processing.ProcessingRecipeRuntime.register(modEventBus);
```

Add `ProcessingFanCacheMixin` to the common `industrial_colonies.mixins.json` list. The existing `AllRecipeTypesMixin`, `SmartBlockEntityTickerMixin` and exact tier bindings remain prerequisites and are not replaced.

The central content registry must provide `industrial_colonies:roasted_cinnabar`. No duplicate hammer is registered. The handler uses the installed `immersiveengineering:hammer`.

## Manual Cinnabar interaction

1. Fuel and light the existing `createlowheated:basic_burner`, using its normal placement/operating conditions.
2. Hold exactly **one** `industrial_colonies:cinnabar` in the main hand and right-click the lit burner.
3. Remain within 4.5 blocks, continuously aiming at that burner and holding the same one-item input, for 1,200 ticks (60 seconds).
4. The held input is replaced with one `industrial_colonies:roasted_cinnabar`. Processing stops; it never starts another batch automatically.
5. Put exactly one roasted item in the off hand. Use a working Engineer's Hammer in the main hand to right-click the top of a solid block. That one off-hand item becomes one Redstone Dust; the hammer takes durability damage and a 20-tick cooldown.

Action-bar messages explain start, interruption, remaining time, finish, working-surface requirements and cooldown. Hammer breakage uses vanilla's damage/break handling; creative mode and Unbreaking retain normal vanilla durability semantics.

Only a genuine server-listed player object can operate this route. NeoForge FakePlayers and unlisted synthetic ServerPlayers cannot. There is no recipe-grid endpoint, item-handler capability, dropped-item loop, automatic transfer, or shift-craft path. Each burner accepts only one player's active session and each player only one burner. Another block, extinguishing the burner, moving out of reach, looking away, changing the held item/count, dying, becoming a spectator, changing dimension or disconnecting interrupts work. Interruption does not consume or escrow an item. The next manual start begins from zero. World/server stop clears transient reservations.

Settings are copied on first runtime access from `data/industrial_colonies/processing/manual_cinnabar.json` to `config/industrial_colonies/processing/manual_cinnabar.json`; changing them requires restart. Defaults:

```json
{"enabled":true,"heatingTicks":1200,"hammerCooldownTicks":20,"hammerDamage":1,"reach":4.5,"manualNoBatch":true}
```

All settings are read and validated. `manualNoBatch=false` is rejected because batch processing belongs to the independent industrial route, not this manual capability. Heating range is 20–72,000 ticks; cooldown 1–1,200 ticks; damage 1–100; reach 1–5 blocks. Invalid/missing overrides fail loudly. `enabled=false` disables the manual handler only.

This is physical Basic Burner interaction, not a disguised `create:mixing` recipe. Low Heat's standard basin recipes do not implement attended one-item roasting, and mixer duration is speed-dependent; those systems remain untouched.

## Exclusive PGM milling schema

Serializer: `industrial_colonies:exclusive_milling`.

Runtime recipe type remains `create:milling`, via `ExclusiveMillingRecipe extends MillingRecipe`. Keeping the native recipe type lets millstones and Create's normal JEI milling category discover it. Proper industrial crushing uses a separate `create:crushing` recipe for the same rock, avoiding two competing recipes of the same type/input.

```json
{
  "type": "industrial_colonies:exclusive_milling",
  "ingredients": [{"item": "industrial_colonies:ultramafic_rock"}],
  "processing_time": 400,
  "recovery_chance": 0.20,
  "results": [
    {"id": "example:osmium_fragment", "count": 1, "chance": 0.70},
    {"id": "example:platinum_fragment", "count": 1, "chance": 0.25},
    {"id": "example:iridium_fragment", "count": 1, "chance": 0.05}
  ]
}
```

Output IDs above are deliberately placeholders: the root compiler chooses actual registered canonical nugget-type outputs. The serializer uses standard Create `ProcessingRecipeParams` fields plus a required `recovery_chance`. Item results must be nonempty count-one stacks. Their `chance` values are **one mutually exclusive distribution**, not independent rolls; they must sum to one. Recovery can yield nothing, or exactly one selected item. There is never a second metal roll. Default distribution is Os/Pt/Ir 70/25/5 conditional on successful recovery; default success rate 20% is supplied by the generated recipe, not hardcoded in Java. JSON and network decode both validate the exclusive distribution. Fluid outputs are rejected.

Both `rollResults(RandomSource)` and the list overload are overridden. Native independent-roll implementation is never called. This serializer is standalone milling, not a sequenced-assembly transitional recipe.

## Fan cache repair

Create 6.0.10 caches a failed fan operation by fan-processing type alone, with `Time=-1` on dropped items and `processingTime=-1` on transported items. A wrong low-tier fan can therefore prevent the same item from being reconsidered at the correct Industrial Iron fan.

The new common mixin rechecks only inputs participating in machine-bound SPLASHING/HAUNTING recipes. It invalidates cached rejection when processing becomes possible, and clears progress while the current machine cannot perform the recipe. Both dropped entities and transported belt/depot stacks are covered. Completion still uses the existing exact-machine recipe matcher. Normal ungated fan inputs retain native caching. The ingredient index is cleared after datapack synchronization and server stop; no permanent player/item metadata is added.

## Focused verification

`tools/test_processing_runtime.ps1` compiles/runs only the pure session state machine, manual settings validation and exclusive probability helper using Java 21 plus installed Gson. It never starts Minecraft or reads/writes runtime configuration. It covers all 65 item counts × 64 continuation-condition combinations, station/player exclusivity, interrupted progress, timer boundaries, 50 invalid cases and 600,000 sampled recovery rolls, plus an exact 10,000-point 70/25/5 partition.

Initial pure test result: `PROCESSING_RUNTIME_PURE PASS assertions=1205434 invalidCases=50`. The local Windows javac process additionally printed a Gson JAR ZipFS-close `AccessDeniedException` after emitting classes and returned exit 0; the subsequent independent Java test process completed the full PASS above. This does not substitute for a clean full project compile or game runtime test. No Gradle or Minecraft launch has been performed by this bounded task.
