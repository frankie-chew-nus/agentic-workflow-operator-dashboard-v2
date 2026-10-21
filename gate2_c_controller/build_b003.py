import argparse,json,hashlib,datetime,re,shutil,py_compile
from pathlib import Path
import c_controller as core

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def strip_source(s):
    s=s.strip()
    try:
        o=json.loads(s)
        if isinstance(o,dict) and isinstance(o.get("python_source"),str):
            return o["python_source"]
    except Exception:
        pass
    m=re.search(r"```(?:python|json)?\s*(.*?)```",s,re.S|re.I)
    return m.group(1) if m else s

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--env",default=".env")
    ap.add_argument("--spec",required=True)
    ap.add_argument("--run-root",default="evidence/b003_builds")
    a=ap.parse_args()
    core.env(a.env)

    reg=json.load(open(a.spec,encoding="utf-8"))
    c=next(x for x in reg["candidates"] if x["candidate_id"]=="CAND-B-003")
    rid=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    rd=Path(a.run_root)/c["candidate_id"]/rid
    ws=rd/"workspace"; rel=rd/"release"
    ws.mkdir(parents=True); rel.mkdir()

    clarification={
      "candidate_id":"CAND-B-003","version":"v2.1.1",
      "operator_clarification":"wick_body_ratio replaces fixed 3 in (High-Low) > 3*abs(Close-Open) during C optimisation",
      "permitted_range":[2.0,5.0],"performance_seen":False
    }
    core.save(rd/"operator_clarification.json",clarification)

    agents=json.load(open("config/agent_registry.json",encoding="utf-8"))
    base,model,key=core.agent(agents,"orchestrator")
    prompt="""Implement frozen CAND-B-003 as an inspectable vectorized local Python module.
Return JSON only: {"python_source":"<complete source>"}.

Required interface:
- metadata()
- parameter_schema()
- prepare(history, params)
- signal_at(index, prepared, params)

Frozen/clarified semantics:
- parameter_schema preserves wick_body_ratio [2.0,5.0] and pivot_lookback [1,1].
- Human clarification: wick_body_ratio replaces the fixed 3 in:
  (High-Low) > wick_body_ratio * abs(Close-Open).
- pivot_lookback is fixed at one completed previous calendar day.
- Compute classic pivots using ONLY previous completed day's OHLC:
  P=(Hprev+Lprev+Cprev)/3
  R1=2*P-Lprev
  S1=2*P-Hprev
  R2=P+(Hprev-Lprev)
  S2=P-(Hprev-Lprev)
- Pin bar additionally requires either:
  lower wick / range > 0.75, or upper wick / range > 0.75.
- LONG only for qualifying LOWER-wick pin bar within 0.05% of S1 or S2.
- SHORT only for qualifying UPPER-wick pin bar within 0.05% of R1 or R2.
- signal_at returns +1 LONG, -1 SHORT, 0 otherwise.
- signal_at(index,...) may use only information available through index.
- prepare must expose enough fields for the harness to retrieve the signal bar high/low and relevant pivot target.
- Stop/target execution, position sizing, friction, CPC, drawdown and PASS/FAIL remain harness-owned.
- No files, network, MT5, cloud, ML, Martingale, grid or averaging-down.

Frozen candidate:
""" + json.dumps(c,indent=2)

    d=core.call(base,model,[
      {"role":"system","content":"Restricted implementation agent. Preserve frozen strategy and Operator clarification. Do not invent new parameters."},
      {"role":"user","content":prompt}
    ],key)

    src=strip_source(d["choices"][0]["message"]["content"])
    mp=ws/"strategy_module.py"
    mp.write_text(src,encoding="utf-8")
    try:
        py_compile.compile(str(mp),doraise=True)
    except Exception as e:
        out={"state":"HOLD_FOR_HUMAN","reason":"COMPILE_FAILURE","error":str(e)}
        core.save(rd/"summary.json",out); print(json.dumps(out,indent=2)); return

    target=rel/"strategy_module.py"
    shutil.copy2(mp,target)
    if sha(target)!=sha(mp):
        raise SystemExit("HOLD: release copy hash mismatch")

    rec={
      "state":"IMPLEMENTATION_RELEASED","candidate_id":c["candidate_id"],
      "version":c["version"],"run_id":rid,"module":"strategy_module.py",
      "module_sha256":sha(target),"frozen_spec_sha256":sha(a.spec),
      "operator_clarification_sha256":sha(rd/"operator_clarification.json"),
      "stage1_performance_seen":False
    }
    core.save(rel/"implementation_release.json",rec)
    out={
      "state":"IMPLEMENTATION_RELEASED","candidate_id":c["candidate_id"],
      "release_module":str(target),
      "release_record":str(rel/"implementation_release.json"),
      "module_sha256":sha(target),"release_hash_verified":sha(target)==rec["module_sha256"],
      "stage1_performance_seen":False,"usage":d.get("usage",{})
    }
    core.save(rd/"summary.json",out)
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
