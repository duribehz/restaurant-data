"""Conservative cleaning; preserves invalid source values for traceability."""
from __future__ import annotations
import re
import unicodedata
import pandas as pd
from src.config.settings import CHANNEL_ALIASES, COLUMN_MAPPING

def normalize_text(value: object) -> str | None:
    if pd.isna(value): return None
    return " ".join(str(value).strip().split()) or None

def normalize_channel(value: object) -> str:
    text = normalize_text(value) or "Otros"
    folded = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    for channel, aliases in CHANNEL_ALIASES.items():
        if any(alias in folded for alias in aliases): return channel
    return "Otros"

def to_number(series: pd.Series) -> pd.Series:
    clean = (series.astype("string").str.replace(r"[^0-9,.-]", "", regex=True)
             .str.replace(",", "", regex=False).replace({"-": None, "": None}))
    return pd.to_numeric(clean, errors="coerce")

def parse_closed_at(series: pd.Series) -> pd.Series:
    # The source uses Spanish month/day names, which pandas cannot parse reliably.
    # This function deliberately extracts only the clock portion; date comes from sale_id.
    clock = series.astype("string").str.extract(r"(\d{1,2}:\d{2}\s*[AP]M)", expand=False)
    return pd.to_datetime(clock, format="%I:%M %p", errors="coerce")

def standardize(frame: pd.DataFrame, kind: str) -> tuple[pd.DataFrame, dict]:
    original = len(frame); data = frame.rename(columns=COLUMN_MAPPING.get(kind, {})).copy()
    data.columns = [normalize_text(c) or str(c) for c in data.columns]
    for col in ("product_name", "category", "status", "order_type", "sale_id"):
        if col in data: data[col] = data[col].map(normalize_text)
    for col in ("total_amount", "line_amount", "quantity", "item_count"):
        if col in data: data[col] = to_number(data[col])
    if "closed_at" in data:
        clock = parse_closed_at(data["closed_at"])
        if "sale_id" in data:
            id_date = pd.to_datetime(data["sale_id"].str.extract(r"^(\d{4}-\d{2}-\d{2})")[0], errors="coerce")
            data["date"] = id_date
            data["datetime"] = id_date + (clock - clock.dt.normalize())
        else:
            data["datetime"] = clock
            data["date"] = clock.dt.normalize()
    if "order_type" in data: data["channel"] = data["order_type"].map(normalize_channel)
    before = len(data); data = data.drop_duplicates(); duplicates = before - len(data)
    return data, {"original_rows": original, "final_rows": len(data), "duplicates_removed": duplicates,
                  "relevant_nulls": {c: int(data[c].isna().sum()) for c in ["sale_id", "date", "total_amount", "product_name"] if c in data}}
