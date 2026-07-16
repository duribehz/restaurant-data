from __future__ import annotations
import pandas as pd
def monthly_trend(sales: pd.DataFrame) -> pd.DataFrame:
    if sales.empty or "date" not in sales: return pd.DataFrame()
    d=sales.assign(Mes=sales.date.dt.to_period("M").astype(str)).groupby("Mes").agg(Ventas=("total_amount","sum"), Pedidos=("sale_id","nunique")).reset_index()
    d["Ticket promedio"]=d.Ventas/d.Pedidos; d["MoM ventas %"]=d.Ventas.pct_change()*100; d["MoM pedidos %"]=d.Pedidos.pct_change()*100
    return d

def delivery_daily_sales(sales: pd.DataFrame) -> pd.DataFrame:
    """Daily delivery sales from aggregate delivery rows only; never includes table sales."""
    if sales.empty: return pd.DataFrame()
    d=sales[sales.get("sale_id",pd.Series(index=sales.index,dtype=str)).astype(str).str.endswith("_servicioEntrega")].copy()
    if d.empty: d=sales[sales.get("order_type",pd.Series(index=sales.index,dtype=str)).eq("Pedido a Domicilio")].copy()
    return d.groupby("date",dropna=True).agg(Ventas=("total_amount","sum"),Artículos=("item_count","sum")).reset_index()

def delivery_monthly_trend(sales: pd.DataFrame) -> pd.DataFrame:
    d=delivery_daily_sales(sales)
    if d.empty: return d
    d["Mes"]=d.date.dt.to_period("M").astype(str)
    out=d.groupby("Mes",as_index=False).agg(Ventas=("Ventas","sum"),Artículos=("Artículos","sum"))
    out["MoM ventas %"]=out.Ventas.pct_change().where(out.Ventas.shift().ne(0))*100
    return out
