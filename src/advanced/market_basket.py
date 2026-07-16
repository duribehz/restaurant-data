"""Pairs only from true individual sale IDs, never daily aggregate IDs."""
from itertools import combinations
import pandas as pd
from src.data.quality import is_individual_sale_id
def basket_diagnostic(items: pd.DataFrame) -> dict:
    valid=items[is_individual_sale_id(items.sale_id)] if "sale_id" in items else pd.DataFrame()
    return {"Pedidos individuales válidos":valid.sale_id.nunique() if not valid.empty else 0,"Pedidos con 2+ productos":int((valid.groupby("sale_id").product_name.nunique()>=2).sum()) if not valid.empty else 0,"Productos":valid.product_name.nunique() if not valid.empty else 0}
def frequent_pairs(items: pd.DataFrame) -> pd.DataFrame:
    valid=items[is_individual_sale_id(items.sale_id)]
    baskets=valid.groupby("sale_id").product_name.apply(lambda x: sorted(set(x.dropna())))
    rows=[pair for basket in baskets if len(basket)>=2 for pair in combinations(basket,2)]
    if not rows:return pd.DataFrame(columns=["Producto A","Producto B","Pedidos juntos","Soporte"])
    out=pd.DataFrame(rows,columns=["Producto A","Producto B"]).value_counts().reset_index(name="Pedidos juntos"); out["Soporte"]=out["Pedidos juntos"]/len(baskets); return out
