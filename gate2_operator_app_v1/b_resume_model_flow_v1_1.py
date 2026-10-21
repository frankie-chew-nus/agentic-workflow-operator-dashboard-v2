import argparse,json,subprocess,sys
from pathlib import Path
from b_regression_guard import validate
p=argparse.ArgumentParser();p.add_argument("--db",default="evidence/operator.db");p.add_argument("--register",default=r"..\gate2_c_controller\inputs\candidate_strategy_register_v2_1_1_frozen.json");p.add_argument("--candidate",default="CAND-B-002");p.add_argument("--output-dir",default=r"evidence\b_resume\CAND-B-002");p.add_argument("--env",default=r"..\gate2_c_controller\.env");a=p.parse_args()
out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
reg=json.load(open(a.register,encoding="utf-8"));base=next(x for x in reg["candidates"] if x["candidate_id"]==a.candidate)
# parent = most recent corrected release if present, else frozen register candidate
rp=out/"b_corrected_release.json"
parent=json.load(open(rp,encoding="utf-8"))["candidate"] if rp.exists() else base
def run(cmd):
 q=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);print(q.stdout,end="")
 if q.returncode:raise SystemExit(q.returncode)
# package still derives current Human RETURN_TO_B authority from DB
run([sys.executable,"b_resume.py","--db",a.db,"--register",a.register,"--candidate",a.candidate,"--output-dir",a.output_dir])
# enrich work package with immutable parent + cumulative constraints
wp=out/"b_resume_work_package.json";w=json.load(open(wp,encoding="utf-8"));w["revision_parent"]=parent;w["required_next_version"]=__import__("b_regression_guard").bump(parent.get("version"));w["cumulative_constraints"]=["strict NR-N semantics throughout","volatility expansion = breakout candle range > average range of preceding N candles and required in long/short entry","ATR 2.0 is default/starting value within authorised 1.5-3.0 search range","preserve hypothesis/evidence/parameter ranges/inputs/prohibited dependencies"]
wp.write_text(json.dumps(w,indent=2),encoding="utf-8")
run([sys.executable,"b_model_adapter.py","--env",a.env,"--work-package",str(wp),"--output",str(out/"corrected_candidate.json")])
raw=json.load(open(out/"corrected_candidate.json",encoding="utf-8"));new=raw.get("candidate",raw)
fails=validate(parent,new,w["human_return_decision"].get("rationale",""))
if fails:
 h={"state":"GOVERNANCE_HOLD","reason":"CORRECTION_REGRESSION","failures":fails,"parent_version":parent.get("version"),"attempted_version":new.get("version")}
 (out/"b_regression_hold.json").write_text(json.dumps(h,indent=2),encoding="utf-8");print(json.dumps(h,indent=2));raise SystemExit(2)
# Only after cumulative regression guard passes do we allow ordinary boundary validation/freeze.
run([sys.executable,"b_resume.py","--db",a.db,"--register",a.register,"--candidate",a.candidate,"--corrected-candidate",str(out/"corrected_candidate.json"),"--output-dir",a.output_dir])
print(json.dumps({"state":"B_RESUME_FLOW_COMPLETE","regression_guard":"PASS","next":"Human review"},indent=2))
