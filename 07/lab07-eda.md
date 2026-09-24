# Laboratorio 7 — Análisis exploratorio de datos (EDA)

**EIN146A25 · 2026-2 · Jueves 24-sep, 09:40–12:15 · Lab. Central 114**
Notebook: [`lab07-eda.ipynb`](lab07-eda.ipynb) · Referencia técnica: [`lab07-guia-eda.md`](lab07-guia-eda.md)

## Objetivo

Mirar los datos antes de modelarlos: una variable a la vez, relaciones entre dos, y una segmentación que puede cambiar la conclusión (paradoja de Simpson). Todo con figuras que dicen un hallazgo, no que decoran. Esto es exactamente la sección de EDA del Informe 3.

## Antes de empezar

```bash
git pull            # en el repositorio del curso
pip install pandas numpy matplotlib seaborn jupyter
```

`seaborn` es **opcional**: el notebook funciona completo solo con Matplotlib y pandas, y avisa si no está instalado.

**Datos sintéticos generados para el lab: ninguna cifra describe a una comuna, establecimiento o estudiante real.**

Abran el notebook y ejecuten las celdas de *Setup* y de generación de archivos. El archivo de práctica (24.000 estudiantes de enseñanza media de las 12 comunas de la provincia de Concepción) **se genera solo** en `data_practica/`: no hay que descargar nada y el lab no usa internet.

## Mecánica

| Hora | Qué |
|---|---|
| 09:40 | `git pull`, Setup y generación de datos |
| 09:50 | **Ej. 1 — Una variable a la vez** (~20 min) |
| 10:10 | **Ej. 2 — Relaciones y correlación** (~20 min) |
| 10:30 | **Ej. 3 — Paradoja de Simpson** (~15 min) · si alcanza, **Ej. 4 — Una figura que comunica** |
| 10:45 | Recreo |
| 11:00 | **Proyecto:** `03-eda.ipynb` y las primeras 3 filas de la bitácora de EDA |
| 11:35 | **Gate del Informe 2 en vivo** con su propio repo + ronda de consulta docente (~8 min por equipo) |
| 12:05 | Checklist de salida |

## Ejercicios

Los cuatro trabajan sobre el mismo archivo: `estudiantes_media.csv`.

**1 · Una variable a la vez.** `promedio_general` trae 720 estudiantes con nota 0,0 — un nulo disfrazado, no un desempeño real, y casi todos son retirados. `distancia_km` tiene una asimetría fuerte que la escala logarítmica corrige. Se mide con `skew()`, sin `scipy`.

**2 · Relaciones y correlación.** Asistencia vs. promedio con 24.000 puntos es una mancha: se resuelve con `hexbin` o muestreo con transparencia. Pearson y Spearman dan una lectura distinta según se incluyan o no los ceros disfrazados — y eso dice algo sobre qué mide cada uno.

**3 · Paradoja de Simpson.** Penco parece "mejor" que Tomé en la tasa de riesgo total, pero es peor en las tres dependencias por separado. El confusor es la composición del alumnado: sin segmentar, la conclusión se invierte.

**4 · Una figura que comunica** (opcional). Rehacer una figura anterior con título = hallazgo, unidades y `savefig` a `figs/`. Si no alcanza en clase, queda para la casa.

Cada ejercicio trae su celda de **verificación automática** (debe imprimir todos los ✓) y una **solución propuesta** plegada. Ábranla después de intentarlo, no antes.

## Gate del Informe 2 (11:35)

Clonen **su propio** repositorio en una carpeta vacía y hagan `Restart & Run All` en `01-obtencion.ipynb` y `02-preprocesamiento.ipynb`. Anoten la primera falla y su causa (archivo ausente, ruta, dependencia, paso manual no documentado) — con esto sobra el fin de semana para corregirlo antes del domingo.

## Parte de proyecto (11:00)

Sobre su repositorio, con la sección 5 del notebook:

```
proyecto/
├── README.md
├── data/
│   ├── raw/                    ← intocable
│   └── processed/              ← lo que produce 02-preprocesamiento
└── notebooks/
    ├── 01-obtencion.ipynb
    ├── 02-preprocesamiento.ipynb
    └── 03-eda.ipynb            ← nuevo hoy
figs/                            ← figuras del EDA
```

Copien la plantilla de la sección 5 a `notebooks/03-eda.ipynb`. Completen hoy: qué es una fila y cuántas hay, la variable objetivo (n, balance, nulos) y las primeras 3 filas de la **bitácora de EDA**, cada una con su figura en `figs/` y la celda que la produce.

## Checklist de salida

- [ ] Ejercicios 1, 2 y 3 pasan su verificación automática (el 4 puede quedar para la casa)
- [ ] `notebooks/03-eda.ipynb` creado en el repo, leyendo solo desde `data/processed/`
- [ ] Unidad de análisis y variable objetivo descritas (n, balance, nulos)
- [ ] 3 filas de la bitácora de EDA, cada una con figura en `figs/` y su celda
- [ ] Gate del Informe 2 probado: su repo clonado en una carpeta vacía, `01` y `02` corren de punta a punta
- [ ] Primera falla del gate (si hubo) anotada y con plan de arreglo antes del domingo

## Entrega

El laboratorio **no se entrega por separado**: alimenta la sección de EDA del **Informe 3 (jue 08-oct)**. Recuerden que el **Informe 2 se entrega el domingo 27-sep, 23:59, vía AULA-USM**.
