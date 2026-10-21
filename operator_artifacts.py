"""Resolve authoritative workflow paths and record immutable artifact references."""
import hashlib,json
from pathlib import Path

def resolve_paths(base):
    base=Path(base).resolve()
    config=json.loads((base/"operator_paths.json").read_text(encoding="utf-8"))
    out={}
    for key,value in config["paths"].items():
        if not isinstance(value,str) or not value.strip():raise ValueError("Invalid path configuration: "+key)
        out[key]=str((base/value).resolve())
    return out

def record_artifact(run_root,role,path,required=True):
    run_root=Path(run_root).resolve()
    path=Path(path).resolve()
    if not path.is_file():
        if required:raise FileNotFoundError("Required artifact missing: "+str(path))
        return None
    data=path.read_bytes()
    entry={"role":role,"path":str(path),"sha256":hashlib.sha256(data).hexdigest(),"size_bytes":len(data)}
    registry=run_root/"artifact_registry.json"
    obj=json.loads(registry.read_text(encoding="utf-8")) if registry.exists() else {"schema_version":1,"artifacts":{}}
    prior=obj["artifacts"].get(role)
    if prior and prior!=entry:raise RuntimeError("Artifact registry conflict: "+role)
    obj["artifacts"][role]=entry
    registry.parent.mkdir(parents=True,exist_ok=True)
    registry.write_text(json.dumps(obj,indent=2),encoding="utf-8")
    return entry

def stage1_inventory(output_dir):
    root=Path(output_dir)
    if not root.is_dir():return {"state":"MISSING_OUTPUT_DIRECTORY","files":[]}
    files=[]
    for p in sorted(root.rglob("*")):
        if p.is_file():
            files.append({"path":str(p.resolve()),"size_bytes":p.stat().st_size})
    return {"state":"OUTPUT_INVENTORIED" if files else "EMPTY_OUTPUT_DIRECTORY","files":files}
