"""
Limpieza y transformacion del export CEAD (Casos Policiales, Region de Valparaiso).

El export del CEAD trae un bloque de metadatos arriba y luego un bloque
"DELITOS O FALTAS" con el total por familia de delito. Este script recorre las
hojas (una por anio) y arma un dataset en formato largo:

    anio | familia | casos

NOTA: el archivo actual es ANUAL. Cuando descargues el export MENSUAL desde el
CEAD (temporalidad por Mes), agrega aca el parseo de la columna de mes para
obtener anio | mes | familia | casos. Ver la funcion parse_mensual() (TODO).
"""

from pathlib import Path
import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"
ARCHIVO = RAW / "estadisticas_delitos_valparaiso.xlsx"

MARCADOR_FAMILIAS = "DELITOS O FALTAS"


def parse_anual(archivo: Path) -> pd.DataFrame:
    """Extrae el total por familia de delito de cada hoja (una por anio)."""
    xl = pd.ExcelFile(archivo)
    filas = []
    for hoja in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=hoja, header=None)
        # anio: intentar sacarlo del nombre de la hoja ("Año 2025")
        anio = "".join(c for c in str(hoja) if c.isdigit())
        anio = int(anio) if anio else None
        # ubicar el marcador del bloque de familias
        idx = df.index[df[0] == MARCADOR_FAMILIAS]
        if len(idx) == 0:
            continue
        inicio = idx[0] + 1
        for i in range(inicio, len(df)):
            familia = df.iloc[i, 0]
            valor = df.iloc[i, 1]
            if pd.isna(familia):
                break  # fin del bloque
            if pd.isna(valor):
                continue
            filas.append({"anio": anio, "familia": str(familia).strip(),
                          "casos": int(valor)})
    return pd.DataFrame(filas)


def parse_mensual(archivo: Path) -> pd.DataFrame:
    """TODO: parsear el export mensual del CEAD (anio | mes | tipo | casos).

    Cuando tengas el archivo mensual, inspecciona su estructura y completa aca.
    El objetivo es devolver columnas: anio, mes, familia (o tipo), casos.
    """
    raise NotImplementedError("Pendiente: descargar export mensual del CEAD.")


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df = parse_anual(ARCHIVO)
    salida = PROCESSED / "delitos_valparaiso_anual.csv"
    df.to_csv(salida, index=False)
    print(f"Guardado: {salida}  ({len(df)} filas)")
    print(df.pivot_table(index="familia", columns="anio", values="casos").to_string())


if __name__ == "__main__":
    main()
