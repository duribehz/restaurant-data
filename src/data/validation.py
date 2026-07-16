from __future__ import annotations
import pandas as pd
def validate_data(sales: pd.DataFrame, items: pd.DataFrame) -> list[str]:
    warnings=[]
    if "sale_id" in sales and sales.sale_id.duplicated().any(): warnings.append("Hay IDs de venta repetidos; se conservaron porque pueden ser agregados diarios.")
    if "sale_id" in sales and "sale_id" in items:
        orphan = items.loc[~items.sale_id.isin(sales.sale_id), "sale_id"].nunique()
        if orphan: warnings.append(f"{orphan} IDs de detalle no aparecen en Ventas.")
    for df, label, col in ((sales,"ventas","total_amount"),(items,"artículos","quantity")):
        if col in df and (df[col] < 0).any(): warnings.append(f"Hay valores negativos en {label}.{col}.")
    return warnings
