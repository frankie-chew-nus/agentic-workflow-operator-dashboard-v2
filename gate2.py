import json,sqlite3,datetime,uuid,subprocess,threading,webbrowser,html,sys,hashlib
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import parse_qs

BASE=Path(__file__).resolve().parent
DB=BASE/'evidence'/'operator.db'
PROJECT=BASE.parent
from operator_artifacts import resolve_paths
OPERATOR_PATHS=resolve_paths(BASE)
CROOT=Path(OPERATOR_PATHS['c_engine'])
LEGACY_OPERATOR=Path(OPERATOR_PATHS['b_engine'])
PORT=8787

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load_json(p):
    try: return json.load(open(p,encoding='utf-8')) if Path(p).exists() else None
    except Exception: return None

def cx():
    DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB,timeout=30);c.row_factory=sqlite3.Row
    c.executescript("""CREATE TABLE IF NOT EXISTS research(id TEXT PRIMARY KEY,title TEXT,state TEXT,stage TEXT);
CREATE TABLE IF NOT EXISTS candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,stage TEXT,version TEXT,detail TEXT,q INTEGER);
CREATE TABLE IF NOT EXISTS decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT);
CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,kind TEXT,state TEXT,detail TEXT,log_path TEXT,created_at TEXT,started_at TEXT,finished_at TEXT,return_code INTEGER);
CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY,candidate_id TEXT,kind TEXT,path TEXT,sha256 TEXT,created_at TEXT);""")
    return c

def decision(c,rid,cid,d,rat): c.execute('INSERT INTO decisions VALUES(?,?,?,?,?,?)',('DEC-'+uuid.uuid4().hex[:10].upper(),rid,cid,d,rat,now()))
def reconcile_orphan_jobs(c):
    # Jobs are executed only by this dashboard process. After a process restart,
    # any persisted RUNNING row is historical evidence, not proof of a live child.
    rows=list(c.execute("SELECT * FROM jobs WHERE state='RUNNING'"))
    for j in rows:
        c.execute("UPDATE jobs SET state='INTERRUPTED',finished_at=?,return_code=? WHERE id=?",(now(),-999,j['id']))
        x=c.execute("SELECT * FROM candidates WHERE id=?",(j['candidate_id'],)).fetchone()
        if x and str(j['kind']).startswith('C_'):
            c.execute("UPDATE candidates SET state='C_SYSTEM_HOLD',stage='C',detail=? WHERE id=?",
                      ('Previous C execution was interrupted by dashboard/process shutdown; preserved as '+j['id']+'. Fresh governed retry required.',j['candidate_id']))
            runroot=BASE/'evidence'/'c_runs'/j['candidate_id']/(x['version'] or '')
            progress=runroot/'stage1_output'/'progress.json'
            if progress.exists():
                archive=runroot/('interrupted_progress_'+j['id']+'.json')
                try: progress.replace(archive)
                except OSError: pass

def init():
    c=cx()
    reconcile_orphan_jobs(c)
    if not c.execute('SELECT 1 FROM research').fetchone():
        rid='RES-XAUUSD';c.execute('INSERT INTO research VALUES(?,?,?,?)',(rid,'XAUUSD M1 Price Action','ACTIVE','B'))
        for x in [('CAND-B-001','C_FAIL','C','v2.1.1','0/50 PASS',1),('CAND-B-002','B_REVIEW','B','v2.1.2','Corrected B release awaiting Human review',2),('CAND-B-003','C_FAIL','C','v2.1.1','0/7 PASS',3)]: c.execute('INSERT INTO candidates VALUES(?,?,?,?,?,?,?)',(x[0],rid,x[1],x[2],x[3],x[4],x[5]))
        decision(c,rid,'CAND-B-002','RETURN_TO_B','Volatility expansion is not deterministically defined. Return to B for a corrected specification before C implementation.')
    # Durable Start-C authority resumes automatically after dashboard updates/restarts.
    x=c.execute("SELECT * FROM candidates WHERE id='CAND-B-002'").fetchone()
    if x and x['state']=='C_START_COMMISSIONED' and not active_job(c):
        queue(c,'RES-XAUUSD','CAND-B-002','C_RUN','Governed C workflow: boundary → build → semantic gate → plan freeze → Stage 1')
    c.commit();c.close()

def active_job(c): return c.execute("SELECT * FROM jobs WHERE state IN ('QUEUED','RUNNING') ORDER BY created_at LIMIT 1").fetchone()
def queue(c,rid,cid,kind,detail):
    if active_job(c): return False
    jid='JOB-'+uuid.uuid4().hex[:10].upper();log=BASE/'evidence'/'logs'/(jid+'.log');log.parent.mkdir(parents=True,exist_ok=True)
    c.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?,?,?,?)',(jid,rid,cid,kind,'QUEUED',detail,str(log),now(),None,None,None));return True

def failed_rule_instruction():
    hold=regression_hold() or {}
    if hold.get('reason')!='CORRECTION_REGRESSION': return None
    mapping={
      'VERSION_MUST_BE':'Increment to the required next immutable patch version.',
      'STRICT_NR_N_NOT_PRESERVED':'Preserve strict < NR-N semantics consistently throughout.',
      'VOLATILITY_EXPANSION_RULE_MISSING':'Restore the deterministic rule: breakout candle range > average range of the preceding N candles.',
      'VOLATILITY_EXPANSION_NOT_IN_ENTRY':'Require volatility-expansion confirmation in both long and short entry logic.',
      'ATR_DEFAULT_SEARCH_RELATION_NOT_PRESERVED':'Preserve ATR(14) multiplier 2.0 as default/start within the authorized 1.5-3.0 range.'
    }
    items=[]
    for f in hold.get('failures',[]):
        key=str(f).split(':',1)[0];items.append(mapping.get(key,'Correct failed contract rule: '+str(f)))
    return 'Correction is limited to these failed revision-contract rules. Preserve every passing rule and all previously accepted requirements. ' + ' '.join(items) + ' No other changes are authorized.'

def sync_b_authority_to_existing_workflow(candidate_id):
    # The dashboard owns the new Human decision; the existing B boundary reads its own
    # workflow DB for RETURN_TO_B authority. Bridge the decision without migrating workflow logic.
    dc=cx()
    d=dc.execute("SELECT * FROM decisions WHERE candidate_id=? ORDER BY created_at DESC LIMIT 1",(candidate_id,)).fetchone()
    dc.close()
    if not d: raise RuntimeError('No dashboard Human decision found for '+candidate_id)
    workflow_db=LEGACY_OPERATOR/'evidence'/'operator.db'
    if not workflow_db.exists(): workflow_db=LEGACY_OPERATOR/'evidence'/'state.db'
    if not workflow_db.exists(): raise FileNotFoundError('Existing workflow decision DB not found')
    wc=sqlite3.connect(workflow_db); wc.row_factory=sqlite3.Row
    mapped='RETURN_TO_B' if d['decision'] in ('RETURN_TO_B','RETURN_FAILED_RULES','RETRY_B','RESUME_B') else d['decision']
    bridge_id='DASH-'+d['id']
    exists=wc.execute("SELECT 1 FROM decisions WHERE id=?",(bridge_id,)).fetchone()
    if not exists:
        wc.execute("INSERT INTO decisions(id,research_id,candidate_id,decision,rationale,created_at) VALUES(?,?,?,?,?,?)",
                   (bridge_id,d['research_id'],candidate_id,mapped,d['rationale'],d['created_at']))
        wc.commit()
    wc.close()
    return workflow_db

def deterministic_b_patch_from_failed_rules(candidate_id):
    # Patch-based correction: preserve the last valid candidate and deterministically
    # apply only contract repairs already authorized by Human decisions.
    rel=review_data() or {}
    parent=rel.get('candidate')
    hold=regression_hold() or {}
    if not parent or hold.get('reason')!='CORRECTION_REGRESSION': return None
    import copy,re
    new=copy.deepcopy(parent)
    failures=set(str(x).split(':',1)[0] for x in hold.get('failures',[]))
    # Versioning belongs to the controller, never the model.
    m=re.fullmatch(r'v(\d+)\.(\d+)\.(\d+)',str(parent.get('version','')))
    if not m: raise RuntimeError('Cannot deterministically increment candidate version')
    new['version']=f"v{m.group(1)}.{m.group(2)}.{int(m.group(3))+1}"
    ass=new.setdefault('operator_assumptions',{})
    if 'STRICT_NR_N_NOT_PRESERVED' in failures:
        ass['narrow_range_definition']='Current candle range (High - Low) is strictly less than the range of each of the prior N candles; N is searched only within 5-10 in C.'
        new['candle_definition']='NR-N candle: current (High - Low) < (High - Low) for every candle in {t-1, t-2, ..., t-N}, where N is bounded to 5-10.'
    if 'VOLATILITY_EXPANSION_RULE_MISSING' in failures:
        ass['volatility_expansion_definition']='The range (High - Low) of the breakout candle must be greater than the average range (High - Low) of the preceding N candles used to identify the NR-N pattern.'
    if 'VOLATILITY_EXPANSION_NOT_IN_ENTRY' in failures:
        new['entry_logic']='Enter long if price exceeds High of the identified NR-N candle + breakout_buffer AND breakout candle range > average range of the preceding N candles; enter short if price falls below Low of the identified NR-N candle - breakout_buffer AND breakout candle range > average range of the preceding N candles.'
    if 'ATR_DEFAULT_SEARCH_RELATION_NOT_PRESERVED' in failures:
        new['exit_logic']='Trailing stop based on 2.0 * ATR(14) from current price; 2.0 is the default/starting value within the authorized trailing_atr_multiplier search range 1.5-3.0.'
    return {'candidate':new,'patch_mode':'DETERMINISTIC_CONTRACT_REPAIR','parent_version':parent.get('version'),'applied_failures':sorted(failures)}

def write_deterministic_patch(candidate_id):
    obj=deterministic_b_patch_from_failed_rules(candidate_id)
    if not obj: return None
    out=LEGACY_OPERATOR/'evidence'/'b_resume'/candidate_id/'corrected_candidate.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(obj,indent=2),encoding='utf-8')
    return out

def b_flow_cmd():
    # Dashboard orchestrates the already-proven B adapter; it does not migrate/reimplement it.
    import os
    configured=os.environ.get('GATE2_B_ADAPTER')
    candidates=[
        Path(configured) if configured else None,
        LEGACY_OPERATOR/'b_resume_model_flow_v1_1.py',
        LEGACY_OPERATOR/'b_resume_model_flow.py'
    ]
    flow=next((p for p in candidates if p and p.exists()),None)
    if not flow:
        raise FileNotFoundError('Existing B adapter not found. Expected gate2_operator_app_v1\\b_resume_model_flow_v1_1.py (or set GATE2_B_ADAPTER).')
    # Keep B adapter state/evidence with the existing workflow location.
    workflow_db=sync_b_authority_to_existing_workflow('CAND-B-002')
    return [sys.executable,str(flow),'--db',str(workflow_db),'--register',str(CROOT/'inputs'/'candidate_strategy_register_v2_1_1_frozen.json'),'--candidate','CAND-B-002','--output-dir',str(LEGACY_OPERATOR/'evidence'/'b_resume'/'CAND-B-002'),'--env',str(CROOT/'.env')]

def c_cli_candidates():
    return [
      CROOT/'build_candidate_v2.py',
      CROOT/'semantic_gate_v2.py',
      CROOT/'stage1_runner_v3.py'
    ]

def c_preflight_cmd():
    # Read-only discovery of the existing authoritative C CLI contracts.
    # --help must not build, mutate, or backtest a candidate.
    missing=[str(p) for p in c_cli_candidates() if not p.exists()]
    if missing: raise FileNotFoundError('Existing C CLI component(s) not found: '+', '.join(missing))
    script=BASE/'c_preflight.py'
    if not script.exists(): raise FileNotFoundError('Dashboard C preflight adapter missing: '+str(script))
    return [sys.executable,str(script),'--c-root',str(CROOT)]

def c_run_cmd(candidate):
    script=BASE/'c_controller.py'
    runroot=BASE/'evidence'/'c_runs'/candidate['id']/candidate['version']
    log=BASE/'evidence'/'logs'/('C-RUN-'+candidate['id']+'-'+candidate['version'].replace('.','_')+'.log')
    return [sys.executable,str(script),'--c-root',str(CROOT),'--legacy-evidence',str(external_evidence_root()),'--candidate',candidate['id'],'--version',candidate['version'],'--run-root',str(runroot),'--log',str(log)]

def c_run_log(candidate):
    p=BASE/'evidence'/'logs'/('C-RUN-'+candidate['id']+'-'+candidate['version'].replace('.','_')+'.log')
    return p

def c_source_diagnosis(candidate):
    return load_json(BASE/'evidence'/'c_runs'/candidate['id']/candidate['version']/'source_authority_diagnosis.json')

def run_c_source_diagnosis(candidate):
    script=BASE/'c_source_diagnose.py'
    root=BASE/'evidence'/'c_runs'/candidate['id']/candidate['version']
    q=subprocess.run([sys.executable,str(script),'--run-root',str(root),'--c-root',str(CROOT)],cwd=BASE,capture_output=True,text=True,timeout=30)
    if q.returncode: raise RuntimeError(q.stderr or q.stdout)
    return c_source_diagnosis(candidate)

def c_source_provenance(candidate):
    runroot=BASE/'evidence'/'c_runs'/candidate['id']/candidate['version']
    script=BASE/'c_source_provenance.py'
    evidence=runroot/'source_provenance_inspection.json'
    if not evidence.exists():
        q=subprocess.run([sys.executable,str(script),'--c-root',str(CROOT),'--run-root',str(runroot)],cwd=BASE,capture_output=True,text=True,timeout=30)
        if q.returncode: raise RuntimeError(q.stderr or q.stdout)
    return load_json(evidence)

def c_source_authority_analysis(candidate):
    runroot=BASE/'evidence'/'c_runs'/candidate['id']/candidate['version']
    from c_source_authority import diagnose
    return diagnose(runroot)

def c_stage1_diagnosis(candidate):
    from c_stage1_diagnose import diagnose
    root=BASE/'evidence'/'c_runs'/candidate['id']/candidate['version']
    return diagnose(root,c_run_log(candidate))

def c_stage1_review(candidate):
    from c_stage1_evidence import inspect
    return inspect(c_run_summary(candidate) or {})

def c_hold_html(candidate):
    summary=c_run_summary(candidate) or {}
    log=c_run_log(candidate)
    reason=summary.get('error') or summary.get('state') or candidate['detail']
    bits=['<div class="stage-work hold"><h3>ACTION REQUIRED — C SYSTEM HOLD</h3>',
          '<p><b>Reason:</b> '+html.escape(str(reason))+'</p>']
    if log.exists(): bits.append(expandable_log(str(log)))
    bits.append(spec_details('View C run summary',summary))
    boundary=BASE/'evidence'/'c_runs'/candidate['id']/candidate['version']/'c_boundary.json'
    if boundary.exists(): bits.append(spec_details('View frozen C boundary',load_json(boundary)))
    bits.append(form_buttons([('RETRY_C','Retry governed C workflow'),('RETURN_C_TO_B','Return to B'),('REJECT','Reject candidate')],'Human rationale for C recovery decision'))
    bits.append('</div>')
    return ''.join(bits)

def c_run_summary(candidate):
    return load_json(BASE/'evidence'/'c_runs'/candidate['id']/candidate['version']/'c_run_summary.json')

def c_preflight_evidence():
    return load_json(BASE/'evidence'/'c_preflight.json')

def c_prepare_discovery_cmd():
    script=BASE/'c_prepare_discovery.py'
    if not script.exists(): raise FileNotFoundError('C preparation discovery adapter missing')
    return [sys.executable,str(script),'--c-root',str(CROOT)]

def c_prepare_discovery_evidence():
    return load_json(BASE/'evidence'/'c_preparation_discovery.json')

def dispatcher():
    while True:
        try:
            c=cx();j=c.execute("SELECT * FROM jobs WHERE state='QUEUED' ORDER BY created_at LIMIT 1").fetchone()
            if not j: c.close();threading.Event().wait(1);continue
            c.execute("UPDATE jobs SET state='RUNNING',started_at=? WHERE id=?",(now(),j['id']))
            if str(j['kind']).startswith('C_'):
                c.execute("UPDATE candidates SET state='C_RUNNING',stage='C',detail=? WHERE id=?",(j['detail'],j['candidate_id']))
            else:
                c.execute("UPDATE candidates SET state='B_RUNNING',stage='B',detail='Governed B correction via configured model endpoint' WHERE id=?",(j['candidate_id'],))
            c.commit();c.close()
            if j['kind']=='C_RUN':
                dc=cx();cand=dc.execute("SELECT * FROM candidates WHERE id=?",(j['candidate_id'],)).fetchone();dc.close()
                cmd=c_run_cmd(cand)
            elif j['kind']=='C_PREP_DISCOVERY':
                cmd=c_prepare_discovery_cmd()
            elif j['kind']=='C_PREFLIGHT':
                cmd=c_preflight_cmd()
            else:
                latest=cx();ld=latest.execute("SELECT decision FROM decisions WHERE candidate_id=? ORDER BY created_at DESC LIMIT 1",(j['candidate_id'],)).fetchone();latest.close()
                if ld and ld['decision']=='RETURN_FAILED_RULES':
                    patched=write_deterministic_patch(j['candidate_id'])
                    if not patched: raise RuntimeError('Patch-mode repair requested but no regression evidence/parent release is available')
                    flow_dir=LEGACY_OPERATOR
                    workflow_db=sync_b_authority_to_existing_workflow(j['candidate_id'])
                    cmd=[sys.executable,str(flow_dir/'b_resume.py'),'--db',str(workflow_db),'--register',str(CROOT/'inputs'/'candidate_strategy_register_v2_1_1_frozen.json'),'--candidate',j['candidate_id'],'--corrected-candidate',str(patched),'--output-dir',str(flow_dir/'evidence'/'b_resume'/j['candidate_id'])]
                else:
                    cmd=b_flow_cmd()
            with open(j['log_path'],'w',encoding='utf-8') as f: q=subprocess.run(cmd,cwd=Path(cmd[1]).parent,stdout=f,stderr=subprocess.STDOUT,text=True)
            c=cx();c.execute("UPDATE jobs SET state='COMPLETE',finished_at=?,return_code=? WHERE id=?",(now(),q.returncode,j['id']))
            if j['kind']=='C_RUN':
                dc=cx();cand=dc.execute("SELECT * FROM candidates WHERE id=?",(j['candidate_id'],)).fetchone();dc.close();ev=c_run_summary(cand) or {}
                st=ev.get('state','C_SYSTEM_HOLD')
                detail={'C_PASS':'Stage 1 PASS; Human review required before D','C_FAIL':'Stage 1 FAIL; candidate withheld from D','C_STAGE1_REVIEW_REQUIRED':'Stage 1 evidence verified; Human review required','C_STAGE1_EVIDENCE_HOLD':'Stage 1 evidence missing or ambiguous; D blocked','C_STAGE1_PREFLIGHT_HOLD':'Stage 1 preflight blocked; check frozen variant plan','C_STAGE1_INTERFACE_HOLD':'Stage 1 interface contract incompatible; execution blocked','C_COMPLETE_REVIEW':'Stage 1 complete; Human review required','C_SEMANTIC_HOLD':'Semantic gate HOLD; C stopped before Stage 1','C_BUILD_GOVERNANCE_HOLD':'Atomic build governance HOLD; source authority mismatch blocked downstream code','C_SYSTEM_HOLD':'C controller/system HOLD'}.get(st,'C controller result: '+st)
                c.execute("UPDATE candidates SET state=?,stage='C',detail=? WHERE id=?",(st,detail,j['candidate_id']))
                c.commit();c.close();continue
            if j['kind']=='C_PREP_DISCOVERY':
                ev=c_prepare_discovery_evidence() or {}
                if q.returncode==0 and ev.get('state')=='C_PREPARATION_DISCOVERY_READY':
                    c.execute("UPDATE candidates SET state='C_PREP_DISCOVERED',stage='C',detail='Existing C preparation/freezing command contracts discovered read-only' WHERE id=?",(j['candidate_id'],))
                else:
                    c.execute("UPDATE candidates SET state='C_SYSTEM_HOLD',stage='C',detail=? WHERE id=?",('C preparation discovery failed. View '+j['log_path'],j['candidate_id']))
                c.commit();c.close();continue
            if j['kind']=='C_PREFLIGHT':
                ev=c_preflight_evidence() or {}
                if q.returncode==0 and ev.get('state')=='C_PREFLIGHT_READY':
                    c.execute("UPDATE candidates SET state='C_READY_TO_INTEGRATE',stage='C',detail='Existing C CLI contracts discovered; integration command not yet executed' WHERE id=?",(j['candidate_id'],))
                else:
                    c.execute("UPDATE candidates SET state='C_SYSTEM_HOLD',stage='C',detail=? WHERE id=?",('C preflight failed. View '+j['log_path'],j['candidate_id']))
                c.commit();c.close();continue
            rel=external_evidence_root()/'b_resume'/j['candidate_id']/'b_corrected_release.json'; gx=load_json(external_evidence_root()/'b_resume'/j['candidate_id']/'b_regression_hold.json') or {}
            if q.returncode==0 and rel.exists():
                x=load_json(rel) or {};ver=x.get('candidate',{}).get('version','');c.execute("UPDATE candidates SET state='B_REVIEW',stage='B',version=?,detail='Corrected B release awaiting Human review' WHERE id=?",(ver,j['candidate_id']))
            elif gx.get('reason')=='CORRECTION_REGRESSION': c.execute("UPDATE candidates SET state='GOVERNANCE_HOLD',stage='B',detail='Correction regression blocked. Review failed B revision contract rules.' WHERE id=?",(j['candidate_id'],))
            else: c.execute("UPDATE candidates SET state='SYSTEM_HOLD',stage='B',detail=? WHERE id=?",('B workflow failed. View '+j['log_path'],j['candidate_id']))
            c.commit();c.close()
        except Exception: threading.Event().wait(1)

def external_evidence_root():
    # Dashboard owns UI state, not workflow evidence. Prefer configured/existing workflow evidence.
    import os
    configured=os.environ.get('GATE2_OPERATOR_EVIDENCE_ROOT')
    candidates=[Path(configured) if configured else None, PROJECT/'gate2_operator_app_v1'/'evidence', BASE/'evidence']
    for p in candidates:
        if p and (p/'b_resume'/'CAND-B-002').exists(): return p
    return BASE/'evidence'

def review_data(): return load_json(external_evidence_root()/'b_resume'/'CAND-B-002'/'b_corrected_release.json')
def attempted_data(): return load_json(external_evidence_root()/'b_resume'/'CAND-B-002'/'corrected_candidate.json')
def regression_hold(): return load_json(external_evidence_root()/'b_resume'/'CAND-B-002'/'b_regression_hold.json')
def contract_data(): return load_json(BASE/'b002_revision_contract.json') or {'rules':[]}
def expandable_log(path,running=False,stage='B'):
    p=Path(path)
    if running and not p.exists():
        return '<details><summary>View execution log</summary><pre>Execution has started. The log file has not been created yet; refresh while '+html.escape(stage)+' is running.</pre></details>'
    try: text=p.read_text(encoding='utf-8',errors='replace') if p.exists() else 'Log file unavailable: '+str(p)
    except Exception as e: text='Unable to read log: '+str(e)
    return '<details><summary>'+('View execution log' if running else 'View failure log')+'</summary><pre>'+html.escape(text)+'</pre></details>'
def spec_details(label,obj): return '<details><summary>'+html.escape(label)+'</summary><pre>'+html.escape(json.dumps(obj or {},indent=2))+'</pre></details>'

def governance_html():
    hold=regression_hold() or {};contract=contract_data();prev=(review_data() or {}).get('candidate',{});att=attempted_data() or {};att=att.get('candidate',att) if isinstance(att,dict) else {}
    mapping={'VERSION_MUST_BE':'VERSION','STRICT_NR_N_NOT_PRESERVED':'STRICT_NR_N','VOLATILITY_EXPANSION_RULE_MISSING':'VOL_RULE','VOLATILITY_EXPANSION_NOT_IN_ENTRY':'VOL_ENTRY','ATR_DEFAULT_SEARCH_RELATION_NOT_PRESERVED':'ATR_DEFAULT'}
    failed=set(mapping.get(str(f).split(':',1)[0],str(f).split(':',1)[0]) for f in hold.get('failures',[]));protected={'STRICT_NR_N','VOL_RULE','VOL_ENTRY','ATR_DEFAULT','HYPOTHESIS','EVIDENCE','PARAMETERS','DEPENDENCIES'}
    if failed & protected: failed.add('NO_REGRESSION')
    rows=[]
    for r in contract.get('rules',[]):
        bad=r['id'] in failed;diag=''
        if bad: diag={'VERSION':'Expected '+str(hold.get('required_version') or ('v2.1.3' if hold.get('parent_version')=='v2.1.2' else 'next immutable patch version'))+'; attempted '+str(hold.get('attempted_version','')),'STRICT_NR_N':'Expected strict < semantics throughout.','VOL_RULE':'Expected breakout range > average range of preceding N candles.','VOL_ENTRY':'Expected volatility confirmation in both long and short entry logic.','NO_REGRESSION':'One or more previously accepted protected requirements regressed.'}.get(r['id'],'Contract check failed.')
        rows.append('<tr class="'+('rule-fail' if bad else 'rule-pass')+'"><td>'+('✗' if bad else '✓')+'</td><td>'+html.escape(r['id'])+'</td><td>'+html.escape(r['label'])+'</td><td>'+html.escape(diag)+'</td></tr>')
    hold_path=external_evidence_root()/'b_resume'/'CAND-B-002'/'b_regression_hold.json'
    updated=datetime.datetime.fromtimestamp(hold_path.stat().st_mtime).astimezone().isoformat(timespec='seconds') if hold_path.exists() else 'unknown'
    return '<div class="governance-panel"><h3>GOVERNANCE HOLD — CORRECTION REGRESSION</h3><p>The attempted B correction was blocked before release.</p><p><b>Latest attempt evidence updated:</b> '+html.escape(updated)+' · <b>Failed rules:</b> '+str(len(failed))+'</p><table class="rules"><tr><th></th><th>Rule</th><th>Requirement</th><th>Observed / expected</th></tr>'+''.join(rows)+'</table>'+spec_details('View previous valid specification',prev)+spec_details('View attempted specification',att)+spec_details('View raw failed-rule evidence',hold)+'</div>'

def form_buttons(buttons,placeholder='Human rationale'):
    bs=''.join('<button class="'+('bad' if v=='REJECT' else 'good' if v=='RELEASE_TO_C' else '')+'" name=decision value="'+v+'">'+html.escape(lbl)+'</button>' for v,lbl in buttons)
    return '<form method=post action=/decide><textarea name=rationale required minlength=12 placeholder="'+html.escape(placeholder)+'"></textarea><input type=hidden name=candidate value=CAND-B-002>'+bs+'</form>'

def stage_body(candidate,job):
    if job and job['candidate_id']=='CAND-B-002' and str(job['kind']).startswith('B_'): return '<div class="stage-work running"><h3>RUNNING — NO ACTION REQUIRED</h3><p>'+html.escape(job['detail'])+'</p>'+expandable_log(job['log_path'],running=True,stage='B')+'<button onclick="location.reload()">Refresh</button></div>'
    if not candidate:return ''
    st=candidate['state']
    if st=='B_REVIEW':
        cand=(review_data() or {}).get('candidate',{});vol=cand.get('operator_assumptions',{}).get('volatility_expansion_definition') or cand.get('operator_assumptions',{}).get('volatility_expansion_condition','')
        return '<div class="stage-work"><h3>ACTION REQUIRED — HUMAN B→C REVIEW</h3><p><b>Hypothesis:</b> '+html.escape(cand.get('hypothesis',''))+'</p><p><b>Volatility expansion:</b> '+html.escape(vol)+'</p>'+spec_details('View corrected specification',cand)+form_buttons([('RETURN_TO_B','Return to B'),('REJECT','Reject'),('RELEASE_TO_C','Release to C')])+'</div>'
    if st=='GOVERNANCE_HOLD': return '<div class="stage-work hold"><h3>ACTION REQUIRED — GOVERNANCE HOLD</h3>'+governance_html()+form_buttons([('RETURN_FAILED_RULES','Return to B with failed rules'),('REJECT','Reject candidate')])+'</div>'
    if st=='SYSTEM_HOLD':
        path=candidate['detail'].split('View ',1)[1] if 'View ' in candidate['detail'] else ''
        return '<div class="stage-work hold"><h3>ACTION REQUIRED — SYSTEM HOLD</h3><p>'+html.escape(candidate['detail'])+'</p>'+expandable_log(path)+spec_details('View last corrected specification',(review_data() or {}).get('candidate',{}))+form_buttons([('RETRY_B','Retry same B work'),('REJECT','Reject candidate')])+'</div>'
    if st=='WAITING_FOR_B': return '<div class="stage-work"><h3>ACTION REQUIRED — RESUME B</h3>'+form_buttons([('RESUME_B','Resume B'),('REJECT','Reject candidate')])+'</div>'
    if st=='READY_FOR_C': return '<div class="stage-work"><h3>B COMPLETE — READY FOR C</h3><p>Human release recorded. C integration is the next backend milestone.</p></div>'
    return ''

def c_mapping_candidates():
    # Read-only inventory of likely authoritative C inputs. No C script is executed.
    patterns={
      'env':['.env'],
      'spec':['inputs/*.json','*spec*.json','*candidate*.json'],
      'release_record':['**/*release*.json'],
      'config':['**/*config*.json'],
      'plan':['**/*plan*.json'],
      'manifest':['**/*manifest*.json'],
      'semantic_pass':['**/*semantic*.json']
    }
    out={}
    for key,pats in patterns.items():
        seen=[]
        for pat in pats:
            for p in CROOT.glob(pat):
                if p.is_file() and str(p) not in seen: seen.append(str(p))
        out[key]=seen[:50]
    return out

def c_mapping_plan():
    cand=(review_data() or {}).get('candidate',{})
    return {
      'state':'C_INPUT_MAPPING_REVIEW',
      'candidate_id':cand.get('candidate_id'),
      'version':cand.get('version'),
      'authoritative_c_root':str(CROOT),
      'required_inputs':{
        'build_candidate_v2.py':['env','spec','candidate','workdir'],
        'semantic_gate_v2.py':['release_record','output'],
        'stage1_runner_v3.py':['config','plan','manifest','release_record','semantic_pass','output_dir']
      },
      'discovered_existing_artifacts':c_mapping_candidates(),
      'policy':{
        'read_only_inventory':True,
        'no_command_executed':True,
        'no_filename_guess_promoted_to_authority':True,
        'human_review_before_start_c':True
      }
    }

def c_preparation_assessment():
    ev=c_prepare_discovery_evidence() or {}
    scripts=ev.get('scripts',{})
    return {
      'state':'C_PREPARATION_PATH_IDENTIFIED',
      'candidate_id':'CAND-B-002',
      'version':'v2.1.3',
      'recommended_existing_path':[
        {'step':1,'script':'atomic_build_release_clean.py','purpose':'candidate-specific immutable C build/release','contract':'--spec --candidate [--run-root]'},
        {'step':2,'script':'release_semantic_gate.py','purpose':'semantic gate against released specification','contract':'--release-record --spec --output'},
        {'step':3,'script':'freeze_stage1_plan.py','purpose':'freeze B-002 Stage-1 config/variant plan','contract':'--manifest --release-record --spec [--output-dir]'},
        {'step':4,'script':'stage1_runner_v3.py','purpose':'run Stage 1 only after semantic PASS','contract':'--config --plan --manifest --release-record --semantic-pass --output-dir'}
      ],
      'excluded_or_non_primary':{
        'atomic_build_release.py':'Do not use: --help itself crashes with NameError wd; clean wrapper exists.',
        'make_atomic_build.py':'Generator/maintenance utility; --help caused file creation output, so it is not a read-only execution contract.',
        'file_authoritative_build.py':'Available alternative build path, but clean atomic wrapper is the clearer candidate-specific entry point.',
        'semantic_repair_release.py':'Repair path only if semantic gate returns HOLD.',
        'stage1_runner.py':'Older runner lacks required --semantic-pass boundary; prefer v3.'
      },
      'required_new_B002_artifacts':[
        'candidate-specific spec input derived from frozen B v2.1.3',
        'immutable implementation release record',
        'semantic PASS evidence',
        'B-002 Stage-1 config',
        'B-002 variant plan',
        'new B-002 run/output directories'
      ],
      'shared_existing_artifact':'evidence/market_data/stage1_manifest.json',
      'execution_started':False
    }

def c_execution_plan():
    ev=c_preflight_evidence() or {}
    cand=(review_data() or {}).get('candidate',{})
    return {
      'state':'C_EXECUTION_PLAN_READY',
      'candidate_id':cand.get('candidate_id'),
      'version':cand.get('version'),
      'frozen_b_handoff':cand,
      'authoritative_c_root':str(CROOT),
      'verified_steps':[
        {'step':1,'script':'build_candidate_v2.py','contract':'--env --spec --candidate --workdir'},
        {'step':2,'script':'semantic_gate_v2.py','contract':'--release-record --output'},
        {'step':3,'script':'stage1_runner_v3.py','contract':'--config --plan --manifest --release-record --semantic-pass --output-dir'}
      ],
      'preflight_state':ev.get('state'),
      'execution_policy':{
        'existing_c_cli_authoritative':True,
        'dashboard_does_not_reimplement_c':True,
        'human_start_required':True,
        'stop_on_nonzero_return_code':True,
        'do_not_advance_to_d_automatically':True
      }
    }

def c_stage_body(candidate,job):
    if job and job['kind'] in ('C_PREFLIGHT','C_PREP_DISCOVERY','C_RUN'):
        prog={}
        if job['kind']=='C_RUN' and candidate:
            prog=load_json(BASE/'evidence'/'c_runs'/candidate['id']/candidate['version']/'stage1_output'/'progress.json') or {}
        phtml=''
        if prog:
            phtml='<p><b>Stage 1 progress:</b> '+html.escape(str(prog.get('phase','')))+' · '+html.escape(str(prog.get('completed',0)))+'/'+html.escape(str(prog.get('total',0)))+' · '+html.escape(str(prog.get('percent',0)))+'% · elapsed '+html.escape(str(prog.get('elapsed_seconds',0)))+'s</p><p>'+html.escape(str(prog.get('detail','')))+'. Refresh to update.</p>'
        return '<div class="stage-work running"><h3>'+('C WORKFLOW — RUNNING · NO ACTION REQUIRED' if job['kind']=='C_RUN' else 'C PREFLIGHT — RUNNING · NO ACTION REQUIRED')+'</h3><p>'+html.escape(job['detail'])+'</p>'+phtml+expandable_log(job['log_path'],running=True,stage='C')+'<button onclick="location.reload()">Refresh</button></div>'
    if not candidate: return ''
    st=candidate['state']
    if st=='READY_FOR_C':
        handoff=(review_data() or {}).get('candidate',{})
        return '<div class="stage-work"><h3>ACTION REQUIRED — C PREFLIGHT</h3><p>Human B→C release is frozen. Before executing C, the dashboard will discover the existing authoritative C CLI contracts using read-only --help calls.</p>'+spec_details('View frozen B handoff specification',handoff)+form_buttons([('START_C_PREFLIGHT','Verify existing C CLI')],'Human rationale for C preflight')+'</div>'
    if st=='C_READY_TO_INTEGRATE':
        ev=c_preflight_evidence() or {};plan=c_execution_plan()
        return '<div class="stage-work"><h3>ACTION REQUIRED — REVIEW C EXECUTION PLAN</h3><p>Existing C CLI contracts were discovered without executing C. Review the frozen handoff and verified command sequence before commissioning Stage 1.</p>'+spec_details('View frozen B handoff specification',plan.get('frozen_b_handoff'))+spec_details('View verified C CLI contracts',ev)+spec_details('View C execution plan',plan)+form_buttons([('APPROVE_C_PLAN','Approve C execution plan')],'Human rationale for C execution plan')+'</div>'
    if st=='C_PLAN_APPROVED':
        mapping=c_mapping_plan()
        return '<div class="stage-work"><h3>ACTION REQUIRED — REVIEW C INPUT MAPPING</h3><p>Human C-plan approval is recorded. The dashboard has performed a read-only inventory of existing C artifacts; it has not executed C and has not promoted filename guesses into authority.</p>'+spec_details('View approved C execution plan',c_execution_plan())+spec_details('View discovered C input candidates',mapping)+'<p>Review the discovered artifacts before we bind exact files to the verified CLI arguments.</p>'+form_buttons([('APPROVE_C_MAPPING_REVIEW','Approve C mapping review')],'Human rationale for C input mapping review')+'</div>'
    if st=='C_MAPPING_REVIEWED':
        return '<div class="stage-work hold"><h3>C BINDING HOLD — B-002 INPUTS NOT YET FROZEN</h3><p>Historical B-001/B-003 artifacts will not be reused for CAND-B-002 v2.1.3.</p>'+spec_details('View reviewed C input candidates',c_mapping_plan())+form_buttons([('DISCOVER_C_PREP','Discover existing C preparation commands')],'Human rationale for read-only C preparation discovery')+'</div>'
    if st=='C_PREP_DISCOVERED':
        return '<div class="stage-work"><h3>ACTION REQUIRED — REVIEW C PREPARATION PATH</h3><p>No C build or backtest has executed. The existing preparation contracts identify a candidate-specific path and also expose scripts that should not be used.</p>'+spec_details('View C preparation path assessment',c_preparation_assessment())+spec_details('View raw C preparation command contracts',c_prepare_discovery_evidence())+form_buttons([('APPROVE_C_PREP_PATH','Approve C preparation path')],'Human rationale for C preparation path')+'</div>'
    if st=='C_PREP_PATH_APPROVED':
        return '<div class="stage-work"><h3>ACTION REQUIRED — START GOVERNED C</h3><p>The C preparation path is approved. Starting C will commission the dashboard controller to create the B-002-specific boundary package and execute only the approved existing C chain, stopping automatically on any HOLD/non-zero result and before D.</p>'+spec_details('View approved C preparation path',c_preparation_assessment())+form_buttons([('START_GOVERNED_C','Start governed C workflow')],'Human rationale to commission governed C execution')+'</div>'
    if st=='C_START_COMMISSIONED':
        return '<div class="stage-work running"><h3>C START COMMISSIONED — CONTROLLER WILL RESUME</h3><p>Your durable Human authority is recorded. The autonomous C controller will start/resume without another approval.</p></div>'
    if st in ('C_PASS','C_FAIL','C_COMPLETE_REVIEW','C_STAGE1_REVIEW_REQUIRED','C_STAGE1_EVIDENCE_HOLD','C_STAGE1_PREFLIGHT_HOLD','C_STAGE1_INTERFACE_HOLD','C_SEMANTIC_HOLD','C_BUILD_GOVERNANCE_HOLD'):
        summary=c_run_summary(candidate) or {}
        diagnosis=''
        if st=='C_BUILD_GOVERNANCE_HOLD':
            try:
                diagnosis=spec_details('View source-authority diagnosis',run_c_source_diagnosis(candidate))
                diagnosis+=spec_details('View C source-hash provenance inspection',c_source_provenance(candidate))
                diagnosis+=spec_details('View source-hash serialization analysis',c_source_authority_analysis(candidate))
            except Exception as e: diagnosis='<p>Diagnosis unavailable: '+html.escape(str(e))+'</p>'
        title={'C_PASS':'C STAGE 1 PASS — HUMAN REVIEW REQUIRED','C_FAIL':'C STAGE 1 FAIL — WITHHELD FROM D','C_STAGE1_REVIEW_REQUIRED':'C STAGE 1 EVIDENCE VERIFIED — HUMAN REVIEW REQUIRED','C_STAGE1_EVIDENCE_HOLD':'C STAGE 1 EVIDENCE HOLD — D BLOCKED','C_STAGE1_PREFLIGHT_HOLD':'C STAGE 1 PREFLIGHT HOLD — D BLOCKED','C_STAGE1_INTERFACE_HOLD':'C STAGE 1 INTERFACE HOLD — D BLOCKED','C_COMPLETE_REVIEW':'C STAGE 1 COMPLETE — HUMAN REVIEW REQUIRED','C_SEMANTIC_HOLD':'C SEMANTIC HOLD — STAGE 1 NOT RUN','C_BUILD_GOVERNANCE_HOLD':'C BUILD GOVERNANCE HOLD — DOWNSTREAM CODE NOT EXECUTED'}.get(st,st)
        actions=''
        if st in ('C_COMPLETE_REVIEW','C_STAGE1_REVIEW_REQUIRED','C_STAGE1_EVIDENCE_HOLD','C_STAGE1_PREFLIGHT_HOLD','C_STAGE1_INTERFACE_HOLD'):
            inventory=c_stage1_review(candidate)
            actions=spec_details('View Stage 1 output evidence',inventory)
            if inventory.get('review_status')=='MISSING_STAGE1_SUMMARY_HOLD' or st=='C_STAGE1_EVIDENCE_HOLD':
                actions+=spec_details('View Stage 1 execution diagnosis',c_stage1_diagnosis(candidate))
            actions+='<p><b>Review status:</b> '+html.escape(inventory['review_status'])+'. No automatic C PASS or D handoff is authorized.</p>'
            if st=='C_STAGE1_PREFLIGHT_HOLD':
                actions+=spec_details('View Stage 1 preflight checks',summary.get('preflight',{}))
                actions+=form_buttons([('REPAIR_C_STAGE1_CONTRACT','Align Stage 1 semantic contract')],'Human authorization for guarded C Stage 1 compatibility repair')
            if st=='C_STAGE1_INTERFACE_HOLD':
                actions+=spec_details('View Stage 1 interface contract',summary.get('interface',{}))
                actions+=form_buttons([('RETRY_C_CANDIDATE_STAGE1','Retry C with candidate-driven Stage 1')],'Human authorization to retry C using only frozen B parameter ranges')
            if st=='C_STAGE1_REVIEW_REQUIRED':
                eq=load_json(BASE/'evidence'/'c_runs'/candidate['id']/candidate['version']/'stage1_equivalence.json') or {}
                actions+=spec_details('View Stage 1 execution-equivalence evidence',eq) if eq else '<p><b>Execution equivalence:</b> Not yet validated. Run the equivalence gate before acknowledging Stage 1.</p>'
                if eq.get('state')=='C_STAGE1_EXECUTION_EQUIVALENCE_PASS':
                    actions+=form_buttons([('ACK_C_REVIEW','Record Stage 1 review acknowledgment')],'Human rationale for Stage 1 evidence review')
                else:
                    actions+=form_buttons([('RUN_C_STAGE1_EQUIVALENCE','Validate optimized Stage 1 equivalence')],'Human authorization for read-only full-history vs bounded-history signal equivalence validation')
            elif st in ('C_COMPLETE_REVIEW','C_STAGE1_EVIDENCE_HOLD'):
                actions+=form_buttons([('RECONCILE_C_STAGE1','Reconcile Stage 1 evidence')],'Human rationale for read-only evidence reconciliation')
                if st=='C_STAGE1_EVIDENCE_HOLD':
                    actions+=form_buttons([('ALIGN_AND_RETRY_C_STAGE1','Verify runner contract and retry C')],'Human authorization for guarded Stage 1 compatibility fix and retry')
        elif st=='C_BUILD_GOVERNANCE_HOLD':
            actions='<p>The builder reported a text hash instead of the exact generated file bytes. The proposed repair changes only the builder hash-reporting code, preserves the atomic verifier, and backs up the original file.</p>'+form_buttons([('REPAIR_C_SOURCE_AND_RETRY','Apply guarded source-hash repair and retry C')],'Human authorization for C source-hash repair')
        elif st=='C_SEMANTIC_HOLD':
            sem=load_json(summary.get('semantic','')) or {}
            actions=spec_details('View semantic gate checks',sem)+form_buttons([('RETRY_C_SEMANTIC_REPAIR','Run governed semantic repair')],'Human authorization for one immutable C semantic repair attempt')
        return '<div class="stage-work '+('hold' if st!='C_PASS' else '')+'"><h3>'+title+'</h3><p>'+html.escape(candidate['detail'])+'</p>'+spec_details('View C run evidence summary',summary)+diagnosis+actions+'</div>'
    if st=='C_SYSTEM_HOLD':
        return c_hold_html(candidate)
    return ''

def journey_html(r,cs,job):
    # Display stage follows the governed handoff state, not only the research row's historical stage.
    b2=next((x for x in cs if x['id']=='CAND-B-002'),None)
    display_stage='C' if b2 and (b2['stage']=='C' or str(b2['state']).startswith('C_') or b2['state']=='READY_FOR_C') else r['stage']
    defs={'A':('Research & Source Qualification','Grounded Researcher + Human Operator'),'B':('Evidence Synthesis & Strategy Formulation','Knowledge Archivist + Strategy Optimizer + Human Operator'),'C':('Local Integration & Stage 1 Backtesting','Existing local C CLI / Local Backtest Runner'),'D':('Hidden OOS / Walk-Forward Validation','Local deterministic harness + MT5 + Human OOS boundary'),'E':('Commissioning Audit & Decision','Human Operator + deterministic commissioning checks')}
    order='ABCDE';idx=order.index(display_stage);candidate=next((x for x in cs if x['id']=='CAND-B-002'),None);cards=[]
    for i,k in enumerate(order):
        title,owner=defs[k]
        if i<idx: state,status,cls='FROZEN','HANDED OVER TO '+order[i+1],'done'
        elif i==idx: state,cls='ACTIVE','active';status='RUNNING — NO ACTION REQUIRED' if job and ((k=='B' and str(job['kind']).startswith('B_')) or (k=='C' and str(job['kind']).startswith('C_'))) else ('HUMAN ACTION REQUIRED' if candidate and (candidate['state'] in ('B_REVIEW','WAITING_FOR_B','SYSTEM_HOLD','GOVERNANCE_HOLD') or (k=='C' and candidate['state'] in ('C_SYSTEM_HOLD','C_SEMANTIC_HOLD','C_BUILD_GOVERNANCE_HOLD','C_STAGE1_EVIDENCE_HOLD','C_STAGE1_PREFLIGHT_HOLD','C_STAGE1_INTERFACE_HOLD','C_STAGE1_REVIEW_REQUIRED'))) else ('PREFLIGHT COMPLETE · READY TO INTEGRATE' if k=='C' and candidate and candidate['state']=='C_READY_TO_INTEGRATE' else 'WORKFLOW ACTIVE'))
        else: state,status,cls='NOT STARTED','Awaiting '+order[i-1]+' handoff','future'
        extra=''
        if k=='B' and candidate and candidate['stage']=='B': extra='<p><b>Current candidate:</b> '+html.escape(candidate['id'])+' · '+html.escape(candidate['version'] or '')+' · '+html.escape(candidate['state'])+'</p>'+stage_body(candidate,job)
        elif k=='C' and candidate: extra='<p><b>Candidate received:</b> '+html.escape(candidate['id'])+' · '+html.escape(candidate['version'] or '')+' · '+html.escape(candidate['state'])+'</p>'+c_observability(candidate)+c_stage_body(candidate,job)
        elif k=='D': extra=production_gate_panel('D',candidate)+d_sandbox_body()
        elif k=='E': extra=production_gate_panel('E',candidate)+e_sandbox_body()
        cards.append('<section class="journey-card '+cls+'"><div class="journey-head"><span class="stage-letter">'+k+'</span><div><b>'+title+'</b><div class="state">'+state+' · '+status+'</div></div></div><p><b>Owner:</b> '+owner+'</p>'+extra+'</section>')
    return '<div class="card"><h2>Full research journey</h2><div class="journey">'+'<div class="arrow">↓</div>'.join(cards)+'</div></div>'

def governance_checks_html(title,checks):
    rows=[]
    for label,value in checks:
        ok=bool(value)
        rows.append('<tr class="'+('rule-pass' if ok else 'rule-fail')+'"><td>'+('✓' if ok else '✗')+'</td><td>'+html.escape(label)+'</td><td>'+('PASS' if ok else 'HOLD')+'</td></tr>')
    return '<div class="governance-panel"><h4>'+html.escape(title)+'</h4><table><tr><th></th><th>Governance check</th><th>State</th></tr>'+''.join(rows)+'</table></div>'

def c_observability(candidate):
    summary=c_run_summary(candidate) or {}
    eq=load_json(BASE/'evidence'/'c_runs'/candidate['id']/candidate['version']/'stage1_equivalence.json') or {}
    return governance_checks_html('C governance status',[
      ('Candidate identity present',bool(candidate['id'] and candidate['version'])),
      ('Stage 1 evidence resolved',summary.get('state')=='C_STAGE1_REVIEW_REQUIRED'),
      ('Released implementation identity recorded',bool(summary.get('release_record'))),
      ('Semantic PASS evidence recorded',bool(summary.get('semantic_pass'))),
      ('Execution equivalence validated',eq.get('state')=='C_STAGE1_EXECUTION_EQUIVALENCE_PASS'),
      ('Production D authorization',candidate['state']=='C_PASS')])

def production_gate_panel(stage,candidate):
    if stage=='D':
        eligible=bool(candidate and candidate['state']=='C_PASS')
        title='PRODUCTION D GATE';msg='Eligible for production D admission.' if eligible else 'LOCKED — requires verified PRODUCTION_EVIDENCE + C_PASS for the same candidate/version.'
        checks=[('Upstream C production PASS',eligible),('Candidate/version identity available',bool(candidate and candidate['id'] and candidate['version'])),('Production evidence required',eligible),('Human D admission authority',eligible)]
    else:
        eligible=bool(candidate and candidate['state']=='D_OOS_PASS')
        title='PRODUCTION E GATE';msg='Eligible for production E provenance audit.' if eligible else 'LOCKED — requires verified production D_OOS_PASS and complete A→D provenance.'
        checks=[('Upstream D OOS production PASS',eligible),('Complete production provenance required',eligible),('Sandbox/test evidence excluded',eligible),('Human final decision required',True)]
    cls='good' if eligible else 'hold'
    return '<div class="stage-work '+cls+'"><h3>'+title+'</h3><p><b>'+html.escape(msg)+'</b></p>'+governance_checks_html(title+' checks',checks)+'<p>Sandbox/test evidence can never satisfy this production gate.</p></div>'

def d_sandbox_body():
    root=BASE/'evidence'/'d_sandbox_demo'
    ev=load_json(root/'dashboard_summary.json') or {}
    warning='<div class="stage-work hold"><h3>D WORKFLOW DEVELOPMENT SANDBOX</h3><p><b>WORKFLOW TEST SANDBOX — NO PRODUCTION AUTHORITY</b></p><p>This exercises D using a typed test fixture. It does not assert C PASS, does not use B-002 as a production D input, and cannot authorize E.</p>'
    body=spec_details('View D sandbox evidence',ev) if ev else '<p>No D sandbox run recorded yet.</p>'
    return warning+body+form_buttons([('RUN_D_SANDBOX','Run D sandbox test')],'Human authorization to run isolated D workflow test fixture')+'</div>'

def e_sandbox_body():
    root=BASE/'evidence'/'e_sandbox_demo'
    ev=load_json(root/'dashboard_summary.json') or {}
    warning='<div class="stage-work hold"><h3>E WORKFLOW DEVELOPMENT SANDBOX</h3><p><b>COMMISSIONING TEST ONLY — NO PRODUCTION AUTHORITY</b></p><p>E audits typed D sandbox evidence and must block commissioning because its provenance is a workflow test fixture.</p>'
    body=spec_details('View E sandbox audit evidence',ev) if ev else '<p>No E sandbox audit recorded yet. Run D sandbox first.</p>'
    return warning+body+form_buttons([('RUN_E_SANDBOX','Run E commissioning sandbox audit')],'Human authorization to audit workflow-test D evidence; no commissioning authority')+'</div>'

def render():
    c=cx();r=c.execute("SELECT * FROM research WHERE state='ACTIVE'").fetchone();cs=list(c.execute('SELECT * FROM candidates ORDER BY q'));job=active_job(c)
    b='<div class=card><small>ACTIVE RESEARCH</small><h1>'+html.escape(r['title'])+'</h1></div>'+journey_html(r,cs,job)
    b+='<div class=card><h2>Candidate pipeline</h2><table><tr><th>ID</th><th>Version</th><th>Stage</th><th>State</th><th>Detail</th></tr>'
    for x in cs:b+='<tr'+(' class="candidate-active"' if x['id']=='CAND-B-002' else '')+'><td>'+x['id']+'</td><td>'+html.escape(x['version'] or '')+'</td><td>'+x['stage']+'</td><td>'+x['state']+'</td><td>'+html.escape(x['detail'])+'</td></tr>'
    b+='</table></div><div class=card><h2>Human decision ledger</h2><table><tr><th>Candidate</th><th>Decision</th><th>Rationale</th></tr>'
    for d in c.execute('SELECT * FROM decisions ORDER BY created_at DESC'):b+='<tr><td>'+d['candidate_id']+'</td><td>'+d['decision']+'</td><td>'+html.escape(d['rationale'])+'</td></tr>'
    b+='</table></div>';c.close()
    css='body{font-family:Segoe UI,Arial;background:#f3f5f7;margin:0}header{background:#111827;color:white;padding:18px}main{max-width:1120px;margin:auto;padding:22px}.card{background:white;padding:18px;margin:14px 0;border:1px solid #ddd;border-radius:12px}.journey{display:grid;gap:10px}.journey-card{border:1px solid #d1d5db;border-radius:10px;padding:14px}.done{background:#f0fdf4}.active{border:2px solid #2563eb;background:#eff6ff}.future{background:#f3f4f6;color:#6b7280}.journey-head{display:flex;gap:12px;align-items:center}.stage-letter{display:inline-flex;width:42px;height:42px;border-radius:50%;align-items:center;justify-content:center;background:#111827;color:white;font-weight:700}.state{font-size:13px;font-weight:700}.arrow{text-align:center}.stage-work{margin-top:16px;padding-top:16px;border-top:2px solid #93c5fd}.hold{border-top-color:#d97706}.candidate-active{background:#eff6ff}textarea{width:96%;min-height:75px;padding:10px}button{padding:10px 14px;margin:8px 5px 0 0;background:#2563eb;color:white;border:0;border-radius:6px}.good{background:#15803d}.bad{background:#b91c1c}table{width:100%;border-collapse:collapse}td,th{padding:9px;border-bottom:1px solid #ddd;text-align:left}pre{white-space:pre-wrap;background:#f8fafc;padding:12px;max-height:520px;overflow:auto}details{margin:12px 0;border:1px solid #bfdbfe;border-radius:8px;background:white;padding:10px}.rule-pass{background:#f0fdf4}.rule-fail{background:#fef2f2;font-weight:600}'
    return '<html><head><meta charset=utf-8><style>'+css+'</style></head><body><header><h2>Gate 2 Operator App</h2></header><main>'+b+'</main></body></html>'

def action_authorized(state,action):
    # Server-side authorization. UI visibility is never authority.
    rules={
      'RUN_D_SANDBOX':lambda st: True,
      'RUN_E_SANDBOX':lambda st: True,
      'RETRY_C_CANDIDATE_STAGE1':lambda st: st=='C_STAGE1_INTERFACE_HOLD',
      'ALIGN_AND_RETRY_C_STAGE1':lambda st: st=='C_STAGE1_EVIDENCE_HOLD',
      'REPAIR_C_STAGE1_CONTRACT':lambda st: st=='C_STAGE1_PREFLIGHT_HOLD',
      'RECONCILE_C_STAGE1':lambda st: st in ('C_COMPLETE_REVIEW','C_STAGE1_EVIDENCE_HOLD'),
      'RUN_C_STAGE1_EQUIVALENCE':lambda st: st=='C_STAGE1_REVIEW_REQUIRED',
      'ACK_C_REVIEW':lambda st: st in ('C_COMPLETE_REVIEW','C_STAGE1_REVIEW_REQUIRED'),
      'RETRY_C_SEMANTIC_REPAIR':lambda st: st=='C_SEMANTIC_HOLD',
      'REPAIR_C_SOURCE_AND_RETRY':lambda st: st=='C_BUILD_GOVERNANCE_HOLD',
      'RETRY_C':lambda st: st=='C_SYSTEM_HOLD',
      'RETURN_C_TO_B':lambda st: str(st).startswith('C_'),
      'START_GOVERNED_C':lambda st: st=='C_PREP_PATH_APPROVED',
      'APPROVE_C_PREP_PATH':lambda st: st=='C_PREP_DISCOVERED',
      'DISCOVER_C_PREP':lambda st: st=='C_MAPPING_REVIEWED',
      'APPROVE_C_MAPPING_REVIEW':lambda st: st=='C_PLAN_APPROVED',
      'APPROVE_C_PLAN':lambda st: st=='C_READY_TO_INTEGRATE',
      'START_C_PREFLIGHT':lambda st: st=='READY_FOR_C',
      'RELEASE_TO_C':lambda st: st=='B_REVIEW',
      'RETURN_TO_B':lambda st: st in ('B_REVIEW','GOVERNANCE_HOLD'),
      'RETURN_FAILED_RULES':lambda st: st=='GOVERNANCE_HOLD',
      'RESUME_B':lambda st: st=='WAITING_FOR_B',
      'RETRY_B':lambda st: st=='SYSTEM_HOLD',
      'REJECT':lambda st: True}
    fn=rules.get(action)
    return bool(fn and fn(state))

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        b=render().encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(b)
    def do_POST(self):
        n=int(self.headers.get('Content-Length',0));f=parse_qs(self.rfile.read(n).decode());c=cx();r=c.execute("SELECT * FROM research WHERE state='ACTIVE'").fetchone();cid=f.get('candidate',[''])[0];d=f.get('decision',[''])[0];rat=f.get('rationale',[''])[0].strip();x=c.execute('SELECT * FROM candidates WHERE id=?',(cid,)).fetchone()
        if x and len(rat)>=12 and not active_job(c) and action_authorized(x['state'],d):
            if d=='RUN_E_SANDBOX':
                decision(c,r['id'],cid,d,rat)
                from e_dashboard_sandbox import execute
                result=execute(BASE/'evidence'/'e_sandbox_demo',BASE/'evidence'/'d_sandbox_demo')
            elif d=='RUN_D_SANDBOX':
                decision(c,r['id'],cid,d,rat)
                from d_dashboard_sandbox import execute
                result=execute(BASE/'evidence'/'d_sandbox_demo')
            elif d=='RETRY_C_CANDIDATE_STAGE1' and x['state']=='C_STAGE1_INTERFACE_HOLD':
                decision(c,r['id'],cid,d,rat)
                c.execute("UPDATE candidates SET state='C_START_COMMISSIONED',stage='C',detail='Human authorized candidate-driven Stage 1 retry using frozen B parameters only' WHERE id=?",(cid,))
                queue(c,r['id'],cid,'C_RUN','Candidate-driven C retry: frozen B parameters → semantic gate → Stage 1')
            elif d=='ALIGN_AND_RETRY_C_STAGE1' and x['state']=='C_STAGE1_EVIDENCE_HOLD':
                decision(c,r['id'],cid,d,rat)
                try:
                    from repair_c_stage1_contract import apply
                    status=apply(CROOT/'stage1_runner_v3.py')
                    c.execute("UPDATE candidates SET state='C_START_COMMISSIONED',stage='C',detail=? WHERE id=?",('Stage 1 contract: '+status+'; governed retry commissioned',cid))
                    queue(c,r['id'],cid,'C_RUN','Governed C retry after Stage 1 contract alignment')
                except Exception as e:
                    c.execute("UPDATE candidates SET detail=? WHERE id=?",('Stage 1 contract repair HOLD: '+str(e),cid))
            elif d=='REPAIR_C_STAGE1_CONTRACT' and x['state']=='C_STAGE1_PREFLIGHT_HOLD':
                decision(c,r['id'],cid,d,rat)
                try:
                    from repair_c_stage1_contract import apply
                    status=apply(CROOT/'stage1_runner_v3.py')
                    c.execute("UPDATE candidates SET state='C_STAGE1_PREFLIGHT_HOLD',stage='C',detail=? WHERE id=?",('Stage1 contract: '+status+'; check variant plan before retry',cid))
                except Exception as e:
                    c.execute("UPDATE candidates SET detail=? WHERE id=?",('Stage1 compatibility HOLD: '+str(e),cid))
            elif d=='RETRY_C_STAGE1' and x['state']=='C_STAGE1_EVIDENCE_HOLD':
                decision(c,r['id'],cid,d,rat)
                c.execute("UPDATE candidates SET state='C_START_COMMISSIONED',stage='C',detail='Human authorized C retry after missing Stage 1 evidence' WHERE id=?",(cid,))
                queue(c,r['id'],cid,'C_RUN','Governed C retry after Stage 1 evidence HOLD')
            elif d=='RECONCILE_C_STAGE1' and x['state'] in ('C_COMPLETE_REVIEW','C_STAGE1_EVIDENCE_HOLD'):
                decision(c,r['id'],cid,d,rat)
                from c_stage1_resolver import resolve_stage1
                from operator_artifacts import record_artifact
                current=c_run_summary(x) or {}
                resolved=resolve_stage1(current.get('output_dir') or '')
                newstate=resolved['state']
                current['state']=newstate
                current['stage1_evidence']=resolved
                if newstate=='C_STAGE1_REVIEW_REQUIRED':
                    record_artifact(BASE/'evidence'/'c_runs'/cid/x['version'],'c_stage1_summary',resolved['summary_path'])
                (BASE/'evidence'/'c_runs'/cid/x['version']/'c_run_summary.json').write_text(json.dumps(current,indent=2),encoding='utf-8')
                c.execute("UPDATE candidates SET state=?,stage='C',detail=? WHERE id=?",(newstate,'Stage 1 evidence reconciled: '+resolved.get('reason',newstate),cid))
            elif d=='RUN_C_STAGE1_EQUIVALENCE' and x['state']=='C_STAGE1_REVIEW_REQUIRED':
                decision(c,r['id'],cid,d,rat)
                root=BASE/'evidence'/'c_runs'/cid/x['version']
                cur=c_run_summary(x) or {}
                script=BASE/'c_stage1_equivalence.py'
                cmd=[sys.executable,str(script),'--plan',str(cur.get('plan','')),'--manifest',str(cur.get('manifest','')),
                     '--release-record',str(cur.get('release_record','')),'--semantic-pass',str(cur.get('semantic_pass','')),
                     '--stage1-summary',str(cur.get('result','')),'--output',str(root/'stage1_equivalence.json')]
                q=subprocess.run(cmd,cwd=BASE,capture_output=True,text=True)
                ev=load_json(root/'stage1_equivalence.json') or {}
                c.execute("UPDATE candidates SET detail=? WHERE id=?",('Stage 1 equivalence: '+ev.get('state','NO_EVIDENCE')+'; comparisons='+str(ev.get('comparisons',0))+'; mismatches='+str(ev.get('signal_mismatch_count','?')),cid))
            elif d=='ACK_C_REVIEW' and x['state'] in ('C_COMPLETE_REVIEW','C_STAGE1_REVIEW_REQUIRED'):
                decision(c,r['id'],cid,d,rat)
                c.execute("UPDATE candidates SET detail='Human acknowledged Stage 1 evidence; C remains in review pending explicit outcome classification' WHERE id=?",(cid,))
            elif d=='RETRY_C_SEMANTIC_REPAIR' and x['state']=='C_SEMANTIC_HOLD':
                decision(c,r['id'],cid,d,rat)
                c.execute("UPDATE candidates SET state='C_START_COMMISSIONED',stage='C',detail='Human authorized governed semantic repair retry' WHERE id=?",(cid,))
                queue(c,r['id'],cid,'C_RUN','Governed C retry with one immutable semantic repair attempt')
            elif d=='REPAIR_C_SOURCE_AND_RETRY' and x['state']=='C_BUILD_GOVERNANCE_HOLD':
                decision(c,r['id'],cid,d,rat)
                try:
                    from repair_c_source_hash import apply
                    repair_state=apply(CROOT/'build_candidate_v2.py')
                    c.execute("UPDATE candidates SET state='C_START_COMMISSIONED',stage='C',detail=? WHERE id=?",('Source-hash builder repair: '+repair_state+'; governed C retry commissioned',cid))
                    queue(c,r['id'],cid,'C_RUN','Governed C retry after source-byte hash reporting repair')
                except Exception as e:
                    c.execute("UPDATE candidates SET detail=? WHERE id=?",('C source repair HOLD: '+str(e),cid))
            elif d=='RETRY_C':
                decision(c,r['id'],cid,d,rat);c.execute("UPDATE candidates SET state='C_START_COMMISSIONED',stage='C',detail='Human authorized governed C retry' WHERE id=?",(cid,));queue(c,r['id'],cid,'C_RUN','Governed C retry: boundary → build → semantic gate → plan freeze → Stage 1')
            elif d=='RETURN_C_TO_B':
                decision(c,r['id'],cid,d,rat);c.execute("UPDATE candidates SET state='B_REVIEW',stage='B',detail='Human returned candidate from C to B review' WHERE id=?",(cid,))
            elif d=='START_GOVERNED_C':
                decision(c,r['id'],cid,d,rat);c.execute("UPDATE candidates SET state='C_START_COMMISSIONED',stage='C',detail='Human commissioned governed C workflow; controller execution adapter pending' WHERE id=?",(cid,))
            elif d=='APPROVE_C_PREP_PATH':
                decision(c,r['id'],cid,d,rat);c.execute("UPDATE candidates SET state='C_PREP_PATH_APPROVED',stage='C',detail='Human approved existing C preparation path; execution not started' WHERE id=?",(cid,))
            elif d=='DISCOVER_C_PREP':
                decision(c,r['id'],cid,d,rat);queue(c,r['id'],cid,'C_PREP_DISCOVERY','Read-only discovery of existing C preparation/freezing commands')
            elif d=='APPROVE_C_MAPPING_REVIEW':
                decision(c,r['id'],cid,d,rat);c.execute("UPDATE candidates SET state='C_MAPPING_REVIEWED',stage='C',detail='Human reviewed read-only C input inventory; exact bindings still require verification' WHERE id=?",(cid,))
            elif d=='APPROVE_C_PLAN':
                decision(c,r['id'],cid,d,rat);c.execute("UPDATE candidates SET state='C_PLAN_APPROVED',stage='C',detail='Human approved verified C execution plan; awaiting deterministic input mapping' WHERE id=?",(cid,))
            elif d=='START_C_PREFLIGHT':
                decision(c,r['id'],cid,d,rat);queue(c,r['id'],cid,'C_PREFLIGHT','Read-only discovery of existing C CLI contracts')
            elif d in ('RETURN_TO_B','RESUME_B','RETRY_B','RETURN_FAILED_RULES'):
                if d=='RETURN_FAILED_RULES':
                    auto=failed_rule_instruction()
                    if auto: rat=(rat+'\n\nAUTO FAILED-RULE INSTRUCTION: '+auto).strip()
                decision(c,r['id'],cid,d,rat);queue(c,r['id'],cid,'B_RESUME','Governed B correction via configured model endpoint')
            elif d=='REJECT':decision(c,r['id'],cid,d,rat);c.execute("UPDATE candidates SET state='REJECTED',detail='Human rejected candidate' WHERE id=?",(cid,))
            elif d=='RELEASE_TO_C':
                # Operational inspection is read-only and fail-closed. No release
                # decision or C queue action is authorized by this path.
                from b_operational_boundary import inspect
                review=inspect(c,cid,r['id'],x['version'],
                    BASE/'gate2_submission_evidence'/'governance_tests')
                if review['release_authorized']:
                    raise RuntimeError('UNEXPECTED_ACTIVE_RELEASE_AUTHORITY')
                c.execute("UPDATE candidates SET detail=? WHERE id=?",
                          ('B governance HOLD: '+', '.join(review['failures']),cid))
        c.commit();c.close();self.send_response(303);self.send_header('Location','/');self.end_headers()
    def log_message(self,*a):pass

if __name__=='__main__':
    init();threading.Thread(target=dispatcher,daemon=True).start();u=f'http://127.0.0.1:{PORT}/';print(u);threading.Timer(.5,lambda:webbrowser.open(u)).start();ThreadingHTTPServer(('127.0.0.1',PORT),H).serve_forever()
