import argparse,json,hashlib,shutil,datetime
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def main():
 p=argparse.ArgumentParser(description="Gate2 immutable implementation release")
 p.add_argument("--candidate",required=True);p.add_argument("--module",required=True);p.add_argument("--build-summary",required=True);p.add_argument("--spec",required=True);p.add_argument("--release-root",default="evidence/releases")
 a=p.parse_args()
 summary=json.load(open(a.build_summary,encoding="utf-8"))
 if summary.get("state")!="IMPLEMENTATION_READY": raise SystemExit("HOLD: build summary is not IMPLEMENTATION_READY")
 if summary.get("candidate_id")!=a.candidate: raise SystemExit("HOLD: candidate mismatch")
 module=Path(a.module)
 if not module.exists(): raise SystemExit("HOLD: source module missing")
 source_hash=sha(module)
 if summary.get("module_sha256")!=source_hash: raise SystemExit("HOLD: module hash does not match build summary")
 base=Path(a.release_root)/a.candidate;base.mkdir(parents=True,exist_ok=True)
 existing=sorted([x for x in base.iterdir() if x.is_dir() and x.name.startswith("release_")])
 n=1
 if existing:
  nums=[]
  for x in existing:
   try:nums.append(int(x.name.split("_")[1]))
   except:pass
  n=max(nums+[0])+1
 rd=base/f"release_{n:03d}";rd.mkdir()
 target=rd/"strategy_module.py";shutil.copy2(module,target)
 release_hash=sha(target)
 if release_hash!=source_hash: raise SystemExit("HOLD: post-copy hash mismatch")
 record={"state":"IMPLEMENTATION_RELEASED","candidate_id":a.candidate,"release_id":f"{a.candidate}-R{n:03d}",
         "released_at_utc":now(),"module":"strategy_module.py","module_sha256":release_hash,
         "source_module":str(module),"source_build_summary":str(Path(a.build_summary)),
         "source_build_summary_sha256":sha(a.build_summary),"frozen_spec":str(Path(a.spec)),
         "frozen_spec_sha256":sha(a.spec),"stage1_performance_seen":False,
         "immutability_rule":"Downstream semantic and Stage-1 gates must consume this release copy, never workspace."}
 (rd/"implementation_release.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
 # Copy resource summary if present next to build summary
 rs=Path(a.build_summary).parent/"resource_summary.json"
 if not rs.exists(): rs=Path(a.build_summary).parent/"resource_summary_partial.json"
 if rs.exists(): shutil.copy2(rs,rd/rs.name)
 print(json.dumps({"state":"IMPLEMENTATION_RELEASED","release_dir":str(rd),"release_module":str(target),"module_sha256":release_hash,"release_record":str(rd/"implementation_release.json")},indent=2))
if __name__=="__main__":main()
