"""Qualify gzip exceptions without disabling integrity checks or editing archives."""
from pathlib import Path
import hashlib,json,zipfile,zlib
from scan_acquisition import binary_refs
H=Path(__file__).resolve().parent
R=H.parent/'client-editor-validation/runtime/mods'
original=json.loads((H/'ACQUISITION_REFERENCES.json').read_text())
rows=[]
for issue in original['errors']:
    archive=R/issue['archive'];before=hashlib.sha256(archive.read_bytes()).hexdigest()
    with zipfile.ZipFile(archive) as z:raw=z.read(issue['resource'])
    row=dict(issue,archiveSHA256=before,resourceSHA256=hashlib.sha256(raw).hexdigest())
    try:
        decoder=zlib.decompressobj(31);payload=decoder.decompress(raw)+decoder.flush()
        assert decoder.eof,'Incomplete gzip member'
        trailing=decoder.unused_data
        row.update(status='FIRST_GZIP_MEMBER_CRC_VERIFIED',trailingBytes=len(trailing),trailingHex=trailing.hex(),identifiers=binary_refs(payload),payloadBytes=len(payload))
    except (zlib.error,AssertionError) as exc:row.update(status='STILL_UNREADABLE',followupError=str(exc))
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==before
    rows.append(row)
(H/'STRUCTURE_EXCEPTIONS.json').write_text(json.dumps({'rows':rows,'scope':'First gzip member checked with normal CRC validation; no CRC bypass, archive edits, game-load claim or universal acquisition proof.'},indent=2)+'\n')
print(json.dumps(rows,indent=2))
