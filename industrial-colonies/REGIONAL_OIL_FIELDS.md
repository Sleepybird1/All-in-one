# Regional, Finite Oil Fields

TFMG remains the owner of crude oil and petroleum refining. The authoritative geological framework replaces the previous dry-biome-only placement. See `OIL_WORLDGEN_FRAMEWORK.md` for the current data-driven regional oil implementation and configuration.

- The globally common TFMG deposit placement is removed.
- New fields favor desert/badlands/outback and ocean/offshore basins; plains/sedimentary lowlands are secondary, and lowland forest/wetland chances are reduced. Mountain, highland, volcanic/ashen and cold mountain terrain are prohibited.
- The replacement adapter plans seeded regional fields, then invokes TFMG's native single-deposit builder for eligible wells in their owning chunks at Y=-64. The Surface Scanner and Pumpjack remain the intended tools. The old 1/32 + 1/20 placement rolls are superseded by the central oil config.
- TFMG 1.2.0 already creates persistent reservoirs containing 1,000–10,000 reserve units and groups nearby deposit blocks into one reservoir. Its shipped Pumpjack never subtracts those units. `TFMGPumpjackFiniteReservoirMixin` completes that unfinished behavior by treating one reserve unit as one bucket, consuming fractional extraction statistically, saving every change, and stopping the Pumpjack at zero.
- Create Diesel Generators' Oil Scanner and Pumpjack parts are retired by their five exact construction recipe IDs. Its result-bearing `CDGEvents.oilAmount` hook also returns zero, so previously built or creative-mode CDG Pumpjacks cannot bypass finite reservoirs. CDG engines remain available and use TFMG diesel/gasoline; only its duplicate prospecting/extraction path is removed.

At the default TFMG setting, one reservoir therefore represents roughly 1–10 million mB of crude. The Industrial Reserve Core needs enough diesel that a player should develop and connect several fields rather than feed the entire pack from one permanent source.

Existing generated deposit blocks are not deleted. Once the updated companion mod is loaded, their persisted reservoirs become finite too. The regional worldgen rule applies only to newly generated chunks.
