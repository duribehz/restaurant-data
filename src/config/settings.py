from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "output"

# Mapeo verificado contra las exportaciones Currucucu recibidas. Ajuste esta capa
# si una futura exportación cambia sus encabezados.
COLUMN_MAPPING = {
    "ventas": {"ID único": "sale_id", "Estatus": "status", "Tipo de Venta": "order_type",
               "Artículos": "item_count", " Total ": "total_amount", "Cierre de Cuenta": "closed_at"},
    "articulos": {"ID Venta Único": "sale_id", "ID Artículo": "product_id",
                  "Descripción Artículo": "product_name", "Categoría": "category",
                  "Cantidad Artículo": "quantity", " Importe Artículo ": "line_amount",
                  "Estatus": "status", "Tipo de Venta": "order_type", "Cierre de Venta": "closed_at"},
    "productos": {"ID Alfanumérico": "product_id", "Nombre": "product_name", "Categoría": "category",
                   "Cantidad": "quantity", " Importe ": "line_amount"},
    "domicilio": {"Concepto": "concept", "Importe o porcentaje": "value"},
}
FILE_TYPES = {"ventas": "Ventas", "articulos": "Ventas_Articulos", "productos": "Ventas_Productos", "domicilio": "Ventas_a_Domicilio"}
CHANNEL_ALIASES = {
    "Uber": ["uber", "uber eats"], "Rappi": ["rappi"],
    "Envío Propio": ["envio", "envío", "domicilio", "pedido a domicilio", "servicio entrega"],
    "Ordena y Recoge": ["recoge", "recoger", "ordena"], "Para Llevar": ["llevar", "takeaway"],
}
DELIVERY_CHANNEL_ALIASES = {
    "Uber": ["uber"], "Rappi": ["rappi"], "Envío Propio": ["envio propio", "envío propio"],
    "Ordena y Recoge": ["ordene y recoja", "ordena y recoja", "orden y recoja"],
}
VALID_CHANNELS = ["Uber", "Rappi", "Envío Propio", "Ordena y Recoge"]
