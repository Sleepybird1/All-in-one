# Create machine recipe-stage gate

Industrial Colonies gates exact Create recipe IDs from the generated
`data/industrial_colonies/progression/recipe_stages.json` manifest. The recipes
remain globally loaded and visible. Client-side lookups are never stage-filtered;
on the logical server, only mapped IDs require the owning machine's FTB Team to
hold the exact MineColonies research stage. Unmapped recipes retain normal Create
behavior.

## Persistent machine ownership

Every player-placed Create `SmartBlockEntity` receives a persistent UUID
attachment. Both ordinary placement and NeoForge multi-place events are stamped.
Create's complete smart-block-entity tick and its belt/depot processing callback
are wrapped in a nested `ThreadLocal` scope with `try`/`finally` semantics, so a
recipe lookup can identify the machine that initiated it without leaking an
owner into the next tick. A mapped server recipe fails closed when that scope,
the persistent owner, the FTB Teams manager/team, or the required stage is
missing.

Machines placed before this attachment existed have no inferred owner and must
be broken and placed again before they can run mapped recipes. Schematicannon,
contraption, automation/fake-player, or other non-player placement is deliberately
not assigned to a nearby or arbitrary team.

## Runtime coverage

- `AllRecipeTypes.find` aggregates the native Create type and every registered
  Industrial Colonies tier type for that family, retaining native recipes first,
  and filters the chosen exact holder ID for the current owner on the server.
- Mechanical Press and Mechanical Mixer admit the matching tiered compacting and
  mixing types into Create's global basin recipe trie. The subsequent
  `BasinOperatingBlockEntity.matchBasinRecipe` check performs the per-owner test;
  team state is never placed in Create's global recipe cache key.
- Sequenced Assembly filters the parent assembly holders before Create extracts a
  nested deploying, pressing, filling, or other next-step recipe. Authorization
  therefore follows the stable parent recipe ID across every loop and step.
- Both direct `FillingBySpout` recipe-list lookups are replaced with the same
  native-plus-tiered, owner-filtered resolver.
- Mechanical Crafting uses the aggregate resolver for native/tiered mechanical
  recipes. Its ordinary crafting-table fallback receives an additional exact-ID
  guard, preventing a shaped or shapeless mapped recipe from bypassing the
  machine gate.
- Belt/depot processing callbacks use the processing block entity rather than the
  belt's outer tick as owner context. Encased-fan processing is covered while the
  fan's smart block entity performs its air-current tick and calls
  `AllRecipeTypes.find`.

The construction dependency catalog contains 93 rows resolving to 92 unique
recipe IDs. A separate 43-row source-processing catalog covers existing Create,
Mekanism, chemical, and storage-conversion recipes that need research ownership
without being construction overhauls. The generated runtime manifest merges
both sources into 135 unique exact staged recipe IDs.

Mapped Create construction recipes use Mechanical Crafting, Sequenced Assembly,
and Crushing as top-level families; the pre-steel Oil Processing slice adds
ordinary shaped crafting recipes handled by the player gate. The source catalog
also stages Create uranium crushing, splashing, and compacting. The Create
recipes, including nested deploying and pressing steps, are covered by the hooks
above. The Yellorium Refinement crushing recipe is therefore enforced at the
same exact-ID boundary as the later nuclear construction lines that consume its
compound.

## Deliberate gaps and operational limits

- The Mechanical Saw's cutting lookup uses its own globally cached predicate and
  does not call `AllRecipeTypes.find`. No current construction-manifest row uses
  a cutting recipe, so this release does not patch that cache. A future mapped
  cutting recipe requires a cache-safe family-visibility hook plus a per-owner
  identity check analogous to the basin implementation.
- Contraption-mounted processing does not have a persistent stationary
  `SmartBlockEntity` owner scope. A mapped recipe reached only from that path
  fails closed instead of borrowing a player or allowing a bypass.
- A connected Mechanical Crafter grid is authorized with the smart block entity
  whose tick initiates the recipe. Mixed-owner grids are unsupported; keep every
  block in one crafter array under the same placing team.
- Third-party Create addons that enumerate `RecipeManager` directly instead of
  using `AllRecipeTypes.find`, basin matching, Sequenced Assembly, or the covered
  filling paths need their own exact call-site audit before mapped recipes are
  assigned to them.

Changing `tools/machine_recipe_dependencies.json` or
`tools/additional_recipe_stages.json` and rebuilding regenerates the shared
manifest. `/reload` refreshes both the mapping and the basin recipe identity
cache; replacing this mod JAR or changing Create/addon versions warrants a full
restart and a repeat descriptor audit.
