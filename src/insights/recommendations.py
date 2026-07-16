from __future__ import annotations
import pandas as pd
from src.metrics.kpis import sales_total
def generate_insights(sales: pd.DataFrame, items: pd.DataFrame) -> list[str]:
    if sales.empty: return ["No hay datos para los filtros seleccionados."]
    texts=[]; total=sales_total(sales)
    if "Sucursal" in sales:
        branch=sales.groupby("Sucursal").total_amount.sum().sort_values(ascending=False)
        if len(branch) and total: texts.append(f"{branch.index[0]} representa {branch.iloc[0]/total:.1%} de las ventas observadas.")
    if "channel" in sales:
        ch=sales.groupby("channel").sale_id.nunique().sort_values(ascending=False)
        if len(ch): texts.append(f"{ch.index[0]} es el canal/tipo de venta con más IDs únicos disponibles.")
    if "Día de la semana" in sales:
        day=sales.groupby("Día de la semana", observed=False).total_amount.sum().sort_values(ascending=False)
        if len(day) and total: texts.append(f"{day.index[0]} concentra {day.iloc[0]/total:.1%} de las ventas observadas.")
    return texts
