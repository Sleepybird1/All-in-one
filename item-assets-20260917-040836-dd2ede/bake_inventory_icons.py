from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import zipfile

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image


LAYER_KEYS = [f"layer{i}" for i in range(16)]

FALLBACK_TEXTURE_KEYS = [
    "all",
    "particle",
    "side",
    "top",
    "bottom",
    "front",
    "back",
    "end"
]


def split_resource_location(value: str, default_namespace: str):
    if ":" in value:
        namespace, path = value.split(":", 1)
        return namespace, path
    return default_namespace, value


def safe_filename(item_id: str):
    namespace, path = item_id.split(":", 1)

    safe_path = (
        path
        .replace("/", "__")
        .replace("\\", "__")
        .replace(":", "__")
    )

    return f"{namespace}__{safe_path}.png"


class AssetRepository:

    def __init__(self, root: Path):
        self.root = root

        self.files = {}
        self.zip_handles = {}

        self.json_cache = {}
        self.image_cache = {}

        self.item_models = {}

        self.scan()


    def scan(self):

        zip_files = sorted(self.root.glob("item-assets-*.zip"))

        if not zip_files:
            raise RuntimeError(
                f"No item-assets-*.zip files found in {self.root}"
            )

        print()
        print(f"Found {len(zip_files)} ZIP archives.")
        print("Building virtual Minecraft resource tree...")

        for index, zip_path in enumerate(zip_files, start=1):

            print(
                f"[{index}/{len(zip_files)}] "
                f"Reading {zip_path.name}"
            )

            zf = zipfile.ZipFile(zip_path, "r")

            self.zip_handles[str(zip_path)] = zf

            for member in zf.namelist():

                match = re.match(
                    r"sources/(m\d{4})/assets/([^/]+)/(.+)",
                    member
                )

                if not match:
                    continue

                source_key, namespace, relative_path = match.groups()

                virtual_path = (
                    f"assets/{namespace}/{relative_path}"
                )

                self.files[virtual_path] = (
                    str(zip_path),
                    member
                )

                model_match = re.match(
                    r"models/item/(.+)\.json$",
                    relative_path
                )

                if model_match:

                    item_path = model_match.group(1)

                    item_id = (
                        f"{namespace}:{item_path}"
                    )

                    self.item_models[item_id] = (
                        virtual_path
                    )

        print()
        print(
            f"Detected {len(self.item_models):,} "
            f"item models."
        )


    def read_bytes(self, virtual_path):

        entry = self.files.get(virtual_path)

        if not entry:
            return None

        zip_path, member = entry

        try:
            return self.zip_handles[zip_path].read(member)
        except Exception:
            return None


    def load_json(self, virtual_path):

        if virtual_path in self.json_cache:
            return self.json_cache[virtual_path]

        raw = self.read_bytes(virtual_path)

        if raw is None:
            self.json_cache[virtual_path] = None
            return None

        try:

            data = json.loads(raw)

            if isinstance(data, dict):
                self.json_cache[virtual_path] = data
            else:
                self.json_cache[virtual_path] = None

        except Exception:
            self.json_cache[virtual_path] = None

        return self.json_cache[virtual_path]


    def load_image(self, virtual_path):

        if virtual_path in self.image_cache:

            image = self.image_cache[virtual_path]

            if image is None:
                return None

            return image.copy()


        raw = self.read_bytes(virtual_path)

        if raw is None:
            self.image_cache[virtual_path] = None
            return None

        try:

            image = Image.open(
                io.BytesIO(raw)
            ).convert("RGBA")

            #
            # Minecraft animated textures are commonly stored
            # as vertical texture strips.
            #
            # For inventory icons we use the first frame.
            #

            if (
                image.height > image.width
                and image.height % image.width == 0
            ):

                image = image.crop(
                    (
                        0,
                        0,
                        image.width,
                        image.width
                    )
                )

            self.image_cache[virtual_path] = image.copy()

            return image

        except Exception:

            self.image_cache[virtual_path] = None

            return None


    def model_path(self, namespace, model):

        return (
            f"assets/{namespace}/models/"
            f"{model}.json"
        )


    def texture_path(self, namespace, texture):

        return (
            f"assets/{namespace}/textures/"
            f"{texture}.png"
        )


class InventoryIconBaker:

    def __init__(self, repo):

        self.repo = repo

        self.model_cache = {}


    def resolve_model(self, item_id):

        if item_id in self.model_cache:
            return self.model_cache[item_id]

        original_model_path = (
            self.repo.item_models.get(item_id)
        )

        if not original_model_path:

            self.model_cache[item_id] = None

            return None


        namespace = item_id.split(":", 1)[0]


        def recurse(
            model_path,
            current_namespace,
            visited
        ):

            if model_path in visited:
                return None

            visited.add(model_path)

            data = self.repo.load_json(model_path)

            if not isinstance(data, dict):
                return None


            merged = {}

            parent = data.get("parent")


            if isinstance(parent, str):

                parent_namespace, parent_path = (
                    split_resource_location(
                        parent,
                        current_namespace
                    )
                )

                parent_model_path = (
                    self.repo.model_path(
                        parent_namespace,
                        parent_path
                    )
                )

                parent_model = recurse(
                    parent_model_path,
                    parent_namespace,
                    visited
                )

                if parent_model:
                    merged.update(parent_model)


            parent_textures = {}

            if isinstance(
                merged.get("textures"),
                dict
            ):

                parent_textures.update(
                    merged["textures"]
                )


            own_textures = data.get(
                "textures",
                {}
            )

            if isinstance(own_textures, dict):

                for key, value in own_textures.items():

                    if isinstance(value, str):
                        parent_textures[key] = value


            merged.update(data)

            merged["textures"] = parent_textures

            return merged


        resolved = recurse(
            original_model_path,
            namespace,
            set()
        )

        self.model_cache[item_id] = resolved

        return resolved


    def resolve_texture_variable(
        self,
        value,
        namespace,
        textures
    ):

        seen = set()

        while (
            value
            and isinstance(value, str)
            and value.startswith("#")
        ):

            variable = value[1:]

            if variable in seen:
                return None

            seen.add(variable)

            value = textures.get(variable)


        if not isinstance(value, str):
            return None


        texture_namespace, texture_path = (
            split_resource_location(
                value,
                namespace
            )
        )

        return self.repo.texture_path(
            texture_namespace,
            texture_path
        )


    def find_layers(
        self,
        item_id,
        model
    ):

        namespace = item_id.split(
            ":",
            1
        )[0]

        textures = model.get(
            "textures",
            {}
        )

        if not isinstance(textures, dict):
            textures = {}


        layers = []


        #
        # Normal Minecraft inventory item layers:
        #
        # layer0
        # layer1
        # layer2
        # ...
        #

        for layer_name in LAYER_KEYS:

            if layer_name not in textures:
                continue

            texture = self.resolve_texture_variable(
                textures[layer_name],
                namespace,
                textures
            )

            if texture:
                layers.append(texture)


        if layers:

            return (
                layers,
                "multi_layer_inventory"
            )


        #
        # Flat block/item fallback.
        #

        for key in FALLBACK_TEXTURE_KEYS:

            if key not in textures:
                continue

            texture = self.resolve_texture_variable(
                textures[key],
                namespace,
                textures
            )

            if texture:

                return (
                    [texture],
                    f"fallback_{key}"
                )


        #
        # Direct inventory texture fallback.
        #

        item_path = item_id.split(
            ":",
            1
        )[1]


        direct_item = (
            self.repo.texture_path(
                namespace,
                f"item/{item_path}"
            )
        )


        if self.repo.read_bytes(
            direct_item
        ) is not None:

            return (
                [direct_item],
                "direct_item_texture"
            )


        direct_block = (
            self.repo.texture_path(
                namespace,
                f"block/{item_path}"
            )
        )


        if self.repo.read_bytes(
            direct_block
        ) is not None:

            return (
                [direct_block],
                "direct_block_texture"
            )


        return (
            [],
            "unresolved"
        )


    def composite(self, texture_paths):

        loaded = []

        width = 0
        height = 0


        for texture_path in texture_paths:

            image = self.repo.load_image(
                texture_path
            )

            if image is None:
                continue


            loaded.append(image)

            width = max(
                width,
                image.width
            )

            height = max(
                height,
                image.height
            )


        if not loaded:

            return None


        canvas = Image.new(
            "RGBA",
            (
                width,
                height
            ),
            (
                0,
                0,
                0,
                0
            )
        )


        for image in loaded:

            if image.size != (
                width,
                height
            ):

                image = image.resize(
                    (
                        width,
                        height
                    ),
                    Image.Resampling.NEAREST
                )


            canvas.alpha_composite(
                image
            )


        return canvas


    def bake(self, item_id):

        model = self.resolve_model(
            item_id
        )

        if not model:

            return (
                None,
                "missing_model",
                []
            )


        textures, method = self.find_layers(
            item_id,
            model
        )


        if not textures:

            return (
                None,
                method,
                []
            )


        icon = self.composite(
            textures
        )


        if icon is None:

            return (
                None,
                "texture_read_failed",
                textures
            )


        return (
            icon,
            method,
            textures
        )


def main():

    root = Path.cwd()

    output_directory = (
        root / "baked_icons"
    )

    output_directory.mkdir(
        exist_ok=True
    )


    manifest_path = (
        root
        / "baked_icons_manifest.csv"
    )


    print()
    print(
        "Minecraft Inventory Icon Baker"
    )
    print(
        "=============================="
    )
    print()

    print(
        f"Working directory:"
        f" {root}"
    )

    print(
        f"Output directory:"
        f" {output_directory}"
    )

    print()


    repository = AssetRepository(
        root
    )


    baker = InventoryIconBaker(
        repository
    )


    item_ids = sorted(
        repository.item_models.keys()
    )


    total = len(item_ids)

    baked_count = 0
    unresolved_count = 0


    report = []


    print()
    print(
        "Baking inventory icons..."
    )
    print()


    for index, item_id in enumerate(
        item_ids,
        start=1
    ):

        icon, method, textures = (
            baker.bake(item_id)
        )


        output_path = ""


        if icon is not None:

            filename = safe_filename(
                item_id
            )

            icon_file = (
                output_directory
                / filename
            )

            icon.save(
                icon_file
            )

            output_path = str(
                icon_file
            )

            baked_count += 1

            status = "OK"

        else:

            unresolved_count += 1

            status = "UNRESOLVED"


        report.append(
            {
                "item_id": item_id,
                "status": status,
                "method": method,
                "textures": " | ".join(
                    textures
                ),
                "output_png": output_path,
            }
        )


        if (
            index % 250 == 0
            or index == total
        ):

            percentage = (
                index / total * 100
            )

            print(
                f"{percentage:6.2f}%  "
                f"{index:,}/{total:,}  "
                f"Baked: {baked_count:,}  "
                f"Unresolved: "
                f"{unresolved_count:,}"
            )


    print()
    print(
        "Writing manifest..."
    )


    with open(
        manifest_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "item_id",
                "status",
                "method",
                "textures",
                "output_png",
            ]
        )

        writer.writeheader()

        writer.writerows(
            report
        )


    print()
    print(
        "==================================="
    )

    print(
        "Finished."
    )

    print(
        "==================================="
    )

    print()

    print(
        f"Total item models: "
        f"{total:,}"
    )

    print(
        f"Baked icons: "
        f"{baked_count:,}"
    )

    print(
        f"Unresolved: "
        f"{unresolved_count:,}"
    )

    if total:

        print(
            f"Success rate: "
            f"{baked_count / total * 100:.2f}%"
        )

    print()

    print(
        f"Icons:"
    )

    print(
        output_directory
    )

    print()

    print(
        f"Report:"
    )

    print(
        manifest_path
    )

    print()


if __name__ == "__main__":

    try:

        main()

    except Exception as exc:

        print()

        print(
            "ERROR:"
        )

        print(
            str(exc)
        )

        print()

        import traceback

        traceback.print_exc()

        input(
            "Press Enter to close..."
        )

        raise
