"""Página 3 - Análisis de la Pregunta."""
import sys
from pathlib import Path

_p = Path(__file__).resolve()
while not (_p / "data" / "processed").exists() and _p != _p.parent:
    _p = _p.parent
ROOT = _p
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st
import viz

DATA = ROOT / "data" / "processed" / "delitos_valparaiso_mensual.csv"


@st.cache_data
def load():
    return viz.load_data(DATA)


st.set_page_config(page_title="Análisis · Delitos Valparaíso", page_icon="🎯", layout="wide")
df = load()
fam = viz.familias(df)

st.title("Análisis de la Pregunta")

opciones = fam.groupby("Familia")["casos"].sum().sort_values(ascending=False).index.tolist()
c1, c2 = st.columns([1, 1])
familia_sel = c1.selectbox("Familia a analizar en detalle", opciones,
                           index=opciones.index("Propiedad no violentos")
                           if "Propiedad no violentos" in opciones else 0)
sel_serie = c2.multiselect("Familias en la serie temporal", opciones,
                           default=opciones[:4])

st.subheader("Evolución mensual (tendencia + estacionalidad)")
st.plotly_chart(viz.fig_serie_mensual(fam, sel_serie or opciones), use_container_width=True)
st.markdown(
    "La serie mensual deja ver a la vez la **tendencia** y la **estacionalidad**. "
    "Destaca la caída general en **2020-2021** (pandemia) y la recuperación posterior."
)

st.subheader("Tendencia interanual")
st.plotly_chart(viz.fig_tendencia(fam), use_container_width=True)
st.markdown(
    "*Otros delitos o faltas* crece de forma sostenida hacia 2024-2025, mientras que "
    "las **incivilidades caen fuerte** (de ~60.847 en 2019 a ~30.473 en 2023)."
)

st.subheader(f"Estacionalidad: {familia_sel}")
a, b = st.columns(2)
a.plotly_chart(viz.fig_indice_estacional(fam, familia_sel), use_container_width=True)
b.plotly_chart(viz.fig_variacion(fam, familia_sel), use_container_width=True)
st.markdown(
    f"El índice estacional de **{familia_sel}** muestra en qué meses supera o baja del "
    "promedio anual. Para *Propiedad no violentos*, enero (verano) está ~+14% sobre el "
    "promedio y junio ~-8%: un patrón consistente año a año."
)

st.divider()
st.subheader("Hallazgos preliminares")
st.markdown(
    "1. La carga del delito está **dominada por faltas, propiedad e incivilidades**, no por "
    "delitos violentos.\n"
    "2. Hay una **caída pandémica clara (2020-2021)** común a casi todas las familias.\n"
    "3. Las **incivilidades bajan de forma sostenida** desde 2019; *otros delitos o faltas* es "
    "lo que más crece.\n"
    "4. Los **delitos contra la propiedad tienen estacionalidad de verano** (peak en enero).\n\n"
    "**Cómo refina la pregunta:** el foco más prometedor es cruzar composición y estacionalidad "
    "por familia, y explicar la caída/recuperación 2020-2025."
)
