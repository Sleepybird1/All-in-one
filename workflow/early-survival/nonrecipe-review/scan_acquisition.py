"""Read-only installed data/structure/script references; not effective runtime loot proof."""
from pathlib import Path
import collections,gzip,hashlib,json,re,zipfile
H=Path(__file__).resolve().parent;W=H.parents[2];R=H.parent/'client-editor-validation/runtime'
TARGETS={'mekanism:precision_sawmill','mekanism:combiner'}|{f'mekanism:{tier}_{family}_factory' for tier in ('basic','advanced','elite','ultimate') for family in ('sawing','combining')}
TOKEN=re.compile(rb'(?<![a-z0-9_.:/-])(?:mekanism|mekanismgenerators):[a-z0-9_./-]+')
sha=lambda b:hashlib.sha256(b).hexdigest()
def relevant(s):return s in TARGETS or s.startswith('mekanismgenerators:')
def walk(obj,path='$'):
    if isinstance(obj,str) and relevant(obj):yield (path,obj)
    elif isinstance(obj,list):
        for i,v in enumerate(obj):yield from walk(v,f'{path}[{i}]')
    elif isinstance(obj,dict):
        for k,v in obj.items():
            if relevant(k):yield (path+'.<key>',k)
            yield from walk(v,path+'.'+k)
def binary_refs(data):return sorted({x.decode() for x in TOKEN.findall(data) if relevant(x.decode())})
def main():
    assert list(walk({'entries':[{'name':'mekanism:combiner'}]}))==[('$.entries[0].name','mekanism:combiner')]
    assert not list(walk({'name':'mekanism:combiner_extra'}))
    assert binary_refs(b'\x00\x12mekanism:combiner\x00')==['mekanism:combiner']
    assert binary_refs(b'mekanism:combiner_extra')==[]
    assert list(walk({'conditions':[{'modid':'mekanismgenerators'}],'item':'mekanismgenerators:reactor_glass'}))==[('$.item','mekanismgenerators:reactor_glass')]
    matches=[];archives=[];counts=collections.Counter();errors=[];nested=[]
    for archive in sorted((R/'mods').glob('*.jar')):
        before=sha(archive.read_bytes())
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                name=member.filename
                if name.endswith('.jar'):nested.append({'archive':archive.name,'entry':name});continue
                if not name.startswith('data/') or not name.endswith(('.json','.nbt')):continue
                kind='recipe' if '/recipe/' in name or '/recipes/' in name else 'structure' if name.endswith('.nbt') else 'loot' if '/loot_table' in name else 'tag' if '/tags/' in name else 'other_data'
                counts[kind]+=1
                try:
                    raw=z.read(member);payload=raw
                    if name.endswith('.nbt'):
                        if raw[:2]==b'\x1f\x8b':payload=gzip.decompress(raw)
                        hits=[('binary_resource_identifier',s) for s in binary_refs(payload)]
                    else:
                        if not any(s in raw for s in (b'mekanism:',b'mekanismgenerators:')):continue
                        hits=list(walk(json.loads(raw)))
                    if hits:matches.append({'archive':archive.name,'resource':name,'kind':kind,'sha256':sha(raw),'references':[{'path':p,'id':s} for p,s in hits]})
                except (ValueError,OSError,EOFError) as exc:errors.append({'archive':archive.name,'resource':name,'error':str(exc)})
        assert sha(archive.read_bytes())==before
        archives.append({'name':archive.name,'sha256':before})
    scripts=[]
    for base in (R/'kubejs',R/'config'):
        for path in sorted(base.rglob('*')):
            if not path.is_file() or path.suffix not in ('.js','.json','.toml','.snbt'):continue
            raw=path.read_bytes();counts['script_or_config']+=1;hits=binary_refs(raw)
            if hits:scripts.append({'path':str(path.relative_to(R)),'sha256':sha(raw),'identifiers':hits,'scope':'Text reference, not proof of active code or acquisition.'})
    result={'status':'STATIC_REFERENCE_SCAN','checks':5,'counts':dict(counts),'targets':sorted(TARGETS),'archives':archives,'matches':matches,'scripts':scripts,'errors':errors,'unscannedNestedJars':nested,
            'limits':'Scans top-level installed lab JAR data JSON, gzip/raw structure NBT identifiers and local kubejs/config text. Recipes are references only and unchanged. Tags/removal scripts/block self-drop entries are not independent obtainable sources. Native Java trades, dynamic code, nested JARs, condition evaluation, datapack priority, saves and production are NOT_AUDITED. No absence proof for all acquisition.'}
    (H/'ACQUISITION_REFERENCES.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'archives':len(archives),'resources':dict(counts),'matches':len(matches),'scripts':len(scripts),'errors':len(errors),'nestedJars':len(nested)}))
if __name__=='__main__':main()
