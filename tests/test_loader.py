from pathlib import Path
from src.data.loader import classify_file
def test_classify_files():
    assert classify_file(Path("Ventas_Articulos.csv"))=="articulos"
    assert classify_file(Path("Ventas.csv"))=="ventas"
