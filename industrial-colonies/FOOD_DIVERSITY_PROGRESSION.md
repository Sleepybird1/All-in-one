# Food Diversity Progression

Industrial Colonies rewards eating a broad diet without turning food into an
uncapped source of player power. Every item that exposes Minecraft's
`FoodProperties` is eligible. This automatically includes vanilla food, Pam's
HarvestCraft foods, Farmer's Delight meals, and edible items from future mods;
there is no fragile hand-maintained item list.

## Rules

- A food is identified by its registry item ID. Another serving, a renamed
  stack, or an NBT/component variant of an already-eaten item gives no progress.
- Non-food items, potions, and other use animations without `FoodProperties` do
  not count.
- Progress belongs to the player, is serialized by a NeoForge data attachment,
  survives logout, and uses `copyOnDeath()` so it survives death and respawn.
- The `/cuisine` command shows the current count and next milestone. Eating a
  new food also shows compact action-bar progress; reaching a milestone sends a
  durable chat message.

## Health milestones

| Unique foods | Permanent reward |
| ---: | ---: |
| 10 | +1 heart |
| 25 | +2 hearts total |
| 45 | +3 hearts total |
| 70 | +4 hearts total |
| 100 | +5 hearts total |

The reward is one namespaced permanent max-health attribute modifier whose
value is reconciled from saved diversity data on login, respawn, and each new
food. It caps at +10 health points (+5 hearts), so adding hundreds of Pam's
foods expands the discovery journey but cannot inflate combat power beyond the
designed ceiling.

## Implementation ownership

This is companion-mod code only. It does not add, remove, or alter recipes and
does not interact with bosses, Apotheosis, KJSGen, or the managed recipe
manifest.
