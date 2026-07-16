"""Dynamic loading of CSV/XLSX exports from all branch folders."""
from __future__ import annotations
from pathlib import Path
from typing import Iterable
import pandas as pd
from src.config.settings import FILE_TYPES, RAW_DATA_DIR

def discover_branches(raw_dir: Path = RAW_DATA_DIR) -> list[Path]:
    if not raw_dir.exists(): raise FileNotFoundError(f"No existe {raw_dir}")
    return sorted(p for p in raw_dir.iterdir() if p.is_dir())

def classify_file(path: Path) -> str | None:
    name = path.name.lower()
    if "articulos" in name: return "articulos"
    if "productos" in name: return "productos"
    if "domicilio" in name: return "domicilio"
    if name.startswith("ventas"): return "ventas"
    return None

def _read_export(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path, skiprows=4)
    # Las exportaciones actuales incluyen cuatro líneas descriptivas antes del encabezado.
    return pd.read_csv(path, encoding="utf-8-sig", skiprows=4)

def load_branch(path: Path) -> dict[str, pd.DataFrame]:
    result: dict[str, pd.DataFrame] = {}
    for file in path.iterdir():
        kind = classify_file(file)
        if kind and file.suffix.lower() in {".csv", ".xlsx", ".xls"}:
            frame = _read_export(file)
            frame["Sucursal"] = path.name
            frame["source_file"] = file.name
            result[kind] = frame
    return result

def load_all_branches(raw_dir: Path = RAW_DATA_DIR) -> dict[str, pd.DataFrame]:
    collected: dict[str, list[pd.DataFrame]] = {k: [] for k in FILE_TYPES}
    for branch in discover_branches(raw_dir):
        for kind, frame in load_branch(branch).items(): collected[kind].append(frame)
    return {kind: pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()
            for kind, frames in collected.items()}
