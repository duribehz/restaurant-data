from __future__ import annotations
import pandas as pd
def product_table(items: pd.DataFrame, ascending: bool=False) -> pd.DataFrame:
    columns=[c for c in ["product_id","product_name","category"] if c in items]
    if not columns or "quantity" not in items: return pd.DataFrame()
    valid=items[items["quantity"].gt(0) & items["product_name"].notna()].copy()
    if valid.empty: return pd.DataFrame(columns=columns+["Cantidad","Ingresos","Participación"])
    aggregations={"Cantidad":("quantity","sum"),"Ingresos":("line_amount","sum")}
    if "sale_id" in valid: aggregations["Pedidos"]=("sale_id","nunique")
    if "date" in valid: aggregations["Última fecha"]=("date","max")
    group=valid.groupby(columns, dropna=False).agg(**aggregations).reset_index()
    group["Participación"] = group.Ingresos / group.Ingresos.sum() if group.Ingresos.sum() else 0
    return group.sort_values("Cantidad", ascending=ascending)
def pareto(items: pd.DataFrame) -> pd.DataFrame:
    data=product_table(items).sort_values("Ingresos", ascending=False).copy()
    if not data.empty: data["Participación acumulada"] = data.Ingresos.cumsum()/data.Ingresos.sum()
    return data
