# Guía de evaluación de modelos — Clase 11 (material para estudiantes)

**Para qué sirve:** referencia técnica para evaluar modelos sin engañarse: elegir la métrica según el costo del error, compararla contra un baseline, comparar modelos en las mismas particiones, ajustar hiperparámetros y evitar la filtración. Acompaña al notebook `lab11-evaluacion-modelos.ipynb` y es la base de la **sección 6 del informe** (`04-modelado.ipynb`).

Todas las cifras de ejemplo son del mini-caso sintético del lab (6.000 pedidos de reparto, 11,4 % con retraso).

---

## 0. Las tres preguntas de la clase

| Pregunta | Qué decide | Secciones |
|---|---|---|
| **¿Con qué mido?** | La métrica principal (y las secundarias) y el baseline que hay que superar | §1, §2, §8 |
| **¿Cómo comparo?** | Qué partición, cuántos folds, y cuándo una diferencia entre modelos es real | §3, §4 |
| **¿Cómo ajusto?** | Qué hiperparámetros, en qué rango, y cómo hacerlo sin filtrar información | §5, §6, §7 |

Herramientas del Setup del notebook que se usan en toda la guía:

| Nombre | Qué hace |
|---|---|
| `guardar_figura(fig, nombre)` | Crea `figs/` si no existe y guarda con `dpi=150, bbox_inches="tight"` |
| `X_tr, X_te, y_tr, y_te` | Partición entrenamiento (80 %) / test (20 %), estratificada, con `random_state=SEED` |
| `CV` | `StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)`: los mismos 5 folds para todos los modelos |
| `costo_total(y_real, y_pred)` | `C_FN · FN + C_FP · FP`, con `C_FN = 10` y `C_FP = 1` |
| `crear_modelos()` | Diccionario con tres modelos nuevos sin ajustar: logística (con escalado), árbol y bosque |
| `evaluar_test(modelo, umbral)` | Evalúa en el test y **cuenta cuántas veces se usó**: avisa desde la segunda |

## 1. Costo del error → métrica

Todo clasificador binario comete dos errores distintos. La **matriz de confusión** los separa:

| | predice 0 (no avisa) | predice 1 (avisa) |
|---|---|---|
| **real 0** (no hay retraso) | VN (verdadero negativo) | **FP** (aviso de más) |
| **real 1** (hay retraso) | **FN** (retraso no avisado) | VP (verdadero positivo) |

```python
from sklearn.metrics import confusion_matrix
tn, fp, fn, tp = confusion_matrix(y_real, y_pred, labels=[0, 1]).ravel()
```

**La métrica sale de una frase:** *qué error es más caro, y por qué*. En el lab: "no avisar un retraso (FN) cuesta 10 unidades (reclamo y compensación); un aviso de más (FP) cuesta 1 (un mensaje)". Con esa frase, la exactitud queda descartada.

| Métrica | Fórmula | Cuándo usarla | Ojo |
|---|---|---|---|
| Exactitud | (VP+VN) / total | Clases balanceadas y errores de costo parecido | Con 11 % de positivos, "nunca avisar" tiene 88,6 % |
| Sensibilidad (*recall*) | VP / (VP+FN) | El FN es caro: "¿cuántos retrasos detecto?" | Sube a 1 avisando siempre |
| Precisión | VP / (VP+FP) | El FP es caro: "de mis avisos, ¿cuántos son ciertos?" | Sube avisando poco |
| F1 | media armónica de precisión y sensibilidad | Los dos errores pesan parecido | Ignora los VN |
| F2 | como F1, pero la sensibilidad pesa el doble | El FN es claramente más caro | `fbeta_score(y, p, beta=2)` |
| **PR-AUC** (`average_precision`) | área bajo la curva precisión–sensibilidad | Comparar modelos **sin fijar umbral**, con clase rara | Su valor sin modelo = **prevalencia** (0,114) |
| ROC-AUC | área bajo la curva VP–FP | Comparar modelos sin umbral, clases no tan raras | Sin modelo = 0,5; con clase rara se ve optimista |
| **Costo por pedido** | `costo_total / n` | Cuando el costo del error está declarado | Necesita un umbral (§8) |

Regla práctica: una **métrica principal** que refleje el costo (en el lab, el costo por pedido; para comparar sin umbral, PR-AUC) y una o dos **secundarias** para mostrar el otro lado (sensibilidad y precisión).

**Regresión** (objetivo numérico):

| Métrica | Qué mide | Cuándo |
|---|---|---|
| MAE | Error absoluto medio, en las unidades del objetivo | Todos los errores pesan igual; fácil de explicar ("me equivoco en 12 minutos en promedio") |
| RMSE | Raíz del error cuadrático medio | Los errores grandes son mucho peores que los chicos |
| R² | Fracción de la varianza explicada (1 = perfecto, 0 = predecir la media) | Complemento; no tiene unidades y no dice si el error es tolerable |

En `cross_validate`, las de error van con signo menos: `scoring="neg_mean_absolute_error"`, `"neg_root_mean_squared_error"`.

## 2. Baselines

Un **baseline** es lo que se logra sin modelo. Todo resultado se reporta **junto a su baseline**: un 0,35 de PR-AUC no dice nada si no se sabe que sin modelo es 0,114.

```python
from sklearn.dummy import DummyClassifier, DummyRegressor
DummyClassifier(strategy="most_frequent").fit(X_tr, y_tr)   # siempre la clase más frecuente
DummyClassifier(strategy="prior")                           # misma predicción, probabilidad = prevalencia
DummyRegressor(strategy="mean")                             # siempre la media (o "median")
```

En clasificación con costos hay **dos políticas triviales**, y el piso es **la más exigente de las dos**:

| Política | Exactitud | Sensibilidad | Costo por pedido (entrenamiento) |
|---|---|---|---|
| "Nunca avisar" (`DummyClassifier(strategy="most_frequent")`) | **0,886** | 0,000 | 1,144 |
| "Avisar siempre" (a mano: `np.ones(len(y))`) | 0,114 | 1,000 | **0,886** |

"Nunca avisar" tiene la mejor exactitud y es la **peor** en costo. Con un FN 10 veces más caro, avisar a todos ya es mejor que no avisar a nadie, así que el piso real es **0,886**: un modelo que no baje de ahí no le sirve a la empresa.

## 3. Particiones

**El test se separa al inicio** (`train_test_split` con semilla) y se usa **una sola vez**, al final, con el modelo ya elegido. Todo lo demás (comparar modelos, ajustar hiperparámetros, elegir umbral) se hace con validación cruzada **dentro del entrenamiento**.

| Estructura del dato | Partición | Por qué |
|---|---|---|
| Clase rara (pocos positivos) | `StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)` | Cada fold tiene la misma proporción de positivos |
| La misma unidad aparece varias veces (cliente, estudiante, comercio, repartidor) | `GroupKFold(n_splits=5)` con `groups=` | Si una unidad está en entrenamiento y validación, el modelo "la reconoce" y el resultado se infla |
| Hay tiempo (se predice el futuro) | `TimeSeriesSplit(n_splits=5)` | Se entrena con el pasado y se valida con lo que viene después, nunca al revés |

```python
from sklearn.model_selection import cross_validate
r = cross_validate(modelo, X_tr, y_tr, cv=CV, n_jobs=-1,
                   scoring={"ap": "average_precision", "roc": "roc_auc"})
r["test_ap"]          # arreglo con las 5 PR-AUC, una por fold
```

**Las mismas particiones para todos los modelos.** El rendimiento de un modelo cambia según qué pedidos le tocaron en validación. Si cada modelo se evalúa con su propia partición, la diferencia entre modelos se mezcla con la diferencia entre particiones. En el Ej. 2.1 del lab, la misma regresión logística "valía" 0,355, 0,384 o 0,348 según la partición, y en una corrida el bosque "ganaba". Definir `CV` una vez y pasarlo a todos los modelos lo evita.

## 4. Media ± desviación y empate práctico

Cada modelo se resume con **media ± desviación entre folds**. La desviación dice cuánto se mueve la métrica solo por cambiar qué datos se usan para validar.

**Regla del empate práctico (S8):** si la diferencia entre las medias de los dos mejores es **menor que la desviación entre folds**, es un empate práctico → se elige **el más simple** (más fácil de explicar, de mantener y de automatizar).

| Modelo (mismos 5 folds) | PR-AUC | ROC-AUC |
|---|---|---|
| Regresión logística (con escalado) | **0,352 ± 0,027** | 0,766 ± 0,023 |
| Bosque aleatorio (200 árboles, `min_samples_leaf=10`) | 0,337 ± 0,025 | 0,755 ± 0,024 |
| Árbol sin límite de profundidad | 0,131 ± 0,009 | 0,548 ± 0,020 |
| *Baseline* | *0,114* | *0,500* |

Diferencia logística − bosque = 0,015 < 0,027 → **empate, gana la logística** (lineal, rápida, coeficientes interpretables). No es una prueba estadística formal; es una regla honesta para no declarar ganadores por ruido. Un gráfico de cajas de las 5 métricas por modelo, con la línea del baseline, lo muestra de un vistazo.

## 5. Curva de validación

Un hiperparámetro de **complejidad** controla cuánto puede memorizar el modelo: `max_depth` y `min_samples_leaf` en árboles y bosques, `C` en la regresión logística, `n_neighbors` en vecinos. La curva de validación muestra la métrica en entrenamiento y en validación para cada valor:

```python
from sklearn.model_selection import validation_curve
tr, va = validation_curve(DecisionTreeClassifier(random_state=SEED), X_tr, y_tr,
                          param_name="max_depth", param_range=range(1, 21),
                          cv=CV, scoring="roc_auc", n_jobs=-1)
tr.mean(axis=1), va.mean(axis=1)       # una media por valor del hiperparámetro
```

Cómo leerla:

| Zona | Entrenamiento | Validación | Brecha | En el lab (árbol, ROC-AUC) |
|---|---|---|---|---|
| **Subajuste** | bajo | bajo | chica | profundidad 1–2 (0,61 / 0,61) |
| **Buen punto** | sube | en su máximo | moderada | profundidad 3–5, máximo en la **4** (0,688) |
| **Sobreajuste** | sigue subiendo | baja | crece | desde la **7**; en la 20: 1,000 vs. 0,547 |

La **brecha** entre las dos curvas es la medida del sobreajuste. Un 1,000 en entrenamiento no es un logro: es un examen con las respuestas a la vista.

## 6. `GridSearchCV` vs. `RandomizedSearchCV`

| | `GridSearchCV` | `RandomizedSearchCV` |
|---|---|---|
| Qué prueba | **Todas** las combinaciones del espacio | `n_iter` combinaciones al azar |
| Cuándo | Pocos hiperparámetros y pocos valores (≤ 50 combinaciones) | Espacios grandes; con 15–30 iteraciones suele bastar |
| Costo | combinaciones × folds ajustes | `n_iter` × folds ajustes |

```python
from sklearn.model_selection import RandomizedSearchCV
espacio = {"max_depth": list(range(3, 13)),                  # 10 valores
           "min_samples_leaf": [1, 3, 5, 10, 20, 30, 50],    # 7 valores
           "max_features": [0.2, 0.3, 0.5, 0.7, 1.0]}        # 5 valores → 350 combinaciones
busqueda = RandomizedSearchCV(RandomForestClassifier(n_estimators=150, random_state=SEED, n_jobs=-1),
                              espacio, n_iter=15, scoring="average_precision", cv=CV, random_state=SEED)
busqueda.fit(X_tr, y_tr)                                     # SOLO con el entrenamiento
busqueda.best_params_, busqueda.best_score_
busqueda.cv_results_["std_test_score"][busqueda.best_index_] # desviación entre folds de la mejor
```

Lo que hay que **declarar** en el informe: el espacio (valores de cada hiperparámetro), el número de combinaciones probadas de las posibles (15 de 350), la métrica, la semilla y que la búsqueda se hizo dentro del entrenamiento.

**Bordes.** Si el mejor valor es el mínimo o el máximo de su lista (en el lab, `max_features = 0,2`), el óptimo podría estar fuera del espacio: hay que **ampliar el rango** en esa dirección antes de concluir.

**Más búsqueda ≠ mejor modelo.** La mejor combinación del lab da **0,334 ± 0,027**, frente a 0,337 del bosque por defecto: no mejora nada más allá del ruido. Con muchas combinaciones, la mejor puede ganar por suerte en esos 5 folds; si la mejora es menor que la desviación, no hay evidencia de que valga la pena el modelo más complejo (§4).

## 7. La filtración

Hay **filtración** cuando información de la validación o del test entra al entrenamiento. El síntoma típico: un resultado demasiado bueno, que se cae en producción.

**Qué pasos "aprenden" del dato** (y por lo tanto filtran si se ajustan antes de dividir):

| Paso | Qué aprende | Ejemplo de filtración |
|---|---|---|
| Imputar | La media o la mediana de la columna | Imputar con la media de **todos** los datos |
| Escalar | Media y desviación de cada columna | `StandardScaler().fit(X)` antes de `cross_validate` |
| Seleccionar variables | Qué variables se relacionan con el objetivo | Elegir las 10 más correlacionadas con `y` usando todo el conjunto |
| **Codificar por la tasa del objetivo** | La tasa de `y` por categoría | La tasa de retraso por comercio con todo el entrenamiento (Ej. 4) |

**La receta:** *dividir → ajustar el paso con el entrenamiento → aplicarlo a la validación*. Dentro de la validación cruzada, eso significa repetirlo **en cada fold**:

```python
for a, b in CV.split(X_tr, y_tr):                                  # a = entrenamiento del fold, b = validación
    tasas = pd.Series(y_tr.values[a]).groupby(com_tr[a]).mean()     # aprende SOLO con el fold
    Xa, Xb = X_tr.iloc[a].copy(), X_tr.iloc[b].copy()
    Xa["tasa_comercio"] = pd.Series(com_tr[a]).map(tasas).values
    Xb["tasa_comercio"] = pd.Series(com_tr[b]).map(tasas).fillna(y_tr.values[a].mean()).values
    ...
```

En el lab: filtrada **0,855 ± 0,021** → honesta **0,689 ± 0,021**, y sin la variable **0,737**. Con ≈ 9,6 pedidos por comercio, la etiqueta de cada pedido era una parte grande de la tasa de su comercio: el modelo veía la respuesta.

**`make_pipeline` (adelanto de la Clase 12).** Un pipeline encadena los pasos y el modelo en un solo objeto; `cross_validate` lo ajusta entero **en cada fold**, así que el escalado aprende solo con el entrenamiento del fold:

```python
from sklearn.pipeline import make_pipeline
modelo = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
cross_validate(modelo, X_tr, y_tr, cv=CV)          # sin filtración del escalado
```

Hoy solo se usa (en `crear_modelos()`); la Clase 12 enseña a escribir `Pipeline` y `ColumnTransformer` propios.

**Nota sobre `GroupKFold`.** En el lab, el mismo comercio aparece en entrenamiento y validación. Si el modelo se va a usar con **comercios nuevos** (o repartidores nuevos), hay que validar como se va a usar: con `GroupKFold(n_splits=5)` y `groups=com_tr`, ningún comercio está a la vez en entrenamiento y validación. El número suele bajar, y es el honesto. Regla: si la unidad se repite y el modelo tiene que funcionar con unidades que no vio, la partición es por grupo.

## 8. Umbral y costo

`predict` usa el umbral **0,5** por defecto: avisa si la probabilidad de retraso es ≥ 0,5. Es un valor por defecto, no una decisión. Con costos asimétricos, el umbral que minimiza el costo esperado (con probabilidades bien calibradas) es:

$$u^* = \frac{C_{FP}}{C_{FP} + C_{FN}} = \frac{1}{1 + 10} \approx 0{,}09$$

Si la probabilidad de retraso es p: avisar cuesta 1 solo cuando no había retraso (probabilidad 1 − p), y no avisar cuesta 10 cuando sí lo había (probabilidad p). Conviene avisar cuando 10·p > 1·(1 − p), es decir, p > 1/11 ≈ 0,09.

El umbral se elige **con el entrenamiento**, con probabilidades **fuera de fold** (cada pedido predicho por un modelo que no lo vio), nunca mirando el test:

```python
from sklearn.model_selection import cross_val_predict
p_oof = cross_val_predict(modelo, X_tr, y_tr, cv=CV, method="predict_proba")[:, 1]
umbrales = np.round(np.arange(0.02, 0.70, 0.01), 2)
costos = [costo_total(y_tr, (p_oof >= u).astype(int)) / len(y_tr) for u in umbrales]
umbral_opt = umbrales[np.argmin(costos)]
```

En el lab, la logística con umbral **0,08** (fuera de fold: 0,601 por pedido) da en el **test** sensibilidad 0,825, precisión 0,199 y **0,579 por pedido**; con el umbral 0,5 casi no avisa (sensibilidad 0,058, costo 1,083). Frente a "nunca avisar" (1,142) es −49 %; frente a "avisar siempre" (0,886), −35 %.

**Alternativas fuera de alcance hoy:** `class_weight="balanced"` o remuestrear (sobremuestreo, SMOTE) cambian el entrenamiento para dar más peso a la clase rara; muchas veces mover el umbral logra lo mismo con menos riesgo. Calibrar probabilidades (`CalibratedClassifierCV`) acerca el umbral óptimo al teórico.

## 9. Cómo reportar

La tabla de la S12 (sección 6.4 del informe), una fila por modelo:

| modelo | métrica (por qué) | media ± desv. (CV) | vs. baseline | hiperparámetros | veredicto |
|---|---|---|---|---|---|

**Bien escrito:**

| modelo | métrica (por qué) | media ± desv. (CV, 5 folds) | vs. baseline | hiperparámetros | veredicto |
|---|---|---|---|---|---|
| Regresión logística | PR-AUC (el FN cuesta 10 veces el FP) | 0,352 ± 0,027 | +0,238 sobre 0,114 | escalado + `max_iter=1000`, sin búsqueda | **elegido**: empata con el bosque y es el más simple |
| Bosque aleatorio | PR-AUC | 0,337 ± 0,025 | +0,223 | 200 árboles, `min_samples_leaf=10`; búsqueda aleatoria 15/350 → 0,334 ± 0,027, sin mejora | empate con la logística |
| Árbol | PR-AUC | 0,131 ± 0,009 | +0,017 | sin límite; curva de `max_depth`: mejor 4, sobreajuste desde 7 | descartado |

Y debajo, una frase y el test: *"Se elige la regresión logística: empata con el bosque (diferencia 0,015 < desviación 0,027) y es la más simple de explicar. En el test (usado una vez), con umbral 0,08 elegido fuera de fold, cuesta 0,579 unidades por pedido, 35 % menos que avisar siempre."*

**Mal escrito:**

| modelo | métrica | resultado | veredicto |
|---|---|---|---|
| Bosque aleatorio | accuracy | 0,89 | el mejor |

Qué le falta: la métrica no está justificada (y con clase rara, la exactitud engaña), no hay desviación ni baseline (0,89 es apenas lo que da "nunca avisar", 0,886), no se sabe si se evaluó en el test o en el entrenamiento, ni qué hiperparámetros se probaron, y "el mejor" no dice frente a qué.

Cada cifra de la tabla tiene que poder rastrearse hasta la celda que la produce (trazabilidad).

## 10. Lista de auditoría y criterios de la pauta

La misma lista de la S12 y la S19; en el notebook, la tabla `auditoria` con columnas `punto · criterio_pauta · cumple · que_cambio_hago`:

| Punto | Criterio de la pauta |
|---|---|
| La métrica está justificada por el costo del error (una frase) | II.1 |
| Hay baseline trivial, con su valor | II.1 |
| Mismas particiones para todos los modelos | II.3 |
| Ningún paso aprende con datos de validación o de prueba | II.2 |
| Los hiperparámetros tienen espacio declarado, n.º de combinaciones, métrica y semilla | II.3 |
| El test se usó una sola vez, con el modelo ya elegido | II.1 / II.4 |
| El modelo elegido tiene una frase de justificación | II.4 |

Los criterios de la sección 6 (Informe 4): **II.1** diseño de la evaluación (20 pts) · **II.2** modelos (20) · **II.3** validación cruzada e hiperparámetros (25) · **II.4** comparación, elección y limitaciones (15) · **II.5** reproducibilidad y trazabilidad (10): semilla fijada, corre desde un clon vacío, cada cifra cita su celda · **II.6** redacción y declaración de IA (10).

Ojo con lo que la pauta ya marca como error del Informe 2: **una métrica casi perfecta es señal para sospechar de la evaluación, no para celebrar** (Ej. 4), y la exactitud con una clase rara, o R² sin decir cuánto se equivoca el modelo en unidades reales, descuenta en II.1.

Lo que no se alcance a corregir se declara como **limitación** en 6.4: una limitación declarada es mejor que un problema escondido.

**Lo que viene:** Clase 12 — `Pipeline` y `ColumnTransformer`: escribir el preprocesamiento y el modelo como un solo objeto, para que la regla de §7 se cumpla sola. Traigan `04-modelado.ipynb` corriendo de principio a fin.
