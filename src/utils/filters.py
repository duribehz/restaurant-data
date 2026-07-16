from __future__ import annotations
import pandas as pd
def apply_filters(df: pd.DataFrame, branch=None, dates=None, channels=None, categories=None, products=None) -> pd.DataFrame:
    d=df.copy()
    if branch and "Todas" not in branch: d=d[d.Sucursal.isin(branch)]
    if dates and "date" in d: d=d[d.date.between(pd.Timestamp(dates[0]),pd.Timestamp(dates[1]))]
    if channels and "Todos" not in channels and "channel" in d: d=d[d.channel.isin(channels)]
    if categories and "Todas" not in categories and "category" in d: d=d[d.category.isin(categories)]
    if products and "Todos" not in products and "product_name" in d: d=d[d.product_name.isin(products)]
    return d
