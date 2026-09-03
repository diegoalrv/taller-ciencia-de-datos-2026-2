# Laboratorio 2 — Búsqueda y recolección de datos

**EIN146A25 · 2026-2 · Jueves 13-ago, 09:40–12:15 · Lab. Central 114**
Notebook: [`lab02-recoleccion-datos.ipynb`](lab02-recoleccion-datos.ipynb) · Referencia técnica: [`lab02-guia-recoleccion-datos.md`](lab02-guia-recoleccion-datos.md)

## Objetivo

Leer datos correctamente por las tres vías que usarán en el proyecto — archivo plano, base SQL y API — y aplicar el estándar de obtención reproducible a su propio dataset aprobado.

## Antes de empezar

```bash
pip install pandas requests jupyter
```

Abran el notebook y ejecuten la celda de *Setup*. Los archivos de práctica (CSV sucio y base sqlite) **se generan solos** en `data_practica/`: no hay que descargar nada para los ejercicios 1 y 2. El 3 usa internet, con respaldo embebido si el WiFi falla.

## Mecánica

Tres carriles en paralelo. Trabajen a su ritmo: quien termina un ejercicio pasa al siguiente sin esperar.

| Hora | Qué |
|---|---|
| 09:40 | Clonar/actualizar el repo del curso, correr el Setup |
| 09:50 | **Ej. 1 — CSV con trampas** (~25 min) |
| 10:15 | **Ej. 2 — SQL con sqlite** (~20 min) |
| 10:35 | **Ej. 3 — API Mindicador** (~15 min) |
| 10:50 | Recreo |
| 11:05 | Puesta en común + demo en vivo |
| 11:20 | **Proyecto:** repo, descarga del dataset propio, metadata |
| 12:05 | Checklist de salida por equipo |

En paralelo desde las 09:50 corre la **ronda de aprobación de propuestas**: los llamo equipo por equipo (~5 min), el orden queda proyectado. Sigan trabajando hasta su turno.

## Ejercicios

**1 · CSV con trampas.** Leer un CSV "chileno" (latin-1, `;`, decimal con coma, notas antes del header, `S/I` como nulo, códigos con cero a la izquierda) de modo que `df.info()` quede limpio. Antes de tocar `read_csv`: mirar el archivo crudo.

**2 · SQL.** Una sola consulta vía `pd.read_sql` con JOIN + GROUP BY sobre `farmacia.db`. Criterio: reducción de volumen en SQL, análisis fino en pandas.

**3 · API.** Serie histórica de la UF desde `mindicador.cl`, JSON → DataFrame, y **guardar la respuesta cruda a disco** antes de transformar nada.

Cada ejercicio trae su celda de **verificación automática** (debe imprimir todos los ✓) y su solución plegada. Abran la solución después de intentarlo, no antes: el error es parte del ejercicio.

## Parte de proyecto (11:20)

Con la propuesta aprobada, sobre su repositorio:

```
proyecto/
├── README.md                  ← tabla de metadata de la fuente
├── data/raw/                  ← datos crudos: NO SE TOCAN
└── notebooks/01-obtencion.ipynb
```

La sección 4 del notebook trae la plantilla de `01-obtencion` — cópienla y complétenla con su dataset.

## Checklist de salida

- [ ] Los 3 ejercicios pasan su verificación automática
- [ ] Propuesta aprobada (o ajustes aplicados / respaldo activado)
- [ ] Dataset principal en `data/raw/`, sin modificaciones
- [ ] Obtención automatizada, o documentada paso a paso con URL y fecha
- [ ] Metadata completa, copiada al README
- [ ] Verificación básica: dimensiones, `info()`, nulos
- [ ] Si usaron API: respuesta cruda guardada a disco

## Entrega

El laboratorio **no se entrega por separado**: su resultado es la sección de obtención del **Informe 1 (20-ago, 23:59, AULA)**. Lo que quede pendiente hoy se termina antes de la Clase 3.
