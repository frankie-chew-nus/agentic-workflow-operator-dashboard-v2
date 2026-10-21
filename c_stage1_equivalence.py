"""Validate bounded-history Stage 1 against full completed-history semantics.

This is a validation harness only. It never modifies the released strategy,
Stage 1 results, frozen B specification, or parameter plan.
"""
import argparse,hashlib,importlib.util,json,sys,time
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadmod(p):
    s=importlib.util.spec_from_file_location("equivalence_strategy",p)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def save(p,o): Path(p).write_text(json.dumps(o,indent=2),encoding="utf-8")

def main():
    p=argparse.ArgumentParser()
    for n in ("plan","manifest","release-record","semantic-pass","stage1-summary","output"):p.add_argument("--"+n,required=True)
    p.add_argument("--sample-bars",type=int,default=600)
    a=p.parse_args();plan=json.load(open(a.plan));man=json.load(open(a.manifest));rec=json.load(open(a.release_record));sem=json.load(open(a.semantic_pass));s1=json.load(open(a.stage1_summary))
    mp=Path(a.release_record).parent/rec["module"]
    identity={"release_hash":sha(mp)==rec.get("module_sha256"),
              "semantic_hash":sem.get("module_sha256")==rec.get("module_sha256") and sem.get("state")=="SEMANTIC_GATE_PASS",
              "stage1_release_hash":s1.get("release_sha256")==rec.get("module_sha256"),
              "bounded_model":s1.get("execution_model")=="BOUNDED_COMPLETED_HISTORY"}
    if not all(identity.values()):
        out={"state":"C_STAGE1_EQUIVALENCE_HOLD","identity":identity,"reason":"IDENTITY_OR_EXECUTION_MODEL_MISMATCH"};save(a.output,out);print(json.dumps(out,indent=2));raise SystemExit(20)
    croot=Path(a.manifest).resolve().parents[2]
    if str(croot) not in sys.path:sys.path.insert(0,str(croot))
    from market_data.policy import create_source
    bars=create_source("C","CSV",path=man["raw_file"]).get_bars()
    bars=[{**b,"Open":b.get("Open",b.get("open")),"High":b.get("High",b.get("high")),"Low":b.get("Low",b.get("low")),"Close":b.get("Close",b.get("close"))} for b in bars]
    m=loadmod(mp);window=int(s1["history_window"]);sample=min(a.sample_bars,len(bars)-window)
    # Use a late contiguous segment so full-history calls contain substantial prior
    # history while bounded calls see exactly the production Stage 1 window.
    end=len(bars);start=max(window-1,end-sample)
    mismatches=[];checked=0;t0=time.time()
    for v in plan["variants"]:
        params=v["parameters"]
        for i in range(start,end):
            full=bars[:i+1];bounded=bars[i-window+1:i+1]
            sf=m.signal(full,m.prepare(full),params)
            sb=m.signal(bounded,m.prepare(bounded),params)
            checked+=1
            if sf!=sb:
                mismatches.append({"variant_id":v["variant_id"],"bar_index":i,"full_signal":sf,"bounded_signal":sb})
                if len(mismatches)>=25:break
        if mismatches:break
    out={"state":"C_STAGE1_EXECUTION_EQUIVALENCE_PASS" if not mismatches else "C_STAGE1_EXECUTION_EQUIVALENCE_HOLD",
         "candidate_id":rec.get("candidate_id"),"module_sha256":rec.get("module_sha256"),
         "history_window":window,"sample_start_index":start,"sample_end_index":end-1,
         "sample_bars":end-start,"variants_planned":len(plan["variants"]),"comparisons":checked,
         "signal_mismatch_count":len(mismatches),"mismatches":mismatches,
         "elapsed_seconds":round(time.time()-t0,3),"identity":identity,
         "criterion":"ZERO_SIGNAL_MISMATCHES_REQUIRED"}
    save(a.output,out);print(json.dumps(out,indent=2))
    raise SystemExit(0 if not mismatches else 21)
if __name__=="__main__":main()
