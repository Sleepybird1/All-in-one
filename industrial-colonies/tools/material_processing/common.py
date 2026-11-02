"""Shared, deterministic recipe/content builder for the material-processing batch.

Native installed-mod codecs remain authoritative. This layer only centralizes values,
registers genuinely missing intermediates and makes stage ownership explicit.
"""
from copy import deepcopy
from math import isfinite

NS = 'industrial_colonies:'

# Installed Modern Foundry temperatures, not real-world Celsius. Keeping early
# metals within its 800-degree solid-fuel tier avoids needing an iron lava bucket
# before the first iron ingot. Explicit high-tier reduction overrides still win.
NATIVE_MELTING_TEMPERATURES = {
    'iron': 800, 'copper': 500, 'gold': 700, 'zinc': 420, 'tin': 225,
    'lead': 330, 'nickel': 950, 'aluminum': 425, 'osmium': 975,
    'silver': 790, 'cobalt': 950, 'chromium': 900, 'tungsten': 950,
    'platinum': 970, 'steel': 950, 'brass': 605, 'bronze': 700,
}


def I(item):
    return {'tag': item[1:]} if item.startswith('#') else {'item': item}


def O(item, count=1, chance=None):
    result = {'id': item, 'count': count}
    if chance is not None:
        result['chance'] = chance
    return result


def F(fluid, amount):
    return {'type': 'neoforge:single', 'fluid': fluid, 'amount': amount}


class Builder:
    def __init__(self, config=None):
        self.config = deepcopy(config or {})
        self.items = {}
        self.fluids = {}
        self.recipes = {}
        self.notes = {}
        self.remove_ids = set()
        self.claim_outputs = set()
        self.metals = {}

    def value(self, path, default):
        obj = self.config
        parts = path.split('.')
        for key in parts[:-1]:
            obj = obj.setdefault(key, {})
        value = obj.setdefault(parts[-1], default)
        if isinstance(default, (int, float)) and not isinstance(default, bool):
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value) or value < 0:
                raise ValueError(f'Invalid finite nonnegative processing value {path}: {value}')
            if isinstance(default, int) and not isinstance(value, int):
                raise ValueError(f'Processing count/time/volume must be an integer at {path}: {value}')
        return value

    def item(self, name, label=None, texture='minecraft:item/gunpowder'):
        name = name.removeprefix(NS)
        ident = NS + name
        entry = {'name': label or name.replace('_', ' ').title(), 'texture': texture}
        if name in self.items and self.items[name] != entry:
            # The first explicit display definition wins, never register twice.
            return ident
        self.items[name] = entry
        return ident

    def fluid(self, name, color=0xFF668877, label=None):
        name = name.removeprefix(NS)
        self.fluids.setdefault(name, {'name': label or name.replace('_', ' ').title(), 'color': color})
        return NS + name

    def add(self, path, recipe, comment='', family=''):
        ident = path if ':' in path else NS + 'processing/' + path
        if ident in self.recipes:
            raise ValueError('Duplicate processing recipe ' + ident)
        if recipe.get('type', '').startswith('modernfoundry:'):
            recipe['id'] = ident
        self.recipes[ident] = recipe
        self.notes[ident] = {'comment': comment, 'family': family or path.split('/')[0]}
        return ident

    def crush(self, path, input, outputs, time=250, comment=''):
        return self.add(path, {'type': 'create:crushing', 'ingredients': [I(input)] if isinstance(input, str) else input,
                              'results': outputs, 'processing_time': time}, comment)

    def mix(self, path, inputs, outputs, heat='none', time=200, tier=None, comment=''):
        recipe = {'type': NS + tier + '_mixing' if tier else 'create:mixing',
                  'ingredients': inputs, 'results': outputs, 'processing_time': time}
        if heat != 'none':
            recipe['heat_requirement'] = heat
        return self.add(path, recipe, comment)

    def vat(self, path, inputs, outputs, heat='none', time=200, machines=None,
            vat='both', min_size=1, comment=''):
        vats = {'both': ['tfmg:steel_vat', 'tfmg:firebrick_lined_vat'],
                'steel': ['tfmg:steel_vat'], 'firebrick': ['tfmg:firebrick_lined_vat']}
        recipe = {'type': 'tfmg:vat_machine_recipe', 'allowed_vat_types': vats.get(vat, [vat]),
                  'ingredients': inputs, 'results': outputs, 'machines': machines or ['tfmg:mixing'],
                  'min_size': min_size, 'processing_time': time}
        if heat != 'none':
            recipe['heat_requirement'] = heat
        return self.add(path, recipe, comment)

    def arc(self, path, input, outputs, additives=None, energy=51200, time=100, comment=''):
        return self.add(path, {'type': 'immersiveengineering:arc_furnace',
                              'input': I(input) if isinstance(input, str) else input,
                              'additives': additives or [], 'results': outputs,
                              'energy': energy, 'time': time}, comment)

    def melt(self, path, input, metal, amount, temp=None, comment=''):
        fluid = self.metals[metal]['fluid']
        if temp is None:
            temp = NATIVE_MELTING_TEMPERATURES.get(metal, 1000)
        return self.add(path, {'type': 'modernfoundry:melting',
                              'ingredient': I(input) if isinstance(input, str) else input,
                              'result': {'fluid': fluid, 'amount': amount},
                              'temperature': temp, 'time': self.value('timing.melting', 80)}, comment)
