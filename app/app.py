"""Punto de entrada de la app. Ejecutar con: streamlit run app/app.py"""
import streamlit as st

pg = st.navigation([
    st.Page("pages/1_Contexto.py", title="Contexto y Datos", default=True),
    st.Page("pages/2_EDA.py", title="Análisis Exploratorio"),
    st.Page("pages/3_Analisis.py", title="Análisis de la Pregunta"),
])
pg.run()
