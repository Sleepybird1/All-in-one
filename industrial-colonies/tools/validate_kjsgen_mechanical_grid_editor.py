#!/usr/bin/env python3
"""Validate the KJSGen 2.0.5 expandable mechanical-crafting canvas bridge."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KJSGEN = ROOT / "libs" / "kjsgen-neoforge-2.0.5+mc1.21.1.jar"
LAYOUT = "assets/kjsgen/kjsgen_layouts/create_mechanical_crafting.json"
MODEL_CLASS = "com/zizazr/kjsgen/core/CreateSpecialModel.class"
CODEGEN_CLASS = "com/zizazr/kjsgen/codegen/handlers/CreateMechanicalCraftingCodegen.class"
HELPER = ROOT / "src/main/java/dev/godpc/industrialcolonies/KjsGenMechanicalGrid.java"
MIXIN = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/KjsGenMechanicalGridMixin.java"
MIXIN_CONFIG = ROOT / "src/main/resources/industrial_colonies.mixins.json"
LANG = ROOT / "src/main/resources/assets/industrial_colonies/lang/en_us.json"
INTEGRATION = ROOT / "src/main/java/dev/godpc/industrialcolonies/KjsGenIntegration.java"


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def contains_all(source: str, tokens: tuple[str, ...], label: str, errors: list[str]) -> None:
    for token in tokens:
        require(token in source, f"{label} is missing {token!r}", errors)


def resize_strip_geometry(
    canvas: tuple[int, int, int, int],
    grid_origin: tuple[int, int],
    columns: int,
    rows: int,
) -> tuple[int, int, list[int]] | None:
    """Mirror the mixin's geometry for small-grid and compact-canvas checks."""
    canvas_x, canvas_y, canvas_w, canvas_h = canvas
    grid_x, grid_y = grid_origin
    button_w = 16
    button_h = 18
    pair_gap = 2
    group_gap = 6
    strip_w = button_w * 4 + pair_gap * 2 + group_gap

    if canvas_w < strip_w + 2:
        return None

    diagram_w = columns * 18 + 54
    desired_x = grid_x + (diagram_w - strip_w) // 2
    minimum_x = canvas_x + 1
    maximum_x = canvas_x + canvas_w - strip_w - 1
    strip_x = max(minimum_x, min(desired_x, maximum_x))

    minimum_y = canvas_y + 1
    maximum_y = canvas_y + canvas_h - button_h - 1
    below = grid_y + rows * 18 + 2
    above = grid_y - button_h - 2
    if below <= maximum_y:
        strip_y = below
    elif above >= minimum_y:
        strip_y = above
    else:
        return None

    xs = [
        strip_x,
        strip_x + button_w + pair_gap,
        strip_x + button_w * 2 + pair_gap + group_gap,
        strip_x + button_w * 3 + pair_gap * 2 + group_gap,
    ]
    return strip_x, strip_y, xs


def native_grid_origin(
    canvas: tuple[int, int, int, int], columns: int, rows: int
) -> tuple[int, int]:
    """Mirror KJSGen's centered grid origin (including its four-pixel floor)."""
    canvas_x, canvas_y, canvas_w, canvas_h = canvas
    return (
        canvas_x + max(4, (canvas_w - (18 * columns + 54)) // 2),
        canvas_y + max(4, (canvas_h - 18 * rows) // 2),
    )


def intersects(
    first: tuple[int, int, int, int], second: tuple[int, int, int, int]
) -> bool:
    ax, ay, aw, ah = first
    bx, by, bw, bh = second
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def main() -> int:
    errors: list[str] = []
    require(KJSGEN.is_file(), f"missing exact KJSGen dependency: {KJSGEN}", errors)
    if errors:
        return fail(errors)

    with zipfile.ZipFile(KJSGEN) as archive:
        names = set(archive.namelist())
        for entry in (LAYOUT, MODEL_CLASS, CODEGEN_CLASS):
            require(entry in names, f"KJSGen jar is missing {entry}", errors)
        if errors:
            return fail(errors)

        layout = json.loads(archive.read(LAYOUT))
        model = archive.read(MODEL_CLASS)
        codegen = archive.read(CODEGEN_CLASS)

    require(layout.get("id") == "kjsgen:create_mechanical_crafting", "wrong grid layout ID", errors)
    require(layout.get("editorKind") == "grid", "mechanical crafting is not the native grid editor", errors)
    require(layout.get("codegen") == "kjsgen:create_mechanical_crafting", "native grid codegen changed", errors)
    parameters = {entry.get("key"): entry for entry in layout.get("parameters", [])}
    for key in ("gridW", "gridH"):
        require(parameters.get(key, {}).get("type") == "INT", f"{key} is not an INT parameter", errors)
        require(parameters.get(key, {}).get("default") == "3", f"{key} default is not 3", errors)

    # These constants/method names are direct evidence from the exact 2.0.5
    # classes that its persistence and codegen layers are already dynamic.
    for token in (b"GRID_MAX", b"gridW", b"gridH", b"cell_"):
        require(token in model, f"KJSGen CreateSpecialModel lacks {token!r}", errors)
    require(
        b"event.recipes.create.mechanical_crafting(" in codegen,
        "KJSGen native mechanical-crafting generator is missing its KubeJS call",
        errors,
    )

    helper = HELPER.read_text(encoding="utf-8")
    mixin = MIXIN.read_text(encoding="utf-8")
    integration = INTEGRATION.read_text(encoding="utf-8")
    mixin_config = json.loads(MIXIN_CONFIG.read_text(encoding="utf-8"))
    lang = json.loads(LANG.read_text(encoding="utf-8"))

    contains_all(
        helper,
        (
            'WIDTH_PARAMETER = "gridW"',
            'HEIGHT_PARAMETER = "gridH"',
            "GRID_POLICY_MAX = 7",
            '"grid".equals(type.editorKind())',
            '"mechanical_crafting".equals(family.id())',
            "CreateSpecialModel.GRID_MAX",
            "return Math.min(GRID_POLICY_MAX, CreateSpecialModel.GRID_MAX)",
            "recipe.setParam(parameter, Integer.toString(current + 1))",
            "recipe.setParam(parameter, Integer.toString(current - 1))",
            "if (current <= 1)",
            "removeColumn",
            "removeRow",
        ),
        "grid model adapter",
        errors,
    )
    require("setSlot(" not in helper, "growing the grid must not rewrite or discard cells", errors)

    contains_all(
        mixin,
        (
            '@Inject(method = "drawGridCanvas", at = @At("TAIL"))',
            '@Inject(method = "clickGridCanvas", at = @At("HEAD"), cancellable = true)',
            "industrialColonies$drawResizeButton(graphics, x, controlsY, hovered, false)",
            "industrialColonies$drawResizeButton(graphics, x, controlsY, hovered, true)",
            "KjsGenMechanicalGrid.addColumn(recipe, type)",
            "KjsGenMechanicalGrid.addRow(recipe, type)",
            "KjsGenMechanicalGrid.removeColumn(recipe, type)",
            "KjsGenMechanicalGrid.removeRow(recipe, type)",
            "KjsGenMechanicalGrid.maximumSize()",
            "industrialColonies$controlsFit()",
            "markDirty()",
            "rebuildWidgets()",
        ),
        "grid canvas mixin",
        errors,
    )
    require("setSlot(" not in mixin, "canvas controls must not rewrite or discard recipe cells", errors)
    require(
        "canvasBoxX + canvasBoxW - industrialColonies$STRIP_WIDTH - 1" in mixin,
        "the resize strip must be horizontally clamped inside KJSGen's clickable canvas",
        errors,
    )
    require(
        "canvasBoxY + canvasBoxH - industrialColonies$CONTROL_HEIGHT - 1" in mixin,
        "the resize strip must be vertically clamped inside KJSGen's clickable canvas",
        errors,
    )
    require(
        "gridRows * industrialColonies$GRID_CELL_SIZE" in mixin
        and "if (below <= maximum)" in mixin
        and "if (above >= minimum)" in mixin,
        "the resize strip must prefer below-grid placement and fall back above tall grids",
        errors,
    )
    require(
        mixin.count("if (!industrialColonies$controlsFit())") >= 2
        and "canvasBoxW < industrialColonies$STRIP_WIDTH + 2" in mixin
        and "return below <= maximum || above >= minimum;" in mixin,
        "draw and click paths must both suppress controls when no safe strip fits",
        errors,
    )

    # Coordinate regressions use KJSGen's exact centered origin. Every visible
    # control must stay inside the click canvas and avoid cells, arrow, output,
    # and the other controls. Both one- and two-row cases guard the original
    # right-side-arrow collision.
    geometry_cases = tuple(
        (f"normal {size}x{size}", (0, 0, 258, 242), size, size)
        for size in (1, 2, 3, 5, 9)
    ) + tuple(
        (f"compact {size}x{size}", (0, 0, 182, 146), size, size)
        for size in (1, 2, 3, 5)
    ) + (("compact-boundary 5x5", (0, 0, 176, 132), 5, 5),)
    for label, canvas, columns, rows in geometry_cases:
        origin = native_grid_origin(canvas, columns, rows)
        geometry = resize_strip_geometry(canvas, origin, columns, rows)
        require(geometry is not None, f"{label} unexpectedly has no safe control strip", errors)
        if geometry is None:
            continue
        strip_x, strip_y, control_xs = geometry
        canvas_x, canvas_y, canvas_w, canvas_h = canvas
        grid_x, grid_y = origin
        grid_bottom = grid_y + rows * 18
        require(strip_x >= canvas_x + 1, f"{label} strip escapes canvas left", errors)
        require(strip_x + 74 <= canvas_x + canvas_w - 1, f"{label} strip escapes canvas right", errors)
        require(strip_y >= canvas_y + 1, f"{label} strip escapes canvas top", errors)
        require(strip_y + 18 <= canvas_y + canvas_h - 1, f"{label} strip escapes canvas bottom", errors)
        require(
            all(control_xs[index] + 16 <= control_xs[index + 1] for index in range(3)),
            f"{label} controls overlap each other",
            errors,
        )
        require(
            strip_y >= grid_bottom + 2 or strip_y + 18 <= grid_y - 2,
            f"{label} strip overlaps the grid",
            errors,
        )

        grid_rect = (grid_x, grid_y, columns * 18, rows * 18)
        vertical_center = grid_y + rows * 9
        arrow_rect = (grid_x + columns * 18 + 6, vertical_center - 5, 23, 10)
        output_rect = (grid_x + columns * 18 + 36, vertical_center - 9, 18, 18)
        controls = [(x, strip_y, 16, 18) for x in control_xs]
        for index, control in enumerate(controls):
            require(not intersects(control, grid_rect), f"{label} control {index} covers a cell", errors)
            require(not intersects(control, arrow_rect), f"{label} control {index} covers the arrow", errors)
            require(not intersects(control, output_rect), f"{label} control {index} covers output", errors)
            for other in controls[index + 1 :]:
                require(not intersects(control, other), f"{label} controls intersect", errors)

    no_fit_cases = (
        ("compact 5x5 no-fit", (0, 0, 176, 110), 5, 5),
        ("compact 9x9 no-fit", (0, 0, 182, 146), 9, 9),
        ("too-narrow 1x1", (0, 0, 75, 100), 1, 1),
    )
    for label, canvas, columns, rows in no_fit_cases:
        origin = native_grid_origin(canvas, columns, rows)
        require(
            resize_strip_geometry(canvas, origin, columns, rows) is None,
            f"{label} should suppress controls instead of covering native UI",
            errors,
        )
    require(
        "KjsGenMechanicalGridMixin" in mixin_config.get("client", []),
        "grid canvas mixin is not registered as client-only",
        errors,
    )

    for key in (
        "industrial_colonies.kjsgen.mechanical_grid.add_column",
        "industrial_colonies.kjsgen.mechanical_grid.add_row",
        "industrial_colonies.kjsgen.mechanical_grid.remove_column",
        "industrial_colonies.kjsgen.mechanical_grid.remove_row",
    ):
        require(bool(lang.get(key)), f"missing tooltip translation {key}", errors)

    # Old tier-specific cards must retain the specialized native generator;
    # this is the existing migration path for pre-machine-centric projects.
    contains_all(
        integration,
        (
            "LEGACY_MECHANICAL_CODEGEN",
            "new CreateMechanicalCraftingCodegen()",
            '"event.recipes.create.mechanical_crafting"',
            "register.accept(copy(processDefinition",
        ),
        "legacy mechanical-crafting migration",
        errors,
    )

    if errors:
        return fail(errors)

    print(
        "PASS: KJSGen mechanical crafting has independent -/+ column and row controls, "
        "retains native 1-9 grid codegen, preserves hidden cell slots, and keeps legacy cards loadable."
    )
    return 0


def fail(errors: list[str]) -> int:
    print("FAIL: KJSGen expandable mechanical-crafting grid")
    for error in errors:
        print(f" - {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
