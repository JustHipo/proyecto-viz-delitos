"""
Limpieza y transformacion del export CEAD (Casos Policiales, Region de Valparaiso).

El CEAD entrega el reporte como un HTML disfrazado de .xls. El reporte "por
trimestre" en realidad baja hasta el nivel MES: sus columnas son un MultiIndex
(anio, TRIM x, mes 1-12). Eso nos da granularidad mensual 2019-2026.

Las filas mezclan FAMILIAS de delito (8 categorias grandes) con sus SUBTIPOS.
El valor de cada familia es la suma de sus subtipos.

Salidas (formato largo / tidy):
  - delitos_valparaiso_mensual.csv : anio | mes | familia | delito | nivel | casos
  - delitos_valparaiso_anual.csv   : anio | familia | delito | nivel | casos
    (agregado desde el mensual, para vistas de composicion)

Numeros en formato chileno (miles con punto, decimales con coma).
"""

from pathlib import Path
import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"
ARCHIVO_MENSUAL = RAW / "reportes_mensual.xls"

FAMILIAS = {
    "Delitos contra la vida o integridad de las personas",
    "Robos violentos",
    "Violencia intrafamiliar",
    "Delitos asociados a drogas",
    "Delitos asociados a armas",
    "Delitos contra la propiedad no violentos",
    "Incivilidades",
    "Otros delitos o faltas",
}


def parse_mensual(archivo: Path) -> pd.DataFrame:
    """Devuelve tidy: anio | mes | familia | delito | nivel | casos."""
    t = pd.read_html(archivo, thousands=".", decimal=",", header=[0, 1, 2])[1]
    cols = list(t.columns)
    delito_col = cols[0]  # ('Unnamed..','Unnamed..','DELITOS O FALTAS')

    # columnas de datos: nivel 0 es un anio de 4 digitos
    data_cols = [c for c in cols[1:] if str(c[0]).strip().isdigit()]

    filas = []
    familia_actual = None
    for _, row in t.iterrows():
        nombre = str(row[delito_col]).strip()
        if nombre in FAMILIAS:
            familia_actual = nombre
            nivel = "familia"
        else:
            nivel = "subtipo"
        for c in data_cols:
            anio = int(c[0])
            mes = int(c[2])
            val = row[c]
            if pd.isna(val):
                continue
            filas.append({
                "anio": anio, "mes": mes,
                "familia": familia_actual, "delito": nombre,
                "nivel": nivel, "casos": int(round(float(val))),
            })
    df = pd.DataFrame(filas)

    # descartar meses sin datos (ej. meses futuros de 2026 vienen en 0)
    tot = df.groupby(["anio", "mes"])["casos"].transform("sum")
    df = df[tot > 0].reset_index(drop=True)
    return df


def to_anual(mensual: pd.DataFrame) -> pd.DataFrame:
    """Agrega el mensual a totales anuales."""
    return (mensual.groupby(["anio", "familia", "delito", "nivel"], as_index=False)
            ["casos"].sum())


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    mensual = parse_mensual(ARCHIVO_MENSUAL)
    anual = to_anual(mensual)

    mensual.to_csv(PROCESSED / "delitos_valparaiso_mensual.csv", index=False)
    anual.to_csv(PROCESSED / "delitos_valparaiso_anual.csv", index=False)
    print(f"Mensual: {len(mensual)} filas -> delitos_valparaiso_mensual.csv")
    print(f"Anual:   {len(anual)} filas -> delitos_valparaiso_anual.csv")

    fam = mensual[mensual["nivel"] == "familia"]
    print("\nMeses con datos por anio:")
    print(fam.groupby("anio")["mes"].nunique().to_string())


if __name__ == "__main__":
    main()
