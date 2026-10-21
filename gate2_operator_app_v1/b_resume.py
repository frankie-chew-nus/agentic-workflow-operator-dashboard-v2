import argparse,json,hashlib,datetime,sqlite3
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

p=argparse.ArgumentParser(description="Governed B return/resume boundary v2")
p.add_argument("--db",required=True,help="Dispatcher SQLite DB containing Human decisions")
p.add_argument("--register",required=True,help="Frozen candidate strategy register JSON")
p.add_argument("--candidate",required=True)
p.add_argument("--corrected-candidate",help="Corrected candidate JSON from the EXISTING B reasoning process")
p.add_argument("--output-dir",required=True)
a=p.parse_args()

dbp=Path(a.db); regp=Path(a.register); out=Path(a.output_dir)
if not dbp.exists(): raise SystemExit("GOVERNANCE_HOLD: dispatcher DB not found: "+str(dbp))
if not regp.exists(): raise SystemExit("GOVERNANCE_HOLD: frozen register not found: "+str(regp))
out.mkdir(parents=True,exist_ok=True)

c=sqlite3.connect(dbp);c.row_factory=sqlite3.Row
try:
    dec=c.execute("""SELECT * FROM decisions
      WHERE candidate_id=? AND decision='RETURN_TO_B'
      ORDER BY created_at DESC LIMIT 1""",(a.candidate,)).fetchone()
except sqlite3.Error as e:
    c.close();raise SystemExit("GOVERNANCE_HOLD: decisions table unavailable: "+str(e))
c.close()
if not dec: raise SystemExit("GOVERNANCE_HOLD: no Human RETURN_TO_B authority found for "+a.candidate)
if not (dec["rationale"] or "").strip(): raise SystemExit("GOVERNANCE_HOLD: RETURN_TO_B rationale is blank")

reg=json.load(open(regp,encoding="utf-8"))
orig=next((x for x in reg.get("candidates",[]) if x.get("candidate_id")==a.candidate),None)
if not orig: raise SystemExit("GOVERNANCE_HOLD: candidate absent from frozen register")

decision_record={k:dec[k] for k in dec.keys()}
work={
 "state":"B_RESUME_PACKAGE_FROZEN",
 "candidate_id":a.candidate,
 "original_register":str(regp),
 "original_register_sha256":sha(regp),
 "human_return_decision":decision_record,
 "authority":{
   "B_may":[
     "reformulate the returned candidate",
     "reassess/rerank it within B",
     "use only the Human-approved A evidence package",
     "label B-created assumptions/inferences explicitly"
   ],
   "B_may_not":[
     "use C performance results to redesign the candidate",
     "independently retrieve new evidence",
     "silently widen the strategy/search authority",
     "send the candidate directly to C without Human release"
   ]
 },
 "original_candidate":orig,
 "created_at":now()
}
wp=out/"b_resume_work_package.json"
wp.write_text(json.dumps(work,indent=2),encoding="utf-8")

if not a.corrected_candidate:
    print(json.dumps({
      "state":"B_RESUME_PACKAGE_FROZEN",
      "candidate_id":a.candidate,
      "work_package":str(wp),
      "work_package_sha256":sha(wp),
      "return_decision_id":dec["id"] if "id" in dec.keys() else None,
      "next":"Pass this frozen package to the EXISTING B reasoning process. No provider is invoked by b_resume.py."
    },indent=2))
    raise SystemExit(0)

cp=Path(a.corrected_candidate)
if not cp.exists(): raise SystemExit("GOVERNANCE_HOLD: corrected candidate file not found")
new=json.load(open(cp,encoding="utf-8"))
if isinstance(new,dict) and "candidate" in new: new=new["candidate"]

fails=[]
# Identity/evidence/boundary continuity that this wrapper can check deterministically.
for k in ["candidate_id","research_domain","evidence_refs","prohibited_dependencies"]:
    if new.get(k)!=orig.get(k): fails.append("unauthorised_change:"+k)

required=[
 "candidate_id","version","research_domain","hypothesis","evidence_refs",
 "operator_assumptions","candle_definition","entry_logic","exit_logic",
 "parameter_ranges","required_inputs","prohibited_dependencies","unresolved_questions"
]
for k in required:
    if k not in new: fails.append("missing:"+k)

# Specific returned ambiguity: corrected B output must contain a deterministic
# volatility-expansion rule, not merely repeat the phrase.
text=json.dumps(new,ensure_ascii=False).lower()
if "volatility expansion" in text:
    deterministic_tokens=["atr","range","ratio","multiplier","threshold","standard deviation","std","percentile","rolling"]
    if not any(t in text for t in deterministic_tokens):
        fails.append("volatility_expansion_still_nondeterministic")

if fails:
    hold={
      "state":"GOVERNANCE_HOLD",
      "candidate_id":a.candidate,
      "failures":sorted(set(fails)),
      "work_package_sha256":sha(wp),
      "corrected_candidate_sha256":sha(cp),
      "created_at":now()
    }
    (out/"b_resume_validation.json").write_text(json.dumps(hold,indent=2),encoding="utf-8")
    print(json.dumps(hold,indent=2))
    raise SystemExit(2)

release={
 "state":"B_CORRECTED_AWAITING_HUMAN_RELEASE",
 "candidate_id":a.candidate,
 "parent_register_sha256":sha(regp),
 "work_package_sha256":sha(wp),
 "corrected_candidate_sha256":sha(cp),
 "candidate":new,
 "c_performance_used_by_boundary":False,
 "independent_research_performed_by_boundary":False,
 "created_at":now()
}
rp=out/"b_corrected_release.json"
rp.write_text(json.dumps(release,indent=2),encoding="utf-8")
print(json.dumps({
 "state":release["state"],
 "candidate_id":a.candidate,
 "release":str(rp),
 "release_sha256":sha(rp)
},indent=2))
