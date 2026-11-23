"""
Funciones de visualización reutilizables (notebook + app Streamlit).

Todas las funciones devuelven figuras de Plotly (interactivas) y usan una
paleta consistente por familia de delito. La carga de datos vive aquí también
para que la app y el notebook lean lo mismo.
"""

from pathlib import Path
import pandas as pd
import plotly.express as px

TEAL, CLAY, SLATE, GREEN = "#2C6E75", "#B25B3E", "#35617D", "#5C8A6A"
GREY = "#B8BEC6"  # gris para contexto (uso del gris, Clase 02)
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# Color consistente por familia (nombre corto)
FAMILIA_COLORS = {
    "Otros delitos o faltas": "#C99A2E",
    "Propiedad no violentos": TEAL,
    "Incivilidades": SLATE,
    "Vida e integridad": GREEN,
    "Violencia intrafamiliar": "#8A6DAE",
    "Robos violentos": CLAY,
    "Drogas": "#4C7A8C",
    "Armas": "#A85751",
}


def short(s):
    return (str(s).replace("Delitos contra la ", "").replace("Delitos ", "")
            .replace("vida o integridad de las personas", "Vida e integridad")
            .replace("propiedad no violentos", "Propiedad no violentos")
            .replace("asociados a ", "").capitalize())


def load_data(csv_path):
    """Lee el CSV mensual tidy y agrega columna fecha y nombre corto de familia."""
    df = pd.read_csv(csv_path)
    df["fecha"] = pd.to_datetime(dict(year=df.anio, month=df.mes, day=1))
    df["Familia"] = df["familia"].map(short)
    return df


def familias(df):
    return df[df["nivel"] == "familia"].copy()


def subtipos(df):
    return df[df["nivel"] == "subtipo"].copy()


def _layout(fig, x, y):
    fig.update_layout(xaxis_title=x, yaxis_title=y, legend_title="Familia",
                      margin=dict(l=10, r=10, t=60, b=10))
    return fig


def fig_composicion(fam, anios):
    """Casos por familia sumando los años indicados (un año o una lista)."""
    anios = [anios] if isinstance(anios, int) else list(anios)
    periodo = str(anios[0]) if len(anios) == 1 else f"{anios[0]}-{anios[-1]}"
    d = (fam[fam.anio.isin(anios)].groupby("Familia", as_index=False)["casos"].sum()
         .sort_values("casos"))
    fig = px.bar(d, x="casos", y="Familia", orientation="h",
                 color="Familia", color_discrete_map=FAMILIA_COLORS,
                 title=f"Composición del delito por familia ({periodo})")
    fig.update_layout(showlegend=False)
    return _layout(fig, "Casos policiales", "")


def fig_serie_mensual(fam, familias_sel=None):
    d = fam if not familias_sel else fam[fam.Familia.isin(familias_sel)]
    fig = px.line(d.sort_values("fecha"), x="fecha", y="casos", color="Familia",
                  color_discrete_map=FAMILIA_COLORS,
                  title="Casos mensuales por familia")
    return _layout(fig, "Mes", "Casos")


def fig_heatmap(fam, anios=None):
    """Heatmap de estacionalidad: cada familia normalizada a su propio promedio.

    Índice 100 = mes promedio de esa familia. Paleta divergente (Clase 02) para
    que la estacionalidad se lea igual de bien en familias grandes y chicas.
    """
    d = fam[fam.anio.isin(anios)] if anios else fam
    piv = d.pivot_table(index="Familia", columns="mes", values="casos", aggfunc="mean")
    piv = piv.div(piv.mean(axis=1), axis=0) * 100  # índice estacional por familia
    # ordenar por volumen total (mayor arriba) para mantener jerarquía visual
    orden = d.groupby("Familia")["casos"].sum().sort_values().index.tolist()
    piv = piv.reindex(orden)
    piv.columns = [MESES[m - 1] for m in piv.columns]
    fig = px.imshow(piv, aspect="auto", text_auto=".0f",
                    color_continuous_scale=[[0, TEAL], [0.5, "#F0EEE9"], [1, CLAY]],
                    color_continuous_midpoint=100,
                    labels=dict(color="Índice (100=prom.)"),
                    title="Estacionalidad por familia (índice 100 = promedio de la familia)")
    fig.update_xaxes(side="bottom")
    return _layout(fig, "Mes", "")


def fig_totales_anuales(fam):
    """Total de casos por año. Gris para contexto, acento en la caída de pandemia
    (uso del gris + color estratégico, Clase 02)."""
    d = fam[fam.anio <= 2025].groupby("anio", as_index=False)["casos"].sum()
    d["Periodo"] = d.anio.map(lambda a: "Pandemia (2020-2021)" if a in (2020, 2021) else "Resto")
    fig = px.bar(d, x="anio", y="casos", color="Periodo",
                 color_discrete_map={"Pandemia (2020-2021)": CLAY, "Resto": GREY},
                 title="Los casos cayeron en 2020-2021 y recién en 2025 volvieron al nivel de 2019")
    fig.update_layout(showlegend=False)
    return _layout(fig, "Año", "Casos policiales")


def fig_boxplot(fam):
    orden = fam.groupby("Familia")["casos"].median().sort_values().index.tolist()
    fig = px.box(fam, x="casos", y="Familia", color="Familia",
                 color_discrete_map=FAMILIA_COLORS, category_orders={"Familia": orden},
                 title="Dispersión de casos mensuales por familia")
    fig.update_layout(showlegend=False)
    return _layout(fig, "Casos", "")


def fig_tendencia(fam):
    d = (fam[fam.anio <= 2025].groupby(["anio", "Familia"], as_index=False)["casos"].sum())
    fig = px.line(d, x="anio", y="casos", color="Familia", markers=True,
                  color_discrete_map=FAMILIA_COLORS,
                  title="Tendencia interanual por familia (2019-2025)")
    return _layout(fig, "Año", "Casos")


def fig_indice_estacional(fam, familia_corta):
    b = fam[(fam.Familia == familia_corta) & (fam.anio <= 2025)]
    prom = b.groupby("mes")["casos"].mean()
    idx = (100 * prom / prom.mean()).reset_index(name="indice")
    idx["Mes"] = idx.mes.map(lambda m: MESES[m - 1])
    idx["Nivel"] = idx.indice.map(lambda v: "Sobre promedio" if v >= 100 else "Bajo promedio")
    fig = px.bar(idx, x="Mes", y="indice", color="Nivel",
                 color_discrete_map={"Sobre promedio": CLAY, "Bajo promedio": TEAL},
                 category_orders={"Mes": MESES},
                 title=f"Índice estacional - {familia_corta} (100 = mes promedio)")
    fig.add_hline(y=100, line_dash="dash", line_color="gray")
    fig.update_layout(showlegend=False)
    return _layout(fig, "", "Índice")


def _es_outlier_iqr(s):
    q1, q3 = s.quantile([0.25, 0.75])
    rango = q3 - q1
    return (s < q1 - 1.5 * rango) | (s > q3 + 1.5 * rango)


def tabla_univariada(fam):
    """Tendencia central, dispersión, asimetría y outliers (regla IQR) de los
    casos mensuales de cada familia."""
    g = fam.groupby("Familia")["casos"]
    t = pd.DataFrame({
        "Media": g.mean(),
        "Mediana": g.median(),
        "Desv. estándar": g.std(),
        "Asimetría": g.skew(),
        "Meses atípicos (IQR)": g.apply(lambda s: int(_es_outlier_iqr(s).sum())),
    })
    return t.sort_values("Media", ascending=False)


def outliers_por_anio(fam):
    """Cantidad de meses atípicos (regla IQR, por familia) en cada año."""
    marca = fam.groupby("Familia")["casos"].transform(_es_outlier_iqr)
    return fam[marca].groupby("anio").size()


def fig_subtipos(sub, familia_corta, anio):
    d = (sub[(sub.Familia == familia_corta) & (sub.anio == anio)]
         .groupby("delito", as_index=False)["casos"].sum().sort_values("casos"))
    fig = px.bar(d, x="casos", y="delito", orientation="h",
                 color_discrete_sequence=[FAMILIA_COLORS.get(familia_corta, TEAL)],
                 title=f"Subtipos de {familia_corta} ({anio})")
    return _layout(fig, "Casos policiales", "")


def fig_correlacion(fam):
    """Correlación (Pearson) entre las series mensuales de las familias, 2019-2025."""
    w = fam[fam.anio <= 2025].pivot_table(index="fecha", columns="Familia", values="casos")
    orden = fam.groupby("Familia")["casos"].sum().sort_values(ascending=False).index.tolist()
    c = w.corr().reindex(index=orden, columns=orden)
    fig = px.imshow(c, text_auto=".2f", zmin=-1, zmax=1,
                    color_continuous_scale=[[0, TEAL], [0.5, "#F0EEE9"], [1, CLAY]],
                    aspect="auto", labels=dict(color="Correlación"),
                    title="Correlación mensual entre familias (2019-2025)")
    fig.update_xaxes(side="bottom", tickangle=-30)
    fig.update_layout(height=560)
    return _layout(fig, "", "")


def fig_variacion(fam, familia_corta):
    d = (fam[(fam.Familia == familia_corta) & (fam.anio <= 2025)]
         .groupby("anio", as_index=False)["casos"].sum())
    d["var_pct"] = d["casos"].pct_change() * 100
    d = d.dropna()
    d["Signo"] = d.var_pct.map(lambda v: "Sube" if v >= 0 else "Baja")
    fig = px.bar(d, x="anio", y="var_pct", color="Signo",
                 color_discrete_map={"Sube": CLAY, "Baja": TEAL},
                 title=f"Variación interanual - {familia_corta}")
    fig.add_hline(y=0, line_color="gray")
    fig.update_layout(showlegend=False)
    return _layout(fig, "Año", "Variación %")
