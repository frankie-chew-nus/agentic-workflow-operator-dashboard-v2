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
 p=argparse.ArgumentParser();p.add_argument("--env",default=".env");p.add_argument("--release-record",required=True);p.add_argument("--spec",required=True);p.add_argument("--run-root",default="evidence/b003_repairs");a=p.parse_args();core.env(a.env)
 old=json.load(open(a.release_record));parent=Path(a.release_record).parent/old["module"]
 if sha(parent)!=old["module_sha256"]:raise SystemExit("HOLD: parent release hash mismatch")
 reg=json.load(open(a.spec));c=next(x for x in reg["candidates"] if x["candidate_id"]=="CAND-B-003")
 rid=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ");rd=Path(a.run_root)/c["candidate_id"]/rid;ws=rd/"workspace";rel=rd/"release";ws.mkdir(parents=True);rel.mkdir()
 authority={"state":"AUTHORIZED_IMPLEMENTATION_REPAIR","parent_release_sha256":old["module_sha256"],"performance_data_used":False,
 "authorized":["metadata candidate_id key","accept normalized list-of-lowercase-bar-dicts","derive calendar date from timestamp","remove undefined history reference","return prepared OHLC+pivot fields"],
 "must_preserve":["pivot equations","0.05% proximity","wick share >0.75","wick_body_ratio replaces fixed 3","wick_body_ratio range 2.0-5.0","pivot_lookback [1,1]","entry direction"]}
 core.save(rd/"repair_authority.json",authority)
 agents=json.load(open("config/agent_registry.json"));base,model,key=core.agent(agents,"orchestrator")
 prompt="""Repair ONLY implementation/interface defects in the parent CAND-B-003 module. Return JSON only {"python_source":"..."}.
Required corrections:
1 metadata() -> candidate_id CAND-B-003, version v2.1.1.
2 prepare(history,params) accepts the common market-data contract: Python list of dicts with timestamp/open/high/low/close/tick_volume/volume/spread, lowercase.
3 Convert locally to an inspectable Pandas DataFrame if useful. Derive calendar date from timestamp.
4 Previous-day pivots use ONLY the completed prior calendar day's H/L/C. Never current/future day values.
5 prepare returns/prepares OHLC plus R1,R2,S1,S2 and any pin-bar fields required by signal_at.
6 signal_at(index,prepared,params) must be O(1), must not reference an undefined/global history object, and must not inspect rows > index.
7 Preserve exact strategy mathematics: range > wick_body_ratio*abs(close-open); lower or upper wick/range >0.75; long near S1/S2, short near R1/R2; proximity <=0.0005; wick_body_ratio 2-5; pivot_lookback fixed 1.
8 No risk/friction/CPC/gates/files/network/MT5/cloud/ML/Martingale/grid/averaging-down.
PARENT SOURCE:
"""+parent.read_text(encoding="utf-8")+"\nFROZEN CANDIDATE:\n"+json.dumps(c,indent=2)
 d=core.call(base,model,[{"role":"system","content":"Restricted bounded repair agent. Correct interface/runtime defects only; preserve strategy semantics."},{"role":"user","content":prompt}],key)
 code=strip(d["choices"][0]["message"]["content"]);mp=ws/"strategy_module.py";mp.write_text(code,encoding="utf-8")
 try:py_compile.compile(str(mp),doraise=True)
 except Exception as e:
  out={"state":"HOLD_FOR_HUMAN","reason":"COMPILE_FAILURE","error":str(e)};core.save(rd/"summary.json",out);print(json.dumps(out,indent=2));return
 target=rel/"strategy_module.py";shutil.copy2(mp,target)
 if sha(target)!=sha(mp):raise SystemExit("HOLD: copy hash mismatch")
 rec={"state":"IMPLEMENTATION_RELEASED","candidate_id":"CAND-B-003","version":"v2.1.1","run_id":rid,"module":"strategy_module.py","module_sha256":sha(target),"parent_release_sha256":old["module_sha256"],"repair_authority_sha256":sha(rd/"repair_authority.json"),"stage1_performance_seen":False}
 core.save(rel/"implementation_release.json",rec)
 out={"state":"IMPLEMENTATION_RELEASED","candidate_id":"CAND-B-003","release_module":str(target),"release_record":str(rel/"implementation_release.json"),"module_sha256":sha(target),"parent_release_sha256":old["module_sha256"],"release_hash_verified":True,"stage1_performance_seen":False,"usage":d.get("usage",{})}
 core.save(rd/"summary.json",out);print(json.dumps(out,indent=2))
if __name__=="__main__":main()
