"""
Modelado del Avance 3: prediccion de casos mensuales por familia de delito.

Tarea de regresion. Para que las 8 familias sean comparables (Otros delitos
tiene ~6.000 casos al mes y Armas ~150), el modelo predice un indice relativo:

    indice = casos del mes / promedio de los 12 meses anteriores de esa familia

1.0 = mes tipico del ultimo año. La prediccion en casos se recupera
multiplicando por ese promedio, y las metricas (MAE, RMSE, R2) se calculan en
casos. Todas las entradas usan solo meses anteriores, para evitar fuga.

Particion temporal: entrenamiento 2020-01 a 2024-12, prueba 2025-01 a 2026-06.
2019 se usa solo para construir los rezagos y el promedio de 12 meses.
"""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

FIN_TRAIN = pd.Timestamp("2024-12-01")
PANDEMIA = (pd.Timestamp("2020-03-01"), pd.Timestamp("2021-12-01"))

NUMERICAS = ["rel_mes_anterior", "rel_mismo_mes_anio_ant", "tendencia",
             "mes_sin", "mes_cos", "pandemia"]
CATEGORICAS = ["Familia"]
FEATURES = CATEGORICAS + NUMERICAS
OBJETIVO = "indice"

# nombres para los graficos SHAP (mes y familia se agrupan en una sola variable)
ETIQUETAS = {
    "rel_mes_anterior": "Mes anterior (relativo)",
    "rel_mismo_mes_anio_ant": "Mismo mes año anterior (relativo)",
    "mes": "Mes del año",
    "Familia": "Familia",
    "tendencia": "Tendencia (meses desde 2019)",
    "pandemia": "Pandemia (2020-03 a 2021-12)",
}


def construir_features(fam):
    """fam: filas a nivel familia con columnas Familia, fecha, mes, casos."""
    d = fam.sort_values(["Familia", "fecha"]).copy()
    g = d.groupby("Familia")["casos"]
    d["base_12m"] = g.transform(lambda s: s.shift(1).rolling(12).mean())
    d["casos_mes_anterior"] = g.shift(1)
    d["casos_mismo_mes_anio_ant"] = g.shift(12)
    d["rel_mes_anterior"] = d["casos_mes_anterior"] / d["base_12m"]
    d["rel_mismo_mes_anio_ant"] = d["casos_mismo_mes_anio_ant"] / d["base_12m"]
    d["tendencia"] = (d["fecha"].dt.year - 2019) * 12 + d["fecha"].dt.month - 1
    d["mes_sin"] = np.sin(2 * np.pi * d["mes"] / 12)
    d["mes_cos"] = np.cos(2 * np.pi * d["mes"] / 12)
    d["pandemia"] = d["fecha"].between(*PANDEMIA).astype(int)
    d[OBJETIVO] = d["casos"] / d["base_12m"]
    # se pierde 2019: no tiene 12 meses anteriores
    return d.dropna(subset=["base_12m", "casos_mismo_mes_anio_ant"]).reset_index(drop=True)


def particion(d):
    train = d[d["fecha"] <= FIN_TRAIN].sort_values(["fecha", "Familia"]).reset_index(drop=True)
    test = d[d["fecha"] > FIN_TRAIN].sort_values(["fecha", "Familia"]).reset_index(drop=True)
    return train, test


def folds_temporales(train, n_splits=5):
    """Validacion cruzada temporal por meses completos (las 8 familias de un mes van juntas)."""
    meses = np.sort(train["fecha"].unique())
    tam = len(meses) // (n_splits + 1)
    folds = []
    for k in range(1, n_splits + 1):
        fin = meses[tam * k - 1]
        val = meses[tam * k: tam * (k + 1)]
        idx_tr = np.where(train["fecha"] <= fin)[0]
        idx_va = np.where(train["fecha"].isin(val))[0]
        folds.append((idx_tr, idx_va))
    return folds


def preprocesador():
    return ColumnTransformer([
        ("fam", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAS),
        ("num", StandardScaler(), NUMERICAS),
    ])


def modelo_ridge():
    return Pipeline([("prep", preprocesador()), ("modelo", Ridge())])


def modelo_rf(seed=42):
    return Pipeline([("prep", preprocesador()),
                     ("modelo", RandomForestRegressor(n_estimators=400, random_state=seed, n_jobs=-1))])


def a_casos(pipe, datos):
    """Prediccion en casos: indice predicho x promedio de los 12 meses anteriores."""
    return pipe.predict(datos[FEATURES]) * datos["base_12m"].values


def metricas(y, yhat):
    return {"MAE": mean_absolute_error(y, yhat),
            "RMSE": np.sqrt(mean_squared_error(y, yhat)),
            "R2": r2_score(y, yhat)}


def agrupar_shap(sv, pipe, datos):
    """Suma las columnas one-hot de familia y el seno/coseno del mes en una sola variable cada una.

    Devuelve (valores SHAP agrupados, valores originales para colorear, texto para mostrar, nombres).
    """
    cols = list(pipe.named_steps["prep"].get_feature_names_out())
    v = pd.DataFrame(sv.values, columns=cols)
    grupos = {
        "rel_mes_anterior": ["num__rel_mes_anterior"],
        "rel_mismo_mes_anio_ant": ["num__rel_mismo_mes_anio_ant"],
        "mes": ["num__mes_sin", "num__mes_cos"],
        "Familia": [c for c in cols if c.startswith("fam__")],
        "tendencia": ["num__tendencia"],
        "pandemia": ["num__pandemia"],
    }
    valores = np.column_stack([v[c].sum(axis=1) for c in grupos.values()])
    datos = datos.reset_index(drop=True)
    color = np.column_stack([
        datos["rel_mes_anterior"], datos["rel_mismo_mes_anio_ant"], datos["mes"],
        np.full(len(datos), np.nan), datos["tendencia"], datos["pandemia"]])
    texto = np.column_stack([
        datos["rel_mes_anterior"].round(2).astype(str), datos["rel_mismo_mes_anio_ant"].round(2).astype(str),
        datos["mes"].astype(str), datos["Familia"], datos["tendencia"].astype(str), datos["pandemia"].astype(str)])
    nombres = [ETIQUETAS[k] for k in grupos]
    return valores, color, texto, nombres
