# Mercury Expedition and Asteroid Freight Audit

Stage 12 extends the source-owned planetary route through Mercury and repairs
the installed Cosmonautics asteroid eligibility check. It does not deploy to
the live instance, edit the Draw.io design, add a locator/claim system, enable
prefabricated stations, or enable the tier-four rocket.

## Canonical Mercury route

Rocketnautics owns navigation node `mercury`, but its only linked survival
dimension is the Ad Astra surface `ad_astra:mercury`. The orbit dimension
`ad_astra:mercury_orbit` is deliberately not linked. The source override has
priority 2000, surface acceleration 3.7 m/s², radius 1,219,850, orbital period
145,600 seconds, and rotation period 2,930 seconds. The matching Sable physics
resource gives ships `[0, -3.7, 0]` gravity with zero pressure and drag while
Ad Astra remains responsible for player oxygen, temperature, sky, and time.

The physical route authority is
`industrial_colonies:mercury_navigation_computer`. Its block entity is a
Sable `BlockEntitySubLevelActor`, so authorization inspects real hardware on
the loaded moving ship rather than a quest, stage, inventory item, or global
flag.

## Manufacturing contract

The one authored route is
`industrial_colonies:planetary/mercury/navigation_computer`. It is a filled
5x5 Mechanical Crafting build in `CR02 — Mercury Expedition`:

```text
CPUPC
CEBEC
SNVNS
CEMEC
CPUPC
```

The symbols use Calorite Plates and Blocks, an Ultimate Control Circuit, AE2
Engineering Processors, TFMG Etched Circuit Boards, a Rocketnautics Sputnik,
the Simulated Navigation Table, the prior Venus Navigation Computer, and a
ComputerCraft Advanced Computer. Direct managed dependencies preserve the
Calorite Plate, Venus computer, and Sputnik manufacturing ancestry. No stock
recipe is removed for this new project-owned output.

## Fail-closed descent policy

The existing `DeepSpaceInstance` permission hook now manages the canonical
Mars, Venus, and Mercury surfaces. For each managed descent it rejects offline
tracked players, unloaded ships, an empty online-player or loaded-ship set,
players that cannot be associated with a loaded ship, and any occupied ship
that lacks the required live computer actor.

- Mercury accepts only a Mercury Navigation Computer on every occupied ship.
- Venus accepts a Venus or Mercury computer and still requires every player to
  wear all four correctly slotted `#ad_astra:heat_resistant_armor` pieces.
- Mars accepts a Mars, Venus, or Mercury computer.

This preserves earlier routes as ships are upgraded while preventing a Venus
computer, an item in inventory, or a quest completion from authorizing
Mercury.

## Installed asteroid contract and repair

The installed Cosmonautics target is `cosmonautics-26.08.307.jar`. Its asteroid
tick code computed eligibility from a dimension path equal to `space` or a
height above 5000, although the installed physical-station dimension is
`rocketnautics:deep_space`. The source mixin replaces that stored eligibility
boolean with the installed API's canonical
`DeepSpaceHelper.isDeepSpace(player.level())` result. It therefore fails
closed outside actual deep space and removes the unrelated high-altitude
bypass; it does not invoke the private spawn routine or create an extra spawn
loop.

The audited installed behavior remains unchanged after eligibility: moving
Sable asteroid bodies are approximately 6–13 blocks in radius, appear roughly
150–400 blocks away after the built-in eligibility interval, and use the
installed ore distribution (approximately 5% coal, 3% iron, 1% copper, 0.5%
gold, and 0.5% `rocketnautics:titanium_ore`). There is no installed asteroid
locator, claim, or miner API, so Stage 12 does not invent one. The stock
`rocketnautics:crushing/titanium_ore` route remains available, while the exact
`rocketnautics:splashing/crushed_raw_titanium` washing shortcut to Netherite
Scrap remains retired.

## Observation-only quest handoff

Planetary Industry now ends with four non-gating observations:

1. real arrival on `ad_astra:mercury` through
   `industrial_colonies:planetary/mercury_arrival`;
2. one returned `ad_astra:mercury_iron_ore` sample;
3. the first `rocketnautics:titanium_ore` recovered from an asteroid; and
4. a retained reserve of 64 Coal, Iron, and Copper Ore plus 32 Gold and
   Titanium Ore.

The sample is ordinary iron ancestry, not a new metallurgy. All tasks consume
nothing and grant no reward, stage, recipe, destination, claim, locator, or
spawn authority. The generated book totals 10 chapters, 113 quests, and 245
tasks: 231 item, 8 structure, and 6 advancement observations.

## Deferred expansion

Constructed station progression, Glacio, gas-giant extraction, tier-four
rockets, Cosmowarp, and solar-system escape remain disabled or unlinked for
later stages. Physical stations continue to use
`rocketnautics:deep_space`; no alternate station dimension was introduced.

## Verification

Run from the project root with the installed catalog and mod directory:

```powershell
python tools/validate_mercury_asteroid_slice.py `
  --catalog 'C:\path\to\recipe-catalog-current' `
  --mods 'C:\path\to\instance\mods' `
  --jar build/libs/industrial_colonies-0.4.0.jar
python tools/test_validate_mercury_asteroid_slice.py -v
python tools/test_validate_space_destination_bridge.py -v
python tools/test_validate_venus_calorite_slice.py -v
python tools/generate_ftbquests_native.py --check
python tools/validate_ftbquests_native.py
```

The focused validator pins the exact installed Cosmonautics and Ad Astra JARs,
the `AsteroidSpawner` and `DeepSpaceHelper` class hashes, source/runtime
resources, recipe and quest topology, candidate-JAR entries, and single-owner
Mercury link. Runtime deployment still requires the controlled client/world
acceptance checks in the deployment checklist.
