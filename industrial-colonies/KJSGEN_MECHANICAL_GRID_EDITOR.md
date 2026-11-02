# KJSGen expandable Mechanical Crafting editor

## Exact upstream behavior

The bundled dependency is `kjsgen-neoforge-2.0.5+mc1.21.1.jar`. Its Create
Mechanical Crafting layout uses `editorKind: grid`, with integer `gridW` and
`gridH` parameters defaulting to 3. `CreateSpecialModel` clamps both dimensions
to 1–9 and names cells `cell_<row>_<column>`. Its native
`CreateMechanicalCraftingCodegen` reads those dimensions and emits
`event.recipes.create.mechanical_crafting(...)`.

The limitation was confined to `VanillaEditorScreen`: `drawGridCanvas` and
`clickGridCanvas` handled the current rectangle but offered no canvas control
that changed its dimensions.

## Project bridge

`KjsGenMechanicalGridMixin` adds paired native-style `−`/`+` buttons:

- the left pair in a horizontal strip removes/adds one column;
- the right pair in that strip removes/adds one row.

The minus controls stop at 1×1 and the plus controls stop at KJSGen's native
9×9 maximum. A click mutates only `gridW` or `gridH`, marks the recipe dirty,
and rebuilds the parameter widgets so the numeric fields remain synchronized.
It never rewrites cell slots. Existing 3×3 recipes therefore remain
byte-compatible. Shrinking merely hides out-of-bounds cells, so expanding the
grid again restores every populated `cell_<row>_<column>` entry.

The strip is centered under the full input/output diagram and clamped inside
KJSGen's canvas click boundary. If there is not enough room under a tall grid,
it moves above the grid. If an unusually compact canvas has room in neither
location, the controls are not rendered or made clickable; the normal `gridW`
and `gridH` fields remain available. This avoids covering the arrow, output, or
input cells and
matters once a recipe reaches 5×5 on a smaller GUI scale: a control placed
outside the canvas can still render, but upstream KJSGen will never dispatch
its click.

The bridge is limited to Create Mechanical Crafting, including the hidden
legacy tier IDs used by old project cards. Other editors are unaffected. The
native KJSGen code generator remains authoritative, including the existing
legacy serializer rewrite in `KjsGenIntegration`.

## Validation

Run:

```powershell
python tools/validate_kjsgen_mechanical_grid_editor.py
.\gradlew.bat compileJava --offline --no-daemon
```

The validator checks the exact dependency JAR, the client mixin registration,
both draw/click hooks, non-destructive bidirectional resizing, tooltip resources, and
the retained legacy codegen path.
