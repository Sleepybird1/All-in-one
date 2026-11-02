# Player crafting recipe-stage gate

Industrial Colonies gates only exact recipe IDs present in the generated
`data/industrial_colonies/progression/recipe_stages.json` manifest. An unmapped
recipe follows vanilla behavior. A mapped recipe requires the exact
MineColonies research ID on the real crafting player's FTB Team; a missing FTB
Teams manager, team, or stage denies the result without removing the recipe for
other teams.

## Result enforcement

`CraftingMenuMixin` redirects the concrete call to
`ResultContainer.setRecipeUsed(Level, ServerPlayer, RecipeHolder)` inside the
shared server-side
`CraftingMenu.slotChangedCraftingGrid(AbstractContainerMenu, Level, Player,
CraftingContainer, ResultContainer, RecipeHolder)` helper. The crafting table
uses this helper directly, and `InventoryMenu` calls the same helper for the
player's 2x2 grid.

If the shared gate denies the holder's exact ID, the redirect returns `false`
without marking the recipe used. Vanilla's existing false branch leaves the
result empty, updates the menu's remote slot, increments the state ID, and sends
the normal `ClientboundContainerSetSlotPacket` for slot 0. The client therefore
sees an empty result instead of a ghost item; there is no post-craft rollback or
inventory race.

## Recipe-book placement

`RecipeBookMenuMixin` cancels, for `CraftingMenu` and `InventoryMenu`,
`RecipeBookMenu.handlePlacement(boolean, RecipeHolder, ServerPlayer)` at method
entry for a locked mapped recipe. This is the earliest server path containing
both the exact holder ID and the real player, so denied placement cannot shuffle
ingredients into either crafting grid. Allowed and unmapped recipes continue
through the original placement logic unchanged.

## Scope and verification

The manifest merges construction overhauls from
`tools/machine_recipe_dependencies.json` with existing source-processing and
conversion IDs from `tools/additional_recipe_stages.json`. Node labels from both
sources resolve to exact research resource IDs through the generated MineColonies
translations. Adding an ordinary shaped or shapeless ID to either appropriate
source automatically makes that exact ID enforceable in both 2x2 and 3x3 player
crafting after rebuilding the mod.

NeoForge's `PlayerEvent.ItemCraftedEvent` is intentionally not used: it fires
after the output is taken, has no `RecipeHolder`, and cannot safely implement a
per-team pre-result denial. Create Mechanical Crafting has no real
`ServerPlayer` at its lookup point and is handled separately through persistent
machine ownership.

`tools/validate_recipe_stage_gate.py` compares the generated and processed
manifests to both source catalogs, checks the source and processed mixin lists,
and requires the four compiled player/shared/Mekanism gate classes. The focused
validator currently passes with 135 unique exact recipe IDs: 92 unique IDs from
93 construction rows plus 43 additional source-processing rows. The aggregate
NeoForge build passes. Runtime multiplayer and client result-sync tests remain
pending.
