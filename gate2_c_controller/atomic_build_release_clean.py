import argparse,subprocess,json,hashlib,shutil,datetime,sys
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description="Clean atomic wrapper for Gate2 C build")
    p.add_argument("--spec",required=True);p.add_argument("--candidate",required=True)
    p.add_argument("--run-root",default="evidence/atomic_runs")
    a=p.parse_args()
    rid=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    rd=Path(a.run_root)/a.candidate/rid;rd.mkdir(parents=True,exist_ok=False)
    child_work=rd/"build"
    cmd=[sys.executable,"build_candidate_v2.py","--spec",a.spec,"--candidate",a.candidate,"--workdir",str(child_work)]
    proc=subprocess.run(cmd,text=True,capture_output=True)
    (rd/"child_stdout.txt").write_text(proc.stdout,encoding="utf-8")
    (rd/"child_stderr.txt").write_text(proc.stderr,encoding="utf-8")
    if proc.returncode!=0:
        out={"state":"HOLD_FOR_HUMAN","reason":"CHILD_BUILD_PROCESS_FAILED","returncode":proc.returncode}
        (rd/"atomic_summary.json").write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2));return
    sp=child_work/a.candidate/"summary.json"
    if not sp.exists():
        out={"state":"HOLD_FOR_HUMAN","reason":"CHILD_SUMMARY_MISSING"}
        (rd/"atomic_summary.json").write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2));return
    s=json.load(open(sp,encoding="utf-8"))
    if s.get("state")!="IMPLEMENTATION_READY":
        out={"state":"HOLD_FOR_HUMAN","reason":"CHILD_NOT_IMPLEMENTATION_READY","child_state":s.get("state"),"child_summary":str(sp)}
        (rd/"atomic_summary.json").write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2));return
    module=Path(s["module"])
    if not module.exists():
        out={"state":"HOLD_FOR_HUMAN","reason":"CHILD_MODULE_MISSING","reported_module":str(module)}
        (rd/"atomic_summary.json").write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2));return
    actual=sha(module);expected=s.get("module_sha256")
    if actual!=expected:
        out={"state":"HOLD_FOR_HUMAN","reason":"SOURCE_HASH_MISMATCH","expected":expected,"actual":actual,"candidate_code_executed_downstream":False}
        (rd/"atomic_summary.json").write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2));return
    rel=rd/"release";rel.mkdir();target=rel/"strategy_module.py";shutil.copy2(module,target)
    copied=sha(target)
    if copied!=expected:
        out={"state":"HOLD_FOR_HUMAN","reason":"RELEASE_COPY_HASH_MISMATCH","expected":expected,"actual":copied}
        (rd/"atomic_summary.json").write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2));return
    rec={"state":"IMPLEMENTATION_RELEASED","candidate_id":a.candidate,"release_id":rid,"module":"strategy_module.py","module_sha256":copied,
         "source_build_summary":str(sp),"source_build_summary_sha256":sha(sp),"frozen_spec":a.spec,"frozen_spec_sha256":sha(a.spec),
         "stage1_performance_seen":False}
    rp=rel/"implementation_release.json";rp.write_text(json.dumps(rec,indent=2),encoding="utf-8")
    if sha(target)!=json.load(open(rp,encoding="utf-8"))["module_sha256"]:
        out={"state":"HOLD_FOR_HUMAN","reason":"FINAL_REVERIFY_FAILED"}
    else:
        out={"state":"IMPLEMENTATION_RELEASED","candidate_id":a.candidate,"run_id":rid,"release_module":str(target),
             "release_record":str(rp),"module_sha256":copied,"release_hash_verified":True,"stage1_performance_seen":False,
             "resources":s.get("resources",{})}
    (rd/"atomic_summary.json").write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2))

if __name__=="__main__": main()
