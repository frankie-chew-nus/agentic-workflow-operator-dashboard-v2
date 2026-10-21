import json,re,hashlib
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def vt(v):
 m=re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)",str(v or ""))
 return tuple(map(int,m.groups())) if m else None
def bump(v):
 t=vt(v)
 return f"v{t[0]}.{t[1]}.{t[2]+1}" if t else None
def validate(parent,new,human_rationale):
 fails=[]
 # hard continuity
 for k in ["candidate_id","research_domain","hypothesis","evidence_refs","parameter_ranges","required_inputs","prohibited_dependencies"]:
  if new.get(k)!=parent.get(k):fails.append("UNAUTHORISED_CHANGE:"+k)
 # immutable revision lineage
 expected=bump(parent.get("version"))
 if not expected or new.get("version")!=expected:fails.append("VERSION_MUST_BE:"+str(expected))
 # cumulative accepted constraints for B002, derived from Human rulings
 ass=new.get("operator_assumptions",{})
 nr=(ass.get("narrow_range_definition") or "").lower()
 candle=(new.get("candle_definition") or "").lower()
 if "strict" not in nr or "<" not in candle:fails.append("STRICT_NR_N_NOT_PRESERVED")
 vol=(ass.get("volatility_expansion_definition") or ass.get("volatility_expansion_condition") or "").lower()
 entry=(new.get("entry_logic") or "").lower()
 if not ("breakout" in vol and "average" in vol and "preceding" in vol):fails.append("VOLATILITY_EXPANSION_RULE_MISSING")
 if not ("breakout candle range" in entry and "average range" in entry):fails.append("VOLATILITY_EXPANSION_NOT_IN_ENTRY")
 ex=(new.get("exit_logic") or "").lower()
 if not ("2.0" in ex and ("default" in ex or "starting" in ex) and "1.5" in json.dumps(new.get("parameter_ranges",{})) and "3.0" in json.dumps(new.get("parameter_ranges",{}))):
  fails.append("ATR_DEFAULT_SEARCH_RELATION_NOT_PRESERVED")
 return fails
