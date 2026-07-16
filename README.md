# Análisis de expansión de restaurante y dark kitchen

Proyecto modular en Pandas, Plotly y Streamlit para consolidar automáticamente las exportaciones de cada sucursal y analizar ventas, productos, tiempo, canales y comparación entre sucursales.

## Datos y trazabilidad

Las carpetas dentro de `data/raw/` se detectan dinámicamente; se admiten CSV y Excel. El perfilado de las exportaciones actuales identificó que `Ventas` contiene los importes de encabezado, `Ventas_Articulos` el detalle de productos, `Ventas_Productos` un agregado por producto y `Ventas_a_Domicilio` un resumen. Para no duplicar importes, las ventas generales se calculan solo desde `Ventas`.

Los KPIs de **pedidos / servicio de entrega** tienen una fuente distinta y autoritativa: `Ventas_a_Domicilio`. Su parser extrae el total de cuentas, importe total y, de cada concepto de canal, el número de pedidos y su importe. No usa filas agregadas de `Ventas` para sustituir estas cifras. La validación actual da 10,161 cuentas en Zibatá, 8,963 en El Refugio y 19,124 en conjunto.

Los IDs actuales incluyen registros agregados diarios por tipo de venta; no se usan como pedidos individuales para productos por pedido u horas pico. `Ventas_Articulos` de Zibatá solo cubre un día, por lo que las comparaciones temporales de detalle se marcan como cobertura desigual. No hay costos: la matriz se llama **Desempeño del menú** y usa popularidad y contribución a ingresos, nunca rentabilidad.

## Instalación y ejecución

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/inspect_data.py
python scripts/process_data.py
streamlit run dashboard/app.py
```

Los datos procesados quedan en `data/processed/` y los reportes en `output/reports/`. Si `pyarrow` no está disponible, el proceso guarda CSV en vez de Parquet.

## Arquitectura

`src/data` carga, limpia, transforma y valida; `src/metrics` contiene cálculos; `src/insights` produce observaciones descriptivas; `dashboard` presenta resultados. `src/advanced` contiene estacionalidad y tendencia lineal.

## Metodología

El ticket de pedidos es ventas de pedidos / cuentas reportadas; el ticket de canal es importe del canal / pedidos del canal. Los promedios por canal se etiquetan como “del periodo” porque el resumen no tiene una serie diaria por canal. El análisis temporal de pedidos usa solo filas agregadas de `Pedido a Domicilio`; MoM no se calcula cuando el mes previo es cero.

## Agregar sucursales

Cree una carpeta nueva en `data/raw/`, incluya las exportaciones y ejecute nuevamente perfilado y procesamiento. Si los encabezados cambian, ajuste el mapeo documentado en `src/config/settings.py` antes de procesar.
