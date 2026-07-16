"""Profile every raw export and document detected relationships."""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config.settings import OUTPUT_DIR, RAW_DATA_DIR
from src.data.loader import discover_branches, load_branch

def profile_frame(df):
    categorical = {c: df[c].dropna().astype(str).unique()[:20].tolist() for c in df.columns if df[c].dtype == "object" and df[c].nunique() <= 25}
    return {"rows":len(df),"columns":len(df.columns),"column_names":df.columns.tolist(),"dtypes":df.dtypes.astype(str).to_dict(),"nulls":df.isna().sum().to_dict(),"null_percent":(df.isna().mean()*100).round(2).to_dict(),"duplicates":int(df.duplicated().sum()),"candidate_identifiers":[c for c in df.columns if "id" in c.lower() or "referencia" in c.lower()],"categorical_values":categorical,"sample":df.head(5).fillna("").to_dict("records")}

def main():
    target=OUTPUT_DIR/"reports"/"data_profile"; target.mkdir(parents=True,exist_ok=True)
    report={"branches":{},"relationships":["Ventas.ID único ↔ Ventas_Articulos.ID Venta Único: relación conceptual uno-a-muchos; varios IDs son agregados diarios.","Ventas_Productos es agregado por producto y no tiene ID de pedido.","Ventas_a_Domicilio es resumen Concepto/Importe, no detalle transaccional."]}
    for branch in discover_branches(RAW_DATA_DIR):
        frames=load_branch(branch); report["branches"][branch.name]={kind:profile_frame(df) for kind,df in frames.items()}
        print(f"\n{branch.name}")
        for kind,df in frames.items(): print(f"  {kind}: {len(df):,} filas × {len(df.columns)} columnas")
    (target/"profile.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    (target/"README.md").write_text("# Perfilado de datos\n\nEl detalle está en `profile.json`. Los importes de encabezado se calculan exclusivamente desde `Ventas` para evitar duplicación.\n",encoding="utf-8")
    print(f"\nReporte guardado en {target}")
if __name__ == "__main__": main()
