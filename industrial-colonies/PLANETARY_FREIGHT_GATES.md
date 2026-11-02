# Planetary Freight Gates

The Moon is the first resource destination. Canonical Mars, Venus, and Mercury
descents are the next physical routes. Mars accepts a placed Mars, Venus, or
Mercury Navigation Computer; Venus accepts the Venus or Mercury computer plus
complete personal heat protection; Mercury requires its own
`industrial_colonies:mercury_navigation_computer` aboard every loaded ship
carrying an online player.

## Managed planetary descent

October 5 staged extension: the user approved offline-owner autonomy with
individual and global server-disable commands. Uncrewed managed descent now
requires an owned native AL transponder and the destination-tier physical
computer on **every** transferred loaded body. The registered owner may be
offline; tracked offline passengers and unloaded bodies still deny transfer.
An uncrewed Venus craft has no person to wear a suit; any online passenger
still invokes the occupied association and personal heat-protection gates.
This adds no thermal immunity. The signed Glacio boundary is unchanged.

Permission-level-4 `/icships disable ship <transponder-uuid>` and
`/icships disable all` stop AL automation and deny its restart and the orbital
ascent/managed descent gates. Corresponding `enable` commands clear only their
own restriction and never automatically launch a stopped route. `/icships list`
and `/icships status` expose identities and current restrictions. These controls
do not suspend whole-body physics or unrelated machine ticks. See
`../workflow/early-survival/autonomous-ships/README.md` for staged evidence and
limits; this is not production installation or full planetary-route acceptance.

`DeepSpaceInstanceMixin` modifies Rocketnautics' sole
`AllowedTransfer.allowToDimension()` result before the distance threshold and
before retirement begins. It deliberately does not cancel
`SpaceTransitionHandler.exitDeepSpace()`: that caller unconditionally marks
the deep-space instance as retiring after the call, so canceling the callee
would strand the instance.

For `ad_astra:mars`, `ad_astra:venus`, and `ad_astra:mercury`, authorization
fails closed when:

- any tracked player is offline;
- any tracked ship is unloaded;
- an online player cannot be associated with a loaded ship; or
- any loaded ship whose inflated Sable bounds contain a player lacks its
  physical route-computer actor.

Mercury accepts only its own physical computer. Venus additionally fails when
any associated player lacks a complete,
correctly slotted head/chest/legs/feet set from
`#ad_astra:heat_resistant_armor`. Later computers satisfy earlier routes, so
upgraded craft need not carry all three route computers.

Other destinations preserve Rocketnautics' original permission result.
The exact Cosmonautics 26.08.307 `DeepSpaceInstance` bytecode is pinned by the
focused validator. A sanitized compile-only mirror removes the mod's broken
Orekit javac service entry without modifying or replacing the runtime JAR.

## Ender Chest boundary

NeoForge's cancellable `PlayerInteractEvent.RightClickBlock` rejects Ender
Chest interaction in the authored Ad Astra surfaces/orbits, Rocketnautics deep
space, and the two legacy Moon/Mars keys. It does not apply to every
non-Overworld dimension, so terrestrial Nether and End gameplay remains
unchanged.

Dimension-change and container-open listeners close an already open Ender
Chest menu. This prevents a player from opening the inventory on Earth and
carrying the GUI through a transition. The event hook also avoids a direct
mixin collision with Particular's visual `EnderChestBlock` injection.

## Validation

Run:

```powershell
python tools/validate_planetary_freight_gates.py `
  --mods 'C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods' `
  --project-jar build/libs/industrial_colonies-0.4.0.jar
python -m unittest tools.test_validate_planetary_freight_gates
python tools/validate_mercury_asteroid_slice.py `
  --catalog 'C:\path\to\recipe-catalog-current' `
  --mods 'C:\path\to\instance\mods' `
  --jar build/libs/industrial_colonies-0.4.0.jar
python -m unittest tools.test_validate_mercury_asteroid_slice
```

Runtime acceptance must exercise Overworld Ender Chest access, every managed
offworld denial, Moon descent without a route computer, Mars denial with no
computer or only one of two occupied ships equipped, successful Mars descent
with either approved computer on every occupied ship, Venus denial for absent
hardware or any missing/mis-slotted armor piece, successful Venus descent, and
Mercury denial with no computer, with a Venus computer, or with only one of two
occupied ships equipped; successful Mercury descent requires a Mercury
computer on every occupied ship. Every route must revoke immediately after
required hardware or armor is removed.
