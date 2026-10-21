import argparse,json,os,hashlib,urllib.request,py_compile,re,datetime,shutil
from pathlib import Path
import c_controller as core

MAX_REPAIRS=4

def file_sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""):
            h.update(b)
    return h.hexdigest()

def strip_source(s):
    s=s.strip()
    m=re.search(r"```(?:json)?\s*(.*?)```",s,re.S|re.I)
    if m:s=m.group(1).strip()
    try:
        o=json.loads(s)
        if isinstance(o,dict) and isinstance(o.get("python_source"),str):
            return o["python_source"]
    except Exception:
        pass
    m=re.search(r"```(?:python)?\s*(.*?)```",s,re.S|re.I)
    return m.group(1) if m else s

def candidate(path,cid):
    r=json.load(open(path,encoding="utf-8"))
    return next(x for x in r["candidates"] if x["candidate_id"]==cid)

def green(task):
    blob=json.dumps(task,ensure_ascii=False).lower()
    blocked=["xauusd","cand-b","cpc","drawdown","9-pip","stage 1","oos",
             "risk_percent","starting_equity","profit factor","parameter range"]
    if any(x in blob for x in blocked): return False
    return any(x in blob for x in ["rolling","mean","atr","true range","numeric","moving average","pure python"])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--env",default=".env")
    p.add_argument("--spec",required=True)
    p.add_argument("--candidate",required=True)
    p.add_argument("--run-root",default="evidence/file_authoritative_runs")
    a=p.parse_args()
    core.env(a.env)

    reg=json.load(open("config/agent_registry.json",encoding="utf-8"))
    c=candidate(a.spec,a.candidate)
    rid=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    rd=Path(a.run_root)/a.candidate/rid
    ws=rd/"workspace"
    rel=rd/"release"
    ws.mkdir(parents=True,exist_ok=False)
    rel.mkdir()

    ledger=[]
    def model_call(agent_name,base,model,key,messages,purpose,payload_class):
        d=core.call(base,model,messages,key)
        u=d.get("usage") or {}
        ledger.append({
            "agent":agent_name,"model":model,"purpose":purpose,"payload_class":payload_class,
            "prompt_tokens":u.get("prompt_tokens",0) or 0,
            "completion_tokens":u.get("completion_tokens",0) or 0,
            "total_tokens":u.get("total_tokens",0) or 0
        })
        core.save(rd/"resource_ledger.json",ledger)
        return d

    ob,om,ok=core.agent(reg,"orchestrator")
    od=model_call("DMR",ob,om,ok,[
        {"role":"system","content":"Restricted lead orchestrator. Sanitize external tasks aggressively."},
        {"role":"user","content":"Decompose the frozen candidate into generic utilities safe to disclose without instrument/candidate/combined rules/parameter ranges, plus a local integration plan. JSON only: generic_tasks [{task_id,instruction}], integration_plan. Candidate:\n"+json.dumps(c,indent=2)}
    ],"DECOMPOSITION","RED_LOCAL")
    try: plan=core.parse(od["choices"][0]["message"]["content"])
    except Exception: plan={"generic_tasks":[],"integration_plan":"Implement locally."}
    core.save(rd/"decomposition.json",plan)

    parts=[];released=0;withheld=0
    for i,t in enumerate(plan.get("generic_tasks",[]),1):
        allow=green(t)
        core.save(rd/f"gateway_{i:02d}.json",{"task":t,"classification":"GREEN" if allow else "RED","released":allow})
        if not allow:
            withheld+=1
            continue
        cb,cm,ck=core.agent(reg,"coding_agent")
        d=model_call("CODING_AGENT",cb,cm,ck,[
            {"role":"system","content":"Implement only this generic utility. Return Python source only."},
            {"role":"user","content":t["instruction"]}
        ],t.get("task_id","GENERIC"),"GREEN")
        released+=1
        source=strip_source(d["choices"][0]["message"]["content"])
        cp=ws/f"component_{i:02d}.py"
        cp.write_text(source,encoding="utf-8")
        disk_hash=file_sha(cp)
        try:
            py_compile.compile(str(cp),doraise=True); state="PASS";err=None
            parts.append({"task":t,"source":cp.read_text(encoding="utf-8"),"file_sha256":disk_hash})
        except Exception as e:
            state="HOLD";err=str(e)
        core.save(rd/f"component_{i:02d}.json",{"state":state,"file_sha256":disk_hash,"error":err})

    base = """Implement COMPLETE self-contained Python strategy module.
Return JSON ONLY with one key "python_source" containing complete Python source.
Required top-level functions: metadata(), parameter_schema(), prepare(history), signal(history,prepared,params).
history is a list of completed OHLC dictionaries.
No network/files/MT5/cloud calls from the strategy module.
No account sizing, equity, friction, CPC, drawdown or PASS/FAIL.
Frozen candidate:
""" + json.dumps(c,indent=2) + "\nIntegration plan:\n" + str(plan.get("integration_plan","")) + "\nGeneric utilities:\n" + json.dumps(parts,indent=2)

    previous="";failures=[];repairs=0;last_signature=None;module_path=None
    for rev in range(1,MAX_REPAIRS+2):
        prompt=base if rev==1 else base+"\nRepair ONLY these implementation failures:\n"+json.dumps(failures)+"\nPrevious source:\n"+previous
        d=model_call("DMR",ob,om,ok,[
            {"role":"system","content":"Restricted integrator. Return requested JSON only."},
            {"role":"user","content":prompt}
        ],"INTEGRATION" if rev==1 else "REPAIR","RED_LOCAL")
        source=strip_source(d["choices"][0]["message"]["content"])
        module_path=ws/f"strategy_module_r{rev}.py"
        module_path.write_text(source,encoding="utf-8")

        # FILE BYTES ARE THE ONLY AUTHORITATIVE ARTIFACT.
        disk_hash=file_sha(module_path)
        previous=module_path.read_text(encoding="utf-8")
        try:
            py_compile.compile(str(module_path),doraise=True)
            failures=[]
        except Exception as e:
            failures=["COMPILE:"+str(e)]

        core.save(rd/f"integration_r{rev}.json",{
            "state":"PASS" if not failures else "HOLD",
            "module":str(module_path),
            "file_sha256":disk_hash,
            "failures":failures
        })
        if not failures: break
        repairs+=1
        signature=(disk_hash,tuple(failures))
        if signature==last_signature:
            failures.append("NO_REPAIR_PROGRESS")
            break
        last_signature=signature

    if failures:
        out={"state":"HOLD_FOR_HUMAN","candidate_id":c["candidate_id"],"run_id":rid,
             "failures":failures,"stage1_performance_seen":False}
        core.save(rd/"summary.json",out);print(json.dumps(out,indent=2));return

    # Atomic release from authoritative on-disk bytes.
    source_hash=file_sha(module_path)
    target=rel/"strategy_module.py"
    shutil.copy2(module_path,target)
    release_hash=file_sha(target)
    if release_hash!=source_hash:
        out={"state":"HOLD_FOR_HUMAN","reason":"RELEASE_COPY_HASH_MISMATCH",
             "source_hash":source_hash,"release_hash":release_hash}
        core.save(rd/"summary.json",out);print(json.dumps(out,indent=2));return

    release_record={
        "state":"IMPLEMENTATION_RELEASED",
        "candidate_id":c["candidate_id"],"version":c.get("version"),
        "run_id":rid,"module":"strategy_module.py","module_sha256":release_hash,
        "frozen_spec_sha256":file_sha(a.spec),
        "stage1_performance_seen":False,
        "artifact_identity_rule":"SHA-256 is calculated only from persisted file bytes."
    }
    core.save(rel/"implementation_release.json",release_record)
    verified=file_sha(target)==json.load(open(rel/"implementation_release.json",encoding="utf-8"))["module_sha256"]

    resources={
        "total_calls":len(ledger),
        "total_tokens":sum(x["total_tokens"] for x in ledger),
        "dmr_tokens":sum(x["total_tokens"] for x in ledger if x["agent"]=="DMR"),
        "coding_agent_tokens":sum(x["total_tokens"] for x in ledger if x["agent"]=="CODING_AGENT"),
        "green_released":released,"withheld":withheld,"repairs":repairs
    }
    core.save(rd/"resource_summary.json",resources)
    out={
        "state":"IMPLEMENTATION_RELEASED" if verified else "HOLD_FOR_HUMAN",
        "candidate_id":c["candidate_id"],"run_id":rid,
        "release_module":str(target),"release_record":str(rel/"implementation_release.json"),
        "module_sha256":release_hash,"release_hash_verified":verified,
        "stage1_performance_seen":False,"resources":resources
    }
    core.save(rd/"summary.json",out)
    print(json.dumps(out,indent=2))

if __name__=="__main__": main()
