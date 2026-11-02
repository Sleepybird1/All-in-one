"""Curated heavy-manufacturing coverage for Create Big Cannons and CBC AT.

This module deliberately leaves cannon material conversion, dynamic casting,
boring recipes, ammunition variants, and decorative blocks source-owned.  It
instead replaces the inexpensive hand-crafts around the cannon foundry,
builder/drill/loader equipment, mounts, loading tools, and serviceable breech
hardware.  Heavy machines are assembled on the Railway steelworking line;
large structures use readable physical silhouettes rather than filled 5x5
rings.

``apply`` is idempotent and mutates only the seed dictionary supplied by its
caller.  Importing this module performs no file, registry, build, test, or
deployment work.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any


Recipe = dict[str, Any]

RAILWAY_DEPLOYER = "createcasing:railway_deployer"
RAILWAY_PRESS = "createcasing:railway_press"
RAILWAY_SAW = "createcasing:railway_mechanical_saw"
RAILWAY_MIXER = "createcasing:railway_mixer"

_COUNTED_ITEM = re.compile(r"^\s*\d+x\s+(.+?)\s*$")


def _item_id(value: Any) -> str | None:
    if isinstance(value, str):
        match = _COUNTED_ITEM.fullmatch(value)
        return match.group(1) if match else value.strip()
    if isinstance(value, dict) and value.get("kind", "ITEM") == "ITEM":
        item_id = value.get("id") or value.get("item")
        return item_id if isinstance(item_id, str) else None
    return None


def _deploy(ingredient: str) -> dict[str, str]:
    return {
        "op": "deploying",
        "ingredient": ingredient,
        "machine": RAILWAY_DEPLOYER,
    }


def _press() -> dict[str, str]:
    return {"op": "pressing", "machine": RAILWAY_PRESS}


def _cut() -> dict[str, str]:
    return {"op": "cutting", "machine": RAILWAY_SAW}


def _assembly_steps(*ingredients: str) -> list[dict[str, str]]:
    return [_deploy(ingredient) for ingredient in ingredients] + [_press()]


def _sequence(
    recipe_id: str,
    *,
    node: str,
    order: int,
    comment: str,
    input_item: str,
    output: str,
    remove: list[str],
    steps: list[dict[str, str]],
    transitional: str | None = None,
    loops: int = 1,
) -> Recipe:
    return {
        "id": recipe_id,
        "phase": "Steel & Petroleum",
        "node": node,
        "order": order,
        "type": "sequenced_assembly",
        "comment": comment,
        "input": input_item,
        "transitional": transitional or input_item,
        "output": output,
        "loops": loops,
        "steps": steps,
        "remove": remove,
        "exclusive_output": True,
    }


def _grid(
    recipe_id: str,
    *,
    node: str,
    order: int,
    comment: str,
    pattern: list[str],
    key: dict[str, str],
    output: str,
    remove: list[str],
    mechanical: bool = True,
) -> Recipe:
    if not pattern or any(len(row) != len(pattern[0]) for row in pattern):
        raise ValueError(f"non-rectangular pattern for {recipe_id}: {pattern!r}")
    return {
        "id": recipe_id,
        "phase": "Steel & Petroleum",
        "node": node,
        "order": order,
        "type": "mechanical_crafting" if mechanical else "shaped",
        "comment": comment,
        "pattern": pattern,
        "key": key,
        "output": output,
        "remove": remove,
        "exclusive_output": True,
    }


def _recipes() -> list[Recipe]:
    return [
        # Foundry consumable and heat-service lid.  The actual CBC casting and
        # boring recipes remain untouched and therefore remain mandatory.
        {
            "id": "industrial_colonies:big_cannons/casting_sand_batch",
            "phase": "Steel & Petroleum",
            "node": "CR01 — Blast Furnace",
            "order": 360,
            "type": "mixing",
            "comment": (
                "Condition sand with clay binder, graded gravel, and water in "
                "the Railway foundry mixer instead of hand-combining one moulding charge"
            ),
            "machine": RAILWAY_MIXER,
            "inputs": [
                "4x minecraft:sand",
                "2x minecraft:clay_ball",
                "2x minecraft:gravel",
                {"kind": "FLUID", "id": "minecraft:water", "amount": 250},
            ],
            "output": "8x createbigcannons:casting_sand",
            "heat": "none",
            "remove": ["createbigcannons:casting_sand"],
            "exclusive_output": True,
        },
        _grid(
            "industrial_colonies:big_cannons/basin_foundry_lid",
            node="CR01 — Blast Furnace",
            order=361,
            comment=(
                "Lay out a refractory foundry hood with a heavy top plate, "
                "cast-iron cheeks, and a valved steel exhaust manifold"
            ),
            pattern=[" H ", "CFC", "PVP"],
            key={
                "H": "tfmg:heavy_plate",
                "C": "tfmg:cast_iron_sheet",
                "F": "tfmg:fireproof_bricks",
                "P": "tfmg:steel_pipe",
                "V": "tfmg:steel_fluid_valve",
            },
            output="createbigcannons:basin_foundry_lid",
            remove=["createbigcannons:basin_foundry_lid"],
        ),
        # Loading heads stay understandable hand tools, while their long rods
        # require Create extension poles rather than ordinary sticks.
        _grid(
            "industrial_colonies:big_cannons/ram_head",
            node="CR01 — The Steel Age",
            order=366,
            comment=(
                "Laminate a broad hardened-wood ram face around a sturdy backing plate"
            ),
            pattern=["   ", "HHH", "HSH"],
            key={"H": "tfmg:hardened_planks", "S": "create:sturdy_sheet"},
            output="createbigcannons:ram_head",
            remove=["createbigcannons:ram_head"],
            mechanical=False,
        ),
        _grid(
            "industrial_colonies:big_cannons/ram_rod",
            node="CR01 — The Steel Age",
            order=367,
            comment=(
                "Build a full-length ram from its padded head and two rigid piston poles"
            ),
            pattern=[" R ", " P ", " P "],
            key={
                "R": "createbigcannons:ram_head",
                "P": "create:piston_extension_pole",
            },
            output="createbigcannons:ram_rod",
            remove=["createbigcannons:ram_rod"],
            mechanical=False,
        ),
        _grid(
            "industrial_colonies:big_cannons/worm_head",
            node="CR01 — The Steel Age",
            order=368,
            comment=(
                "Form the powder worm as opposed iron hooks pinned to a sturdy socket"
            ),
            pattern=["   ", "IBI", " S "],
            key={
                "I": "minecraft:iron_bars",
                "B": "tfmg:screw",
                "S": "create:sturdy_sheet",
            },
            output="createbigcannons:worm_head",
            remove=["createbigcannons:worm_head"],
            mechanical=False,
        ),
        _grid(
            "industrial_colonies:big_cannons/worm",
            node="CR01 — The Steel Age",
            order=369,
            comment=(
                "Fit the powder-worm head to a reusable two-pole service shaft"
            ),
            pattern=[" W ", " P ", " P "],
            key={
                "W": "createbigcannons:worm_head",
                "P": "create:piston_extension_pole",
            },
            output="createbigcannons:worm",
            remove=["createbigcannons:worm"],
            mechanical=False,
        ),
        # Railway heavy-machine line.
        _sequence(
            "industrial_colonies:big_cannons/cannon_builder",
            node="CR01 — The Steel Age",
            order=370,
            comment=(
                "Equip a heavy casing with a geared steel drive, guided extension pole, "
                "forming plate, and service fasteners on the Railway assembly line"
            ),
            input_item="tfmg:heavy_machinery_casing",
            output="createbigcannons:cannon_builder",
            remove=["createbigcannons:cannon_builder"],
            steps=_assembly_steps(
                "tfmg:steel_mechanism",
                "create:piston_extension_pole",
                "tfmg:large_steel_cogwheel",
                "tfmg:heavy_plate",
                "tfmg:screw",
            ),
        ),
        _sequence(
            "industrial_colonies:big_cannons/cannon_drill",
            node="CR01 — The Steel Age",
            order=371,
            comment=(
                "Turn a heavy casing into the cannon borer with a Railway drill "
                "head, coolant pipes, long feed screw, reduction gear, and fasteners"
            ),
            input_item="tfmg:heavy_machinery_casing",
            output="createbigcannons:cannon_drill",
            remove=["createbigcannons:cannon_drill"],
            steps=_assembly_steps(
                "createcasing:railway_mechanical_drill",
                "2x tfmg:steel_pipe",
                "create:piston_extension_pole",
                "tfmg:large_steel_cogwheel",
                "tfmg:screw",
            ),
        ),
        _sequence(
            "industrial_colonies:big_cannons/cannon_welder",
            node="CR01 — The Steel Age",
            order=372,
            comment=(
                "Convert a Blaze Burner into a mobile pressure welder with a TFMG propane "
                "cylinder, steel lance, brass control valve, copper lead, and heat shield"
            ),
            input_item="create:blaze_burner",
            output="createbigcannons:cannon_welder",
            remove=[
                "createbigcannons:cannon_welder",
                "minecraft:cannon_welder_mirrored",
            ],
            steps=_assembly_steps(
                "tfmg:propane_bucket",
                "tfmg:steel_pipe",
                "tfmg:brass_fluid_valve",
                "tfmg:copper_wire",
                "tfmg:heavy_plate",
            ),
        ),
        _sequence(
            "industrial_colonies:big_cannons/cannon_loader",
            node="CR01 — The Steel Age",
            order=373,
            comment=(
                "Build the powered loading stroke around a mechanical piston, guided pole, "
                "recoil spring, steel drive mechanism, and service fasteners"
            ),
            input_item="tfmg:steel_casing",
            output="createbigcannons:cannon_loader",
            remove=["createbigcannons:cannon_loader"],
            steps=_assembly_steps(
                "create:mechanical_piston",
                "create:piston_extension_pole",
                "createbigcannons:recoil_spring",
                "tfmg:steel_mechanism",
                "tfmg:screw",
            ),
        ),
        # Traversing hardware and mobile carriage structures.
        _grid(
            "industrial_colonies:big_cannons/fixed_cannon_mount",
            node="CR01 — The Steel Age",
            order=380,
            comment=(
                "Set a vertical trunnion shaft into a steel housing between heavy cheeks "
                "and a three-plate reinforced foundation"
            ),
            pattern=[" S ", "HCH", "PPP"],
            key={
                "S": "create:shaft",
                "H": "tfmg:heavy_plate",
                "C": "tfmg:steel_casing",
                "P": "create:sturdy_sheet",
            },
            output="createbigcannons:fixed_cannon_mount",
            remove=["createbigcannons:fixed_cannon_mount"],
        ),
        _grid(
            "industrial_colonies:big_cannons/cannon_mount",
            node="CR01 — Advanced Metallurgy",
            order=381,
            comment=(
                "Upgrade a fixed pedestal into a powered traverse mount with a turntable, "
                "opposed large steel gears, a heavy drive housing, and braced trunnions"
            ),
            pattern=["STS", "GHG", "PFP"],
            key={
                "S": "create:sturdy_sheet",
                "T": "create:turntable",
                "G": "tfmg:large_steel_cogwheel",
                "H": "tfmg:heavy_machinery_casing",
                "P": "tfmg:heavy_plate",
                "F": "createbigcannons:fixed_cannon_mount",
            },
            output="createbigcannons:cannon_mount",
            remove=["createbigcannons:cannon_mount"],
        ),
        _sequence(
            "industrial_colonies:big_cannons/cannon_mount_extension",
            node="CR01 — Advanced Metallurgy",
            order=382,
            comment=(
                "Extend the traverse drive from a Railway gearbox using opposed "
                "shafts, a steel housing, bearing plate, and locked fasteners"
            ),
            input_item="createcasing:railway_gearbox",
            output="createbigcannons:cannon_mount_extension",
            remove=["createbigcannons:cannon_mount_extension"],
            steps=_assembly_steps(
                "2x create:shaft",
                "tfmg:steel_casing",
                "tfmg:heavy_plate",
                "tfmg:screw",
            ),
        ),
        _grid(
            "industrial_colonies:big_cannons/cannon_wheel_batch",
            node="CR01 — The Steel Age",
            order=383,
            comment=(
                "Build two matched wheel pairs from cast-iron rim plates, hardened wooden "
                "spokes, and a common steel axle"
            ),
            pattern=[" C ", "HPH", " C "],
            key={
                "C": "tfmg:cast_iron_sheet",
                "H": "tfmg:hardened_planks",
                "P": "create:shaft",
            },
            output="2x createbigcannons:pair_of_cannon_wheels",
            remove=["createbigcannons:pair_of_cannon_wheels"],
        ),
        _grid(
            "industrial_colonies:big_cannons/cannon_carriage",
            node="CR01 — The Steel Age",
            order=384,
            comment=(
                "Lay out the wooden gun cradle over plated axle cheeks and two completed "
                "wheel pairs instead of assembling the carriage from loose planks"
            ),
            pattern=[" H ", "PHP", "WSW"],
            key={
                "H": "tfmg:hardened_planks",
                "P": "tfmg:heavy_plate",
                "S": "create:shaft",
                "W": "createbigcannons:pair_of_cannon_wheels",
            },
            output="createbigcannons:cannon_carriage",
            remove=["createbigcannons:cannon_carriage"],
        ),
        # Serviceable breech and recoil mechanisms.  These deliberately use no
        # processor clutter: their difficulty comes from steelworking geometry.
        {
            "id": "industrial_colonies:big_cannons/spring_wire_batch",
            "phase": "Steel & Petroleum",
            "node": "CR01 — Advanced Metallurgy",
            "order": 389,
            "type": "compacting",
            "comment": (
                "Draw one TFMG steel ingot into three matched spring-wire coils on the "
                "Railway press, closing the cheaper iron-plate recoil-spring bypass"
            ),
            "machine": RAILWAY_PRESS,
            "inputs": ["tfmg:steel_ingot"],
            "output": "3x createbigcannons:spring_wire",
            "heat": "none",
            "remove": [
                "createbigcannons:cutting/spring_wire_iron",
                "createbigcannons:cutting/spring_wire_steel",
            ],
            "exclusive_output": True,
        },
        _sequence(
            "industrial_colonies:big_cannons/recoil_spring",
            node="CR01 — Advanced Metallurgy",
            order=390,
            comment=(
                "Progressively coil spring wire through three Railway press strokes; the "
                "repetition represents forming, not unrelated ingredient padding"
            ),
            input_item="createbigcannons:spring_wire",
            transitional="createbigcannons:partial_recoil_spring",
            output="createbigcannons:recoil_spring",
            loops=3,
            steps=[_press()],
            remove=["createbigcannons:sequenced_assembly/recoil_spring"],
        ),
        _sequence(
            "industrial_colonies:big_cannons/quickfiring_mechanism",
            node="CR01 — Advanced Metallurgy",
            order=391,
            comment=(
                "Populate a steel mechanism with its large drive gear, timing pinion, "
                "return spring, precision cam, and manual selector"
            ),
            input_item="tfmg:steel_mechanism",
            output="createbigcannons:quickfiring_mechanism",
            remove=["createbigcannons:quickfiring_mechanism"],
            steps=_assembly_steps(
                "tfmg:large_steel_cogwheel",
                "tfmg:steel_cogwheel",
                "createbigcannons:recoil_spring",
                "create:precision_mechanism",
                "minecraft:lever",
            ),
        ),
        _sequence(
            "industrial_colonies:big_cannons/steel_sliding_breechblock",
            node="CR01 — Advanced Metallurgy",
            order=392,
            comment=(
                "Machine a solid TFMG steel block into a sliding breech with opposed rack "
                "gears, return spring, wear plate, and pinned service fastener"
            ),
            input_item="tfmg:steel_block",
            output="createbigcannons:steel_sliding_breechblock",
            remove=["createbigcannons:steel_sliding_breechblock"],
            steps=_assembly_steps(
                "2x tfmg:steel_cogwheel",
                "createbigcannons:recoil_spring",
                "tfmg:heavy_plate",
                "tfmg:screw",
            ),
        ),
        _sequence(
            "industrial_colonies:big_cannons/steel_screw_lock",
            node="CR01 — Advanced Metallurgy",
            order=393,
            comment=(
                "Turn a steel pipe blank into a screw-lock housing with its axial shaft, "
                "large thread gear, steel mechanism, and retaining screws"
            ),
            input_item="tfmg:steel_pipe",
            output="createbigcannons:steel_screw_lock",
            remove=["createbigcannons:steel_screw_lock"],
            steps=_assembly_steps(
                "create:shaft",
                "tfmg:large_steel_cogwheel",
                "tfmg:steel_mechanism",
                "tfmg:screw",
            ),
        ),
        _sequence(
            "industrial_colonies:big_cannons/steel_breech_extractor",
            node="CR01 — Advanced Metallurgy",
            order=394,
            comment=(
                "Saw the extractor hook from TFMG steel, pin its pivot, and press-calibrate "
                "the profile twice on the Railway precision line"
            ),
            input_item="tfmg:steel_ingot",
            transitional="createbigcannons:partial_steel_autocannon_breech_extractor",
            output="createbigcannons:steel_autocannon_breech_extractor",
            loops=2,
            steps=[_cut(), _deploy("tfmg:screw"), _press()],
            remove=[
                "createbigcannons:sequenced_assembly/steel_autocannon_breech_extractor"
            ],
        ),
        # Ammunition logistics only; individual shell and colour/type variants
        # stay with CBC so this does not create a sprawling duplicate recipe set.
        _grid(
            "industrial_colonies:big_cannons/autocannon_ammo_container",
            node="CR01 — Advanced Metallurgy",
            order=400,
            comment=(
                "Fold a cast-iron cartridge box around a brass feed throat and a stock "
                "sensor, leaving the centre open as the ammunition well"
            ),
            pattern=["BCB", "H H", "HHH"],
            key={
                "B": "create:brass_sheet",
                "C": "create:content_observer",
                "H": "tfmg:cast_iron_sheet",
            },
            output="createbigcannons:autocannon_ammo_container",
            remove=["createbigcannons:autocannon_ammo_container"],
        ),
        _grid(
            "industrial_colonies:big_cannons/heavy_autocannon_ammo_box",
            node="CR01 — Advanced Metallurgy",
            order=401,
            comment=(
                "Build the CBC heavy-ammunition box around an item-vault magazine with a "
                "sensed brass feed throat and a fully plated impact shell"
            ),
            pattern=["BCB", "HVH", "HHH"],
            key={
                "B": "create:brass_sheet",
                "C": "create:content_observer",
                "H": "tfmg:heavy_plate",
                "V": "create:item_vault",
            },
            output="cbc_at:heavy_autocannon_ammo_box",
            remove=[
                "cbc_at:munition/heavy_autocannon_munition/heavy_autocannon_ammo_box"
            ],
        ),
    ]


def _assert_unclaimed(data: dict[str, Any], additions: list[Recipe]) -> None:
    addition_ids = {recipe["id"] for recipe in additions}
    if len(addition_ids) != len(additions):
        raise ValueError("Big Cannons coverage contains duplicate managed recipe IDs")

    wanted_outputs: dict[str, str] = {}
    wanted_removals: dict[str, str] = {}
    for recipe in additions:
        output = _item_id(recipe.get("output"))
        if output is None:
            raise ValueError(f"{recipe['id']} does not declare a concrete item output")
        if output in wanted_outputs:
            raise ValueError(
                f"Big Cannons output {output} is claimed by both "
                f"{wanted_outputs[output]} and {recipe['id']}"
            )
        wanted_outputs[output] = recipe["id"]
        for removal in recipe.get("remove", []):
            if removal in wanted_removals:
                raise ValueError(
                    f"Big Cannons stock recipe {removal} is claimed by both "
                    f"{wanted_removals[removal]} and {recipe['id']}"
                )
            wanted_removals[removal] = recipe["id"]

    for existing in data.get("recipes", []):
        if not isinstance(existing, dict):
            raise TypeError("managed recipe entries must be objects")
        if existing.get("id") in addition_ids:
            continue
        output = _item_id(existing.get("output"))
        if output in wanted_outputs:
            raise ValueError(
                f"{wanted_outputs[output]} cannot claim {output}; it is already "
                f"managed by {existing.get('id')}"
            )
        for removal in existing.get("remove", []):
            if removal in wanted_removals:
                raise ValueError(
                    f"{wanted_removals[removal]} cannot remove {removal}; it is "
                    f"already owned by {existing.get('id')}"
                )

    globally_removed = set(data.get("additional_removals", []))
    overlap = sorted(globally_removed.intersection(wanted_removals))
    if overlap:
        raise ValueError(
            f"Big Cannons coverage removals are already globally claimed: {overlap}"
        )

    preserved = set(data.get("preserve_recipe_ids", []))
    overlap = sorted(preserved.intersection(wanted_removals))
    if overlap:
        raise ValueError(
            f"Big Cannons coverage cannot remove preserved stock recipes: {overlap}"
        )


def _upsert(data: dict[str, Any], recipe: Recipe) -> None:
    recipes = data.setdefault("recipes", [])
    if not isinstance(recipes, list):
        raise TypeError("managed seed field 'recipes' must be a list")
    matches = [
        index
        for index, existing in enumerate(recipes)
        if isinstance(existing, dict) and existing.get("id") == recipe["id"]
    ]
    if len(matches) > 1:
        raise ValueError(f"managed recipe is duplicated: {recipe['id']}")
    if matches:
        recipes[matches[0]] = deepcopy(recipe)
    else:
        recipes.append(deepcopy(recipe))


def apply(data: dict[str, Any]) -> None:
    """Apply the audited Create Big Cannons/CBC heavy-industry wave in place."""

    additions = _recipes()
    _assert_unclaimed(data, additions)
    for recipe in additions:
        _upsert(data, recipe)
