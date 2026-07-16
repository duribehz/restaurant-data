"""Load, standardize, validate and save dashboard datasets."""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config.settings import OUTPUT_DIR, PROCESSED_DIR
from src.data.loader import load_all_branches
from src.data.cleaning import standardize
from src.data.transformations import add_time_dimensions
from src.data.validation import validate_data
from src.data.delivery import parse_delivery_summary
from src.data.quality import coverage_report
def save(df,path):
    try: df.to_parquet(path,index=False); return path
    except ImportError: df.to_csv(path.with_suffix(".csv"),index=False); return path.with_suffix(".csv")
def main():
    PROCESSED_DIR.mkdir(parents=True,exist_ok=True); (OUTPUT_DIR/"reports").mkdir(parents=True,exist_ok=True)
    raw=load_all_branches(); cleaned={}; report={"cleaning":{},"files":{}}
    for kind,df in raw.items():
        clean,detail=standardize(df,kind); clean=add_time_dimensions(clean); cleaned[kind]=clean
        report["cleaning"][kind]=detail; report["files"][kind]=str(save(clean,PROCESSED_DIR/f"{kind}.parquet"))
    delivery_channels, delivery_totals=parse_delivery_summary(cleaned["domicilio"])
    report["files"]["delivery_channels"]=str(save(delivery_channels,PROCESSED_DIR/"delivery_channels.parquet"))
    report["files"]["delivery_totals"]=str(save(delivery_totals,PROCESSED_DIR/"delivery_totals.parquet"))
    quality=coverage_report(cleaned)
    report["files"]["data_quality"]=str(save(quality,PROCESSED_DIR/"data_quality.parquet"))
    report["delivery_validation"]=delivery_totals.to_dict("records")
    report["warnings"]=validate_data(cleaned["ventas"],cleaned["articulos"])
    (OUTPUT_DIR/"reports"/"processing_summary.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2,default=str))
if __name__ == "__main__": main()
