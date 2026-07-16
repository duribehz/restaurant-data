from __future__ import annotations
import pandas as pd
AGGREGATE_ID_PATTERN=r"^\d{4}-\d{2}-\d{2}_(servicioEntrega|cuentaCliente)$"
def is_individual_sale_id(series: pd.Series) -> pd.Series:
    return series.notna() & ~series.astype(str).str.match(AGGREGATE_ID_PATTERN,na=False)
def coverage_report(frames: dict[str,pd.DataFrame]) -> pd.DataFrame:
    rows=[]
    for dataset,df in frames.items():
        if df.empty: continue
        for branch,part in df.groupby("Sucursal",dropna=False):
            dates=pd.to_datetime(part.get("date"),errors="coerce") if "date" in part else pd.Series(dtype="datetime64[ns]")
            rows.append({"Sucursal":branch,"Dataset":dataset,"Periodo inicial":dates.min(),"Periodo final":dates.max(),"Días cubiertos":int((dates.max()-dates.min()).days+1) if dates.notna().any() else None,"Registros":len(part),"Cobertura de canal":float(part.get("channel",pd.Series(index=part.index,dtype=object)).notna().mean()) if "channel" in part else None,"Cobertura de hora":float(part.get("datetime",pd.Series(index=part.index,dtype="datetime64[ns]")).notna().mean()) if "datetime" in part else None,"Cobertura ID individual":float(is_individual_sale_id(part.sale_id).mean()) if "sale_id" in part else None})
    return pd.DataFrame(rows)
