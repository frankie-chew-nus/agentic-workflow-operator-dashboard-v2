from pathlib import Path
import sys
p=Path('build_candidate_v2.py')
s=p.read_text(encoding='utf-8')
old='ws=Path("workspace")/a.candidate/"build_v2"'
new='ws=Path(a.workdir)/a.candidate/"workspace"'
if old not in s:
    print('HOLD: expected workspace expression not found');sys.exit(1)
s=s.replace(old,new)
needle='core.save(wd/"summary.json",out);print(json.dumps(out,indent=2))'
block="""if state=='IMPLEMENTATION_READY':
  import shutil
  release=wd/'release';release.mkdir(parents=True,exist_ok=True)
  target=release/'strategy_module.py';shutil.copy2(mp,target)
  source_hash=hashlib.sha256(Path(mp).read_bytes()).hexdigest()
  release_hash=hashlib.sha256(target.read_bytes()).hexdigest()
  if source_hash!=release_hash or release_hash!=out['module_sha256']:
   out['state']='HOLD_FOR_HUMAN';out['failures']=['ATOMIC_RELEASE_HASH_MISMATCH']
  else:
   rec={'state':'IMPLEMENTATION_RELEASED','candidate_id':c['candidate_id'],'version':c.get('version'),'module':'strategy_module.py','module_sha256':release_hash,'frozen_spec_sha256':hashlib.sha256(Path(a.spec).read_bytes()).hexdigest(),'stage1_performance_seen':False}
   core.save(release/'implementation_release.json',rec)
   if hashlib.sha256(target.read_bytes()).hexdigest()==rec['module_sha256']:
    out['state']='IMPLEMENTATION_RELEASED';out['release_module']=str(target);out['release_record']=str(release/'implementation_release.json');out['release_hash_verified']=True
   else:
    out['state']='HOLD_FOR_HUMAN';out['failures']=['RELEASE_RECORD_REVERIFY_FAILED']
core.save(wd/'summary.json',out);print(json.dumps(out,indent=2))"""
if needle not in s:
    print('HOLD: expected final save expression not found');sys.exit(1)
s=s.replace(needle,block)
Path('atomic_build_release.py').write_text(s,encoding='utf-8')
print('CREATED: atomic_build_release.py')
