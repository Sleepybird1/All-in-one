# Machine-centric Create recipe environments

## Why the old editor became slow

The first implementation treated every casing tier as a separate recipe
environment. Ten tiers multiplied by seventeen Create families produced 170
runtime recipe types and schemas. KJSGen supports fourteen of those Create
editors, so the build also cloned 140 visible picker cards.

KJSGen 2.0.5 filters every registered card on each search change and walks the
complete filtered list while rendering the picker. The repeated tier cards,
not a meaningful difference in a recipe's inputs or outputs, caused the picker
clutter and most of the slowdown.

The v2 catalog is process-first. KJSGen presents one card for Pressing, Mixing,
Cutting, Filling, and so on. A selector inside that editor chooses the actual
machine. Casing tier and casing item remain metadata for display or optional
ingredients; neither creates another visible editor environment.

The runtime compatibility IDs remain registered, but each process's native and
hidden type list is cached once. Hot paths such as fan processing therefore do
not rescan the full legacy matrix or allocate a new type list for every item.

## Runtime identity model

- An editor-authored **Base Create** selection routes to the hidden type
  `industrial_colonies:base_<family>`.
- A Create Encased selection routes to the existing hidden type
  `industrial_colonies:<tier>_<family>`.
- The hidden type binds the decoded recipe to a whitelist of exact block IDs.
  The server compares that whitelist with the block entity actually performing
  the operation.
- Native `create:<family>` recipes remain universal. This is intentional: a
  mod's existing recipe does not silently stop working in Create Encased
  machines merely because the editor gained an exclusive routing option.
- The original 170 custom IDs remain registered for old scripts and worlds.
  A valid old pair becomes an exact Encased lock. A pair for which Create
  Encased has no such machine, such as `andesite_pressing`, aliases to the base
  Create machine instead of becoming permanently unusable.

## Discovery audit

| Process | Create lookup path | Custom hidden types | Exact machine context |
| --- | --- | --- | --- |
| Pressing | `MechanicalPressBlockEntity.getRecipe` -> `AllRecipeTypes.find` | Aggregated by `AllRecipeTypesMixin` | Press block entity, including Encased subclasses |
| Compacting | Basin `RecipeFinder` / recipe trie | `MechanicalPressBlockEntityMixin` recognizes bound COMPACTING types | Explicit press block entity in basin match |
| Mixing | Basin `RecipeFinder` / recipe trie | `MechanicalMixerBlockEntityMixin` recognizes bound MIXING types | Explicit mixer block entity in basin match |
| Generic Basin | Basin `RecipeFinder` / recipe trie | Mixer mixin recognizes bound BASIN types | Explicit mixer block entity |
| Cutting | Saw's private `RecipeFinder` only recognizes native CUTTING | `SawBlockEntityMixin` explicitly appends matching bound CUTTING types and repeats Create's output/automation filters | Explicit saw block entity |
| Deploying | `DeployerBlockEntity.checkRecipe` -> `AllRecipeTypes.find` | Aggregated by `AllRecipeTypesMixin` | Deployer block entity |
| Item Application | Deployer recipe-search event -> `AllRecipeTypes.find` | Aggregated by `AllRecipeTypesMixin` | Deployer block entity; manual application has no machine and therefore cannot execute an exclusive Deployer recipe |
| Filling | `AllRecipeTypes.find`, plus two direct `RecipeManager.getRecipesFor` paths | Find aggregation plus `FillingBySpoutMixin` for the direct paths | Spout block entity |
| Emptying | `GenericItemEmptying` -> `AllRecipeTypes.find` | Aggregated by `AllRecipeTypesMixin`; direct belt/capability insertion probes are wrapped by the Item Drain mixins | Explicit Item Drain block entity, including probes outside its tick |
| Splashing / Haunting | Fan processing types -> `AllRecipeTypes.find` | Aggregated by `AllRecipeTypesMixin` | Encased Fan block entity |
| Sequenced Assembly | Parent lookup plus nested operation lookup | The outer assembly has no single machine identity. Each nested operation must carry its own route. | Per-step operator; never a cosmetic outer tier |

Crushing, Milling, Sandpaper Polishing, Mechanical Crafting, Conversion, and
the outer Sequenced Assembly currently have no alternative Create Encased
machine in this pack. They continue to use their native Create editor and type.

## Compatibility and remaining risks

- Exact routing is checked on both logical sides whenever a processing machine
  is present, preventing client-side animation/probe mismatches. Ownership and
  research-stage authorization remain server-authoritative.
- A recipe exported by an older editor with an impossible tier/family pair now
  means the base Create machine. This preserves playability but cannot recover
  an intention the old UI never represented.
- Create Encased 1.9.0 currently supplies eight variants of presses, mixers,
  saws, deployers and fans, plus Andesite/Zinc/Brass variants of Spouts and Item
  Drains. Updating that mod requires rerunning the catalog validator and
  checking for newly added or renamed block IDs.
- Sequenced Assembly must be tested separately because machine identity belongs
  to each step. Applying one machine choice to the whole sequence would be
  misleading and would reject otherwise valid multi-machine assembly lines.
  KJSGen therefore stores an exact per-row selector for Pressing, Deploying,
  Cutting, and Filling; code generation routes each nested recipe independently,
  runtime checks the currently operating block, and JEI renders that selection.
- The exact lock currently identifies stationary block entities. Create
  contraption-mounted saws and deployers use movement contexts rather than the
  placed machine block entity, so an exclusive editor-authored recipe fails
  closed there. Native Create recipes remain usable on contraptions. Supporting
  exclusive contraption recipes requires a separate movement-context identity
  adapter.
- Native Create recipes are checked before hidden machine-bound recipes. If two
  recipes intentionally share the same input, remove/replace the native recipe
  when authoring the exclusive one; otherwise the native compatibility recipe
  keeps priority.

Run `python tools/validate_machine_recipe_environments.py` after changing the
catalog, registration model, or runtime filters.
