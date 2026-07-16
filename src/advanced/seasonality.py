"""Descriptive observed-seasonality analysis for delivery sales."""
import pandas as pd
from src.metrics.time_analysis import delivery_daily_sales
def seasonality(sales: pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame]:
    d=delivery_daily_sales(sales)
    if d.empty: return pd.DataFrame(),pd.DataFrame()
    d["Mes"]=d.date.dt.month; d["Día de semana"]=d.date.dt.day_name()
    month=d.groupby("Mes",as_index=False).Ventas.mean().rename(columns={"Ventas":"Venta promedio diaria"})
    month["Índice estacional observado"]=month["Venta promedio diaria"]/d.Ventas.mean()
    weekdays=d.groupby("Día de semana",as_index=False).Ventas.agg(["sum","mean","count"]).reset_index()
    return month,weekdays
