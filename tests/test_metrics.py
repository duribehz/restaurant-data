import pandas as pd
from src.metrics.kpis import sales_total, unique_orders, ticket_average
from src.data.cleaning import normalize_channel
from src.utils.filters import apply_filters
from src.data.delivery import parse_delivery_summary, normalize_delivery_channel
from src.metrics.delivery import channel_kpis, delivery_summary
def sample(): return pd.DataFrame({"sale_id":["a","b"],"total_amount":[100,200],"status":["Completada","Completada"],"Sucursal":["x","y"],"channel":["Uber","Rappi"],"date":pd.to_datetime(["2026-01-01","2026-01-02"])})
def test_kpis():
    d=sample(); assert sales_total(d)==300 and unique_orders(d)==2 and ticket_average(d)==150
def test_channel_normalization(): assert normalize_channel("UBER EATS")=="Uber"
def test_filters(): assert len(apply_filters(sample(),branch=["x"]))==1
def test_delivery_parser_current_totals():
    raw=pd.DataFrame({"Sucursal":["z","z","z","r","r"],"concept":["Número de cuentas","Uber - x: 981","Ordene y recoja: 6911","Número de cuentas","Rappi: 300"],"value":["10161","$85,851.50","$2,029,259.02","8963","$80.00"]})
    channels,totals=parse_delivery_summary(raw)
    assert totals["Número de cuentas reportado"].sum()==19124
    assert set(channels.Canal)=={"Uber","Ordena y Recoge","Rappi"}
    assert channel_kpis(channels).query("Canal == 'Uber'").iloc[0]["Ticket promedio"]==85851.50/981
def test_delivery_channel_aliases():
    assert normalize_delivery_channel("Envío Propio: 2")=="Envío Propio"
    assert normalize_delivery_channel("Servicio desconocido: 3") is None
def test_unknown_delivery_channel_is_not_in_channel_kpis():
    raw=pd.DataFrame({"Sucursal":["x","x"],"concept":["Uber Eats: 2","Servicio externo: 3"],"value":["$20.00","$30.00"]})
    channels,_=parse_delivery_summary(raw)
    assert channel_kpis(channels).Canal.tolist()==["Uber"]
