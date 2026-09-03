# Laboratorio 5 — Integración de fuentes y creación de características

**EIN146A25 · 2026-2 · Jueves 3-sep, 09:40–12:15 · Lab. Central 114**
Notebook: [`lab05-integracion-features.ipynb`](lab05-integracion-features.ipynb) · Referencia técnica: [`lab05-guia-integracion-features.md`](lab05-guia-integracion-features.md)

## Objetivo

Juntar fuentes sin inventar ni perder datos — apilar periodos, cruzar por llaves que no vienen escritas igual, cambiar de granularidad antes de unir — y crear las primeras características del proyecto con una justificación que salga de la pregunta de datos. Todo con conteos: lo que hoy practican es exactamente la sección de integración y preprocesamiento del Informe 2.

## Antes de empezar

```bash
git pull            # en el repositorio del curso
pip install pandas numpy jupyter
```

Abran el notebook y ejecuten las celdas de *Setup* y de generación de archivos. Los datos de práctica (emisiones estilo RETC, permisos de circulación estilo INE y una tabla de homologación de comunas) **se generan solos** en `data_practica/`: no hay que descargar nada y el lab no usa internet.

## Mecánica

Dos carriles en paralelo. Trabajen a su ritmo: quien termina un ejercicio pasa al siguiente sin esperar.

| Hora | Qué |
|---|---|
| 09:40 | `git pull`, correr el Setup. Se proyecta el orden de la devolución del Informe 1 |
| 09:50 | **Ej. 1 — Apilar tres años con esquema distinto** (~15 min) |
| 10:05 | **Ej. 2 — Cruzar por nombre con tabla de homologación** (~20 min) |
| 10:25 | **Ej. 3 — Granularidad y cardinalidad** (~20 min) · si alcanza, **Ej. 4 — Tres características** (~10 min) |
| 10:45 | Recreo |
| 11:00 | **Clonar y correr el repositorio del otro equipo** (A → B → C → A) |
| 11:20 | **Proyecto:** plantilla de `02-preprocesamiento` — mapa de integración, registro de decisiones, características candidatas |
| 12:05 | Checklist de salida por equipo |

En paralelo desde las 09:50 corre la **devolución individual del Informe 1**: los llamo equipo por equipo (~5 min), el orden queda proyectado. Sigan trabajando hasta su turno.

## Ejercicios

Los cuatro trabajan sobre el mismo mini-caso: emisiones vehiculares y permisos de circulación de las 12 comunas del Gran Concepción, 2022–2024.

**1 · Apilar tres años con esquema distinto.** El archivo 2024 renombró dos columnas y perdió las coordenadas; 2022 y 2023 publicaron el código de comuna como número y perdieron el cero. Una sola tabla de 288 × 13, con la llave como texto de 5 caracteres, una columna `origen`, y la suma de toneladas conservada.

**2 · Cruzar por nombre con tabla de homologación.** Los permisos solo traen el nombre de la comuna, escrito a mano (`CONCEPCION`, `Coronel `, `Tome`). Normalizar una llave auxiliar en ambas tablas, cruzar con la tabla CUT usando `validate` e `indicator`, y diagnosticar con un anti-join. Las 108 filas se conservan; ninguna queda sin código.

**3 · Granularidad y cardinalidad.** Emisiones y permisos tienen filas distintas (comuna-año-contaminante-fuente vs. comuna-año-tipo de vehículo). Primero el error: el cruce ingenuo produce 2.592 filas y multiplica las toneladas por nueve sin lanzar ninguna excepción. Después lo correcto: agregar cada lado a comuna-año, unir con `validate="one_to_one"`, verificar con sumas de control, y crear `ton_por_vehiculo`.

**4 · Tres características en diez minutos.** Una razón (`pct_diesel`), una temporal (variación respecto del año anterior de la misma comuna) y un indicador por umbral (`alta_emision`). Cada una con su regla de verificación. Si no alcanza en clase, queda para la casa: no es requisito de salida.

Cada ejercicio trae su celda de **verificación automática** (debe imprimir todos los ✓), una **solución propuesta** plegada, y una tabla de referencia `df_solN` para que el siguiente ejercicio no dependa del anterior. Abran la solución después de intentarlo, no antes.

## Clonar el repositorio del otro equipo (11:00)

Cada equipo clona el repositorio del equipo siguiente **en una carpeta vacía**, abre `01-obtencion.ipynb` y hace `Restart & Run All`. Se anota la primera falla y su causa: archivo ausente, ruta, dependencia, driver, paso manual no documentado. Dos minutos por equipo de puesta en común. Esto es el gate del Informe 2 aplicado entre pares, con tres semanas de ventaja.

## Parte de proyecto (11:20)

Sobre su repositorio, con la sección 5 del notebook:

```
proyecto/
├── README.md
├── data/
│   ├── raw/                    ← intocable
│   └── processed/              ← lo que produce 02-preprocesamiento
└── notebooks/
    ├── 01-obtencion.ipynb
    └── 02-preprocesamiento.ipynb
```

Completen hoy las tres tablas de la plantilla con lo que ya saben del proyecto: el **mapa de integración** (fuentes, operación, llave, granularidad final, tipo de join, filas antes y después), el **registro de decisiones** iniciado con los hallazgos del Informe 1 (cada uno con la celda que lo evidencia) y **3 características candidatas** justificadas desde la pregunta de datos. El código de limpieza e integración se escribe sobre esas tablas, no al revés.

## Checklist de salida

- [ ] Ejercicios 1, 2 y 3 pasan su verificación automática (el 4 puede quedar para la casa)
- [ ] Mapa de integración del proyecto completo, con conteos
- [ ] Registro de decisiones iniciado con los hallazgos del Informe 1, cada uno con su celda
- [ ] 3 características candidatas, cada una con qué parte de la pregunta responde
- [ ] `02-preprocesamiento.ipynb` creado en el repo y escribiendo a `data/processed/`
- [ ] Repositorio del otro equipo clonado y ejecutado; primera falla anotada
- [ ] Notas y observaciones del Informe 1 recibidas

## Entrega

El laboratorio **no se entrega por separado**: su resultado es la sección de integración y preprocesamiento del **Informe 2 (10-sep, 23:59, AULA)**. La Clase 6 es taller de cierre del informe con el profesor en la sala. Ojo: el miércoles 9 tienen Certamen 1 de Machine Learning.
