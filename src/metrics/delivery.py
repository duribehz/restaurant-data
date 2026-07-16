"""KPIs sourced only from the delivery summary, not from aggregate sales rows."""
from __future__ import annotations
import pandas as pd
from src.config.settings import VALID_CHANNELS
def channel_kpis(channels: pd.DataFrame, period_days: int | None = None) -> pd.DataFrame:
    channels=channels[channels["Canal"].isin(VALID_CHANNELS)].copy()
    if channels.empty: return pd.DataFrame(columns=["Canal","Pedidos","Ventas","Ticket promedio","Participación ventas","Participación pedidos"])
    d=channels.groupby("Canal",as_index=False).agg(Pedidos=("Cantidad_Pedidos","sum"),Ventas=("Importe_Ventas","sum"))
    d["Ticket promedio"]=d.Ventas/d.Pedidos.replace(0,pd.NA)
    d["Participación ventas"]=d.Ventas/d.Ventas.sum(); d["Participación pedidos"]=d.Pedidos/d.Pedidos.sum()
    if period_days:
        d["Promedio diario del periodo"]=d.Ventas/period_days; d["Promedio semanal del periodo"]=d.Ventas/(period_days/7); d["Promedio mensual del periodo"]=d.Ventas/(period_days/30.4375)
    return d
def delivery_summary(totals: pd.DataFrame) -> dict[str,float]:
    sales=float(totals["Ventas de pedidos"].sum()); accounts=int(totals["Número de cuentas reportado"].sum())
    return {"Ventas de pedidos":sales,"Número de cuentas":accounts,"Ticket promedio de pedidos":sales/accounts if accounts else 0.0}

def branch_delivery_kpis(totals: pd.DataFrame, sales: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Comparable branch KPIs using delivery totals and observed delivery-day aggregates."""
    rows=[]
    for _, row in totals.iterrows():
        branch=row["Sucursal"]; daily=sales[(sales.Sucursal==branch) & sales.sale_id.astype(str).str.endswith("_servicioEntrega")].groupby("date").total_amount.sum()
        product_units=float(products.loc[products.Sucursal.eq(branch),"quantity"].sum())
        account=float(row["Número de cuentas reportado"])
        rows.append({"Sucursal":branch,"Ventas de pedidos":row["Ventas de pedidos"],"Número de cuentas":account,"Ticket promedio de pedidos":row["Ventas de pedidos"]/account if account else pd.NA,"Productos vendidos":product_units,"Venta promedio diaria":daily.mean() if len(daily) else pd.NA,"Venta promedio semanal":daily.sum()/(len(daily)/7) if len(daily) else pd.NA,"Venta promedio mensual":daily.sum()/(len(daily)/30.4375) if len(daily) else pd.NA})
    return pd.DataFrame(rows)
