"""Simple descriptive linear trend; not a financial forecast."""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from src.metrics.time_analysis import delivery_daily_sales
def linear_trend(sales: pd.DataFrame) -> tuple[pd.DataFrame,dict]:
    d=delivery_daily_sales(sales)
    if len(d)<2: return d,{"slope":None,"r2":None}
    d=d.set_index("date").resample("W").Ventas.sum().reset_index(); x=np.arange(len(d)).reshape(-1,1); model=LinearRegression().fit(x,d.Ventas)
    d["Tendencia lineal"]=model.predict(x); return d,{"slope":float(model.coef_[0]),"r2":float(model.score(x,d.Ventas))}
