"""Candidate-driven Stage 1 plan adapter.

Builds the executable Stage 1 plan only from the frozen B candidate parameter
ranges. It never introduces strategy parameters that B did not authorize.
"""
import hashlib,json,itertools
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def _values(bounds):
    if not isinstance(bounds,list) or len(bounds)!=2: raise ValueError("parameter range must be [min,max]")
    lo,hi=bounds
    if type(lo) is int and type(hi) is int:
        if lo>hi: raise ValueError("invalid integer range")
        return list(range(lo,hi+1))
    if not all(isinstance(x,(int,float)) and not isinstance(x,bool) for x in bounds): raise ValueError("numeric range required")
    if lo>hi: raise ValueError("invalid numeric range")
    mid=(float(lo)+float(hi))/2
    return [lo,mid,hi] if lo!=hi else [lo]

def build(spec,candidate_id,config_path,output_dir):
    register=json.loads(Path(spec).read_text(encoding="utf-8"))
    def find(node):
        if isinstance(node,dict):
            if node.get("candidate_id")==candidate_id:return node
            for v in node.values():
                r=find(v)
                if r:return r
        if isinstance(node,list):
            for v in node:
                r=find(v)
                if r:return r
    candidate=find(register)
    if not candidate:raise ValueError("candidate not found")
    ranges=candidate.get("parameter_ranges")
    if not isinstance(ranges,dict) or not ranges:raise ValueError("frozen candidate has no parameter ranges")
    keys=list(ranges.keys());grids=[_values(ranges[k]) for k in keys]
    variants=[]
    for i,combo in enumerate(itertools.product(*grids),1):
        variants.append({"variant_id":f"{candidate_id}-V{i:03d}","parameters":dict(zip(keys,combo))})
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    plan={"state":"STAGE1_CANDIDATE_PLAN_FROZEN","candidate_id":candidate_id,
          "source":"FROZEN_B_PARAMETER_RANGES","parameter_names":keys,
          "variant_count":len(variants),"variants":variants,
          "spec_sha256":sha(spec)}
    path=out/"candidate_variant_plan.json"
    path.write_text(json.dumps(plan,indent=2),encoding="utf-8")
    return path,plan
