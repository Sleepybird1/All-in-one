# Extreme Reactors plutonium tier lock

## Audited runtime hook

The target pack contains Extreme Reactors `1.21.1-2.4.28`. Its
`ReactorSolidAccessPortEntity.consumeFuelSource(ItemStack)` method has the exact
descriptor
`(Lnet/minecraft/world/item/ItemStack;)Lnet/minecraft/world/item/ItemStack;`.
`ReactantHelper.refuelSolid` passes this hook a count-limited copy of the actual
fuel stack and treats an empty return as no fuel consumed or inserted.

## Lock behavior

Industrial Colonies returns `ItemStack.EMPTY` only when both audited registry
IDs match:

- requested fuel: `mekanism:pellet_plutonium`
- access-port block state: `bigreactors:basic_reactorsolidaccessport`

The item remains in the basic port and the reactor receives no plutonium.
`bigreactors:reinforced_reactorsolidaccessport` does not match the basic-port
guard and remains able to consume Plutonium Pellets. Every non-plutonium solid
fuel follows the original Extreme Reactors method unchanged.

This is a runtime hard lock, not a recipe or tag removal. It complements the
pack's custom `mek_plutonium` reactant mapping and keeps advanced fuel usable
without allowing it to bypass the reinforced reactor tier.

## Validation

`clean compileJava --rerun-tasks --offline` completed successfully against the
installed Extreme Reactors `2.4.28` and ZeroCore `2.4.21` jars. A subsequent
`processResources` run also completed successfully and included both the mixin
entry and required `bigreactors` dependency metadata.
