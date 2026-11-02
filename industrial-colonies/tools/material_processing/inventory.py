"""Read-only installed JAR resource inventory; no class loading or mod execution."""
import json
import re
from pathlib import Path
from zipfile import ZipFile


def inventory(mods):
    recipes, tags, item_models = {}, {}, set()
    fluids = set()
    for path in sorted(Path(mods).glob('*.jar')):
        with ZipFile(path) as jar:
            for name in jar.namelist():
                match = re.fullmatch(r'data/([^/]+)/recipe/(.+)\.json', name)
                tag = re.fullmatch(r'data/([^/]+)/tags/(item|fluid)/(.+)\.json', name)
                model = re.fullmatch(r'assets/([^/]+)/models/item/(.+)\.json', name)
                if model:
                    item_models.add(':'.join(model.groups()))
                if not match and not tag:
                    continue
                try:
                    data = json.loads(jar.read(name))
                except (ValueError, UnicodeError):
                    continue
                if match:
                    recipes[':'.join(match.groups())] = {'source': path.name, 'data': data}
                    def walk(obj):
                        if isinstance(obj, dict):
                            if isinstance(obj.get('fluid'), str): fluids.add(obj['fluid'])
                            for value in obj.values(): walk(value)
                        elif isinstance(obj, list):
                            for value in obj: walk(value)
                    walk(data)
                else:
                    namespace, kind, suffix = tag.groups()
                    key = f'{kind}/{namespace}:{suffix}'
                    tags.setdefault(key, []).extend(data.get('values', []))
    return {'recipes': recipes, 'tags': tags, 'item_models': sorted(item_models), 'fluid_references': sorted(fluids)}


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--mods', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    data = inventory(a.mods)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print(f"Inventoried {len(data['recipes'])} recipes, {len(data['item_models'])} item models, {len(data['tags'])} tags")
