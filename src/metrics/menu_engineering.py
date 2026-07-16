from __future__ import annotations
import pandas as pd
from src.metrics.products import product_table
def menu_matrix(items: pd.DataFrame) -> pd.DataFrame:
    data=product_table(items)
    if data.empty: return data
    total=data.Ingresos.sum()
    if not total: return pd.DataFrame(columns=data.columns)
    data["Participación unidades"] = data.Cantidad / data.Cantidad.sum()
    data["Contribución a ingresos"] = data.Ingresos / total
    data["Umbral popularidad"] = data.Cantidad.median(); data["Umbral contribución"] = data.Ingresos.median()
    pop=data.Cantidad >= data["Umbral popularidad"]; val=data.Ingresos >= data["Umbral contribución"]
    data["Clasificación"] = "Baja popularidad / Baja contribución"; data.loc[pop & val,"Clasificación"]="Alta popularidad / Alta contribución"; data.loc[pop & ~val,"Clasificación"]="Alta popularidad / Baja contribución"; data.loc[~pop & val,"Clasificación"]="Baja popularidad / Alta contribución"
    return data
