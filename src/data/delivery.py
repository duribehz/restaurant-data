"""Parser for the authoritative, annual delivery-service summary export."""
from __future__ import annotations
import re
import unicodedata
import pandas as pd
from src.config.settings import DELIVERY_CHANNEL_ALIASES
from src.data.cleaning import to_number

def _fold(value: object) -> str:
    return unicodedata.normalize("NFKD", str(value).lower()).encode("ascii", "ignore").decode()

def normalize_delivery_channel(concept: object) -> str | None:
    text=_fold(concept)
    for channel, aliases in DELIVERY_CHANNEL_ALIASES.items():
        if any(alias in text for alias in aliases): return channel
    return None

def parse_delivery_summary(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return normalized channels and branch-level totals, without guessing channels."""
    rows=[]; totals=[]
    for branch, part in df.groupby("Sucursal", dropna=False):
        concept=part["concept"].fillna("").astype(str)
        folded=concept.map(_fold)
        values=to_number(part["value"])
        account=part[folded.str.contains(r"numero de cuentas",regex=True,na=False)]
        total=part[folded.str.contains(r"importe total",regex=True,na=False)]
        totals.append({"Sucursal":branch,"Número de cuentas reportado":int(to_number(account["value"]).iloc[0]) if len(account) else None,"Ventas de pedidos":float(to_number(total["value"]).iloc[0]) if len(total) else None})
        for idx, raw in concept.items():
            match=re.search(r":\s*([\d,]+)\s*$",raw)
            if not match: continue
            rows.append({"Sucursal":branch,"Canal":normalize_delivery_channel(raw),"Cantidad_Pedidos":int(match.group(1).replace(",","")),"Importe_Ventas":float(values.loc[idx]) if pd.notna(values.loc[idx]) else 0.0,"Concepto original":raw})
    channels=pd.DataFrame(rows,columns=["Sucursal","Canal","Cantidad_Pedidos","Importe_Ventas","Concepto original"])
    totals_df=pd.DataFrame(totals)
    if not channels.empty:
        classified=channels.groupby("Sucursal").Cantidad_Pedidos.sum().rename("Cuentas clasificadas")
        totals_df=totals_df.merge(classified,on="Sucursal",how="left").fillna({"Cuentas clasificadas":0})
        totals_df["Diferencia cuentas"]=totals_df["Número de cuentas reportado"]-totals_df["Cuentas clasificadas"]
    return channels, totals_df
