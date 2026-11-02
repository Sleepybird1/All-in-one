"""Extend static references to embedded pack data below non-root resource directories."""
from pathlib import Path
import collections,gzip,hashlib,json,zipfile
from scan_acquisition import walk,binary_refs
H=Path(__file__).resolve().parent;R=H.parent/'client-editor-validation/runtime/mods'
prior=json.loads((H/'ACQUISITION_REFERENCES.json').read_text());matches=[];errors=[];counts=collections.Counter();archives=[]
for archive in prior['archives']:
    path=R/archive['name'];assert hashlib.sha256(path.read_bytes()).hexdigest()==archive['sha256'];found=False
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.startswith('data/') or '/data/' not in name or not name.endswith(('.json','.nbt')):continue
            found=True;kind='nbt' if name.endswith('.nbt') else 'json';counts[kind]+=1
            try:
                raw=z.read(name);payload=raw
                if kind=='nbt':
                    if raw[:2]==b'\x1f\x8b':payload=gzip.decompress(raw)
                    hits=[('binary_resource_identifier',s) for s in binary_refs(payload)]
                else:hits=list(walk(json.loads(payload)))
                if hits:matches.append({'archive':archive['name'],'resource':name,'sha256':hashlib.sha256(raw).hexdigest(),'references':hits})
            except (ValueError,OSError,EOFError) as exc:errors.append({'archive':archive['name'],'resource':name,'error':str(exc)})
    assert hashlib.sha256(path.read_bytes()).hexdigest()==archive['sha256']
    if found:archives.append(archive)
out={'status':'EMBEDDED_PACK_REFERENCE_SCAN','counts':dict(counts),'archives':archives,'matches':matches,'errors':errors,'limits':'Non-root embedded data paths in top-level lab archives. Pack activation and resource priority are not inferred; no recipe edits, code execution or production access.'}
(H/'BUILTIN_PACK_REFERENCES.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({**out,'archives':len(archives)}))
