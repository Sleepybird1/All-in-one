"""Locate exact machine symbols in acquisition-related class constants; no decompilation or execution."""
from pathlib import Path
import hashlib,io,json,re,struct,zipfile
H=Path(__file__).resolve().parent;R=H.parent/'client-editor-validation/runtime/mods'
NAMES=re.compile(r'trade|loot|villag|structure|chest|quest|reward',re.I)
TOKENS={'PRECISION_SAWMILL','COMBINER','SAWING','COMBINING','precision_sawmill','combiner','sawing','combining'}
def utf8_constants(data):
    assert data[:4]==b'\xca\xfe\xba\xbe'
    count=struct.unpack_from('>H',data,8)[0];pos=10;index=1;strings=[]
    sizes={3:4,4:4,5:8,6:8,7:2,8:2,9:4,10:4,11:4,12:4,15:3,16:2,17:4,18:4,19:2,20:2}
    while index<count:
        tag=data[pos];pos+=1
        if tag==1:
            size=struct.unpack_from('>H',data,pos)[0];pos+=2;strings.append(data[pos:pos+size].decode('utf-8',errors='replace'));pos+=size
        else:pos+=sizes[tag]
        index+=2 if tag in (5,6) else 1
    return strings
rows=[];errors=[];seen=set();stats={'classesInspected':0,'archiveContentsInspected':0}
def scan(raw,origin,depth=0):
    digest=hashlib.sha256(raw).hexdigest()
    if digest in seen:return
    seen.add(digest);stats['archiveContentsInspected']+=1
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for m in z.infolist():
            if m.filename.endswith('.jar'):
                if depth>=8 or m.file_size>64*1024*1024:errors.append({'origin':origin+'!/'+m.filename,'error':'Bound'});continue
                scan(z.read(m),origin+'!/'+m.filename,depth+1)
            elif m.filename.endswith('.class') and NAMES.search(m.filename):
                stats['classesInspected']+=1
                try:
                    data=z.read(m);strings=utf8_constants(data)
                    found=sorted(set(strings)&TOKENS)
                    ids=sorted({s for s in strings if s.startswith(('mekanism:','mekanismgenerators:')) and any(t in s for t in ('saw','combin','mekanismgenerators:'))})
                    if found or ids:rows.append({'origin':origin+'!/'+m.filename,'symbols':found,'identifiers':ids,'sha256':hashlib.sha256(data).hexdigest()})
                except (AssertionError,ValueError,KeyError,IndexError,struct.error) as exc:errors.append({'origin':origin+'!/'+m.filename,'error':str(exc)})
prior=json.loads((H/'ACQUISITION_REFERENCES.json').read_text())
for archive in prior['archives']:
    p=R/archive['name'];raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==archive['sha256'];scan(raw,archive['name']);assert hashlib.sha256(p.read_bytes()).hexdigest()==archive['sha256']
out={'status':'STATIC_CLASS_REFERENCE_CANDIDATES',**stats,'matches':rows,'errors':errors,'limits':'Class names filtered for trade/loot/village/structure/chest/quest/reward; constant references are candidates, not active acquisition. Generic/indirect dispatch, other class names and reflective code are not excluded. No modified archives, recipes or execution.'}
(H/'ACQUISITION_CODE_REFERENCES.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
