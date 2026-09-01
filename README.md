# Estacionalidad y composición del delito en la Región de Valparaíso

Proyecto del curso **EIN092B Visualización** (USM, 2026-2). Producto de datos incremental que transforma las estadísticas de Casos Policiales del CEAD en una narrativa visual sobre qué tipos de delito predominan en la Región de Valparaíso y cómo varían mes a mes y año a año.

## Integrantes
- Juan Domenech
- (por definir)

## Problema
La seguridad pública se gestiona mejor cuando se entiende la **composición** del delito (qué tipos pesan más) y su **estacionalidad** (cuándo aumentan). Estas dos dimensiones no siempre son visibles en las cifras crudas del CEAD, que se publican como tablas extensas y poco legibles.

## Motivación
Visibilizar patrones estacionales y de composición permite focalizar prevención y patrullaje en los meses y tipos de delito de mayor carga. Es información directamente útil para decisiones municipales de seguridad.

## Pregunta inicial
¿Qué familias y tipos de delito predominan en la Región de Valparaíso y cómo evoluciona su frecuencia mes a mes y año a año durante el período 2019-2025?

## Alcance
- **Región / contexto**: Región de Valparaíso (nivel regional agregado, no comunal).
- **Unidad de observación**: registro mensual por tipo de delito (año x mes x tipo de delito).
- **Periodo**: 2019-2025.
- **Medida**: Casos Policiales (frecuencia). No incluye la cifra negra (delitos no denunciados).
- **Fuera de alcance**: desglose por comuna y análisis causal.

## Estructura X, Y, T
- **X (variables disponibles)**: familia de delito, tipo de delito, mes, año.
- **Y (objetivo)**: casos policiales; indicadores derivados como participación porcentual por familia, variación interanual e índice estacional.
- **T (contexto temporal)**: 2019-2025, granularidad mensual.

## Fuente del dataset
Centro de Estudios y Análisis del Delito (CEAD), Subsecretaría de Prevención del Delito. Portal: https://data.cead.spd.gob.cl
Reporte: Casos Policiales, Región de Valparaíso, temporalidad mensual.

## Descripción de los datos
Cada fila corresponde a la cantidad de casos policiales registrados para un tipo de delito en un mes y año dados, en la Región de Valparaíso. Variables principales: año, mes, familia de delito, tipo de delito, casos. El archivo crudo del CEAD incluye un bloque de metadatos en la parte superior que debe descartarse durante la limpieza (ver `src/data_prep.py`).

## Estructura del repositorio
```
proyecto-viz-delitos/
├── data/
│   ├── raw/          datos originales del CEAD (no versionados si son pesados)
│   └── processed/    dataset limpio en formato largo (año, mes, tipo, casos)
├── notebooks/
│   └── 01_exploracion.ipynb
├── src/
│   └── data_prep.py  limpieza y transformación del export CEAD
├── figures/          gráficos exportados
├── app/              aplicación Streamlit (avances posteriores)
├── requirements.txt
├── README.md
└── .gitignore
```

## Cómo reproducir
1. `pip install -r requirements.txt`
2. Colocar el export del CEAD en `data/raw/`.
3. Ejecutar `python src/data_prep.py` para generar el dataset limpio en `data/processed/`.
4. Abrir `notebooks/01_exploracion.ipynb`.

## Estado
Avance 1: formulación del problema, pregunta, datos y repositorio.
