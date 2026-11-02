#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_kjsgen_tfmg_chemical_vat as validator


class TfmgChemicalVatMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        self.mods = Path(self.temp.name) / "mods"
        self.mods.mkdir(parents=True)
        source = TOOLS.parent
        for relative in validator.REQUIRED_FILES:
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, target)

        installed = Path(
            r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one\mods"
        ) / validator.TFMG_JAR_NAME
        self.tfmg_jar = self.mods / validator.TFMG_JAR_NAME
        with zipfile.ZipFile(installed) as incoming, zipfile.ZipFile(
            self.tfmg_jar, "w"
        ) as outgoing:
            for entry in (*validator.TFMG_CLASSES, *validator.STOCK_RECIPES):
                outgoing.writestr(entry, incoming.read(entry))

        self.project_jar = Path(self.temp.name) / "industrial_colonies-test.jar"
        self._write_project_jar()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_project_jar(
        self,
        *,
        drop: str | None = None,
        omit_codegen_marker: bytes | None = None,
    ) -> None:
        layout = (self.project / validator.LAYOUT).read_bytes()
        integration = b"industrial_colonies:tfmg_chemical_vat\0TfmgChemicalVatCodegen"
        markers = b"\0".join(
            (
                b"tfmg:vat_machine_recipe",
                b"ingredients",
                b"results",
                b"allowed_vat_types",
                b"machines",
                b"min_size",
                b"processing_time",
                b"heat_requirement",
                b"neoforge:single",
                b"neoforge:tag",
                b"tfmg:steel_vat",
                b"tfmg:firebrick_lined_vat",
                b"tfmg:mixing",
                b"tfmg:electrode",
                b" }).id(",
            )
        )
        if omit_codegen_marker is not None:
            markers = markers.replace(omit_codegen_marker, b"missing")
        entries = {
            validator.PROJECT_JAR_ENTRIES[0]: layout,
            validator.PROJECT_JAR_ENTRIES[1]: integration,
            validator.PROJECT_JAR_ENTRIES[2]: markers,
        }
        with zipfile.ZipFile(self.project_jar, "w") as archive:
            for name, content in entries.items():
                if name != drop:
                    archive.writestr(name, content)

    def failures(self) -> list[str]:
        return validator.validate(
            self.project, mods=self.mods, project_jar=self.project_jar
        )

    def replace(self, relative: Path, old: str, new: str) -> None:
        path = self.project / relative
        source = path.read_text(encoding="utf-8-sig")
        self.assertIn(old, source)
        path.write_text(source.replace(old, new, 1), encoding="utf-8")

    def mutate_layout(self, mutator) -> None:
        path = self.project / validator.LAYOUT
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        mutator(payload)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        self._write_project_jar()

    def mutate_tfmg_jar(self, entry: str, transform) -> None:
        with zipfile.ZipFile(self.tfmg_jar) as incoming:
            entries = {name: incoming.read(name) for name in incoming.namelist()}
        entries[entry] = transform(entries[entry])
        with zipfile.ZipFile(self.tfmg_jar, "w") as outgoing:
            for name, content in entries.items():
                outgoing.writestr(name, content)

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_layout_identity_is_pinned(self) -> None:
        self.mutate_layout(lambda layout: layout.__setitem__("id", "industrial_colonies:wrong"))
        self.assertTrue(any("layout id drifted" in row for row in self.failures()))

    def test_03_layout_inputs_must_accept_fluid_tags(self) -> None:
        self.mutate_layout(
            lambda layout: layout["slots"][0].__setitem__("fluid", False)
        )
        self.assertTrue(any("ingredients.fluid" in row for row in self.failures()))

    def test_04_layout_outputs_may_not_accept_tags(self) -> None:
        self.mutate_layout(lambda layout: layout["slots"][1].__setitem__("tag", True))
        self.assertTrue(any("tagged Chemical Vat outputs" in row for row in self.failures()))

    def test_05_exact_machine_modes_are_pinned(self) -> None:
        self.mutate_layout(
            lambda layout: next(
                p for p in layout["parameters"] if p["key"] == "machineMode"
            )["options"].append("centrifuge")
        )
        self.assertTrue(any("machineMode options" in row for row in self.failures()))

    def test_06_codegen_registration_is_required(self) -> None:
        self.replace(
            validator.INTEGRATION,
            "new TfmgChemicalVatCodegen()",
            "new MekanismMetallurgicInfusingCodegen()",
        )
        self.assertTrue(any("registration" in row for row in self.failures()))

    def test_07_codegen_must_expand_item_counts(self) -> None:
        self.replace(
            validator.CODEGEN,
            "for (int index = 0; index < copies; index++)",
            "for (int index = 0; index < 1; index++)",
        )
        self.assertTrue(any("copies" in row for row in self.failures()))

    def test_08_codegen_must_emit_explicit_recipe_id(self) -> None:
        self.replace(
            validator.CODEGEN,
            ' }).id("',
            ' }"',
        )
        self.assertTrue(any(".id" in row for row in self.failures()))

    def test_09_pressure_cannot_enter_the_120_editor(self) -> None:
        path = self.project / validator.CODEGEN
        path.write_text(path.read_text(encoding="utf-8") + "// pressure\n", encoding="utf-8")
        self.assertTrue(any("pressure" in row for row in self.failures()))

    def test_10_compiler_dispatch_is_required(self) -> None:
        self.replace(
            validator.COMPILER,
            'elif kind == "tfmg_vat":',
            'elif kind == "tfmg_vat_removed":',
        )
        self.assertTrue(any("compiler is missing" in row for row in self.failures()))

    def test_11_compiler_rejects_one_five_count_item_ingredient(self) -> None:
        compiler = validator._load_compiler(self.project / validator.COMPILER)
        spec = {
            "id": "industrial_colonies:test/five",
            "phase": "test",
            "comment": "five slots",
            "type": "tfmg_vat",
            "ingredients": ["5x minecraft:stone"],
            "results": ["minecraft:cobblestone"],
            "vat_mode": "steel",
            "machine_mode": "mixing",
        }
        with self.assertRaisesRegex(ValueError, "four expanded item ingredients"):
            compiler.tfmg_vat(spec, "00000000-0000-0000-0000-000000000000")

    def test_12_compiler_rejects_fluid_result_chance(self) -> None:
        compiler = validator._load_compiler(self.project / validator.COMPILER)
        spec = {
            "id": "industrial_colonies:test/fluid_chance",
            "phase": "test",
            "comment": "invalid chance",
            "type": "tfmg_vat",
            "ingredients": ["minecraft:stone"],
            "results": [
                {"kind": "FLUID", "id": "minecraft:water", "amount": 10, "chance": 0.5}
            ],
            "vat_mode": "steel",
            "machine_mode": "mixing",
        }
        with self.assertRaisesRegex(ValueError, "fluid result cannot use count/chance"):
            compiler.tfmg_vat(spec, "00000000-0000-0000-0000-000000000000")

    def test_13_managed_validator_support_is_required(self) -> None:
        self.replace(
            validator.MANAGED_VALIDATOR,
            '"tfmg_vat": TFMG_VAT_CARD_TYPE',
            '"tfmg_vat_removed": TFMG_VAT_CARD_TYPE',
        )
        self.assertTrue(any("managed validator" in row for row in self.failures()))

    def test_14_pinned_tfmg_bytecode_drift_is_detected(self) -> None:
        entry = next(iter(validator.TFMG_CLASSES))
        self.mutate_tfmg_jar(entry, lambda value: value[:-1] + bytes([value[-1] ^ 1]))
        self.assertTrue(any("bytecode drifted" in row for row in self.failures()))

    def test_15_stock_fluid_codec_shape_is_pinned(self) -> None:
        entry = validator.STOCK_RECIPES[0]

        def mutate(value: bytes) -> bytes:
            payload = json.loads(value)
            payload["ingredients"][-1]["type"] = "neoforge:tag"
            return json.dumps(payload).encode()

        self.mutate_tfmg_jar(entry, mutate)
        self.assertTrue(any("fluid-ingredient codec" in row for row in self.failures()))

    def test_16_candidate_jar_must_package_layout_and_codegen(self) -> None:
        self._write_project_jar(drop=validator.PROJECT_JAR_ENTRIES[2])
        self.assertTrue(any("lacks Chemical Vat entries" in row for row in self.failures()))

    def test_17_candidate_jar_codegen_may_not_be_stale(self) -> None:
        self._write_project_jar(omit_codegen_marker=b"heat_requirement")
        self.assertTrue(any("heat_requirement" in row for row in self.failures()))

    def test_18_compiler_rejects_missing_project_aliases(self) -> None:
        compiler = validator._load_compiler(self.project / validator.COMPILER)
        spec = {
            "id": "industrial_colonies:test/missing_aliases",
            "phase": "test",
            "comment": "missing aliases",
            "type": "tfmg_vat",
            "outputs": ["minecraft:cobblestone"],
            "vat": "steel",
            "machine": "mixing",
        }
        with self.assertRaisesRegex(ValueError, "ingredients/inputs must be an array"):
            compiler.tfmg_vat(spec, "00000000-0000-0000-0000-000000000000")

    def test_19_compiler_rejects_conflicting_aliases(self) -> None:
        compiler = validator._load_compiler(self.project / validator.COMPILER)
        spec = {
            "id": "industrial_colonies:test/conflicting_aliases",
            "phase": "test",
            "comment": "conflicting aliases",
            "type": "tfmg_vat",
            "ingredients": ["minecraft:stone"],
            "inputs": ["minecraft:dirt"],
            "results": ["minecraft:cobblestone"],
            "outputs": ["minecraft:cobblestone"],
            "vat_mode": "steel",
            "vat": "firebrick",
            "machine_mode": "mixing",
            "machine": "mixing",
        }
        with self.assertRaisesRegex(ValueError, "conflicting ingredients/inputs"):
            compiler.tfmg_vat(spec, "00000000-0000-0000-0000-000000000000")


if __name__ == "__main__":
    unittest.main()
