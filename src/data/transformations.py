from __future__ import annotations
import pandas as pd

MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
def add_time_dimensions(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    if "date" not in data: return data
    dates = pd.to_datetime(data["date"], errors="coerce")
    data["Año"] = dates.dt.year; data["Número de mes"] = dates.dt.month
    data["Mes"] = pd.Categorical(dates.dt.month.map(lambda x: MONTHS[int(x)-1] if pd.notna(x) else None), categories=MONTHS, ordered=True)
    data["Semana"] = dates.dt.isocalendar().week.astype("Int64"); data["Día"] = dates.dt.date
    data["Número de día de la semana"] = dates.dt.dayofweek
    data["Día de la semana"] = pd.Categorical(dates.dt.dayofweek.map(lambda x: DAYS[int(x)] if pd.notna(x) else None), categories=DAYS, ordered=True)
    data["Trimestre"] = dates.dt.quarter
    data["Semestre"] = dates.dt.month.map(lambda x: "Enero - Junio" if pd.notna(x) and x <= 6 else ("Julio - Diciembre" if pd.notna(x) else None))
    if "datetime" in data: data["Hora"] = pd.to_datetime(data["datetime"], errors="coerce").dt.hour
    return data
