"""One-time, guarded repair of the existing C builder's source-hash reporting.

The builder already writes generated Python source to disk. Its reported SHA256
must describe those exact bytes, which the existing atomic wrapper independently
verifies. Never change the wrapper or override an expected hash.
"""
import argparse,hashlib,py_compile,shutil
from pathlib import Path

OLD='hashlib.sha256(final.encode()).hexdigest()'
NEW='hashlib.sha256(mp.read_bytes()).hexdigest()'
OLD_COMPONENT='hashlib.sha256(code.encode()).hexdigest()'
NEW_COMPONENT='hashlib.sha256(cp.read_bytes()).hexdigest()'

def apply(path):
    path=Path(path)
    source=path.read_text(encoding="utf-8")
    count=source.count(OLD)
    if count==0 and source.count(NEW)>=3:
        return "ALREADY_APPLIED"
    if count!=3 or source.count(OLD_COMPONENT)!=1:
        raise RuntimeError("HOLD: unexpected builder source; no modification performed")
    updated=source.replace(OLD,NEW).replace(OLD_COMPONENT,NEW_COMPONENT)
    compile(updated,str(path),"exec")
    backup=path.with_suffix(".pre_source_hash_fix.py")
    if backup.exists():
        raise RuntimeError("HOLD: backup already exists; no modification performed")
    backup.write_bytes(path.read_bytes())
    try:
        path.write_text(updated,encoding="utf-8",newline="")
        py_compile.compile(str(path),doraise=True)
    except Exception:
        shutil.copy2(backup,path)
        raise
    return "SOURCE_HASH_FILE_BYTES_FIX_APPLIED"

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--c-root",required=True)
    a=p.parse_args()
    print(apply(Path(a.c_root)/"build_candidate_v2.py"))
