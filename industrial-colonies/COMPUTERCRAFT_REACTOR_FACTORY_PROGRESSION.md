# ComputerCraft and Reactor Factory Progression

## Outcome

CC:Tweaked's stone/redstone hardware shortcuts have been replaced with physical
factory recipes. Normal hardware uses the Brass recipe environment, advanced
digital hardware uses Weathered Iron, and reactor control/instrumentation uses
Refined Radiance. The recipes consume TFMG boards, AE2 printed circuits and
processors, Create mechanisms/casings, and late Mekanism electronics.

The focused validator now reads the actual managed manifest and compiled
KJSGen project, then scans every installed recipe JAR. It proves that the
editable factory cards own construction, exact removals own only the cheap
stock acquisitions, and no independent protected-output bypass survives.

## Removed stock acquisitions

The following 19 recipe IDs are removed explicitly:

- `computercraft:cable`
- `computercraft:computer_normal`
- `computercraft:computer_advanced`
- `computercraft:computer_advanced_upgrade`
- `computercraft:disk_drive`
- `computercraft:monitor_normal`
- `computercraft:monitor_advanced`
- `computercraft:pocket_computer_normal`
- `computercraft:pocket_computer_advanced`
- `computercraft:pocket_computer_advanced_upgrade`
- `computercraft:printer`
- `computercraft:redstone_relay`
- `computercraft:speaker`
- `computercraft:turtle_normal`
- `computercraft:turtle_advanced`
- `computercraft:turtle_advanced_upgrade`
- `computercraft:wired_modem`
- `computercraft:wireless_modem_normal`
- `computercraft:wireless_modem_advanced`

ComputerCraft's peripheral-attachment, turtle-tool, recolouring, overlay, and
full-block wired-modem conversion recipes remain. Those recipes transform an
already-built protected device and cannot bootstrap one. The full wired modem
is a closed conversion whose only producer consumes the protected wired modem.

## New ComputerCraft construction

| Tier | Recipe ID | Output | Physical form |
| --- | --- | --- | --- |
| Brass | `industrial_colonies:computercraft/network/cable` | 8× `computercraft:cable` | Sequenced insulated TFMG copper wire |
| Brass | `industrial_colonies:computercraft/network/wired_modem` | `computercraft:wired_modem` | Sequenced board and printed logic assembly |
| Brass | `industrial_colonies:computercraft/network/wireless_modem` | `computercraft:wireless_modem_normal` | Sequenced wired-modem radio conversion |
| Brass | `industrial_colonies:computercraft/computer/normal` | `computercraft:computer_normal` | 5×5 chassis |
| Brass | `industrial_colonies:computercraft/monitor/normal` | 2× `computercraft:monitor_normal` | 5×5 display-panel batch |
| Brass | `industrial_colonies:computercraft/io/disk_drive` | `computercraft:disk_drive` | 5×5 mechanism/chassis |
| Brass | `industrial_colonies:computercraft/io/printer` | `computercraft:printer` | 5×5 piston/chassis |
| Brass | `industrial_colonies:computercraft/io/speaker` | `computercraft:speaker` | Sequenced note-block electronics |
| Brass | `industrial_colonies:computercraft/io/redstone_relay` | `computercraft:redstone_relay` | Sequenced wired control relay |
| Brass | `industrial_colonies:computercraft/mobile/pocket_computer` | `computercraft:pocket_computer_normal` | 5×5 computer/radio/display integration |
| Brass | `industrial_colonies:computercraft/mobile/turtle` | `computercraft:turtle_normal` | 5×5 robotic chassis |
| Weathered Iron | `industrial_colonies:computercraft/network/advanced_wireless_modem` | `computercraft:wireless_modem_advanced` | Sequenced advanced radio |
| Weathered Iron | `industrial_colonies:computercraft/computer/advanced_upgrade` | `computercraft:computer_advanced` | Sequenced normal-computer rebuild |
| Weathered Iron | `industrial_colonies:computercraft/monitor/advanced` | `computercraft:monitor_advanced` | Sequenced colour-display rebuild |
| Weathered Iron | `industrial_colonies:computercraft/mobile/advanced_pocket_upgrade` | `computercraft:pocket_computer_advanced` | Sequenced mobile digital rebuild |
| Weathered Iron | `industrial_colonies:computercraft/mobile/advanced_turtle_upgrade` | `computercraft:turtle_advanced` | Sequenced robotic digital rebuild |

Every sequence uses its own owned unfinished item. This prevents an incomplete
cable or modem run from being inserted into an unrelated advanced-device line.

The primary KJSGen sequences create fresh hardware, because Create's sequenced
assembly serializer cannot copy ComputerCraft runtime components. Four closed
state-transfer recipes cover devices where that state matters. Each transfer
consumes both an already factory-built target device and the old source device,
then uses `computercraft:copy_components` to preserve IDs, labels, programs,
pocket upgrades, and turtle upgrades. Because the completed target is an input,
these transfers cannot bootstrap or bypass factory construction. The target
ingredient is also a strict NeoForge empty-component match: only a pristine,
newly manufactured shell is accepted. A labeled, running, fueled, upgraded, or
otherwise configured target cannot be consumed and silently lose its state.

| State transfer | Copies from | Requires completed target |
| --- | --- | --- |
| Advanced computer | Normal computer | Advanced computer |
| Base turtle | Normal computer | Base turtle |
| Advanced pocket computer | Normal pocket computer | Advanced pocket computer |
| Advanced turtle | Base turtle | Advanced turtle |

## Reactor control integration

| Recipe ID | Output | ComputerCraft requirement |
| --- | --- | --- |
| `industrial_colonies:machine/instrumentation/basic_reactor_controller` | `bigreactors:basic_reactorcontroller` | Advanced computer and four advanced monitors |
| `industrial_colonies:machine/instrumentation/basic_reactor_redstone_port` | `bigreactors:basic_reactorredstoneport` | Industrial redstone relay |
| `industrial_colonies:machine/instrumentation/basic_reactor_power_tap` | `bigreactors:basic_reactorpowertapfe_passive` | Refined Radiance instrumentation environment |
| `industrial_colonies:bigreactors/reprocessor/controller` | `bigreactors:reprocessorcontroller` | Two advanced computers and four advanced monitors |
| `industrial_colonies:machine/advanced_nuclear/reinforced_reactor_controller` | `bigreactors:reinforced_reactorcontroller` | Two advanced computers and four advanced monitors |
| `industrial_colonies:machine/advanced_nuclear/reinforced_computer_port` | `bigreactors:reinforced_reactorcomputerport` | Advanced computer plus wired modem |
| `industrial_colonies:machine/advanced_nuclear/reinforced_display_source` | `er2create:reinforced_reactordisplaysource` | Advanced monitor |

All seven use a Refined Radiance outer recipe type and explicitly consume a
Radiant Casing either directly or in the controller pattern. The original four
fuel/ingot controller shortcuts remain removed by their existing nuclear files.

## Validation

Run from the project root:

```powershell
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/validate_computercraft_reactor_progression.py --project . --node 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' --report 'C:\Users\GodPC\Documents\Codex\2026-08-16\ok\work\industrial-audit\COMPUTERCRAFT_REACTOR_PROGRESSION_VALIDATION.json' 'C:\Users\GodPC\curseforge\minecraft\Instances\All in one'
```

Current focused result:

- PASS: 19 cheap acquisitions removed.
- PASS: 16 Brass/Weathered Iron replacements present with required components.
- PASS: 10 unique closed intermediate items; no cross-sequence transitional reuse.
- PASS: 4 component-preserving state transfers consume a pristine completed
  target, reject configured target shells, and cannot bootstrap hardware.
- PASS: 34 installed peripheral, turtle-tool, overlay, recolouring, and
  full-modem transforms remain available.
- PASS: reactor controller and computer-port recipes still consume advanced
  ComputerCraft instrumentation.
- PASS: 226 JARs / 25,794 recipe definitions scanned; no independent
  protected-output bypass.

The dependency scan also records three reviewed, nonfatal malformed recipes
from the installed third-party
`pamhc2foodextended-NEOFORGE-1.21.1-1.0.0.jar`:

- `pamhc2foodextended:cookedtofabbititem_campfire`
- `pamhc2foodextended:cookedtofabbititem_forge`
- `pamhc2foodextended:cookedtofabbititem_smoker`

Their exact resources contain trailing JSON data and are unrelated to
ComputerCraft acquisition or Industrial Colonies. The validator allowlists
only those three JAR/resource pairs and their `Extra data` parse class;
project-owned or newly malformed resources remain fatal.
