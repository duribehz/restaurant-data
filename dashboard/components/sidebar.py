import streamlit as st
def global_filters(sales,items):
    branches=st.sidebar.multiselect("Sucursal",["Todas"]+sorted(sales.Sucursal.dropna().unique().tolist()),default=["Todas"])
    valid=sales.date.dropna(); dates=st.sidebar.date_input("Rango de fechas",value=(valid.min().date(),valid.max().date()) if len(valid) else None)
    channels=st.sidebar.multiselect("Canal",["Todos"]+sorted(sales.channel.dropna().unique().tolist()),default=["Todos"])
    cats=st.sidebar.multiselect("Categoría",["Todas"]+sorted(items.category.dropna().unique().tolist()),default=["Todas"])
    products=st.sidebar.multiselect("Producto",["Todos"]+sorted(items.product_name.dropna().unique().tolist()),default=["Todos"])
    sem=st.sidebar.multiselect("Semestre",["Todos","Enero - Junio","Julio - Diciembre"],default=["Todos"])
    return dict(branch=branches,dates=dates,channels=channels,categories=cats,products=products,semesters=sem)
