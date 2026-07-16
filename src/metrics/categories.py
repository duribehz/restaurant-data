import pandas as pd
def category_table(items: pd.DataFrame) -> pd.DataFrame:
    if "category" not in items: return pd.DataFrame()
    d=items.groupby("category").agg(Ingresos=("line_amount","sum"),Cantidad=("quantity","sum"),Pedidos=("sale_id","nunique")).reset_index()
    d["Participación de ingresos"]=d.Ingresos/d.Ingresos.sum() if d.Ingresos.sum() else 0; return d
