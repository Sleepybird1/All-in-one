#!/usr/bin/env python3
"""Build exact Ad Astra structure overrides that remove finished metal blocks.

The replacements are deliberately byte-length preserving inside decompressed
structure NBT.  This changes only the offending palette string and leaves the
structure's geometry, block-state indices, entities, and loot markers intact.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import os
import re
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
JAR_NAME = "adastra-1.21.1-1.16.22-neoforge.jar"
JAR_SHA256 = "FAF21D02C71D2D5B5A671A746334ED18A9DDBA79A5A9D9BD95E93A1D9EE9EC86"


@dataclass(frozen=True)
class StructureOverride:
    entry: str
    source_compressed_sha256: str
    source_raw_sha256: str
    old: bytes
    new: bytes
    existing_new_count: int
    output_raw_sha256: str
    output_compressed_sha256: str

    @property
    def output(self) -> Path:
        return PROJECT / "src/main/resources" / self.entry


STRUCTURE_OVERRIDES = (
    StructureOverride(
        entry="data/ad_astra/structure/village/moon/lunar_tower.nbt",
        source_compressed_sha256="CD2A200EA45D064D1ABEE15131182CE016F549B9399A4E77DF2061FD02B829C6",
        source_raw_sha256="5476605AB1F8D26133B8F025E48393AD1AEB8ED9043B8DBBD2B714FD399DD1E0",
        old=b"ad_astra:desh_block",
        new=b"ad_astra:moon_stone",
        existing_new_count=11,
        output_raw_sha256="5AB2729EB7965EAC76DFAED0BC8751C3754BDC5FFC42E73CD2161B19413D88BD",
        output_compressed_sha256="3E565515EE43CFC66E15822B023177115F4D93F0B366B862C0758E727770C2BF",
    ),
    StructureOverride(
        entry="data/ad_astra/structure/temple/mars/mars_temple.nbt",
        source_compressed_sha256="6A3C3333EA52511783EE5676C23D0700516348F69EF6C9CEE573F5D5CF16B48D",
        source_raw_sha256="BAA0B72FD7FEB424F04C9DDF7B144E91FF39ED5E34D13436BC4F26B9CBFE8A2B",
        old=b"ad_astra:ostrum_block",
        new=b"ad_astra:conglomerate",
        existing_new_count=0,
        output_raw_sha256="FD72AAA5289D96E0B34FE1BC68009E34057FCD5CBC3D1B10D7C543DB724ADF4E",
        output_compressed_sha256="BF8F441ACB7F0CB8D7E4B641AF6EE05D4C3B7100743C349ACDAE0DA1D959C38D",
    ),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def default_mods() -> Path:
    properties = (PROJECT / "gradle.properties").read_text(encoding="utf-8-sig")
    match = re.search(r"(?m)^pack_mods_dir=(.+)$", properties)
    if not match:
        raise ValueError("gradle.properties is missing pack_mods_dir")
    return Path(match.group(1).strip()).expanduser().resolve()


def build(mods: Path) -> dict[Path, bytes]:
    jar = mods / JAR_NAME
    if not jar.is_file():
        raise ValueError(f"installed Ad Astra JAR is missing: {jar}")
    jar_bytes = jar.read_bytes()
    if sha256(jar_bytes) != JAR_SHA256:
        raise ValueError(f"installed Ad Astra JAR hash drifted: {jar}")
    outputs: dict[Path, bytes] = {}
    with zipfile.ZipFile(jar) as archive:
        for spec in STRUCTURE_OVERRIDES:
            compressed = archive.read(spec.entry)
            if sha256(compressed) != spec.source_compressed_sha256:
                raise ValueError(f"source structure entry hash drifted: {spec.entry}")
            raw = gzip.decompress(compressed)
            if sha256(raw) != spec.source_raw_sha256:
                raise ValueError(f"source decompressed structure hash drifted: {spec.entry}")
            if len(spec.old) != len(spec.new):
                raise ValueError(f"structure palette replacement is not byte-length preserving: {spec.entry}")
            if raw.count(spec.old) != 1 or raw.count(spec.new) != spec.existing_new_count:
                raise ValueError(f"source structure palette occurrence count drifted: {spec.entry}")
            rewritten = raw.replace(spec.old, spec.new)
            if rewritten.count(spec.old) != 0 or rewritten.count(spec.new) != spec.existing_new_count + 1:
                raise ValueError(f"structure palette replacement did not remain surgical: {spec.entry}")
            if sha256(rewritten) != spec.output_raw_sha256:
                raise ValueError(f"rewritten structure content hash drifted: {spec.entry}")
            encoded = gzip.compress(rewritten, compresslevel=9, mtime=0)
            if sha256(encoded) != spec.output_compressed_sha256:
                raise ValueError(f"deterministic structure encoding hash drifted: {spec.entry}")
            outputs[spec.output] = encoded
    return outputs


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mods", type=Path, default=default_mods())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        outputs = build(args.mods.resolve())
    except (OSError, ValueError, gzip.BadGzipFile, zipfile.BadZipFile, KeyError) as exc:
        print(f"planetary structure override build failed: {exc}")
        return 2
    stale = [path for path, data in outputs.items() if not path.is_file() or path.read_bytes() != data]
    if args.check:
        if stale:
            print("planetary structure overrides are stale: " + ", ".join(str(path) for path in stale))
            return 1
    else:
        for path, data in outputs.items():
            atomic_write(path, data)
    print("Planetary structure overrides are current: lunar_tower Desh Block -> Moon Stone; mars_temple Ostrum Block -> Conglomerate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
