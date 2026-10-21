import argparse,copy,datetime,hashlib,json,subprocess,sys
from pathlib import Path

def load(p):
    return json.load(open(p,encoding="utf-8"))
def save(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2),encoding="utf-8")
def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(cmd,cwd,log):
    with open(log,"a",encoding="utf-8") as f:
        f.write("\n$ "+" ".join(map(str,cmd))+"\n")
        q=subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,text=True)
    if q.returncode!=0: raise RuntimeError("Command failed rc=%s: %s"%(q.returncode,cmd[1]))
def find_candidate(node,cid):
    if isinstance(node,dict):
        if node.get("candidate_id")==cid:return node
        for v in node.values():
            r=find_candidate(v,cid)
            if r is not None:return r
    elif isinstance(node,list):
        for v in node:
            r=find_candidate(v,cid)
            if r is not None:return r
    return None
def newest(root,names):
    hits=[]
    for n in names:hits.extend(Path(root).rglob(n))
    hits=[p for p in hits if p.is_file()]
    return max(hits,key=lambda p:p.stat().st_mtime) if hits else None
from c_gate_predicates import semantic_pass,stage1_completed,semantic_repair_authorized

ap=argparse.ArgumentParser()
ap.add_argument("--c-root",required=True);ap.add_argument("--legacy-evidence",required=True)
ap.add_argument("--candidate",required=True);ap.add_argument("--version",required=True)
ap.add_argument("--run-root",required=True);ap.add_argument("--log",required=True)
a=ap.parse_args()
croot=Path(a.c_root);runroot=Path(a.run_root);runroot.mkdir(parents=True,exist_ok=True)
log=Path(a.log);summary=runroot/"c_run_summary.json"
try:
    release=load(Path(a.legacy_evidence)/"b_resume"/a.candidate/"b_corrected_release.json")
    candidate=release.get("candidate",{})
    if candidate.get("candidate_id")!=a.candidate or candidate.get("version")!=a.version:
        raise RuntimeError("Frozen B release identity/version mismatch")
    template=croot/"inputs"/"candidate_strategy_register_v2_1_1_frozen.json"
    reg=load(template);target=find_candidate(reg,a.candidate)
    if target is None: raise RuntimeError("Candidate not found in authoritative C spec template")
    target.clear();target.update(copy.deepcopy(candidate))
    spec=runroot/("candidate_strategy_register_"+a.version.replace(".","_")+"_frozen.json");save(spec,reg)
    boundary={"state":"C_BOUNDARY_FROZEN","candidate_id":a.candidate,"version":a.version,"spec":str(spec),"spec_sha256":digest(spec),"b_release_sha256":digest(Path(a.legacy_evidence)/"b_resume"/a.candidate/"b_corrected_release.json"),"created_at":datetime.datetime.now(datetime.timezone.utc).isoformat()}
    save(runroot/"c_boundary.json",boundary)

    buildroot=runroot/"build"
    run([sys.executable,str(croot/"atomic_build_release_clean.py"),"--spec",str(spec),"--candidate",a.candidate,"--run-root",str(buildroot)],croot,log)
    release_record=newest(buildroot,["implementation_release.json","*release*.json"])
    if not release_record:
        # The clean atomic wrapper can legitimately stop before candidate code/release
        # when its own source-hash authority check detects a mismatch. Preserve that
        # governed HOLD rather than misclassifying it as a missing-file system error.
        holds=list(buildroot.rglob("*.json"))
        hold_obj=None;hold_path=None
        for hp in sorted(holds,key=lambda p:p.stat().st_mtime,reverse=True):
            try:
                obj=load(hp)
            except Exception:
                continue
            if isinstance(obj,dict) and (str(obj.get("state","")).upper().startswith("HOLD") or obj.get("reason")):
                hold_obj=obj;hold_path=hp;break
        if hold_obj:
            save(summary,{"state":"C_BUILD_GOVERNANCE_HOLD","candidate_id":a.candidate,"version":a.version,"step":"atomic_build_release_clean","hold_evidence":str(hold_path),"hold":hold_obj,"boundary":str(runroot/"c_boundary.json")})
            print(json.dumps(load(summary),indent=2));raise SystemExit(21)
        raise RuntimeError("Atomic build completed but produced neither release record nor governed HOLD evidence")

    semantic=runroot/"semantic_pass.json"
    run([sys.executable,str(croot/"release_semantic_gate.py"),"--release-record",str(release_record),"--spec",str(spec),"--output",str(semantic)],croot,log)
    sem=load(semantic)
    if not semantic_pass(sem):
        # Existing authoritative semantic repair is permitted only for a semantic
        # HOLD tied to the exact frozen implementation release. Never patch a
        # released module in place or substitute a hash.
        repairs=[]
        if semantic_repair_authorized(sem,load(release_record)):
            repairroot=runroot/"semantic_repairs"
            repairroot.mkdir(parents=True,exist_ok=True)
            run([sys.executable,str(croot/"semantic_repair_release.py"),
                 "--env",str(croot/".env"),
                 "--release-record",str(release_record),
                 "--semantic-hold",str(semantic),
                 "--spec",str(spec),
                 "--run-root",str(repairroot)],croot,log)
            # Only a new immutable release record under this repair root is eligible.
            repaired=newest(repairroot,["implementation_release.json"])
            if repaired and repaired.resolve()!=release_record.resolve():
                rrec=load(repaired)
                if (rrec.get("state")=="IMPLEMENTATION_RELEASED"
                    and rrec.get("candidate_id")==a.candidate
                    and rrec.get("parent_release_sha256")==load(release_record).get("module_sha256")):
                    next_sem=runroot/"semantic_repair_pass.json"
                    run([sys.executable,str(croot/"release_semantic_gate.py"),
                         "--release-record",str(repaired),"--spec",str(spec),
                         "--output",str(next_sem)],croot,log)
                    repairs.append({"release_record":str(repaired),"semantic":str(next_sem)})
                    if semantic_pass(load(next_sem)):
                        release_record=repaired
                        semantic=next_sem
                        sem=load(semantic)
        if not semantic_pass(sem):
            save(summary,{"state":"C_SEMANTIC_HOLD","candidate_id":a.candidate,
                          "version":a.version,"release_record":str(release_record),
                          "semantic":str(semantic),"repairs":repairs,
                          "reason":"Semantic validation failed; Stage 1 not authorized"})
            print(json.dumps(load(summary),indent=2));raise SystemExit(20)

    manifest=croot/"evidence"/"market_data"/"stage1_manifest.json"
    if not manifest.exists(): raise RuntimeError("Stage1 manifest not found")
    freeze=runroot/"stage1_config"
    # Keep the existing freeze output as audit evidence, but do not reuse its
    # legacy strategy-specific variant plan for this candidate.
    run([sys.executable,str(croot/"freeze_stage1_plan.py"),"--manifest",str(manifest),"--release-record",str(release_record),"--spec",str(spec),"--output-dir",str(freeze)],croot,log)
    config=newest(freeze,["stage1_config.json"])
    if not config: raise RuntimeError("Stage1 freeze did not produce config")
    from c_candidate_stage1_plan import build as build_candidate_plan
    plan,plan_obj=build_candidate_plan(spec,a.candidate,config,freeze)
    save(runroot/"candidate_stage1_plan_summary.json",{"state":plan_obj["state"],"parameter_names":plan_obj["parameter_names"],"variant_count":plan_obj["variant_count"],"plan":str(plan)})
    from c_stage1_interface import validate as validate_stage1_interface
    interface=validate_stage1_interface(release_record,plan)
    save(runroot/"stage1_interface.json",interface)
    if not interface["checks"]["variant_parameter_keys_match_module"]:
        save(summary,{"state":"C_STAGE1_INTERFACE_HOLD","candidate_id":a.candidate,"version":a.version,
                      "interface":interface,"release_record":str(release_record),"semantic_pass":str(semantic),
                      "config":str(config),"plan":str(plan),"reason":"Frozen B parameters do not match released strategy parameter schema"})
        print(json.dumps(load(summary),indent=2));raise SystemExit(23)
    output=runroot/"stage1_output"
    if output.exists():
        archive=runroot/("stage1_output_archive_"+datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
        output.rename(archive)
    output.mkdir(parents=True,exist_ok=True)
    runner=Path(__file__).resolve().parent/"c_candidate_stage1_runner.py"
    run([sys.executable,str(runner),"--config",str(config),"--plan",str(plan),"--manifest",str(manifest),"--release-record",str(release_record),"--semantic-pass",str(semantic),"--output-dir",str(output)],croot,log)
    from c_stage1_resolver import resolve_stage1
    from operator_artifacts import record_artifact
    resolved=resolve_stage1(output)
    state=resolved["state"]
    out={"state":state,"candidate_id":a.candidate,"version":a.version,
         "boundary":str(runroot/"c_boundary.json"),"release_record":str(release_record),
         "semantic_pass":str(semantic),"config":str(config),"plan":str(plan),
         "manifest":str(manifest),"output_dir":str(output),
         "result":resolved.get("summary_path"),"stage1_evidence":resolved}
    if state=="C_STAGE1_REVIEW_REQUIRED":
        # A verified Stage 1 summary exists; record exact immutable input/output
        # identities, without inferring trading success.
        for role,path in (("b_to_c_boundary",runroot/"c_boundary.json"),
                          ("c_release_record",release_record),("c_semantic_pass",semantic),
                          ("c_stage1_config",config),("c_variant_plan",plan),
                          ("c_market_manifest",manifest),
                          ("c_stage1_summary",resolved["summary_path"])):
            record_artifact(runroot,role,path)
        out["artifact_registry"]=str(runroot/"artifact_registry.json")
    save(summary,out);print(json.dumps(out,indent=2))

except SystemExit: raise
except Exception as e:
    save(summary,{"state":"C_SYSTEM_HOLD","candidate_id":a.candidate,"version":a.version,"error":repr(e),"log":str(log)})
    print(json.dumps(load(summary),indent=2));raise SystemExit(2)
