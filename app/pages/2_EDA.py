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


st.set_page_config(page_title="Delitos en Valparaíso", layout="wide")
df = load()
fam = viz.familias(df)

st.title("Análisis Exploratorio")

opciones = fam.groupby("Familia")["casos"].sum().sort_values(ascending=False).index.tolist()
c1, c2 = st.columns([1, 1])
rango = c1.slider("Rango de años", 2019, 2026, (2019, 2025))
sel = c2.multiselect("Familias a mostrar", opciones, default=opciones)

f = fam[(fam.anio.between(rango[0], rango[1])) & (fam.Familia.isin(sel))]
if f.empty:
    st.warning("Selecciona al menos una familia y un rango con datos.")
    st.stop()

anios = list(range(rango[0], rango[1] + 1))
# 2026 es parcial: la composición usa los años completos del rango, salvo que solo haya 2026
anios_comp = [a for a in anios if a <= 2025] or [2026]
periodo = (str(anios_comp[0]) if len(anios_comp) == 1
           else f"entre {anios_comp[0]} y {anios_comp[-1]}")

st.subheader("Composición del delito")
st.plotly_chart(viz.fig_composicion(f, anios_comp), use_container_width=True)
st.markdown(
    f"En {periodo} la carga se concentra en pocas familias: *Otros delitos o faltas*, "
    "*Propiedad no violentos* e *Incivilidades*. Las familias violentas pesan mucho menos "
    "en volumen. La distribución es muy asimétrica."
)

st.subheader("Estacionalidad por familia")
st.plotly_chart(viz.fig_heatmap(f, anios), use_container_width=True)
st.markdown(
    "Cada fila está normalizada al promedio de su familia (100 es un mes típico), así que "
    "familias grandes y chicas se comparan en la misma escala. En terracota están los meses "
    "sobre el promedio y en teal los meses bajo él. Propiedad e incivilidades suben en enero, "
    "mientras *otros delitos o faltas* casi no cambia en el año. Drogas y armas son las que "
    "más varían, pero tienen pocos casos al mes."
)

st.subheader("Dispersión por familia")
st.plotly_chart(viz.fig_boxplot(f), use_container_width=True)

st.markdown("**Estadísticas de los casos mensuales por familia**")
st.dataframe(
    viz.tabla_univariada(f).style.format(
        {"Media": "{:,.0f}", "Mediana": "{:,.0f}", "Desv. estándar": "{:,.0f}",
         "Asimetría": "{:.2f}"}, thousands=".", decimal=","),
    use_container_width=True,
)
por_anio = viz.outliers_por_anio(f)
detalle = ", ".join(f"{a}: {n}" for a, n in por_anio.items())
st.markdown(
    "Incivilidades y armas tienen asimetría positiva: algunos meses quedan muy por sobre lo "
    "normal. Propiedad, vida e integridad y robos violentos la tienen negativa. "
    f"Meses atípicos por año según la regla IQR: {detalle or 'ninguno'}. Casi todos son de "
    "2020 y 2021, por la pandemia, o de 2019 en incivilidades, antes de su caída."
)
