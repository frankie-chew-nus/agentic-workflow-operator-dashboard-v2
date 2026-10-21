def create_source(stage,kind,**kw):
 stage=stage.upper();kind=kind.upper()
 if stage=="C" and kind!="CSV": raise PermissionError("C_STAGE1_MUST_USE_FROZEN_CSV")
 if stage=="D" and kind!="MT5": raise PermissionError("D_STAGE2_MUST_USE_MT5")
 from .sources import CSVDataSource,MT5DataSource
 return CSVDataSource(**kw) if kind=="CSV" else MT5DataSource(**kw)
