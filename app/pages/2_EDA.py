"""Página 2 - Análisis Exploratorio."""
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


st.set_page_config(page_title="EDA · Delitos Valparaíso", page_icon="🔎", layout="wide")
df = load()
fam = viz.familias(df)

st.title("Análisis Exploratorio")
st.caption("¿Cómo se comportan nuestros datos?")

# --- Controles interactivos ---
opciones = fam.groupby("Familia")["casos"].sum().sort_values(ascending=False).index.tolist()
c1, c2 = st.columns([1, 1])
rango = c1.slider("Rango de años", 2019, 2026, (2019, 2025))
sel = c2.multiselect("Familias a mostrar", opciones, default=opciones)

f = fam[(fam.anio.between(rango[0], rango[1])) & (fam.Familia.isin(sel))]
if f.empty:
    st.warning("Selecciona al menos una familia y un rango con datos.")
    st.stop()

anios = list(range(rango[0], rango[1] + 1))
anio_comp = min(rango[1], 2025)  # ultimo año completo dentro del rango

st.subheader("Composición del delito")
st.plotly_chart(viz.fig_composicion(f, anio_comp), use_container_width=True)
st.markdown(
    f"En {anio_comp} la carga se concentra en pocas familias: *Otros delitos o faltas*, "
    "*Propiedad no violentos* e *Incivilidades*. Las familias violentas pesan mucho menos "
    "en volumen. La distribución es muy asimétrica."
)

st.subheader("Estacionalidad por familia")
st.plotly_chart(viz.fig_heatmap(f, anios), use_container_width=True)
st.markdown(
    "Cada fila está normalizada al promedio de esa familia (**100 = mes típico**), con paleta "
    "divergente: **terracota = meses sobre su promedio**, **teal = bajo su promedio**. Así la "
    "estacionalidad se compara entre familias grandes y chicas. Se ve el alza de verano (enero) "
    "en propiedad e incivilidades, y familias casi planas como drogas. La magnitud absoluta va "
    "en el gráfico de composición."
)

st.subheader("Dispersión por familia")
st.plotly_chart(viz.fig_boxplot(f), use_container_width=True)
st.markdown(
    "El boxplot confirma la asimetría. Los valores extremos coinciden en su mayoría con "
    "**2020-2021** (caída por pandemia), no con errores de datos."
)
