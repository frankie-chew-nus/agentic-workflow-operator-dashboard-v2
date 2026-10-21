"""Conservative redaction of unittest logs before external evidence sharing."""
import re
def sanitize(log):
 if not isinstance(log,str):raise ValueError("log must be text")
 # Only retain unittest case results and the final unittest summary.
 lines=[]
 for line in log.splitlines():
  if re.fullmatch(r"test_[A-Za-z0-9_]+ \([A-Za-z0-9_.]+\) \.\.\. (?:ok|FAIL|ERROR|skipped .*)",line):
   lines.append(line)
  elif re.fullmatch(r"Ran [0-9]+ tests? in [0-9.]+s",line):
   lines.append(line)
  elif line in ("OK","FAILED") or re.fullmatch(r"FAILED \(.*\)",line):
   lines.append(line)
 return "\n".join(lines)+"\n" if lines else ""
