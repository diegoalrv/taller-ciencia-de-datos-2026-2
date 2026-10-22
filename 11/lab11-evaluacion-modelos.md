# Laboratorio 11 — Evaluación de modelos

**EIN146A25 · 2026-2 · Jueves 22-oct, 09:40–12:15 · Lab. Central 114**
Notebook: [`lab11-evaluacion-modelos.ipynb`](lab11-evaluacion-modelos.ipynb) · Referencia técnica: [`lab11-guia-evaluacion.md`](lab11-guia-evaluacion.md)

## Objetivo

Evaluar modelos sin engañarse, con tres preguntas: **¿con qué mido?** (la métrica sale del costo del error, y todo se compara contra un baseline), **¿cómo comparo?** (mismas particiones para todos los modelos, media ± desviación y la regla del empate práctico) y **¿cómo ajusto?** (curva de validación, búsqueda de hiperparámetros y ningún paso que aprenda con datos de validación o de prueba). Esto es la **sección 6 del informe** (`notebooks/04-modelado.ipynb`), que se califica como Informe 4 con los criterios II.1 a II.6 de la pauta.

## Antes de empezar

```bash
git pull                     # en el repositorio del curso
pip install -r requirements.txt
pip install scikit-learn     # si no lo tienen: en este lab es obligatorio
```

`scikit-learn` es **obligatorio** (todo el lab es de modelos): si falta, el Setup lo avisa y se detiene. `seaborn` no se usa.

**Datos sintéticos generados para el lab: ninguna cifra describe a una empresa, un comercio o un reparto real.**

Abran el notebook y ejecuten las celdas de *Setup* y de generación de datos. El archivo de práctica (6.000 pedidos de un servicio de reparto a domicilio; la pregunta es **"¿este pedido llegará con retraso?"**) **se genera solo** en `data_practica/`: no hay que descargar nada y el lab no usa internet. El Setup también separa el **test** (20 %), que no se toca hasta el final.

## Mecánica

| Hora | Qué |
|---|---|
| 09:40 | `git pull`, Setup y generación de datos |
| 09:50 | **Ej. 1 — Métrica y baseline** (~20 min) |
| 10:10 | **Ej. 2 — Tres modelos, mismas particiones** (~20 min) |
| 10:30 | **Ej. 3 — Hiperparámetros: curva y búsqueda** (~20 min; el extra 3.3 es opcional) |
| 10:50 | Recreo |
| 11:05 | **Ej. 4 — Caza de la filtración** (~30 min) |
| 11:35 | **Proyecto:** `04-modelado.ipynb` + tabla de auditoría + ronda de consulta docente |
| 12:05 | Checklist de salida |

## Ejercicios

Todos parten de `X_tr`, `y_tr` y `CV` (5 folds estratificados) del Setup. Si un ejercicio no les sale, el siguiente usa las variables de referencia `_xxx` que deja la celda del profesor.

**1 · Métrica y baseline.** Un "modelo" que predice siempre "sin retraso" acierta el 88,6 % de los pedidos y no detecta ninguno. Con el costo declarado (no avisar un retraso cuesta 10; un aviso de más cuesta 1) se ve qué política trivial es realmente el piso, y de ahí sale la métrica.

**2 · Tres modelos, mismas particiones.** Una regresión logística, un árbol y un bosque aleatorio. Primero se ve qué pasa cuando cada uno se evalúa con su propia partición (el ranking cambia de una corrida a otra). Después se comparan en los **mismos 5 folds** con media ± desviación y se decide, con la regla de la S8 de la cátedra, si hay un ganador o un empate práctico.

**3 · Hiperparámetros: curva y búsqueda.** La curva de validación de la profundidad de un árbol muestra dónde está el subajuste, el buen punto y el sobreajuste. Una búsqueda aleatoria sobre el bosque responde dos preguntas: ¿mejoró algo más allá del ruido? ¿quedó algún hiperparámetro en el borde del espacio? **Extra (opcional):** elegir el umbral de probabilidad que minimiza el costo y reportar el resultado en el test, **una sola vez**.

**4 · Caza de la filtración.** La evaluación de un compañero trae un resultado demasiado bueno y hay que averiguar por qué: encontrar el paso que deja entrar información de la validación, corregirlo y ver cuánto vale de verdad.

Cada ejercicio trae su celda de **verificación automática** (debe imprimir todos los ✓). A diferencia de los labs anteriores, este notebook **no trae las soluciones**: se revisan en clase al cierre de cada bloque, y la guía tiene la referencia técnica de cada paso. La verificación del extra 3.3 imprime `⊘` si no lo hicieron, y no cuenta como falla.

## Parte de proyecto (11:35)

Creen `notebooks/04-modelado.ipynb` en su repositorio y copien la plantilla de la sección 6 del notebook del lab. Lo que entra al modelo es lo que su **ficha de candidatas** (sección 5.3 del informe) marca como `entra`.

- **6.1 Diseño de la evaluación (II.1):** una frase con qué error es más caro → métrica; baseline trivial **con su valor**; partición que respeta la estructura del dato (`GroupKFold` si una unidad se repite, `TimeSeriesSplit` si hay tiempo, `StratifiedKFold` si la clase es rara); test separado al inicio.
- **6.2 Modelos (II.2):** al menos 2 de familias distintas, sobre las variables de la ficha; todo paso que aprende de los datos se ajusta solo con el entrenamiento de cada partición.
- **6.3 Validación cruzada e hiperparámetros (II.3):** mismas particiones, tabla media ± desviación; al menos un hiperparámetro de complejidad con curva o búsqueda (espacio, n.º de combinaciones, métrica y semilla declarados; bordes revisados).
- **6.4 Comparación, elección y limitaciones (II.4):** tabla de comparación, regla del empate, modelo elegido en una frase, test usado una vez, limitaciones.

Hoy completen al menos **6.1 y 6.2**, y la **tabla de auditoría** (7 puntos): para cada uno, `cumple` (sí / no / parcial) y `qué cambio hago`. Lo que no alcancen a corregir, declárenlo como **limitación** en el informe.

Dos recordatorios para la ronda de consulta:

- La **trazabilidad** se revisa por muestreo: 6 cifras de la sección 6 (1 del baseline, 2 de la validación cruzada, 2 de hiperparámetros y 1 del test), cada una con la celda que la produce. Una **cifra central sin celda** gatilla el gate.
- El repositorio debe correr los **cuatro notebooks en orden desde un clon vacío**.

## Checklist de salida

- [ ] Ejercicios 1, 2 y 3 pasan su verificación automática (el 4 y el extra 3.3 pueden quedar para la casa)
- [ ] `notebooks/04-modelado.ipynb` con la estructura 6.1–6.4 (o al menos 6.1 y 6.2 hoy)
- [ ] Tabla de auditoría completa: cada punto con `cumple` y `qué cambio hago`
- [ ] Lo que no se alcanza a corregir hoy, anotado como limitación para el informe
- [ ] Informes 3 y 4 (documento único): **domingo 8-nov, 23:59, AULA-USM** (−10 por día de atraso, máx. 3 días, aplicado a las dos notas; rondas de consulta también en las Clases 12 y 13)
- [ ] Para la Clase 12 (29-oct): `04-modelado.ipynb` en un estado que corra de principio a fin

## Entrega

El laboratorio **no se entrega por separado**: alimenta la **sección 6** de los Informes 3 y 4, que se entregan juntos en un documento único el **domingo 8-nov a las 23:59** por AULA-USM (pauta `informe3-4-pauta`). La **Clase 12 (jue 29-oct)** enseña a escribir `Pipeline` y `ColumnTransformer` propios: traigan `04-modelado.ipynb` corriendo de principio a fin.
