# Taller de Ciencia de Datos — Laboratorios (EIN146A25)

Repositorio del curso · Semestre 2026-2 · Paralelo 701 · Jueves 08:50–12:15, Lab. Central 114

Acá viven los notebooks y enunciados de los laboratorios. Clónenlo una vez y hagan `git pull` antes de cada clase.

```bash
git clone <url-del-repo> taller-cd
cd taller-cd
pip install -r requirements.txt   # seaborn, plotly y streamlit son opcionales
jupyter lab
```

## Laboratorios

| # | Fecha | Tema | Material |
|---|---|---|---|
| 2 | 13-ago | Búsqueda y recolección de datos | [enunciado](02/lab02-recoleccion-datos.md) · [notebook](02/lab02-recoleccion-datos.ipynb) · [guía](02/lab02-guia-recoleccion-datos.md) |
| 5 | 03-sep | Integración de fuentes y creación de características | [enunciado](05/lab05-integracion-features.md) · [notebook](05/lab05-integracion-features.ipynb) · [guía](05/lab05-guia-integracion-features.md) |
| 7 | 24-sep | Análisis exploratorio de datos (EDA) | [enunciado](07/lab07-eda.md) · [notebook](07/lab07-eda.ipynb) · [guía](07/lab07-guia-eda.md) |
| 8 | 01-oct | Visualización avanzada y dashboards | [enunciado](08/lab08-visualizacion-dashboards.md) · [notebook](08/lab08-visualizacion-dashboards.ipynb) · [guía](08/lab08-guia-visualizacion.md) · [app Streamlit (opcional)](08/lab08-app-streamlit.py) |
| 11 | 22-oct | Evaluación de modelos | [enunciado](11/lab11-evaluacion-modelos.md) · [notebook](11/lab11-evaluacion-modelos.ipynb) · [guía](11/lab11-guia-evaluacion.md) |

## Cómo trabajar

Cada laboratorio trae un enunciado (qué hay que lograr y en qué tiempos), un notebook con celdas **✏️ TU TURNO** y su verificación automática, y una guía de referencia técnica. En los Labs 02 a 08 las soluciones vienen plegadas en el notebook: ábranlas después de intentarlo. Desde el Lab 11 el notebook no trae las soluciones: se revisan en clase.

Trabajen sobre una copia del notebook para no chocar con el `git pull` de la clase siguiente:

```bash
cp lab02-recoleccion-datos.ipynb mi-lab02.ipynb
```

Los laboratorios no se entregan por separado — alimentan directamente los informes del proyecto, que se entregan vía AULA-USM.
