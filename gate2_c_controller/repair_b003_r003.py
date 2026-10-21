import argparse,json,hashlib,datetime,re,shutil,py_compile
from pathlib import Path
import c_controller as core
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def strip(s):
 s=s.strip()
 try:
  o=json.loads(s)
  if isinstance(o,dict) and isinstance(o.get("python_source"),str):return o["python_source"]
 except:pass
 m=re.search(r"```(?:python|json)?\s*(.*?)```",s,re.S|re.I);return m.group(1) if m else s
def main():
 p=argparse.ArgumentParser();p.add_argument("--env",default=".env");p.add_argument("--release-record",required=True);p.add_argument("--spec",required=True);p.add_argument("--run-root",default="evidence/b003_r003");a=p.parse_args();core.env(a.env)
 old=json.load(open(a.release_record));parent=Path(a.release_record).parent/old["module"]
 if sha(parent)!=old["module_sha256"]:raise SystemExit("HOLD: parent hash mismatch")
 reg=json.load(open(a.spec));c=next(x for x in reg["candidates"] if x["candidate_id"]=="CAND-B-003")
 rid=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ");rd=Path(a.run_root)/c["candidate_id"]/rid;ws=rd/"workspace";rel=rd/"release";ws.mkdir(parents=True);rel.mkdir()
 auth={"state":"AUTHORIZED_IMPLEMENTATION_REPAIR","parent_release_sha256":old["module_sha256"],"performance_data_used":False,
 "authorized":["metadata id -> candidate_id","explicit invalid/no-prior-day pivot handling","compute prior-day pivots once per calendar date for efficiency"],
 "must_preserve":["prepared representation may remain dict of arrays","pivot equations","0.05% proximity","wick ratio >0.75","wick_body_ratio semantics/range","pivot_lookback fixed 1","entry direction"]}
 core.save(rd/"repair_authority.json",auth)
 agents=json.load(open("config/agent_registry.json"));base,model,key=core.agent(agents,"orchestrator")
 prompt="""Bounded repair of CAND-B-003 R002. Return JSON only {"python_source":"..."}.
Make ONLY these changes:
1 metadata returns {"candidate_id":"CAND-B-003","version":"v2.1.1"}.
2 Bars with no completed prior calendar day must be explicitly non-actionable. Use NaN pivots and/or pivot_valid boolean; signal_at returns 0 before any division if pivots invalid.
3 Improve prepare efficiency: aggregate completed OHLC once per calendar date, compute each date's pivots from the immediately previous available completed calendar date once, then map those pivots to that date's rows. Do NOT repeatedly filter the full DataFrame for every M1 row.
4 The existing prepared representation as dict/arrays is allowed. Include ohlc, pivots and preferably pivot_valid.
5 Preserve all strategy math exactly: classic pivots; range > wick_body_ratio*body; wick/range >0.75; proximity <=0.0005; long S1/S2, short R1/R2; parameter schema unchanged.
6 No future leakage and no risk/friction/performance logic.
PARENT:
"""+parent.read_text(encoding="utf-8")
 d=core.call(base,model,[{"role":"system","content":"Restricted bounded repair agent. Preserve strategy semantics."},{"role":"user","content":prompt}],key)
 code=strip(d["choices"][0]["message"]["content"]);mp=ws/"strategy_module.py";mp.write_text(code,encoding="utf-8")
 try:py_compile.compile(str(mp),doraise=True)
 except Exception as e:raise SystemExit("HOLD: compile "+str(e))
 target=rel/"strategy_module.py";shutil.copy2(mp,target)
 rec={"state":"IMPLEMENTATION_RELEASED","candidate_id":"CAND-B-003","version":"v2.1.1","run_id":rid,"module":"strategy_module.py","module_sha256":sha(target),"parent_release_sha256":old["module_sha256"],"repair_authority_sha256":sha(rd/"repair_authority.json"),"stage1_performance_seen":False}
 core.save(rel/"implementation_release.json",rec)
 out={"state":"IMPLEMENTATION_RELEASED","release_module":str(target),"release_record":str(rel/"implementation_release.json"),"module_sha256":sha(target),"parent_release_sha256":old["module_sha256"],"release_hash_verified":True,"stage1_performance_seen":False,"usage":d.get("usage",{})};core.save(rd/"summary.json",out);print(json.dumps(out,indent=2))
if __name__=="__main__":main()
