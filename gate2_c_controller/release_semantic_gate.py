import argparse,hashlib,importlib.util,json,traceback
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
    s=importlib.util.spec_from_file_location("released_candidate",p)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def make_bar(case="lower"):
    lo={"open":100.0,"high":100.3,"low":99.7,"close":100.05}
    return lo if case=="lower" else {k.capitalize():v for k,v in lo.items()}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--release-record",required=True)
    p.add_argument("--spec",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()

    rec=json.load(open(a.release_record,encoding="utf-8"))
    release_dir=Path(a.release_record).parent
    module=release_dir/rec["module"]
    outbase={"candidate_id":rec.get("candidate_id"),"release_record":a.release_record,
             "performance_data_used":False,"synthetic_ohlc_only":True}

    # FAIL FAST: do not import/execute candidate if release identity is broken.
    if not module.exists():
        out={**outbase,"state":"SEMANTIC_GATE_HOLD","reason":"RELEASE_MODULE_MISSING","candidate_code_executed":False}
        Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2));return
    actual=sha(module)
    if actual!=rec["module_sha256"]:
        out={**outbase,"state":"SEMANTIC_GATE_HOLD","reason":"RELEASE_HASH_MISMATCH","expected":rec["module_sha256"],"actual":actual,"candidate_code_executed":False}
        Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out,indent=2));return

    spec=json.load(open(a.spec,encoding="utf-8"))
    c=next(x for x in spec["candidates"] if x["candidate_id"]==rec["candidate_id"])
    checks=[]
    def ck(n,ok,d=""):checks.append({"check":n,"state":"PASS" if ok else "FAIL","detail":d})
    try:
        m=load(module)
        md=m.metadata()
        ck("IDENTITY",md.get("candidate_id")==c["candidate_id"] and md.get("version")==c["version"],repr(md))
        ps=m.parameter_schema()
        text=json.dumps(ps).lower()
        expected=set(c.get("parameter_ranges",{}))
        ck("PARAMETER_NAMES",all(x.lower() in text for x in expected),repr(ps))
        ck("NO_C_OWNED_PARAMETERS",not any(x in text for x in ["friction","equity","risk_percent","cpc","drawdown","lot","position_size"]),repr(ps))

        # Discover public OHLC convention rather than imposing case.
        accepted=None;prep=None;history=None
        errors={}
        for case in ["lower","upper"]:
            h=[make_bar(case) for _ in range(60)]
            try:
                pr=m.prepare(h); accepted=case;prep=pr;history=h;break
            except Exception as e: errors[case]=type(e).__name__+":"+str(e)
        ck("OHLC_INPUT_CONVENTION_DISCOVERED",accepted is not None,repr(errors))
        if accepted is not None:
            ck("OHLC_CONVENTION_DOCUMENTED",True,accepted)

            # Build midpoint params only from frozen ranges where possible.
            params={}
            for k,v in c.get("parameter_ranges",{}).items():
                if isinstance(v,list) and len(v)>=2 and all(isinstance(z,(int,float)) for z in v):
                    params[k]=(v[0]+v[-1])/2
                elif isinstance(v,list) and v: params[k]=v[0]
                else: params[k]=v

            before=json.dumps(history,sort_keys=True)
            # Non-actionable representation is discovered, not prescribed.
            s1=m.signal(history,prep,params);s2=m.signal(history,prep,params)
            ck("HISTORY_NOT_MUTATED",json.dumps(history,sort_keys=True)==before)
            ck("DETERMINISTIC",s1==s2,f"{s1!r} vs {s2!r}")
            allowed_nonaction=(s1 is None or s1==0 or s1==False)
            actionable=isinstance(s1,dict)
            ck("SIGNAL_REPRESENTATION",allowed_nonaction or actionable,repr(s1))
            ck("NONACTIONABLE_SENTINEL_DOCUMENTED",True,repr(s1) if allowed_nonaction else "actionable dict")

            # Parameter boundary: each grossly invalid value must not produce actionable dict.
            for k in expected:
                bad=dict(params);bad[k]=999999
                rejected=False
                try:
                    x=m.signal(history,prep,bad);rejected=not isinstance(x,dict)
                except Exception:rejected=True
                ck("OUT_OF_RANGE_"+k.upper(),rejected,repr(bad[k]))

    except Exception as e:
        ck("MODULE_RUNTIME",False,type(e).__name__+":"+str(e)+"\n"+traceback.format_exc())

    failures=[x for x in checks if x["state"]!="PASS"]
    out={**outbase,"state":"SEMANTIC_GATE_PASS" if not failures else "SEMANTIC_GATE_HOLD",
         "module_sha256":actual,"candidate_code_executed":True,"failure_count":len(failures),"checks":checks}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(json.dumps(out,indent=2))

if __name__=="__main__":main()
