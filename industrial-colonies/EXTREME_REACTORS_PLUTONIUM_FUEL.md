# Extreme Reactors Plutonium Fuel

The maintained override is
`pack-config-overrides/ExtremeReactors/modpack_api.json`. During pack assembly,
deploy it as `config/extremereactors/modpack_api.json`.

Extreme Reactors reads its ModPack API wrapper during game startup, before a
world or integrated server is opened. Installing or changing this file
therefore requires a **full Minecraft restart**. A datapack reload, KubeJS
`/reload`, or disconnecting from a world is not sufficient.

The override adds the `mek_plutonium` fuel reactant and maps exactly one
Plutonium Pellet from `c:pellets/plutonium` to 1,000 reactor fuel units. Its
fuel properties and Magentite-waste reaction intentionally mirror Extreme
Reactors' built-in Blutonium balance.

All built-in solid and fluid mappings that let Blutonium or generic Plutonium
act as reactor fuel are removed. Blutonium remains available as a crafting and
reprocessing material, but only Mekanism Plutonium Pellets can enter the
Plutonium reactor-fuel path. This makes the intended sequence:

`Fuel Reprocessing -> Actinide Chemistry -> Plutonium Production -> Advanced Nuclear Fuel`

The University/team-stage layer must still gate pellet production and the
advanced reactor recipes at their assigned nodes; this startup configuration
controls Extreme Reactors fuel acceptance, not research authorization.
