from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import plotly.express as px
import streamlit as st
from src.config.settings import PROCESSED_DIR, VALID_CHANNELS
from src.metrics.kpis import summary
from src.metrics.products import product_table, pareto
from src.metrics.menu_engineering import menu_matrix
from src.metrics.delivery import channel_kpis, delivery_summary, branch_delivery_kpis
from src.metrics.time_analysis import delivery_daily_sales, delivery_monthly_trend
from src.advanced.seasonality import seasonality
from src.advanced.forecasting import linear_trend
from src.advanced.market_basket import basket_diagnostic
from src.utils.filters import apply_filters
from src.utils.exports import to_csv_bytes
from dashboard.components.sidebar import global_filters

st.set_page_config(page_title="Expansión Currucucu", layout="wide")
@st.cache_data
def load_processed():
    result={}
    for kind in ("ventas","articulos","productos","delivery_channels","delivery_totals"):
        path=PROCESSED_DIR/f"{kind}.parquet"
        result[kind]=pd.read_parquet(path) if path.exists() else pd.DataFrame()
    return result

data=load_processed()
if data["ventas"].empty:
    st.error("No hay datos procesados. Ejecuta `python scripts/process_data.py`."); st.stop()
st.title("Análisis de expansión y dark kitchen")
filters=global_filters(data["ventas"], data["articulos"])
sales=apply_filters(data["ventas"], **filters)
delivery=data["delivery_channels"]
totals=data["delivery_totals"]
if "Todas" not in filters["branch"]:
    delivery=delivery[delivery.Sucursal.isin(filters["branch"])]
    totals=totals[totals.Sucursal.isin(filters["branch"])]
page=st.sidebar.radio("Sección", ["Resumen Ejecutivo","Canales","Productos","Tiempo","Sucursales","Desempeño del Menú","Análisis Avanzado"])

def filtered_products():
    products=data["productos"].copy()
    if "Todas" not in filters["branch"]: products=products[products.Sucursal.isin(filters["branch"])]
    if "Todas" not in filters["categories"]: products=products[products.category.isin(filters["categories"])]
    if "Todos" not in filters["products"]: products=products[products.product_name.isin(filters["products"])]
    return products

if page=="Resumen Ejecutivo":
    k=delivery_summary(totals)
    for col,(name,value) in zip(st.columns(3),k.items()): col.metric(name, f"${value:,.2f}" if "Venta" in name or "Ticket" in name else f"{value:,.0f}")
    channels=channel_kpis(delivery)
    left,right=st.columns(2)
    left.plotly_chart(px.bar(totals,x="Sucursal",y="Ventas de pedidos",title="Ventas de pedidos por sucursal"),width="stretch")
    if not channels.empty: right.plotly_chart(px.bar(channels,x="Canal",y="Ventas",title="Ventas de pedidos por canal"),width="stretch")
    st.caption("Pedidos y canales proceden del resumen anual de domicilio; los filtros de fecha no modifican estos totales.")
    st.metric("Ventas generales del restaurante (separadas)", f"${summary(sales, data['articulos'])['Ventas totales']:,.2f}")
elif page=="Canales":
    channels=channel_kpis(delivery)
    st.caption("Solo se muestran Uber, Rappi, Envío Propio y Ordena y Recoge. Promedios calculados sobre el periodo completo.")
    if channels.empty: st.info("No hay canales válidos para las sucursales seleccionadas.")
    else:
        st.dataframe(channels,width="stretch")
        st.plotly_chart(px.bar(channels,x="Canal",y="Ticket promedio",title="Ticket promedio por canal"),width="stretch")
elif page=="Productos":
    table=product_table(filtered_products())
    if table.empty: st.info("No hay datos de productos para los filtros seleccionados.")
    else:
        n=st.selectbox("Número de productos",[10,20,50])
        best,bottom,participation,categories=st.tabs(["Más vendidos","Menos vendidos","Participación y Pareto","Categorías"])
        top=table.nlargest(n,"Cantidad").sort_values("Cantidad")
        best.dataframe(top,width="stretch"); best.plotly_chart(px.bar(top,x="Cantidad",y="product_name",orientation="h"),width="stretch")
        low=table.nsmallest(n,"Cantidad").sort_values("Cantidad")
        bottom.dataframe(low,width="stretch"); bottom.plotly_chart(px.bar(low,x="Cantidad",y="product_name",orientation="h"),width="stretch")
        p=pareto(filtered_products()); participation.dataframe(p.head(n),width="stretch"); participation.plotly_chart(px.bar(p.head(n),x="product_name",y="Ingresos"),width="stretch")
        raw=filtered_products(); cats=raw.groupby("category",dropna=False).agg(Cantidad=("quantity","sum"),Importe=("line_amount","sum")).reset_index(); cats["% importe"]=cats.Importe/cats.Importe.sum()
        categories.dataframe(cats.sort_values("Importe",ascending=False),width="stretch")
        st.download_button("Descargar productos",to_csv_bytes(table),"productos.csv","text/csv")
elif page=="Tiempo":
    trend=delivery_monthly_trend(sales); daily=delivery_daily_sales(sales)
    if trend.empty: st.info("No hay ventas de pedidos con fecha para el filtro seleccionado.")
    else:
        st.dataframe(trend,width="stretch"); st.plotly_chart(px.line(trend,x="Mes",y="Ventas",markers=True,title="Ventas de pedidos por mes"),width="stretch")
        st.plotly_chart(px.bar(daily,x="date",y="Ventas",title="Ventas diarias de pedidos"),width="stretch")
elif page=="Sucursales":
    comparison=branch_delivery_kpis(data["delivery_totals"],data["ventas"],data["productos"])
    st.subheader("KPIs comparables por sucursal"); st.dataframe(comparison,width="stretch")
    channels=data["delivery_channels"][data["delivery_channels"].Canal.isin(VALID_CHANNELS)]
    st.plotly_chart(px.bar(channels,x="Canal",y="Importe_Ventas",color="Sucursal",barmode="group",title="Importe por canal y sucursal"),width="stretch")
    st.caption("Los productos se basan en los periodos disponibles de cada archivo; la cobertura de detalle no es equivalente entre sucursales.")
    branch_products=data["productos"].groupby(["Sucursal","product_id","product_name","category"],dropna=False).agg(Cantidad=("quantity","sum"),Ingresos=("line_amount","sum")).reset_index().sort_values(["Sucursal","Cantidad"],ascending=[True,False])
    st.dataframe(branch_products.groupby("Sucursal",group_keys=False).head(10),width="stretch")
    values=comparison.set_index("Sucursal").T; values.insert(0,"Indicador",values.index); st.subheader("Tabla comparativa final"); st.dataframe(values.reset_index(drop=True),width="stretch")
elif page=="Desempeño del Menú":
    st.warning("La información disponible no incluye costos unitarios. Esta matriz analiza popularidad y contribución a ingresos, no rentabilidad.")
    matrix=menu_matrix(filtered_products())
    if matrix.empty: st.info("No hay datos disponibles para los filtros seleccionados.")
    else:
        fig=px.scatter(matrix,x="Cantidad",y="Ingresos",size="Contribución a ingresos",color="Clasificación",hover_name="product_name",hover_data=["category","Participación unidades","Contribución a ingresos"])
        fig.add_vline(x=matrix["Umbral popularidad"].iloc[0]); fig.add_hline(y=matrix["Umbral contribución"].iloc[0])
        st.plotly_chart(fig,width="stretch"); st.dataframe(matrix,width="stretch")
else:
    season,week=seasonality(sales); trend,stats=linear_trend(sales); diagnostic=basket_diagnostic(data["articulos"])
    sea,forecast,basket=st.tabs(["Estacionalidad","Regresión lineal","Productos que se venden juntos"])
    with sea:
        st.warning("Un solo ciclo anual es insuficiente para confirmar patrones estacionales recurrentes."); st.dataframe(season,width="stretch"); st.dataframe(week,width="stretch")
    with forecast:
        st.warning("Esta regresión representa una tendencia lineal simple, no un pronóstico financiero definitivo."); st.write(stats)
        if not trend.empty: st.plotly_chart(px.line(trend,x="date",y=["Ventas","Tendencia lineal"]),width="stretch")
    with basket:
        st.write(diagnostic); st.info("No existe suficiente detalle transaccional representativo del periodo completo; los IDs diarios agregados se excluyen.")
