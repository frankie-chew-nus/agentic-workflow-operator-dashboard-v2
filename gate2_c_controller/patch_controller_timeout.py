from pathlib import Path
p=Path("c_controller.py")
s=p.read_text(encoding="utf-8")
s=s.replace('def call(base,model,msg,key=None):','def call(base,model,msg,key=None,timeout=None):')
s=s.replace('with urllib.request.urlopen(q,timeout=180) as r:return json.load(r)','with urllib.request.urlopen(q,timeout=(timeout or (900 if base.startswith("http://192.168.51.81") else 180))) as r:return json.load(r)')
p.write_text(s,encoding="utf-8")
print("PATCHED: local/private endpoint timeout defaults to 900s; external remains 180s")
