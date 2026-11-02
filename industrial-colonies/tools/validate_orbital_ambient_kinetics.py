#!/usr/bin/env python3
"""Validate dimension-scoped Create wind and water suppression.

The policy is intentionally narrow.  It intercepts only the two Create 6.0.10
generator methods whose ambient inputs are unavailable in the owned orbital
environments.  It does not touch GeneratingKineticBlockEntity, combustion,
motors, hand power, or any other kinetic source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import zipfile
from dataclasses import dataclass
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
CREATE_JAR_NAME = "create-1.21.1-6.0.10.jar"
CREATE_VERSION_RANGE = 'versionRange="[6.0.10,6.0.11)"'

POLICY = Path(
    "src/main/java/dev/godpc/industrialcolonies/space/AmbientKineticPolicy.java"
)
WATER_MIXIN = Path(
    "src/main/java/dev/godpc/industrialcolonies/mixin/WaterWheelBlockEntityMixin.java"
)
WIND_MIXIN = Path(
    "src/main/java/dev/godpc/industrialcolonies/mixin/WindmillBearingBlockEntityMixin.java"
)
MIXIN_CONFIG = Path("src/main/resources/industrial_colonies.mixins.json")
MOD_METADATA = Path("src/main/templates/META-INF/neoforge.mods.toml")

REQUIRED_FILES = (POLICY, WATER_MIXIN, WIND_MIXIN, MIXIN_CONFIG, MOD_METADATA)

DENIED_DIMENSIONS = (
    "rocketnautics:deep_space",
    "ad_astra:earth_orbit",
    "ad_astra:moon",
    "ad_astra:moon_orbit",
    "ad_astra:mars",
    "ad_astra:mars_orbit",
    "ad_astra:mercury",
    "ad_astra:mercury_orbit",
    "ad_astra:venus",
    "ad_astra:venus_orbit",
    "ad_astra:glacio",
    "ad_astra:glacio_orbit",
    "rocketnautics:moon",
    "rocketnautics_addon:mars",
)


@dataclass(frozen=True)
class TargetContract:
    key: str
    class_name: str
    super_name: str
    class_path: str
    sha256: str
    mixin_name: str
    mixin_path: Path
    policy_method: str


TARGETS = (
    TargetContract(
        key="hydro",
        class_name=(
            "com/simibubi/create/content/kinetics/waterwheel/WaterWheelBlockEntity"
        ),
        super_name=(
            "com/simibubi/create/content/kinetics/base/GeneratingKineticBlockEntity"
        ),
        class_path=(
            "com/simibubi/create/content/kinetics/waterwheel/"
            "WaterWheelBlockEntity.class"
        ),
        sha256="1219E362C15D1368645706A537A3632226F7F360F3D4524E9C1E783C103578DA",
        mixin_name="WaterWheelBlockEntityMixin",
        mixin_path=WATER_MIXIN,
        policy_method="deniesHydro",
    ),
    TargetContract(
        key="wind",
        class_name=(
            "com/simibubi/create/content/contraptions/bearing/"
            "WindmillBearingBlockEntity"
        ),
        super_name=(
            "com/simibubi/create/content/contraptions/bearing/"
            "MechanicalBearingBlockEntity"
        ),
        class_path=(
            "com/simibubi/create/content/contraptions/bearing/"
            "WindmillBearingBlockEntity.class"
        ),
        sha256="54D33F65D1E0488A4B2D577616214D8A8B015B1C25B58B2E06EE61B57AD40482",
        mixin_name="WindmillBearingBlockEntityMixin",
        mixin_path=WIND_MIXIN,
        policy_method="deniesWind",
    ),
)

PROJECT_JAR_ENTRIES = (
    "dev/godpc/industrialcolonies/space/AmbientKineticPolicy.class",
    "dev/godpc/industrialcolonies/mixin/WaterWheelBlockEntityMixin.class",
    "dev/godpc/industrialcolonies/mixin/WindmillBearingBlockEntityMixin.class",
    "industrial_colonies.mixins.json",
    "META-INF/neoforge.mods.toml",
)


class ClassFormatError(ValueError):
    """Raised when a target is no longer a parseable JVM class file."""


class _Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def read(self, size: int) -> bytes:
        end = self.offset + size
        if size < 0 or end > len(self.data):
            raise ClassFormatError("truncated class file")
        value = self.data[self.offset:end]
        self.offset = end
        return value

    def u1(self) -> int:
        return self.read(1)[0]

    def u2(self) -> int:
        return struct.unpack(">H", self.read(2))[0]

    def u4(self) -> int:
        return struct.unpack(">I", self.read(4))[0]


@dataclass(frozen=True)
class ParsedMethod:
    access: int
    name: str
    descriptor: str
    attributes: tuple[str, ...]


@dataclass(frozen=True)
class ParsedClass:
    major: int
    name: str
    super_name: str
    methods: tuple[ParsedMethod, ...]


def parse_class_file(data: bytes) -> ParsedClass:
    """Parse just enough JVM structure to pin class and method descriptors."""

    reader = _Reader(data)
    if reader.u4() != 0xCAFEBABE:
        raise ClassFormatError("bad class-file magic")
    reader.u2()  # minor
    major = reader.u2()
    constant_pool_count = reader.u2()
    pool: list[tuple[int, object] | None] = [None] * constant_pool_count

    index = 1
    while index < constant_pool_count:
        tag = reader.u1()
        if tag == 1:
            length = reader.u2()
            pool[index] = (tag, reader.read(length).decode("utf-8", errors="strict"))
        elif tag in (3, 4):
            pool[index] = (tag, reader.read(4))
        elif tag in (5, 6):
            pool[index] = (tag, reader.read(8))
            index += 1
        elif tag in (7, 8, 16, 19, 20):
            pool[index] = (tag, reader.u2())
        elif tag in (9, 10, 11, 12, 17, 18):
            pool[index] = (tag, (reader.u2(), reader.u2()))
        elif tag == 15:
            pool[index] = (tag, (reader.u1(), reader.u2()))
        else:
            raise ClassFormatError(f"unknown constant-pool tag {tag}")
        index += 1

    def utf8(pool_index: int) -> str:
        try:
            entry = pool[pool_index]
        except IndexError as exc:
            raise ClassFormatError("constant-pool index out of range") from exc
        if entry is None or entry[0] != 1 or not isinstance(entry[1], str):
            raise ClassFormatError("constant-pool entry is not UTF-8")
        return entry[1]

    def class_name(pool_index: int) -> str:
        try:
            entry = pool[pool_index]
        except IndexError as exc:
            raise ClassFormatError("class constant-pool index out of range") from exc
        if entry is None or entry[0] != 7 or not isinstance(entry[1], int):
            raise ClassFormatError("constant-pool entry is not a class")
        return utf8(entry[1])

    reader.u2()  # access flags
    this_class = reader.u2()
    super_class = reader.u2()
    for _ in range(reader.u2()):
        reader.u2()

    def skip_attributes() -> tuple[str, ...]:
        names: list[str] = []
        for _ in range(reader.u2()):
            name = utf8(reader.u2())
            names.append(name)
            reader.read(reader.u4())
        return tuple(names)

    for _ in range(reader.u2()):
        reader.u2()  # access
        reader.u2()  # name
        reader.u2()  # descriptor
        skip_attributes()

    methods: list[ParsedMethod] = []
    for _ in range(reader.u2()):
        access = reader.u2()
        name = utf8(reader.u2())
        descriptor = utf8(reader.u2())
        methods.append(ParsedMethod(access, name, descriptor, skip_attributes()))

    skip_attributes()
    if reader.offset != len(data):
        raise ClassFormatError("trailing class-file data")
    return ParsedClass(
        major=major,
        name=class_name(this_class),
        super_name=class_name(super_class),
        methods=tuple(methods),
    )


def _extract_policy_dimensions(source: str, field: str) -> list[str] | None:
    match = re.search(
        rf"\b{re.escape(field)}\s*=\s*Set\.of\((.*?)\n\s*\);",
        source,
        flags=re.DOTALL,
    )
    if match is None:
        return None
    return [
        f"{namespace}:{path}"
        for namespace, path in re.findall(
            r'dimension\("([a-z0-9_.-]+)",\s*"([a-z0-9_./-]+)"\)',
            match.group(1),
        )
    ]


def validate_create_jar(mods: Path, failures: list[str]) -> None:
    expected = mods / CREATE_JAR_NAME
    candidates = sorted(mods.glob("create-1.21.1-*.jar"))
    if candidates != [expected]:
        failures.append(
            "Create target must be exactly create-1.21.1-6.0.10.jar; found "
            f"{[path.name for path in candidates]}"
        )
        return

    try:
        with zipfile.ZipFile(expected) as archive:
            for contract in TARGETS:
                bytecode = archive.read(contract.class_path)
                digest = hashlib.sha256(bytecode).hexdigest().upper()
                if digest != contract.sha256:
                    failures.append(
                        f"Create 6.0.10 {contract.key} target bytecode drifted: {digest}"
                    )
                    continue
                parsed = parse_class_file(bytecode)
                if parsed.major != 65:
                    failures.append(
                        f"Create {contract.key} target is not Java 21 bytecode: {parsed.major}"
                    )
                if parsed.name != contract.class_name:
                    failures.append(
                        f"Create {contract.key} class name drifted: {parsed.name}"
                    )
                if parsed.super_name != contract.super_name:
                    failures.append(
                        f"Create {contract.key} superclass drifted: {parsed.super_name}"
                    )
                methods = [
                    method
                    for method in parsed.methods
                    if method.name == "getGeneratedSpeed"
                    and method.descriptor == "()F"
                ]
                if len(methods) != 1:
                    failures.append(
                        f"Create {contract.key} target must expose exactly one "
                        "getGeneratedSpeed()F method"
                    )
                    continue
                method = methods[0]
                if not method.access & 0x0001 or method.access & (0x0008 | 0x0400):
                    failures.append(
                        f"Create {contract.key} getGeneratedSpeed()F access drifted"
                    )
                if "Code" not in method.attributes:
                    failures.append(
                        f"Create {contract.key} getGeneratedSpeed()F has no Code attribute"
                    )
    except (OSError, KeyError, UnicodeDecodeError, zipfile.BadZipFile, ClassFormatError) as exc:
        failures.append(f"cannot inspect pinned Create 6.0.10 bytecode: {exc}")


def validate_project_jar(project_jar: Path, failures: list[str]) -> None:
    if not project_jar.is_file():
        failures.append(f"missing deployment candidate JAR: {project_jar}")
        return
    try:
        with zipfile.ZipFile(project_jar) as archive:
            names = set(archive.namelist())
            missing = sorted(set(PROJECT_JAR_ENTRIES) - names)
            if missing:
                failures.append(
                    f"deployment candidate JAR lacks ambient-kinetic entries: {missing}"
                )
                return
            config = json.loads(archive.read("industrial_colonies.mixins.json"))
            water = archive.read(PROJECT_JAR_ENTRIES[1])
            wind = archive.read(PROJECT_JAR_ENTRIES[2])
            policy = archive.read(PROJECT_JAR_ENTRIES[0])
            metadata = archive.read(PROJECT_JAR_ENTRIES[4]).decode("utf-8")
    except (OSError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        failures.append(f"cannot inspect deployment candidate JAR: {exc}")
        return

    for contract in TARGETS:
        if config.get("mixins", []).count(contract.mixin_name) != 1:
            failures.append(
                f"deployment candidate JAR does not enable {contract.mixin_name} exactly once"
            )
    for contract, bytecode, method in (
        (TARGETS[0], water, b"deniesHydro"),
        (TARGETS[1], wind, b"deniesWind"),
    ):
        for marker in (
            b"getGeneratedSpeed()F",
            method,
            b"setReturnValue",
            b"HEAD",
            b"cancellable",
            b"require",
            contract.class_name.encode(),
        ):
            if marker not in bytecode:
                failures.append(
                    "deployment candidate ambient mixin bytecode lacks marker "
                    f"{marker.decode()}"
                )
    if metadata.count(CREATE_VERSION_RANGE) != 1:
        failures.append(
            "deployment candidate JAR does not pin Create to exact 6.0.10 range"
        )
    for namespace_path in DENIED_DIMENSIONS:
        namespace, path = namespace_path.split(":", 1)
        for marker in (namespace.encode(), path.encode()):
            if marker not in policy:
                failures.append(
                    "deployment candidate policy bytecode lacks dimension marker "
                    f"{namespace_path}"
                )
                break


def validate(
    project: Path,
    mods: Path | None = None,
    project_jar: Path | None = None,
) -> list[str]:
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        if not (project / relative).is_file():
            failures.append(f"missing ambient-kinetic file: {relative.as_posix()}")
    if failures:
        return failures

    policy_source = (project / POLICY).read_text(encoding="utf-8-sig")
    for field in ("WIND_DENY_DIMENSIONS", "HYDRO_DENY_DIMENSIONS"):
        actual = _extract_policy_dimensions(policy_source, field)
        if actual is None:
            failures.append(f"ambient policy lacks separate explicit {field} set")
        elif actual != list(DENIED_DIMENSIONS):
            failures.append(
                f"ambient policy {field} must equal the exact owned dimension set"
            )
    if "minecraft:overworld" in policy_source or 'dimension("minecraft", "overworld")' in policy_source:
        failures.append("minecraft:overworld must remain outside ambient kinetic deny sets")
    for fragment in (
        "public static boolean deniesWind(Level parentLevel)",
        "public static boolean deniesHydro(Level parentLevel)",
        "return denies(parentLevel, WIND_DENY_DIMENSIONS);",
        "return denies(parentLevel, HYDRO_DENY_DIMENSIONS);",
        "parentLevel != null && dimensions.contains(parentLevel.dimension().location())",
    ):
        if fragment not in policy_source:
            failures.append(f"central ambient kinetic policy drifted: {fragment}")

    for contract in TARGETS:
        source = (project / contract.mixin_path).read_text(encoding="utf-8-sig")
        target_simple_name = contract.class_name.rsplit("/", 1)[-1]
        required_fragments = (
            f"@Mixin({target_simple_name}.class)",
            'method = "getGeneratedSpeed()F"',
            'at = @At("HEAD")',
            "cancellable = true",
            "require = 1",
            f"AmbientKineticPolicy.{contract.policy_method}",
            "callback.setReturnValue(0.0F);",
        )
        for fragment in required_fragments:
            if fragment not in source:
                failures.append(
                    f"{contract.mixin_name} exact HEAD contract drifted: {fragment}"
                )
        if source.count("@Inject(") != 1:
            failures.append(f"{contract.mixin_name} must contain exactly one injection")
        if "@Overwrite" in source:
            failures.append(f"{contract.mixin_name} may not overwrite Create methods")

    mixin_sources = "\n".join(
        path.read_text(encoding="utf-8-sig")
        for path in (project / "src/main/java/dev/godpc/industrialcolonies/mixin").glob(
            "*.java"
        )
    )
    if re.search(
        r"@Mixin\s*\(\s*GeneratingKineticBlockEntity\.class\s*\)", mixin_sources
    ):
        failures.append("base GeneratingKineticBlockEntity mixins are forbidden")

    mixin_config = json.loads((project / MIXIN_CONFIG).read_text(encoding="utf-8-sig"))
    for contract in TARGETS:
        if mixin_config.get("mixins", []).count(contract.mixin_name) != 1:
            failures.append(
                f"{contract.mixin_name} must occur exactly once in the common mixin config"
            )

    metadata = (project / MOD_METADATA).read_text(encoding="utf-8-sig")
    if metadata.count(CREATE_VERSION_RANGE) != 1:
        failures.append(
            "Create dependency must fail closed outside exact 6.0.10 compatibility range"
        )

    if mods is not None:
        validate_create_jar(mods, failures)
    if project_jar is not None:
        validate_project_jar(project_jar, failures)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--mods", type=Path)
    parser.add_argument("--project-jar", type=Path)
    args = parser.parse_args()
    failures = validate(
        args.project.resolve(),
        args.mods.resolve() if args.mods else None,
        args.project_jar.resolve() if args.project_jar else None,
    )
    if failures:
        print("FAIL: orbital ambient kinetic suppression is invalid")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print(
        "PASS: Create 6.0.10 water wheels and windmill bearings are suppressed "
        "only in the explicit orbital/planetary dimension sets; the Overworld "
        "and every other kinetic source remain untouched."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
