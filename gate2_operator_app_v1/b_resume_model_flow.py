import argparse,subprocess,sys,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--db",default="evidence/state.db");p.add_argument("--register",default=r"..\gate2_c_controller\inputs\candidate_strategy_register_v2_1_1_frozen.json");p.add_argument("--candidate",default="CAND-B-002");p.add_argument("--output-dir",default=r"evidence\b_resume\CAND-B-002");p.add_argument("--env",default=r"..\gate2_c_controller\.env");a=p.parse_args()
out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
def run(cmd):
 q=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);print(q.stdout,end="")
 if q.returncode:raise SystemExit(q.returncode)
run([sys.executable,"b_resume.py","--db",a.db,"--register",a.register,"--candidate",a.candidate,"--output-dir",a.output_dir])
run([sys.executable,"b_model_adapter.py","--env",a.env,"--work-package",str(out/"b_resume_work_package.json"),"--output",str(out/"corrected_candidate.json")])
run([sys.executable,"b_resume.py","--db",a.db,"--register",a.register,"--candidate",a.candidate,"--corrected-candidate",str(out/"corrected_candidate.json"),"--output-dir",a.output_dir])
print(json.dumps({"state":"B_RESUME_FLOW_COMPLETE","candidate_id":a.candidate,"fallback_used":False,"next":"Human review/release to C"},indent=2))
