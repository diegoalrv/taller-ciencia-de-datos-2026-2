# Laboratorio 8 — Visualización avanzada y dashboards

**EIN146A25 · 2026-2 · Jueves 01-oct, 09:40–12:15 · Lab. Central 114**
Notebook: [`lab08-visualizacion-dashboards.ipynb`](lab08-visualizacion-dashboards.ipynb) · Referencia técnica: [`lab08-guia-visualizacion.md`](lab08-guia-visualizacion.md)

## Objetivo

Subir un nivel el EDA de la Clase 7 con cuatro preguntas: **cuánta certeza** hay detrás de una diferencia entre grupos (intervalos y embudo), cómo leer el **tiempo** (estacionalidad vs. tendencia), cómo comparar **muchos grupos y el territorio** (paneles y cartograma), y cómo armar una **vista interactiva** mínima para explorar. Esto es material para la sección de EDA del Informe 3.

## Antes de empezar

```bash
git pull            # en el repositorio del curso
pip install pandas numpy matplotlib jupyter
```

`seaborn` y `plotly` son **opcionales**. Los Ejercicios 1, 2 y 3 y la parte A del Ejercicio 4 funcionan solo con Matplotlib y pandas; solo la parte B del Ejercicio 4 necesita Plotly (`pip install plotly`). El Setup avisa qué tienen instalado.

**Datos sintéticos generados para el lab: ninguna cifra describe a una comuna, establecimiento o estudiante real.**

Abran el notebook y ejecuten las celdas de *Setup* y de generación de archivos. Los dos archivos de práctica (tasas de riesgo por comuna y asistencia mensual de 146 establecimientos de la provincia de Concepción, 2023–2025) **se generan solos** en `data_practica/`: no hay que descargar nada y el lab no usa internet.

## Mecánica

| Hora | Qué |
|---|---|
| 09:40 | `git pull`, Setup y generación de datos |
| 09:50 | **Ej. 1 — Incertidumbre: intervalos y embudo** (~20 min) |
| 10:10 | **Ej. 2 — Tiempo: estacionalidad y tendencia** (~20 min) |
| 10:30 | **Ej. 3 — Grupos y territorio: paneles y cartograma** (~20 min) |
| 10:50 | Recreo |
| 11:05 | **Ej. 4 — Dashboard mínimo** (~30 min; la parte B solo con Plotly) |
| 11:35 | **Proyecto:** ampliar `03-eda.ipynb` (3 filas nuevas de bitácora) + ronda de consulta docente |
| 12:05 | Checklist de salida |

## Ejercicios

El Ejercicio 1 usa `comunas_riesgo.csv`; los otros tres, `asistencia_mensual.csv`. Cada ejercicio lee sus datos por su cuenta: si uno no les sale, el siguiente no se traba.

**1 · Incertidumbre: intervalos y embudo.** En el ranking de tasas de riesgo, Florida sale primera y Santa Juana última, pero son las dos comunas con menos estudiantes (150 y 120). Con el intervalo de Wilson y un gráfico de embudo se ve que sus tasas no se distinguen de la global, y que las comunas que sí se distinguen son otras, con una diferencia menor pero con n grande.

**2 · Tiempo: estacionalidad y tendencia.** La serie mensual de asistencia trae 40 ceros que son establecimientos sin reporte, no escuelas vacías: hay que limpiarlos antes de leer nada. Después, una línea por año sobre los meses del calendario separa lo que se repite todos los años (la caída de invierno) de lo que cambia de un año a otro (una baja suave de fondo).

**3 · Grupos y territorio: paneles y cartograma.** Doce comunas en un solo gráfico son ilegibles; en 12 paneles con el mismo eje Y salta a la vista una anomalía. Un residuo contra "lo normal para ese mes" la encuentra sin mirar. Un cartograma de cuadrícula muestra dónde se concentra el deterioro de asistencia en los establecimientos públicos.

**4 · Dashboard mínimo.** Parte A (todos): una función `panel_comuna(df, comuna)` que arma en Matplotlib una figura de 3 paneles (serie por dependencia, mes calendario y una tarjeta con cifras) para cualquier comuna. Parte B (opcional, con Plotly): un HTML autocontenido con un menú desplegable de comunas, que se abre en el navegador sin servidor.

Cada ejercicio trae su celda de **verificación automática** (debe imprimir todos los ✓) y una **solución propuesta** plegada. Ábranla después de intentarlo, no antes. Si Plotly no está instalado, la verificación de la parte B imprime `⊘` y no cuenta como falla.

## Parte de proyecto (11:35)

Abran `notebooks/03-eda.ipynb` de su repositorio (lo crearon en la Clase 7) y agreguen al final la sección 5 del notebook del lab. Usen solo las partes que aplican a su dataset:

- **Incertidumbre:** tasas o promedios por grupo con n e intervalo; embudo si hay muchos grupos de tamaños muy distintos.
- **Tiempo** (si tienen fechas): serie, una línea por año, anomalías. Ojo con ceros que son faltantes y con meses ausentes.
- **Grupos o territorio:** paneles con ejes compartidos, o cartograma o mapa de **tasas** (no de conteos).
- **Dashboard** (opcional): una función `panel(grupo)` y, si quieren, un HTML de Plotly en `figs/`.

Completen hoy **3 filas nuevas** de la bitácora de EDA (quedan 6 o más), cada una con su figura en `figs/` y la celda que la produce. Al menos una debe traer **n e intervalo**, un **patrón en el tiempo** o una **segmentación por grupo o territorio**. La bitácora mantiene sus 5 columnas.

El dashboard es una herramienta de exploración opcional.

## Checklist de salida

- [ ] Ejercicios 1, 2 y 3 pasan su verificación automática (el 4 puede quedar para la casa)
- [ ] `notebooks/03-eda.ipynb` ampliado con la sección de la Clase 8
- [ ] Bitácora con 6 o más filas, cada una con figura en `figs/` y su celda
- [ ] Al menos una fila con n e intervalo, o un patrón en el tiempo, o una segmentación por grupo o territorio
- [ ] Lista corta de variables candidatas para la Clase 9, con una línea por variable

## Entrega

El laboratorio **no se entrega por separado**: alimenta la sección de EDA del **Informe 3** (la fecha y las condiciones, según su pauta). Para la **Clase 9 (jue 08-oct)** traigan la lista corta de variables candidatas: las que el EDA muestra relacionadas con la variable objetivo, con una línea por variable que diga por qué.
