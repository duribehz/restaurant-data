from src.metrics.kpis import summary
import pandas as pd
def compare_branches(sales: pd.DataFrame, items: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([{"Sucursal":b, **summary(g,items[items.Sucursal.eq(b)])} for b,g in sales.groupby("Sucursal")])
