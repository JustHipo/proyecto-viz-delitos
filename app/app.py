"""Página 1 - Contexto y Datos. Ejecutar con: streamlit run app/app.py"""
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


st.set_page_config(page_title="Delitos Valparaíso", page_icon="📊", layout="wide")
df = load()
fam = viz.familias(df)
sub = viz.subtipos(df)

st.title("Estacionalidad y composición del delito en la Región de Valparaíso")
st.caption("EIN092B Visualización · Avance 2 · Fuente: CEAD (Casos Policiales)")

st.markdown(
    "**Problema.** La seguridad pública se gestiona mejor cuando se entiende la "
    "*composición* del delito (qué tipos pesan más) y su *estacionalidad* (cuándo "
    "aumentan). En las cifras crudas del CEAD eso no es visible.\n\n"
    "**Pregunta.** ¿Qué familias y tipos de delito predominan en la Región de "
    "Valparaíso y cómo evoluciona su frecuencia mes a mes y año a año (2019-2025)?"
)

c1, c2, c3 = st.columns(3)
c1.markdown("**X · Variables**\n\nFamilia y tipo de delito, mes, año")
c2.markdown("**Y · Objetivo**\n\nCasos policiales")
c3.markdown("**T · Contexto temporal**\n\n2019-2026, mensual")

st.divider()
st.subheader("El dataset")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Registros (mensuales)", f"{len(df):,}".replace(",", "."))
m2.metric("Familias de delito", fam.Familia.nunique())
m3.metric("Subtipos", sub.delito.nunique())
m4.metric("Periodo", "2019-2026")

st.markdown(
    "**Resumen de calidad.** Sin faltantes ni duplicados tras la limpieza. "
    "2026 es parcial (hasta junio), por lo que se excluye de las comparaciones "
    "anuales. En 5 de las 8 familias el total coincide exacto con la suma de sus "
    "subtipos (no se mezclan niveles para evitar doble conteo). El dato es regional "
    "agregado: no hay desglose por comuna (límite del proyecto)."
)

st.subheader("Indicadores descriptivos")
st.plotly_chart(viz.fig_totales_anuales(fam), use_container_width=True)

st.info("Propósito de esta página: ¿qué estamos estudiando y con qué datos? "
        "Usa el menú lateral para ir a **Análisis Exploratorio** y **Análisis de la Pregunta**.")
