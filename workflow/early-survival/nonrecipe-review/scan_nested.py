"""Read-only recursive JAR data scan, preserving explicit decoder/size/depth gaps."""
from pathlib import Path
import collections,gzip,hashlib,io,json,zipfile
from scan_acquisition import walk,binary_refs
H=Path(__file__).resolve().parent;R=H.parent/'client-editor-validation/runtime/mods'
prior=json.loads((H/'ACQUISITION_REFERENCES.json').read_text());rows=[];hits=[];errors=[];counts=collections.Counter();seen=set()
def scan(raw,origin,depth):
    digest=hashlib.sha256(raw).hexdigest();row={'origin':origin,'sha256':digest,'bytes':len(raw),'duplicateContent':digest in seen};rows.append(row)
    if digest in seen:return
    seen.add(digest)
    if depth>8:errors.append({'origin':origin,'error':'Depth bound'});return
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for member in z.infolist():
                name=member.filename
                if member.file_size>64*1024*1024:errors.append({'origin':origin+'!/'+name,'error':'64MiB member bound'});continue
                if name.endswith('.jar'):scan(z.read(member),origin+'!/'+name,depth+1);continue
                if not name.startswith('data/') or not name.endswith(('.json','.nbt')):continue
                counts['nbt' if name.endswith('.nbt') else 'json']+=1
                try:
                    payload=z.read(member)
                    if name.endswith('.nbt'):
                        if payload[:2]==b'\x1f\x8b':payload=gzip.decompress(payload)
                        found=[('binary_resource_identifier',s) for s in binary_refs(payload)]
                    else:found=list(walk(json.loads(payload)))
                    if found:hits.append({'origin':origin+'!/'+name,'references':found})
                except (ValueError,OSError,EOFError) as exc:errors.append({'origin':origin+'!/'+name,'error':str(exc)})
    except zipfile.BadZipFile as exc:errors.append({'origin':origin,'error':str(exc)})
for outer in prior['archives']:
    path=R/outer['name'];assert hashlib.sha256(path.read_bytes()).hexdigest()==outer['sha256']
    with zipfile.ZipFile(path) as z:
        for member in z.infolist():
            if member.filename.endswith('.jar'):
                if member.file_size>64*1024*1024:errors.append({'origin':outer['name']+'!/'+member.filename,'error':'64MiB member bound'})
                else:scan(z.read(member),outer['name']+'!/'+member.filename,1)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==outer['sha256']
out={'status':'NESTED_STATIC_REFERENCE_SCAN','archiveOccurrences':len(rows),'uniqueArchives':len(seen),'counts':dict(counts),'archives':rows,'matches':hits,'errors':errors,'limits':'Data references only. No code-generated trade/acquisition, runtime condition/priority evaluation, source enabling, recipe changes or production access.'}
(H/'NESTED_REFERENCES.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('archives',)}))
