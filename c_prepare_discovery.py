import argparse,json,subprocess,sys
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--c-root',required=True)
a=p.parse_args()
root=Path(a.c_root)
names=[
 'atomic_build_release.py','atomic_build_release_clean.py','file_authoritative_build.py',
 'make_atomic_build.py','release_semantic_gate.py','semantic_repair_release.py',
 'freeze_stage1_plan.py','stage1_runner.py','stage1_runner_v3.py'
]
out={'state':'C_PREPARATION_DISCOVERY_READY','c_root':str(root),'scripts':{}}
for name in names:
    path=root/name
    if not path.exists():
        out['scripts'][name]={'present':False}
        continue
    q=subprocess.run([sys.executable,str(path),'--help'],cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
    out['scripts'][name]={'present':True,'return_code':q.returncode,'help':q.stdout}
ev=Path(__file__).resolve().parent/'evidence'/'c_preparation_discovery.json'
ev.parent.mkdir(parents=True,exist_ok=True)
ev.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'state':out['state'],'evidence':str(ev)},indent=2))
