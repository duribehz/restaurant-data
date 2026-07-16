from __future__ import annotations
import pandas as pd
def valid_sales(df: pd.DataFrame) -> pd.DataFrame:
    data=df.copy()
    if "status" in data: data=data[data.status.str.lower().eq("completada").fillna(True)]
    return data
def sales_total(df: pd.DataFrame) -> float: return float(valid_sales(df).get("total_amount", pd.Series(dtype=float)).sum())
def unique_orders(df: pd.DataFrame) -> int: return int(valid_sales(df).get("sale_id", pd.Series(dtype=object)).nunique())
def ticket_average(df: pd.DataFrame) -> float:
    orders=unique_orders(df); return sales_total(df)/orders if orders else 0.0
def products_per_order(items: pd.DataFrame, sales: pd.DataFrame) -> float:
    orders=unique_orders(sales); return float(items.get("quantity", pd.Series(dtype=float)).sum()/orders) if orders else 0.0
def summary(sales: pd.DataFrame, items: pd.DataFrame) -> dict[str,float]:
    data=valid_sales(sales); daily=data.groupby("date", dropna=True).total_amount.sum() if "date" in data else pd.Series(dtype=float)
    monthly=data.groupby([data.date.dt.to_period("M")], dropna=True).total_amount.sum() if "date" in data else pd.Series(dtype=float)
    return {"Ventas totales":sales_total(data), "Pedidos / cuentas":unique_orders(data), "Ticket promedio":ticket_average(data), "Productos por pedido":products_per_order(items,data), "Venta promedio diaria":float(daily.mean()) if len(daily) else 0, "Venta promedio mensual":float(monthly.mean()) if len(monthly) else 0}
