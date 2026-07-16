from src.metrics.kpis import summary
import pandas as pd
def by_channel(sales: pd.DataFrame, items: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for channel, group in sales.groupby("channel", dropna=False):
        rows.append({"Canal":channel, **summary(group, items[items.sale_id.isin(group.sale_id)] if "sale_id" in items else items)})
    return pd.DataFrame(rows)
