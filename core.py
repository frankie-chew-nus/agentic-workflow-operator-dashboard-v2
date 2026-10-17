"""Local A-E orchestrator. Fails closed; all artifacts are hashed."""
import csv,hashlib,json,os,sqlite3,time,uuid,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def load_local_env():
    """Load simple KEY=VALUE lines from the project .env without overwriting process env."""
    p=ROOT/".env"
    if not p.exists(): return
    for raw in p.read_text(encoding="utf-8").splitlines():
        line=raw.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        key,value=line.split("=",1)
        key=key.strip();value=value.strip().strip('"').strip("'")
        if key and key not in os.environ: os.environ[key]=value
load_local_env()

CFG=json.loads((ROOT/"config/workstreams.json").read_text(encoding="utf-8"))

def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def db():
    c=sqlite3.connect(ROOT/"operator.db",timeout=30);c.row_factory=sqlite3.Row
    c.executescript("""CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,objective TEXT,stage TEXT,state TEXT,detail TEXT,created REAL,updated REAL);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT,stage TEXT,kind TEXT,detail TEXT,ts REAL);
CREATE TABLE IF NOT EXISTS artifacts(run_id TEXT,stage TEXT,kind TEXT,path TEXT,sha256 TEXT,PRIMARY KEY(run_id,stage,kind));""")
    return c
def event(c,rid,stage,kind,detail): c.execute("INSERT INTO events(run_id,stage,kind,detail,ts) VALUES(?,?,?,?,?)",(rid,stage,kind,detail,time.time()))
def state(c,rid,stage,status,detail):
    c.execute("UPDATE runs SET stage=?,state=?,detail=?,updated=? WHERE id=?",(stage,status,detail,time.time(),rid));event(c,rid,stage,status,detail)
def artifact(c,rid,stage,kind,obj):
    d=ROOT/"artifacts"/rid;d.mkdir(parents=True,exist_ok=True);p=d/f"{stage}_{kind}.json"
    p.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding="utf-8")
    c.execute("INSERT OR REPLACE INTO artifacts VALUES(?,?,?,?,?)",(rid,stage,kind,str(p),digest(p)));return p
def read_artifact(c,rid,stage,kind):
    row=c.execute("SELECT * FROM artifacts WHERE run_id=? AND stage=? AND kind=?",(rid,stage,kind)).fetchone()
    if not row or not Path(row["path"]).exists() or digest(row["path"])!=row["sha256"]: raise ValueError("MISSING_OR_TAMPERED_ARTIFACT")
    return json.loads(Path(row["path"]).read_text(encoding="utf-8"))
def new(objective):
    if not objective.strip(): raise ValueError("Research objective required")
    rid=uuid.uuid4().hex[:12];c=db()
    with c:
        c.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?)",(rid,objective,"A","READY","Awaiting A research",time.time(),time.time()))
        event(c,rid,"A","CREATED","Research commission created")
    c.close();return rid

def call_provider(stage,prompt):
    conf=CFG[stage];provider=conf["provider"];model=conf["model"]
    if provider=="perplexity":
        key=os.getenv("PERPLEXITY_API_KEY");url="https://api.perplexity.ai/chat/completions"
        body={"model":model,"messages":[{"role":"system","content":"Return valid JSON only. Do not claim a source is verified unless you accessed and checked the original."},{"role":"user","content":prompt}]}
        if not key: raise RuntimeError("PERPLEXITY_API_KEY missing in environment")
        headers={"Authorization":"Bearer "+key}
    elif provider=="gemini":
        key=os.getenv("GEMINI_API_KEY");url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        body={"contents":[{"parts":[{"text":prompt+"\nReturn a single JSON object, no markdown."}]}],"generationConfig":{"responseMimeType":"application/json"}}
        if not key: raise RuntimeError("GEMINI_API_KEY missing in environment")
        headers={}
    else: raise RuntimeError("Provider not configured: "+provider)
    req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json",**headers},method="POST")
    with urllib.request.urlopen(req,timeout=conf.get("timeout_seconds",120)) as resp: data=json.loads(resp.read())
    text=(data.get("choices",[{}])[0].get("message",{}).get("content") if provider=="perplexity" else data.get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text",""))
    obj=json.loads(text)
    if not isinstance(obj,dict): raise ValueError("Provider output must be a JSON object")
    return obj

def research(rid):
    c=db()
    try:
        r=c.execute("SELECT * FROM runs WHERE id=?",(rid,)).fetchone()
        if not r or r["stage"]!="A" or r["state"] not in ("READY","HOLD"): raise ValueError("A is not runnable")
        with c: state(c,rid,"A","RUNNING","Perplexity source discovery")
        obj=call_provider("A","Research this objective: "+r["objective"]+". Return {\"sources\":[{\"title\":\"...\",\"url\":\"...\",\"authors\":\"...\",\"published\":\"...\",\"relevance\":\"...\",\"verification\":\"UNVERIFIED\"}],\"summary\":\"...\"}. URLs are leads, not proof. Do not invent bibliographic fields.")
        if not isinstance(obj.get("sources"),list) or not obj["sources"]: raise ValueError("NO_RESEARCH_SOURCES")
        with c: artifact(c,rid,"A","research",obj);state(c,rid,"A","WAIT_HUMAN","Review and verify original source documents; approve the A→B evidence package")
    except Exception as e:
        with c: state(c,rid,"A","HOLD",str(e)[:500])
    finally: c.close()

def approve(rid,decision,rationale):
    if len(rationale.strip())<8: raise ValueError("Human rationale must be at least 8 characters")
    if decision not in ("APPROVE","REJECT"): raise ValueError("Unknown human decision")
    c=db();r=c.execute("SELECT * FROM runs WHERE id=?",(rid,)).fetchone()
    if not r or r["state"]!="WAIT_HUMAN": c.close();raise ValueError("No pending human decision")
    st=r["stage"]
    with c:
        event(c,rid,st,"HUMAN_DECISION",json.dumps({"decision":decision,"rationale":rationale}))
        if decision=="REJECT": state(c,rid,st,"FAIL","Human rejected stage output")
        elif st=="A":
            read_artifact(c,rid,"A","research");state(c,rid,"B","READY","A evidence approved; B can synthesize")
        elif st=="B":
            read_artifact(c,rid,"B","candidates");state(c,rid,"C","READY","Candidate approved; reviewed strategy module and preflight required")
        elif st=="C":
            result=read_artifact(c,rid,"C","stage1")
            if result.get("qualified") is not True: raise ValueError("C_TO_D_BLOCKED: Stage 1 evidence does not qualify")
            state(c,rid,"D","READY","Human released frozen candidate to independent OOS")
        elif st=="D":
            result=read_artifact(c,rid,"D","oos")
            state(c,rid,"E","WAIT_HUMAN","OOS record available. Human commissioning decision required.")
        elif st=="E":
            result=read_artifact(c,rid,"D","oos")
            if result.get("qualified") is not True: raise ValueError("COMMISSION_BLOCKED: OOS evidence is not qualified")
            state(c,rid,"E","COMPLETE","Human commissioning decision recorded; no broker execution performed")
    c.close()

def synthesize(rid):
    c=db()
    try:
        r=c.execute("SELECT * FROM runs WHERE id=?",(rid,)).fetchone()
        if not r or r["stage"]!="B" or r["state"] not in ("READY","HOLD"): raise ValueError("B is not runnable")
        approved=read_artifact(c,rid,"A","research")
        with c: state(c,rid,"B","RUNNING","Gemini strategy formulation")
        obj=call_provider("B","Use only these human-approved A source records to formulate testable XAUUSD M1 hypotheses. No performance claims. Return {\"candidates\":[{\"candidate_id\":\"...\",\"hypothesis\":\"...\",\"parameter_ranges\":{\"parameter\":[1,3]},\"entry_logic\":\"...\",\"exit_logic\":\"...\",\"required_inputs\":[...],\"prohibited_dependencies\":[...],\"source_urls\":[...],\"unresolved_questions\":[...]}]}. Approved evidence: "+json.dumps(approved))
        if not isinstance(obj.get("candidates"),list) or not obj["candidates"]: raise ValueError("NO_CANDIDATES")
        with c: artifact(c,rid,"B","candidates",obj);state(c,rid,"B","WAIT_HUMAN","Review B candidate specifications and authorize one candidate")
    except Exception as e:
        with c: state(c,rid,"B","HOLD",str(e)[:500])
    finally: c.close()

def load_bars(path):
    out=[]
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f);required={"timestamp","open","high","low","close"}
        if not reader.fieldnames or not required.issubset(set(x.strip().lower() for x in reader.fieldnames)): raise ValueError("CSV requires timestamp,open,high,low,close")
        for row in reader:
            rr={k.strip().lower():v for k,v in row.items()}
            b={"timestamp":rr["timestamp"],**{k:float(rr[k]) for k in ("open","high","low","close")}}
            if not(b["low"]<=b["open"]<=b["high"] and b["low"]<=b["close"]<=b["high"]): raise ValueError("INVALID_OHLC")
            out.append(b)
    if len(out)<30: raise ValueError("DATASET_TOO_SHORT")
    ts=[b["timestamp"] for b in out]
    if ts!=sorted(set(ts)): raise ValueError("TIMESTAMPS_NOT_STRICTLY_INCREASING")
    return out
def validate_splits():
    dev=ROOT/"data"/"development.csv";oos=ROOT/"data"/"oos_restricted.csv"
    if not dev.exists() or not oos.exists(): raise ValueError("Both development.csv and oos_restricted.csv required")
    if digest(dev)==digest(oos): raise ValueError("IDENTICAL_DEVELOPMENT_AND_OOS")
    a=load_bars(dev);b=load_bars(oos)
    if not(a[-1]["timestamp"]<b[0]["timestamp"] or b[-1]["timestamp"]<a[0]["timestamp"]): raise ValueError("OVERLAPPING_DEVELOPMENT_AND_OOS")
    return a,b
def simulate(bars,signal,params):
    # Diagnostic one-bar model only; intentionally never qualifies for commissioning.
    cfg=CFG["execution"];trades=[];eq=cfg["starting_equity"];peak=eq;maxdd=0.0;daily={}
    for i in range(25,len(bars)-1):
        v=signal(bars[:i+1],params)
        if type(v) is not int or v not in (-1,0,1): raise ValueError("INVALID_SIGNAL")
        if not v: continue
        entry=bars[i+1]["open"];exitp=bars[i+1]["close"];friction=cfg["friction_pips"]*cfg["pip_size"]
        pnl=v*(exitp-entry)-friction;eq+=pnl;peak=max(peak,eq);maxdd=max(maxdd,100*(peak-eq)/peak if peak else 0)
        day=bars[i+1]["timestamp"][:10];daily[day]=daily.get(day,0)+2
        trades.append({"timestamp":bars[i+1]["timestamp"],"direction":v,"entry":entry,"exit":exitp,"pnl_after_friction":pnl})
    wins=sum(t["pnl_after_friction"] for t in trades if t["pnl_after_friction"]>0);losses=-sum(t["pnl_after_friction"] for t in trades if t["pnl_after_friction"]<0)
    return {"trade_count":len(trades),"gross_wins":wins,"gross_losses":losses,"cpc_proxy":wins/losses if losses else None,"max_drawdown_percent":maxdd,"max_daily_activities":max(daily.values(),default=0),"trades":trades}
def strategy(rid):
    p=ROOT/"strategies"/f"{rid}.py"
    if not p.exists(): raise ValueError("REVIEWED_STRATEGY_MODULE_MISSING: "+str(p))
    import importlib.util
    s=importlib.util.spec_from_file_location("reviewed_strategy_"+rid,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    if not callable(getattr(m,"signal",None)): raise ValueError("STRATEGY_MUST_DEFINE_signal(history, params)")
    return m.signal,digest(p)
def execute(rid,stage):
    c=db()
    try:
        r=c.execute("SELECT * FROM runs WHERE id=?",(rid,)).fetchone()
        if not r or r["stage"]!=stage or r["state"] not in ("READY","HOLD"): raise ValueError("STAGE_NOT_RUNNABLE")
        with c: state(c,rid,stage,"RUNNING","Checking datasets and approved artifacts")
        dev,oos=validate_splits();bars=dev if stage=="C" else oos;sig,codehash=strategy(rid)
        candidates=read_artifact(c,rid,"B","candidates")["candidates"]
        if len(candidates)!=1: raise ValueError("SELECT_ONE_CANDIDATE_BEFORE_C")
        candidate=candidates[0];params={k:v[0] for k,v in candidate["parameter_ranges"].items()}
        if stage=="D":
            prior=read_artifact(c,rid,"C","stage1")
            if prior["strategy_sha256"]!=codehash or prior["parameters"]!=params: raise ValueError("STRATEGY_OR_PARAMETERS_CHANGED_SINCE_C")
        result=simulate(bars,sig,params)
        out={k:v for k,v in result.items() if k!="trades"}
        out.update({"stage":stage,"candidate_id":candidate["candidate_id"],"strategy_sha256":codehash,"dataset_sha256":digest(ROOT/"data"/("development.csv" if stage=="C" else "oos_restricted.csv")),"parameters":params,"execution_model":"DIAGNOSTIC_ONE_BAR_NOT_COMMISSIONABLE","qualified":False,"reason":"Strategy-specific stops/position sizing and independent CPC validation not implemented"})
        with c:
            artifact(c,rid,stage,"ledger",result["trades"])
            artifact(c,rid,stage,"stage1" if stage=="C" else "oos",out)
            state(c,rid,stage,"WAIT_HUMAN","Diagnostic run complete, not a performance PASS. D/E qualification remains blocked.")
    except Exception as e:
        with c: state(c,rid,stage,"HOLD",str(e)[:500])
    finally:c.close()
def snapshot():
    c=db();rows=[dict(x) for x in c.execute("SELECT * FROM runs ORDER BY created DESC LIMIT 30")];c.close();return rows
