# Guía de visualización avanzada y dashboards — Clase 8 (material para estudiantes)

**Para qué sirve:** referencia técnica para subir un nivel el EDA: intervalos y embudo para comparar grupos, series de tiempo, paneles y cartogramas para muchos grupos o territorio, y dashboards exploratorios. Acompaña al notebook `lab08-visualizacion-dashboards.ipynb`.

---

## 0. Las cuatro preguntas de la clase

El ciclo del EDA de la Clase 7 **no cambia**: pregunta → figura → observación con número → decisión o hipótesis. Hoy se agregan cuatro preguntas que hacerle a cada figura antes de escribir la observación:

| Pregunta | Qué revisar | Herramienta |
|---|---|---|
| **Certeza** | ¿La diferencia entre grupos es mayor que el ruido que da su tamaño? | Intervalo (§2), embudo (§3) |
| **Tiempo** | ¿Es un patrón que se repite (estacionalidad) o un cambio de fondo (tendencia)? ¿Hay huecos? | Una línea por año (§4), `reindex` y heatmap (§5) |
| **Grupos y territorio** | ¿El patrón es de todos o de algunos? ¿Tiene forma en el mapa? | Paneles con ejes compartidos (§6), cartograma (§7) |
| **Interactividad** | ¿Necesito mirar lo mismo para muchos grupos? | Función `panel(grupo)`, HTML de Plotly (§8) |

```python
# El ciclo, en la bitácora (5 columnas, igual que en la Clase 7)
{"hallazgo": "Lota (15,0 %, n = 1.100, IC 13,0–17,2 %) supera la tasa provincial de 12,2 %",
 "figura": "figs/embudo_comunas.png", "celda": "03-eda.ipynb, celda 14",
 "pregunta": "¿dónde intervenir primero?", "decision_o_hipotesis": "priorizar Lota y Tomé; Florida no se distingue"}
```

## 1. Por qué un ranking engaña

Una tasa `k / n` calculada sobre pocos casos se mueve mucho por azar: con n = 120, **un** estudiante más en riesgo sube la tasa 0,8 puntos. Por eso, en cualquier ranking de tasas, **los extremos (arriba y abajo) tienden a ser los grupos chicos**, aunque no tengan nada especial.

| Síntoma | Qué hacer |
|---|---|
| El primero y el último del ranking tienen n chico | Poner n en la etiqueta y el intervalo en la figura |
| Se compara la tasa de un grupo de 100 con la de uno de 5.000 | Embudo (§3) |
| Barras de tasa sin n | No sirve para decidir: no se sabe cuánto creerle a cada barra |

```python
tasa = df.groupby("grupo").agg(n=("id", "size"), k=("riesgo", "sum"))
tasa["tasa"] = tasa.k / tasa.n
tasa.sort_values("tasa")          # mirar la columna n junto a los extremos
```

## 2. Intervalos

| Qué se estima | Intervalo al 95 % | Cuándo |
|---|---|---|
| Proporción `k / n` | **Wilson** (abajo) | Siempre que se pueda; el de Wald `p ± 1,96·√(p(1−p)/n)` falla con n chico o p cerca de 0 o 1 |
| Promedio | `media ± 1,96 · desv / √n` | n ≥ 30 y sin outliers fuertes |
| Cualquier otra cosa (mediana, diferencia, cociente) | *Bootstrap* | Cuando no hay fórmula a mano |

**Wilson**, con $\hat p = k/n$ y $z = 1{,}96$:

$$\text{centro} = \frac{\hat p + \frac{z^2}{2n}}{1 + \frac{z^2}{n}} \qquad \text{margen} = \frac{z}{1 + \frac{z^2}{n}}\sqrt{\frac{\hat p(1-\hat p)}{n} + \frac{z^2}{4n^2}}$$

```python
def wilson(k, n, z=1.96):
    p = k / n
    centro = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    margen = z / (1 + z**2 / n) * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return centro - margen, centro + margen
```

Funciona con números o con columnas completas: `df["lo"], df["hi"] = wilson(df.k, df.n)`. No hace falta `statsmodels`.

**Promedio:**

```python
g = df.groupby("grupo").valor.agg(["mean", "std", "size"])
g["lo"] = g["mean"] - 1.96 * g["std"] / np.sqrt(g["size"])
g["hi"] = g["mean"] + 1.96 * g["std"] / np.sqrt(g["size"])
```

**Bootstrap** (remuestrear con reemplazo y mirar la dispersión del estadístico):

```python
rng = np.random.default_rng(2026)
x = df.loc[df.grupo == "A", "valor"].dropna().to_numpy()
boot = [np.median(rng.choice(x, size=len(x), replace=True)) for _ in range(2000)]
lo, hi = np.percentile(boot, [2.5, 97.5])
```

**Regla de n < 30:** con menos de ~30 observaciones por grupo, además del intervalo **muestren los puntos** (un `strip plot`: `ax.scatter(x_con_ruido, valores, alpha=0.5)`); una barra o una caja resume demasiado poco.

Dibujarlos: puntos horizontales con barras de error, ordenados.

```python
d = df1.sort_values("tasa"); y = np.arange(len(d))
ax.errorbar(d.tasa, y, xerr=[d.tasa - d.lo, d.hi - d.tasa], fmt="o", capsize=3)
ax.set_yticks(y, [f"{c} (n={n})" for c, n in zip(d.comuna, d.estudiantes)])
ax.axvline(p_global, linestyle="--")
```

`xerr` recibe **distancias** al punto (no los límites).

## 3. Gráfico de embudo

Pone cada grupo en un plano **tasa vs. tamaño** y dibuja, alrededor de la tasa global `p`, los límites dentro de los cuales caería un grupo de tamaño `n` solo por azar:

$$p \pm 1{,}96\sqrt{\frac{p(1-p)}{n}}$$

Los límites se abren para n chico y se cierran para n grande: por eso tiene forma de embudo.

| Cómo leerlo | Significa |
|---|---|
| Punto dentro del embudo | No se distingue de la tasa global (aunque esté arriba o abajo en el ranking) |
| Punto fuera, arriba | Tasa más alta de lo que el azar explica: candidato a mirar |
| Punto fuera, abajo | Tasa más baja de lo que el azar explica: ¿qué hacen distinto? |
| Eje X | Siempre **logarítmico** cuando los tamaños van de cientos a miles |

```python
n = np.logspace(2, 4, 200)                      # 100 a 10.000
se = np.sqrt(p_global * (1 - p_global) / n)
ax.scatter(df1.estudiantes, df1.tasa)
ax.axhline(p_global, color="gray")
ax.plot(n, p_global + 1.96 * se, "k--"); ax.plot(n, p_global - 1.96 * se, "k--")
ax.set_xscale("log")
fuera = df1[(df1.tasa - p_global).abs() > 1.96 * np.sqrt(p_global * (1 - p_global) / df1.estudiantes)]
```

**Falsos positivos esperados.** Con límites al 95 %, cada grupo tiene ~5 % de probabilidad de quedar fuera **por puro azar**. Con 12 grupos se esperan 12 × 0,05 ≈ **0,6** grupos fuera aunque no pase nada. Uno fuera, entonces, no es gran evidencia; dos o más fuera y del mismo lado (como Lota y Tomé en el lab) sí es una señal. Con muchos grupos (cientos de establecimientos), usar límites al 99,8 % (`z = 3`) para no perseguir ruido.

## 4. Series de tiempo

| Operación | Código |
|---|---|
| Texto → fecha | `df["fecha"] = pd.to_datetime(df.fecha)` (o `format="%Y-%m-%d"` si el formato es raro) |
| Fecha como índice | `s = df.set_index("fecha").valor` |
| Agregar por periodo | `s.resample("MS").mean()` (inicio de mes), `"W"` semanal, `"YS"` anual |
| Suavizar | `s.rolling(3).mean()` (media móvil de 3 periodos) |
| Por mes calendario | `df.groupby(df.fecha.dt.month).valor.mean()` |
| Mes × año | `df.pivot_table(index="mes", columns="anio", values="valor", aggfunc="mean")` |

**Estacionalidad vs. tendencia.** La estacionalidad es lo que **se repite cada año** en los mismos meses (la caída de julio). La tendencia es el **cambio de fondo** entre años. En una sola línea de 30 meses las dos se mezclan; con **una línea por año** sobre el eje de meses calendario se separan: la forma de la curva es la estacionalidad, la distancia entre curvas es la tendencia.

```python
yoy = df.pivot_table(index="mes", columns="anio", values="asistencia_pct", aggfunc="mean")
fig, ax = plt.subplots()
for anio in yoy.columns:
    ax.plot(yoy.index, yoy[anio], marker="o", label=str(anio))
ax.set_xticks(list(MESES), list(MESES.values())); ax.legend(title="año")
```

Para comparar años, comparar **el mismo mes** (julio 2025 vs. julio 2023), nunca julio contra marzo.

## 5. Nulos y huecos en el tiempo

| Problema | Cómo se ve | Qué hacer |
|---|---|---|
| Cero que es "sin reporte" | Caídas bruscas y aisladas en la serie; `(x == 0).sum()` > 0 donde 0 no es posible | Convertir a `NaN` antes de promediar |
| Mes ausente | La línea une dos meses no consecutivos sin avisar | `reindex` sobre un `date_range` completo; el hueco queda como `NaN` y la línea se corta |
| Anomalía puntual | Un valor muy lejos de lo normal **para ese mes** | Residuo contra el promedio del mismo mes; heatmap unidad × mes |

```python
df.loc[df.asistencia_pct == 0.0, "asistencia_pct"] = np.nan        # ceros disfrazados

s = df.groupby("fecha").asistencia_pct.mean()
completo = pd.date_range(s.index.min(), s.index.max(), freq="MS")
s = s.reindex(completo)                                             # meses ausentes → NaN
```

(Ojo: en datos escolares, enero y febrero **no** son huecos, son vacaciones. `reindex` sirve para detectar meses que deberían estar y no están.)

**Heatmap unidad × mes** como detector de anomalías: cada fila es una unidad (comuna, establecimiento), cada columna un mes; se pinta el **residuo** respecto de lo normal para esa unidad y ese mes calendario.

```python
g = df.groupby(["comuna", "dependencia", "anio", "mes"]).asistencia_pct.mean()
residuo = g - g.groupby(level=["comuna", "dependencia", "mes"]).transform("mean")
tabla = residuo.xs("Pública", level="dependencia").unstack(["anio", "mes"])   # comuna × (año, mes)
fig, ax = plt.subplots(figsize=(12, 4))
im = ax.imshow(tabla, aspect="auto", cmap="RdBu", vmin=-10, vmax=10)
ax.set_yticks(range(len(tabla)), tabla.index)
fig.colorbar(im, label="residuo (pp)")
residuo.idxmin()                                                    # la anomalía más fuerte
```

## 6. Muchos grupos

| Técnica | Cuándo |
|---|---|
| Paneles (*small multiples*) con ejes compartidos | 4 a ~20 grupos; se quiere ver la forma de cada uno |
| Destacar uno, el resto en gris | Se quiere mostrar cómo se ve **un** grupo contra todos |
| Heatmap grupo × tiempo (§5) | Más de ~20 grupos |
| Un solo gráfico con 12 colores | Nunca: la leyenda no se puede seguir |

**`sharey=True` siempre** que los paneles se comparen entre sí: si cada panel tiene su propio eje Y, una caída de 1 punto y una de 10 se ven iguales.

```python
fig, axs = plt.subplots(3, 4, figsize=(14, 8), sharex=True, sharey=True)
for ax, c in zip(axs.flat, sorted(df.comuna.unique())):
    s = df[df.comuna == c].groupby(["fecha", "dependencia"]).asistencia_pct.mean().unstack()
    for dep in s.columns:
        ax.plot(s.index, s[dep], lw=1, label=dep)
    ax.set_title(c, fontsize=9)
```

Con seaborn (opcional), lo mismo en una línea: `sns.relplot(df, x="fecha", y="asistencia_pct", hue="dependencia", col="comuna", col_wrap=4, kind="line", errorbar=None)`.

**Destacar uno:**

```python
for c, s in serie_por_comuna.items():
    ax.plot(s.index, s, color="lightgray", lw=0.8)
ax.plot(serie_por_comuna["Lota"], color="C3", lw=2, label="Lota")
```

## 7. Territorio

| Regla | Por qué |
|---|---|
| Mapear **tasas o cambios**, nunca conteos | Un mapa de conteos es un mapa de población: las comunas grandes salen siempre "peores" |
| Código de comuna como **texto con cero** (`"08101"`) | Si se lee como número queda `8101` y el `merge` con la capa oficial falla sin error |
| Un solo mapa de color con barra y unidades | Secuencial (un color) para magnitudes; divergente (dos colores) si hay un centro con sentido (0, la tasa global) |
| La forma del territorio distrae | Las comunas grandes y vacías dominan el mapa; un **cartograma de cuadrícula** da el mismo peso a cada una |

```python
df = pd.read_csv("datos.csv", dtype={"cod_comuna": str})         # conserva el cero
```

**Cartograma de cuadrícula.** Cada comuna es un cuadrado del mismo tamaño en una posición aproximada (`GRILLA` del Setup: columna, fila; fila 0 = norte). No es un mapa a escala: es un diagrama que conserva **vecindades**.

```python
GRILLA = {"Tomé": (0, 0), "Penco": (0, 1), "Florida": (2, 1),
          "Talcahuano": (0, 2), "Concepción": (1, 2), "Chiguayante": (2, 2), "Hualqui": (3, 2),
          "Hualpén": (0, 3), "San Pedro de la Paz": (1, 3), "Santa Juana": (3, 3),
          "Coronel": (1, 4), "Lota": (1, 5)}

from matplotlib.patches import Rectangle
cmap = plt.get_cmap("Reds_r"); norm = plt.Normalize(vmin=cambio.min(), vmax=0)
fig, ax = plt.subplots(figsize=(5, 7))
for comuna, (col, fila) in GRILLA.items():
    ax.add_patch(Rectangle((col, fila), 0.95, 0.95, color=cmap(norm(cambio[comuna]))))
    ax.text(col + 0.475, fila + 0.475, f"{comuna}\n{cambio[comuna]:+.1f} pp", ha="center", va="center", fontsize=7)
ax.set_xlim(0, 4); ax.set_ylim(6, 0)          # Y al revés: norte arriba
ax.set_aspect("equal"); ax.axis("off")
fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, label="cambio (pp)")
```

**Referencia (solo para proyectos territoriales; no se ejecuta en el lab):** un mapa coroplético real necesita GeoPandas y la capa comunal oficial (por ejemplo, la división político-administrativa que publica la Biblioteca del Congreso Nacional o el INE).

```python
import geopandas as gpd                                    # pip install geopandas
comunas = gpd.read_file("comunas.shp")                     # capa oficial, descargada aparte
comunas["cod_comuna"] = comunas["cod_comuna"].astype(str).str.zfill(5)
mapa = comunas.merge(tasas, on="cod_comuna", how="left")   # tasas: cod_comuna (texto) + tasa
mapa.plot(column="tasa", cmap="Reds", legend=True, missing_kwds={"color": "lightgray"})
```

Revisen después del `merge` cuántas comunas quedaron sin dato (`mapa.tasa.isna().sum()`): si son muchas, el problema es el código.

## 8. Dashboard exploratorio

Anatomía de cualquier dashboard: **filtros → datos filtrados → vistas**. El filtro (una comuna, un año) se aplica una vez y todas las vistas se recalculan con los mismos datos.

| Nivel | Qué es | Necesita | Cuándo |
|---|---|---|---|
| 1. Función Matplotlib | `panel(df, grupo)` devuelve una figura con varias vistas | Nada nuevo | Siempre: es la base de los otros dos |
| 2. HTML de Plotly | Figura interactiva con menú; un archivo que se abre en el navegador | `plotly` | Compartir la exploración sin servidor |
| 3. App (Streamlit, Panel) | Página web con controles de verdad | Un **servidor** corriendo | Clase 15 (dashboards para comunicar resultados) |

**Nivel 1:**

```python
def panel_comuna(df, comuna):
    d = df[df.comuna == comuna]                                       # filtro
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(15, 4))
    d.groupby(["fecha", "dependencia"]).asistencia_pct.mean().unstack().plot(ax=a1)
    d.groupby("mes").asistencia_pct.mean().plot(ax=a2, marker="o")
    a3.axis("off"); a3.text(0.05, 0.8, comuna, fontsize=16, transform=a3.transAxes)
    return fig
```

**Nivel 2:** todas las trazas se crean de una vez; el menú solo cambia cuáles son visibles.

```python
import plotly.graph_objects as go
opciones = ["Todas"] + sorted(df.comuna.unique())
fig = go.Figure()
for k, op in enumerate(opciones):
    d = df if op == "Todas" else df[df.comuna == op]
    s = d.groupby(["fecha", "dependencia"]).asistencia_pct.mean().unstack()
    for dep in s.columns:
        fig.add_trace(go.Scatter(x=s.index, y=s[dep], name=dep, visible=(k == 0)))
botones = [dict(label=op, method="update", args=[{"visible": [i // 3 == k for i in range(3 * len(opciones))]}])
           for k, op in enumerate(opciones)]
fig.update_layout(updatemenus=[dict(buttons=botones)], yaxis_title="asistencia (%)")
fig.write_html("figs/dashboard.html", include_plotlyjs=True)     # autocontenido: sin internet
```

`include_plotlyjs=True` mete la librería completa en el archivo (~3–5 MB): funciona sin internet. Con `"cdn"` pesa unos KB pero necesita conexión.

**Nivel 3 (referencia; no se ejecuta en el lab).** Streamlit **exige un servidor**: se corre con `streamlit run app.py` y se abre en `localhost:8501`.

```python
# app.py
import pandas as pd
import streamlit as st
df = pd.read_csv("data/processed/asistencia.csv", parse_dates=["fecha"])
comuna = st.selectbox("Comuna", sorted(df.comuna.unique()))
d = df[df.comuna == comuna]
st.metric("Asistencia 2025", f"{d[d.anio == 2025].asistencia_pct.mean():.1f} %")
st.line_chart(d.pivot_table(index="fecha", columns="dependencia", values="asistencia_pct"))
st.bar_chart(d.groupby("mes").asistencia_pct.mean())
```

El dashboard es para **explorar**: no reemplaza a la bitácora ni a las figuras del informe.

## 9. Una figura que comunica (repaso)

El checklist de la Clase 7 sigue igual, más una regla nueva:

- [ ] **Título = el hallazgo**, no el nombre de la columna
- [ ] Ejes con **unidades** entre paréntesis
- [ ] Escala **declarada** si es logarítmica
- [ ] Barras de conteo o monto empiezan en cero
- [ ] Un solo mensaje por figura
- [ ] Referencia a la **celda de origen** en la bitácora
- [ ] **Nuevo:** si compara grupos, **el intervalo y el n van en la figura o en el pie** ("barras: IC de Wilson al 95 %; n entre paréntesis")

```python
ax.set_xlabel("estudiantes en riesgo (%) · intervalo de Wilson 95 %")
ax.set_yticks(y, [f"{c} (n={n})" for c, n in zip(d.comuna, d.estudiantes)])
guardar_figura(fig, "riesgo_por_comuna.png")
```

`guardar_figura(fig, nombre)` (Setup del notebook) crea `figs/` si no existe y guarda con `dpi=150, bbox_inches="tight"`:

```python
def guardar_figura(fig, nombre):
    FIGS.mkdir(exist_ok=True)
    fig.savefig(FIGS / nombre, dpi=150, bbox_inches="tight")
```

## 10. Bitácora de EDA → Informe 3

La tabla sigue con sus **5 columnas**:

| Columna | Contenido |
|---|---|
| `hallazgo` | Frase con número; **si compara grupos, con n e intervalo** |
| `figura` | Ruta en `figs/` |
| `celda` | `"03-eda.ipynb, celda N"` |
| `pregunta` | Qué término de la pregunta de datos de la Clase 1 responde |
| `decision_o_hipotesis` | Qué se decide o qué hipótesis queda para probar en el modelo |

Cómo se enriquece hoy (al menos una de las 3 filas nuevas):

| Tipo | Ejemplo de `hallazgo` |
|---|---|
| n e intervalo | "Lota: 15,0 % en riesgo (n = 1.100; IC 95 % 13,0–17,2 %), sobre la tasa provincial de 12,2 %" |
| Patrón en el tiempo | "La asistencia cae ~5 pp de junio a julio los tres años; el promedio anual baja 1 pp entre 2023 y 2025" |
| Segmentación por grupo o territorio | "En establecimientos públicos, Lota (−6,4 pp) y Coronel (−5,1 pp) caen el triple que el resto (~−2 pp)" |

**Lo que viene:** Clase 9 — selección de características e importancia de variables. Traigan una **lista corta de variables candidatas**: las que su EDA muestra relacionadas con la variable objetivo, con una línea por variable que diga por qué (qué fila de la bitácora lo respalda).
