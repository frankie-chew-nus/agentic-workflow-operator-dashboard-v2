import argparse,json
from pathlib import Path
from model_endpoint import endpoint_config,chat,safe_endpoint
p=argparse.ArgumentParser();p.add_argument("--work-package",required=True);p.add_argument("--output",required=True);p.add_argument("--env",default=r"..\gate2_c_controller\.env");a=p.parse_args()
try:c=endpoint_config(a.env)
except Exception as e:raise SystemExit("CONFIG_HOLD: "+str(e))
wp=json.load(open(a.work_package,encoding="utf-8"))
prompt={
 "role":"B — Evidence Synthesis & Strategy Formulation",
 "task":"Reformulate only the returned ambiguity, then reassess/rerank the candidate inside B.",
 "rules":["Use only the frozen work package.","No independent research/retrieval.","Do not use C performance results.","Do not change candidate identity, research domain, evidence references or prohibited dependencies.","Do not silently widen B search authority.","Human release to C remains mandatory."],
 "return_reason":wp["human_return_decision"].get("rationale"),
 "candidate":wp["original_candidate"],
 "requirement":"Resolve the volatility-expansion ambiguity deterministically using only already-authorised inputs/search authority. If impossible within authority, return governance_hold=true.",
 "output_schema":{"governance_hold":"boolean","reason":"string|null","candidate":"complete corrected candidate object if permitted","change_note":"string","rerank_note":"string"}
}
msgs=[{"role":"system","content":"Return valid JSON only. No browsing or external retrieval. Obey the governance boundary."},{"role":"user","content":json.dumps(prompt,ensure_ascii=False)}]
try:text,protocol=chat(c,msgs,0,120)
except Exception as e:raise SystemExit("CONFIG_HOLD: configured model endpoint failed; no fallback attempted: "+repr(e))
try:
 t=text.strip()
 if t.startswith("```"):t=t.split("\n",1)[1].rsplit("```",1)[0]
 obj=json.loads(t)
except Exception as e:raise SystemExit("GOVERNANCE_HOLD: model endpoint returned invalid JSON: "+repr(e))
o=Path(a.output);o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps({"state":"B_MODEL_REASONING_COMPLETE","endpoint":safe_endpoint(c["base_url"]),"model":c["model"],"protocol_used":protocol,"fallback_used":False,"output":str(o)},indent=2))
