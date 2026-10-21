"""Fast deterministic D sandbox demonstration."""
import json,tempfile
from pathlib import Path
from operator_handoff import TEST,envelope
from d_sandbox import run
with tempfile.TemporaryDirectory() as d:
 r=Path(d);c=r/"c_summary.json";c.write_text('{"state":"C_TEST_FIXTURE"}')
 h=envelope("C","FIX-001","v0",TEST,[("c_summary",c)],"C_TEST_FIXTURE")
 print(json.dumps(run(h,[{"t":1,"outcome":1},{"t":2,"outcome":-1},{"t":3,"outcome":1}],r/"d"),indent=2))
