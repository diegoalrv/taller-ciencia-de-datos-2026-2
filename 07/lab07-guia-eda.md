# Guía de análisis exploratorio de datos — Clase 7 (material para estudiantes)

**Para qué sirve:** referencia técnica de las operaciones de EDA (univariado, bivariado, nulos disfrazados, correlación, segmentación) y de cómo una figura se convierte en una fila de la bitácora del Informe 3. Acompaña al notebook `lab07-eda.ipynb`.

---

## 0. El ciclo del EDA

**Pregunta → figura → observación con número → decisión o hipótesis.**

Una figura sin ese texto alrededor no sirve: "el histograma de X" no es un hallazgo, es una descripción de lo que ya se ve. El anti-patrón es la **galería sin texto**: veinte gráficos, ninguna frase con un número.

| Paso | Ejemplo |
|---|---|
| Pregunta | ¿La asistencia se relaciona con el rendimiento? |
| Figura | `hexbin` de asistencia vs. promedio |
| Observación | "Pearson pasa de 0,77 a 0,88 al excluir los 720 ceros disfrazados" |
| Decisión/hipótesis | "Se reporta la correlación sin los ceros; se documenta por qué" |

## 1. Antes de graficar

Tres preguntas antes de la primera figura:

1. **Qué es una fila** (la unidad de análisis, ya definida en la Clase 1).
2. **La variable objetivo**: balance de clases, cuántos nulos.
3. `df.shape`, `df.dtypes`, `df.nunique()` — la forma cruda de los datos.

```python
print(df.shape)
print(df.dtypes)
print(df.nunique())
df["situacion_final"].value_counts(normalize=True)
```

## 2. Una variable numérica

| Herramienta | Para qué |
|---|---|
| Histograma (`ax.hist(x, bins=...)`) | Forma de la distribución. Probar más de un `bins`: pocos ocultan estructura, demasiados muestran ruido |
| Boxplot (`ax.boxplot([...])`) | Comparar la misma variable entre grupos, outliers visibles |
| ECDF (`np.sort(x)` vs. rango acumulado) | Comparar dos grupos sin pelear con los bins del histograma |
| Media vs. mediana | Si difieren mucho, la distribución está sesgada o tiene outliers |
| `Series.skew()` | Asimetría: cerca de 0 es simétrica; > 1 en valor absoluto ya es notorio |

**Cuándo usar escala log:** cuando los valores cubren varios órdenes de magnitud y la mayoría se amontona cerca de cero (`distancia_km`, ingresos, población). Se declara con `bins=np.logspace(a, b, n)` + `ax.set_xscale("log")`, y se dice en el título o el eje que la escala es logarítmica.

```python
fig, ax = plt.subplots()
ax.hist(df["distancia_km"], bins=np.logspace(-1, 2, 40))
ax.set_xscale("log")
ax.axvline(df["distancia_km"].median(), linestyle="--")
```

## 3. Nulos disfrazados

Un nulo disfrazado es un valor **válido en apariencia** que en realidad significa "sin dato". No sale en `df.isna()`.

| Cómo suele venir | Dónde buscarlo |
|---|---|
| `0.0` en una escala que no incluye el cero (nota 1-7, ingreso, edad) | Histograma con una barra sospechosa en el extremo; `value_counts()` |
| Edad `999`, año `9999` | Rango fuera de lo posible para la variable |
| Fecha `1900-01-01` | Fecha mínima muy anterior al resto |
| Código `99`, `"S/I"`, `" "` (espacio) | `value_counts().head()` de variables categóricas o de código |

Cómo detectarlo: histograma (una barra aislada), `value_counts().head()` en categóricas, y comparar contra el rango esperado del diccionario de datos (si existe).

**Por qué importa si es informativo.** Un nulo aleatorio (el dato se perdió por azar) se puede imputar sin sesgar el análisis. Un nulo informativo — como `promedio_general == 0.0` en estudiantes retirados — **no es aleatorio**: está correlacionado con la variable objetivo. Imputarlo con la media inventaría un desempeño que nunca existió y contaminaría cualquier modelo posterior. La decisión correcta suele ser dejarlo como `NaN` y decidir explícitamente si esas filas se excluyen o se tratan aparte.

```python
n_disfrazados = (df["promedio_general"] == 0.0).sum()
df.loc[df["promedio_general"] == 0.0, "promedio_general"] = np.nan
df.loc[df["promedio_general"].isna(), "situacion_final"].value_counts()  # ¿quiénes son?
```

## 4. Una variable categórica

| Herramienta | Para qué |
|---|---|
| Barras horizontales ordenadas (`ax.barh`) | Legibles con muchas categorías o etiquetas largas |
| Proporciones (`value_counts(normalize=True)`) | Composición, no solo conteo |
| Categorías raras | Agrupar en "otras" si son < 1-2 % y no son el foco de la pregunta |
| Etiquetas casi iguales | `"Coronel "` ≠ `"Coronel"`: normalizar antes de contar (ver Clase 5, §2) |

## 5. Dos variables

La matriz que decide qué gráfico usar:

| | Objetivo numérico | Objetivo categórico |
|---|---|---|
| **Predictor numérico** | scatter / hexbin, correlación | boxplot o histogramas superpuestos por categoría |
| **Predictor categórico** | boxplot / barras de medias | tabla cruzada, barras agrupadas |

Series de tiempo: `df.set_index("fecha").resample("M").mean()` para agregar por mes, `.rolling(7).mean()` para suavizar.

## 6. Correlación

| Coeficiente | Mide | Sensible a |
|---|---|---|
| Pearson (`Series.corr()`) | Relación **lineal** | Outliers y no linealidad |
| Spearman | Relación **monótona** (por rangos) | Mucho menos a outliers |
| Kendall | Concordancia de pares, más robusto con pocos datos | Poco usado con datasets grandes |

**Spearman = Pearson de los rangos.** `Series.corr(method="spearman")` funciona, pero **importa `scipy` por dentro**, y este lab asume que puede no estar instalado. Se calcula a mano:

```python
def spearman(a, b):
    m = a.notna() & b.notna()          # filas sin NaN en ninguna de las dos
    return a[m].rank().corr(b[m].rank())
```

Matriz completa y heatmap (sin seaborn):

```python
corr_matrix = df[["asistencia_pct", "promedio_general", "distancia_km"]].corr()
fig, ax = plt.subplots()
im = ax.imshow(corr_matrix, vmin=-1, vmax=1, cmap="coolwarm")
ax.set_xticks(range(len(corr_matrix))); ax.set_xticklabels(corr_matrix.columns, rotation=45)
ax.set_yticks(range(len(corr_matrix))); ax.set_yticklabels(corr_matrix.columns)
fig.colorbar(im)
```

Tres advertencias:

1. **No linealidad**: una relación en U o en campana da Pearson ≈ 0 aunque la relación sea fuerte. Mirar el scatter, no solo el número.
2. **Outliers y nulos disfrazados**: un puñado de valores extremos (o un nulo con valor 0.0) puede mover Pearson sin que Spearman se entere — es la comparación del Ej. 2.
3. **Confusor de tamaño → tasas**: correlacionar totales (matrícula, casos) casi siempre da una correlación alta porque ambas crecen con el tamaño de la unidad. Correlacionar tasas o proporciones es lo que suele responder la pregunta real.

**Correlación no es causalidad.** Es el punto de partida para una hipótesis, no la conclusión del informe.

## 7. Datos grandes

- `df.sample(n, random_state=...)` con semilla fija — siempre, para que la figura sea reproducible.
- `hexbin(gridsize=..., mincnt=1)` en vez de scatter cuando hay miles de puntos: agrupa en celdas y colorea por densidad.
- Agregar antes de graficar (`groupby(...).mean()`) cuando la pregunta es sobre el grupo, no sobre cada fila.
- **Nada de `pairplot`** sobre más de ~5.000 filas: el costo crece con el cuadrado del número de variables y de filas.

## 8. Segmentar

`hue=` (color por categoría) y facetas (`col=`, subplots por categoría) muestran si un patrón se mantiene o cambia entre grupos.

**La paradoja de Simpson:** una tendencia que aparece en los datos agregados se invierte (o desaparece) al segmentar por una tercera variable — típicamente porque los grupos no están balanceados en esa tercera variable.

```python
tasa_total = df.groupby("comuna")["riesgo"].mean()          # Penco parece mejor que Tomé
tasa_por_grupo = df.groupby(["comuna", "dependencia"])["riesgo"].mean().unstack()
                                                              # Penco es peor en cada dependencia
composicion = pd.crosstab(df["comuna"], df["dependencia"], normalize="index")
                                                              # el confusor: cómo se reparte la matrícula
```

La regla: cuando una conclusión se apoya en un total, revisar si se sostiene al segmentar por la variable que compone ese total de forma distinta en cada grupo (aquí, el tipo de dependencia).

## 9. Una figura que comunica

Checklist antes de poner una figura en el informe:

- [ ] **Título = el hallazgo**, no el nombre de la columna ("Penco es peor en las tres dependencias", no "tasa de riesgo por comuna")
- [ ] Ejes con **unidades** entre paréntesis
- [ ] Escala **declarada** si es logarítmica
- [ ] Barras de conteo o monto empiezan en cero (no cortar el eje para exagerar una diferencia)
- [ ] Un solo mensaje por figura
- [ ] Referencia a la **celda de origen** en la bitácora

```python
def guardar_figura(fig, nombre):
    Path("figs").mkdir(exist_ok=True)
    fig.savefig(f"figs/{nombre}", dpi=150, bbox_inches="tight")
```

## 10. Bitácora de EDA → Informe 3

Cinco columnas, una fila por hallazgo:

| Columna | Contenido |
|---|---|
| `hallazgo` | Frase con número: "El 12 % de los estudiantes retirados..." |
| `figura` | Ruta en `figs/` |
| `celda` | `"03-eda.ipynb, celda N"` |
| `pregunta` | Qué término de la pregunta de datos de la Clase 1 responde |
| `decision_o_hipotesis` | Qué se decide o qué hipótesis queda para probar en el modelo |

Esta tabla **es** la sección de resultados del Informe 3: cada párrafo del informe debería poder trazarse a una fila de la bitácora y de ahí a la celda que la produjo.

**Lo que viene:** Clase 8 — dashboards interactivos (Plotly, Panel, Streamlit) sobre esta misma bitácora. Clase 9 — selección de características e importancia de variables, ya con el modelo en el horizonte.
