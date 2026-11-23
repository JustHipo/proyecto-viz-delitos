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


st.set_page_config(page_title="Delitos en Valparaíso", layout="wide")
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

st.subheader("Evolución mensual")
st.plotly_chart(viz.fig_serie_mensual(fam, sel_serie or opciones), use_container_width=True)
st.markdown(
    "La serie mensual muestra la tendencia y la estacionalidad juntas. Casi todas las "
    "familias caen en 2020 y 2021, durante la pandemia, y después se recuperan."
)

st.subheader("Tendencia interanual")
st.plotly_chart(viz.fig_tendencia(fam), use_container_width=True)
st.markdown(
    "*Otros delitos o faltas* sube de 61.058 casos en 2023 a 92.360 en 2025. Las "
    "incivilidades bajan de 60.847 en 2019 a 30.473 en 2023."
)

st.subheader(f"Estacionalidad: {familia_sel}")
a, b = st.columns(2)
a.plotly_chart(viz.fig_indice_estacional(fam, familia_sel), use_container_width=True)
b.plotly_chart(viz.fig_variacion(fam, familia_sel), use_container_width=True)
st.markdown(
    f"El índice muestra en qué meses {familia_sel} queda sobre o bajo su promedio. En "
    "propiedad no violentos, enero está un 14% sobre el promedio y junio un 8% bajo él. "
    "Junio queda bajo el promedio los 7 años; enero queda sobre él en 5 de 7 (2021 y 2022 "
    "son la excepción)."
)

st.subheader(f"Tipos de delito dentro de {familia_sel}")
sub = viz.subtipos(df)
if sub[sub.Familia == familia_sel].empty:
    st.markdown(f"El CEAD no desglosa {familia_sel} en subtipos.")
else:
    st.plotly_chart(viz.fig_subtipos(sub, familia_sel, 2025), use_container_width=True)
    st.markdown(
        "Entre todas las familias, los tipos más frecuentes en 2025 son amenazas (17.602), "
        "hurtos (13.999) y daños (13.230). *Otros delitos o faltas*, la familia más grande, "
        "no trae subtipos en el CEAD."
    )

st.subheader("Relación entre familias")
st.plotly_chart(viz.fig_correlacion(fam), use_container_width=True)
st.markdown(
    "Robos violentos y propiedad no violentos suben y bajan juntos mes a mes (r = 0,92). "
    "Vida e integridad se mueve con ambas y con violencia intrafamiliar (r cercano a 0,6), "
    "y *otros delitos o faltas* casi no se mueve con ninguna. Parte de estas correlaciones "
    "viene de la caída común de 2020-2021."
)

st.divider()
st.subheader("Hallazgos preliminares")
st.markdown(
    "1. La mayor parte de los casos son faltas, delitos contra la propiedad e incivilidades. "
    "Los delitos violentos pesan mucho menos.\n"
    "2. Casi todas las familias caen en 2020 y 2021, durante la pandemia.\n"
    "3. Las incivilidades bajan a la mitad entre 2019 y 2023; *otros delitos o faltas* es lo "
    "que más crece.\n"
    "4. Los delitos contra la propiedad suben en verano y bajan a mitad de año.\n"
    "5. Robos violentos y propiedad no violentos se mueven juntos mes a mes (r = 0,92).\n\n"
    "**Cómo refina la pregunta:** el foco más prometedor es cruzar composición y estacionalidad "
    "por familia, y explicar la caída/recuperación 2020-2025."
)
