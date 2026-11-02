"""Read-only, standard-library Anvil/NBT block-state comparison for disposable worlds."""
import argparse
import collections
import gzip
import io
import json
import math
import pathlib
import struct
import zlib


class Nbt:
    def __init__(self, data):
        self.f = io.BytesIO(data)

    def unpack(self, fmt):
        return struct.unpack(fmt, self.f.read(struct.calcsize(fmt)))[0]

    def string(self):
        return self.f.read(self.unpack('>H')).decode('utf-8')

    def value(self, kind):
        if kind in (1, 2, 3, 4, 5, 6):
            return self.unpack({1:'>b', 2:'>h', 3:'>i', 4:'>q', 5:'>f', 6:'>d'}[kind])
        if kind == 7:
            return self.f.read(self.unpack('>i'))
        if kind == 8:
            return self.string()
        if kind == 9:
            item_kind, length = self.unpack('>B'), self.unpack('>i')
            return [self.value(item_kind) for _ in range(length)]
        if kind == 10:
            values = {}
            while (child := self.unpack('>B')) != 0:
                name = self.string()
                values[name] = self.value(child)
            return values
        if kind in (11, 12):
            return [self.unpack('>i' if kind == 11 else '>q') for _ in range(self.unpack('>i'))]
        raise ValueError(f'Unsupported NBT tag {kind}')

    def root(self):
        kind = self.unpack('>B')
        self.string()
        return self.value(kind)


def chunk(world, x, z):
    path = world / 'region' / f'r.{x//32}.{z//32}.mca'
    with path.open('rb') as f:
        f.seek(4 * ((x % 32) + 32 * (z % 32)))
        address = int.from_bytes(f.read(4), 'big')
        if not address:
            raise ValueError(f'Chunk {x},{z} absent from {path}')
        f.seek((address >> 8) * 4096)
        size = int.from_bytes(f.read(4), 'big')
        codec = f.read(1)[0]
        data = f.read(size-1)
    if codec == 2:
        data = zlib.decompress(data)
    elif codec == 1:
        data = gzip.decompress(data)
    elif codec != 3:
        raise ValueError(f'Unsupported region compression {codec}')
    root = Nbt(data).root()
    assert root['xPos'] == x and root['zPos'] == z
    result = {}
    for section in root['sections']:
        states = section.get('block_states')
        if not states:
            continue
        palette = [p['Name'] + (json.dumps(p['Properties'], sort_keys=True) if p.get('Properties') else '') for p in states['palette']]
        bits = max(4, (len(palette)-1).bit_length())
        per_long = 64 // bits
        packed = states.get('data', [])
        for i in range(4096):
            index = ((packed[i//per_long] & ((1<<64)-1)) >> ((i%per_long)*bits)) & ((1<<bits)-1) if packed else 0
            pos = (x*16+(i&15), section['Y']*16+(i>>8), z*16+((i>>4)&15))
            result[pos] = palette[index]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', type=pathlib.Path)
    args = parser.parse_args()
    report = json.loads((args.stage/'terrain-report-a.json').read_text())
    transitions = collections.Counter()
    geology = []
    for request in report['requestOrder']:
        a = chunk(args.stage/'terrain-worlds/terrain-a', request['x'], request['z'])
        b = chunk(args.stage/'terrain-worlds/terrain-b', request['x'], request['z'])
        for pos in sorted(a.keys() | b.keys()):
            before, after = a.get(pos, 'minecraft:air'), b.get(pos, 'minecraft:air')
            if before != after:
                transitions[(before, after)] += 1
                if 'industrial_colonies:' in before or 'industrial_colonies:' in after:
                    geology.append({'pos':pos, 'a':before, 'b':after, 'localX':pos[0]%16, 'localZ':pos[2]%16})
    print(json.dumps({'allTargetChunkBlockTransitions':[{'a':a,'b':b,'count':n} for (a,b),n in transitions.most_common()],
                      'geologyDifferenceCount':len(geology), 'geologyDifferences':geology}, indent=2))


if __name__ == '__main__':
    main()
