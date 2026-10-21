"""Validate released strategy module against the Stage 1 execution contract."""
import importlib.util,json,re
from pathlib import Path

def _load_module(release_record):
    rec=json.loads(Path(release_record).read_text(encoding="utf-8"))
    mp=Path(release_record).parent/rec["module"]
    spec=importlib.util.spec_from_file_location("gate2_stage1_contract_probe",mp)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return rec,mod

def validate(release_record,plan,runner=None):
    rec,mod=_load_module(release_record)
    pl=json.loads(Path(plan).read_text(encoding="utf-8"))
    variants=pl.get("variants",[])
    schema=mod.parameter_schema() if hasattr(mod,"parameter_schema") else {}
    schema_keys=set(schema.keys()) if isinstance(schema,dict) else set()
    variant_keys=set(variants[0].get("parameters",{}).keys()) if variants else set()
    runner_keys=set()
    runner_interface_current=True
    if runner is not None:
        source=Path(runner).read_text(encoding="utf-8")
        runner_keys=set(re.findall(r'par\["([^"]+)"\]',source))
        runner_interface_current=("m.signal(" in source and "m.prepare(prefix)" in source)
    checks={
      "prepare_callable":callable(getattr(mod,"prepare",None)),
      "signal_callable":callable(getattr(mod,"signal",None)),
      "runner_uses_current_signal_interface":runner_interface_current,
      "runner_parameter_keys_available":runner_keys.issubset(variant_keys),
      "variant_parameter_keys_match_module":bool(variants) and variant_keys==schema_keys,
      "release_module_hash_present":isinstance(rec.get("module_sha256"),str) and len(rec["module_sha256"])==64
    }
    return {"state":"C_STAGE1_INTERFACE_READY" if all(checks.values()) else "C_STAGE1_INTERFACE_HOLD",
            "checks":checks,"module_parameter_keys":sorted(schema_keys),
            "variant_parameter_keys":sorted(variant_keys),"runner_parameter_keys":sorted(runner_keys),"variant_count":len(variants),
            "safe_to_run":all(checks.values())}
