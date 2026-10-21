import argparse,json,hashlib,datetime,shutil,py_compile,re
from pathlib import Path
import c_controller as core

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def strip_source(s):
    s=s.strip()
    m=re.search(r"```(?:json)?\s*(.*?)```",s,re.S|re.I)
    if m:s=m.group(1).strip()
    try:
        o=json.loads(s)
        if isinstance(o,dict) and isinstance(o.get("python_source"),str): return o["python_source"]
    except Exception: pass
    m=re.search(r"```(?:python)?\s*(.*?)```",s,re.S|re.I)
    return m.group(1) if m else s

def main():
    p=argparse.ArgumentParser(description="Gate2 semantic HOLD repair -> new immutable release")
    p.add_argument("--env",default=".env");p.add_argument("--release-record",required=True)
    p.add_argument("--semantic-hold",required=True);p.add_argument("--spec",required=True)
    p.add_argument("--run-root",default="evidence/semantic_repairs")
    a=p.parse_args();core.env(a.env)

    old=json.load(open(a.release_record,encoding="utf-8"))
    old_module=Path(a.release_record).parent/old["module"]
    hold=json.load(open(a.semantic_hold,encoding="utf-8"))
    if not old_module.exists(): raise SystemExit("HOLD: prior released module missing")
    if sha(old_module)!=old["module_sha256"]: raise SystemExit("HOLD: prior release hash mismatch")
    if hold.get("state")!="SEMANTIC_GATE_HOLD": raise SystemExit("HOLD: semantic record is not a HOLD")
    if hold.get("module_sha256")!=old["module_sha256"]: raise SystemExit("HOLD: semantic HOLD does not refer to prior release")

    spec=json.load(open(a.spec,encoding="utf-8"))
    c=next(x for x in spec["candidates"] if x["candidate_id"]==old["candidate_id"])
    rid=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    rd=Path(a.run_root)/old["candidate_id"]/rid;ws=rd/"workspace";rel=rd/"release";ws.mkdir(parents=True);rel.mkdir()
    core.save(rd/"repair_authority.json",{
      "state":"AUTHORIZED_SEMANTIC_REPAIR","parent_release_sha256":old["module_sha256"],
      "semantic_hold_sha256":sha(a.semantic_hold),
      "authorized_changes":[
        "prepare(history) must derive candidate indicators from raw completed OHLC and not require precomputed atr input",
        "parameter_schema() must preserve the frozen B parameter ranges rather than collapse them to defaults"
      ],
      "prohibited_changes":["hypothesis","parameter range expansion","risk controls","friction","CPC","Stage-1 criteria"],
      "performance_data_seen":False
    })

    reg=json.load(open("config/agent_registry.json",encoding="utf-8"));base,model,key=core.agent(reg,"orchestrator")
    prompt="""Repair the prior released implementation ONLY for the deterministic semantic HOLD below.
The full frozen candidate remains authoritative.

MANDATORY REPAIR:
1. prepare(history) receives raw completed OHLC bars and must internally derive ATR/regime state. It must not require a precomputed `atr` field from the harness.
2. parameter_schema() must expose the complete frozen parameter ranges, not one default point.
3. Preserve hypothesis, entry/exit semantics and parameter boundaries exactly.
4. Do not add account sizing, friction, CPC, drawdown, PASS/FAIL, network, files, MT5 or cloud calls.
Return JSON only: {"python_source":"<complete corrected Python module>"}.

FROZEN CANDIDATE:
"""+json.dumps(c,indent=2)+"\nSEMANTIC HOLD:\n"+json.dumps(hold,indent=2)+"\nPARENT SOURCE:\n"+old_module.read_text(encoding="utf-8")
    d=core.call(base,model,[{"role":"system","content":"Restricted implementation repair agent. Make only authorized semantic-contract repairs."},{"role":"user","content":prompt}],key)
    source=strip_source(d["choices"][0]["message"]["content"])
    mp=ws/"strategy_module.py";mp.write_text(source,encoding="utf-8")
    disk_hash=sha(mp)
    failures=[]
    try:py_compile.compile(str(mp),doraise=True)
    except Exception as e:failures=["COMPILE:"+str(e)]
    core.save(rd/"repair_result.json",{"state":"PASS" if not failures else "HOLD","module_sha256":disk_hash,"failures":failures,"model":model,"usage":d.get("usage",{})})
    if failures:
        out={"state":"HOLD_FOR_HUMAN","reason":"REPAIRED_MODULE_COMPILE_FAILURE","failures":failures}
        core.save(rd/"summary.json",out);print(json.dumps(out,indent=2));return

    target=rel/"strategy_module.py";shutil.copy2(mp,target);release_hash=sha(target)
    if release_hash!=disk_hash:
        out={"state":"HOLD_FOR_HUMAN","reason":"RELEASE_COPY_HASH_MISMATCH"}
        core.save(rd/"summary.json",out);print(json.dumps(out,indent=2));return
    rec={"state":"IMPLEMENTATION_RELEASED","candidate_id":c["candidate_id"],"version":c["version"],"run_id":rid,
         "module":"strategy_module.py","module_sha256":release_hash,"parent_release_sha256":old["module_sha256"],
         "repair_basis_sha256":sha(a.semantic_hold),"frozen_spec_sha256":sha(a.spec),
         "stage1_performance_seen":False}
    core.save(rel/"implementation_release.json",rec)
    verified=sha(target)==json.load(open(rel/"implementation_release.json",encoding="utf-8"))["module_sha256"]
    out={"state":"IMPLEMENTATION_RELEASED" if verified else "HOLD_FOR_HUMAN","candidate_id":c["candidate_id"],
         "run_id":rid,"release_module":str(target),"release_record":str(rel/"implementation_release.json"),
         "module_sha256":release_hash,"parent_release_sha256":old["module_sha256"],
         "release_hash_verified":verified,"stage1_performance_seen":False,"usage":d.get("usage",{})}
    core.save(rd/"summary.json",out);print(json.dumps(out,indent=2))

if __name__=="__main__":main()
