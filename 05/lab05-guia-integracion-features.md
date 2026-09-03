# Guía de integración de fuentes y creación de características — Clase 5 (material para estudiantes)

**Para qué sirve:** referencia técnica de las cuatro operaciones de integración (apilar, cruzar, enriquecer, agregar), de las trampas de las llaves en datos chilenos, y de los tipos de característica que se justifican desde la pregunta de datos. Acompaña al notebook `lab05-integracion-features.ipynb` y es la base de la sección de integración del Informe 2.

---

## 0. La regla de oro

**Explorar fue diagnosticar. Ahora se corrige — en código, sobre una copia, y cada decisión con su conteo.**

```
data/raw/          ← no se toca (Clase 2)
notebooks/02-preprocesamiento.ipynb
data/processed/    ← lo que produce el notebook
```

Nada de lo que sigue se hace editando un CSV a mano. Si una corrección no está en una celda, no existe.

## 1. Apilar periodos (`pd.concat`)

Es el caso de "misma fuente, otro año". Parece trivial y no lo es: los portales cambian de esquema entre versiones.

| Trampa | Síntoma | Solución |
|---|---|---|
| Columnas renombradas entre años | El `concat` produce columnas duplicadas con NaN (`toneladas` y `ton`) | `.rename(columns={...})` antes de concatenar, hacia un esquema canónico |
| Columnas que desaparecen | NaN en un periodo completo | Se acepta y **se documenta** ("2024 no trae coordenadas: 96 filas NaN"); no se inventa |
| Llave con tipo distinto por archivo | `8101` (int) en un año, `"08101"` (str) en otro: después el merge no encuentra nada | `dtype=str` al leer + `.str.zfill(5)` |
| No saber de qué archivo salió cada fila | Imposible auditar | Columna `origen` antes de concatenar |

```python
CANONICAS = list(pd.read_csv("emisiones_2022.csv", nrows=0).columns)
partes = []
for anio in (2022, 2023, 2024):
    d = pd.read_csv(f"emisiones_{anio}.csv", dtype={"id_comuna": str, "codigo_comuna": str})
    d = d.rename(columns={"codigo_comuna": "id_comuna", "ton": "toneladas"})
    d["origen"] = anio
    partes.append(d)
df = pd.concat(partes, ignore_index=True)[CANONICAS + ["origen"]]
df["id_comuna"] = df["id_comuna"].str.zfill(5)
```

**Verificación mínima:** filas del resultado = suma de filas de las partes; una suma de control (toneladas, casos, montos) igual a la suma de las partes; `df.groupby("origen").size()` con lo esperado.

## 2. La llave: por qué el merge "no encuentra nada"

Un `merge` compara valores **exactamente**. `"Tomé"` ≠ `"TOME"` ≠ `"Tome "`. Y `8101` (número) ≠ `"08101"` (texto).

Trampas frecuentes en fuentes chilenas:

| Cómo viene | Qué hacer |
|---|---|
| Código de comuna con y sin cero (`08101` / `8101`), RBD, códigos CIE-10 | Leer como texto (`dtype=str`) y rellenar (`.str.zfill(n)`) |
| Nombres con tildes, mayúsculas, espacios dobles o al final | Llave auxiliar normalizada en **ambas** tablas (función de abajo) |
| La misma entidad con dos identificadores (nombre en INE, código en RETC) | Tabla de homologación oficial: código único territorial (CUT) para comunas, RBD para establecimientos |
| Códigos que cambian con el tiempo (comunas nuevas, regiones divididas en 2018, RBD que cierran) | Documentar la versión de la tabla de referencia y el año al que corresponde |
| Nulos disfrazados en la llave (`" "`, `"S/I"`, `"-"`) | Detectarlos primero (Clase 3); una llave vacía no cruza con nada |

```python
import unicodedata

def normalizar(s: str) -> str:
    s = " ".join(str(s).split()).upper()                       # espacios sobrantes + mayúsculas
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()   # sin tildes

permisos["llave"] = permisos["Glosa Comuna"].map(normalizar)
cut["llave"] = cut["nombre_comuna"].map(normalizar)
```

Se normaliza una **columna auxiliar**; la original se conserva tal cual (es evidencia).

## 3. Cruzar (`pd.merge`) y saber qué se perdió

```python
res = a.merge(b, on="llave", how="left", validate="many_to_one", indicator=True)
res["_merge"].value_counts()           # both / left_only / right_only
huerfanas_a = a[~a["llave"].isin(b["llave"])]    # anti-join: en a pero no en b
huerfanas_b = b[~b["llave"].isin(a["llave"])]
```

| Parámetro | Para qué | Cuándo usarlo |
|---|---|---|
| `how="inner"` | Solo lo que está en ambas | Cuando una fila sin contraparte no sirve para la pregunta |
| `how="left"` | Todo lo de la izquierda, NaN donde no hubo match | Cuando la tabla izquierda es la unidad de análisis y la derecha enriquece |
| `how="outer"` | Todo de ambas | Solo para **diagnosticar** qué no cruza; rara vez es el resultado final |
| `indicator=True` | Columna `_merge` que dice de dónde salió cada fila | Siempre, al menos la primera vez |
| `validate="one_to_one"` / `"many_to_one"` | Falla si la cardinalidad no es la declarada | Siempre. Convierte el fan-out silencioso en una excepción |

**Dos NaN distintos.** Un NaN que ya venía en la fuente ("no se registró el dato") y un NaN que apareció con el join ("esta comuna no está en la otra tabla") tienen causas distintas y se documentan distinto. `indicator` los separa.

## 4. Granularidad y cardinalidad: el error que no lanza excepción

La pregunta que evita el desastre: **¿qué es una fila en cada tabla?** (la unidad de análisis de la Clase 1).

- Tabla A: una fila = comuna-año-contaminante-fuente (288 filas).
- Tabla B: una fila = comuna-año-tipo de vehículo (108 filas).
- `A.merge(B, on="id_comuna")` → cada fila de A se pega con **todas** las de B de su comuna: 2.592 filas, toneladas multiplicadas por 9, y ningún error.

Regla: **agregar cada lado a la granularidad de la pregunta antes de unir**, y unir con `validate`.

```python
em_ca = em.groupby(["id_comuna", "anio"], as_index=False)["toneladas"].sum()
pe["vehiculos"] = pe["Bencina"] + pe["Diesel"] + pe["Electrico"]
pe_ca = pe.groupby(["id_comuna", "anio"], as_index=False).agg(vehiculos=("vehiculos", "sum"),
                                                              diesel=("Diesel", "sum"))
df = em_ca.merge(pe_ca, on=["id_comuna", "anio"], how="inner", validate="one_to_one")
```

Cuando la granularidad de las dos fuentes es distinta por naturaleza (estudiante vs. establecimiento; paciente vs. comuna), el join es 1:N: la tabla gruesa **enriquece** a la fina (`many_to_one`), nunca al revés, y las columnas del lado grueso se repiten en cada fila fina — eso está bien y se dice.

## 5. Verificación post-integración (lo que se escribe en el informe)

Cinco conteos, siempre:

1. Filas antes y después en cada lado (`288 → 36`, `108 → 36`).
2. Una **suma de control** que se conserva: toneladas, casos, matriculados, montos.
3. Sin duplicados de llave en el resultado: `df.duplicated(subset=llave).sum() == 0`.
4. Nulos introducidos por el join, contados y explicados.
5. Al apilar: columnas alineadas, `origen` presente, llave con un solo tipo.

Un párrafo como *"emisiones agregadas de 288 a 36 filas (comuna-año); permisos de 108 a 36; cruce 1:1 sin pérdida (36/36); suma de toneladas conservada"* vale más que cualquier descripción en prosa del procedimiento.

## 6. Creación de características

Una característica nueva **se justifica desde la pregunta de datos** (unidad de análisis, variable objetivo, decisión que alimenta), no porque "podría servir".

| Tipo | Ejemplo | Qué responde | pandas |
|---|---|---|---|
| Razón / proporción | emisiones por vehículo; casos por 100.000 hab.; reprobados / matriculados | Composición o intensidad, no tamaño | `a / b` |
| Temporal | variación respecto del año anterior; antigüedad; mes de notificación | Tendencia, estacionalidad | `groupby(...).shift(1)`, `dt.month` |
| Agregada por grupo | promedio del establecimiento; total comunal; % de la región | Contexto de la unidad | `groupby(...).transform("mean")` |
| Indicador por umbral | asistencia < 85 %; comuna sobre la mediana | La definición operacional hecha columna | `df["x"] > umbral` |
| Derivada de fecha o código | año desde una fecha; categoría desde un código; región desde el CUT | Nivel de agregación útil | `dt.year`, `.str[:2]`, `map` |

Tres reglas:

1. **Un umbral es una decisión.** Se escribe cuál, por qué ese, y cuántas filas quedan de cada lado. "Mayor que la mediana" es tan defendible como "< 85 %" si se explica.
2. **Sin información del futuro ni de la variable objetivo.** Una feature calculada con el mismo dato que se quiere predecir (o con datos posteriores al momento de la decisión) es *leakage*: el modelo del Informe 4 se vería perfecto y no serviría.
3. **3 a 5 bien justificadas** valen más que 30 "por si acaso". Selección y PCA ya los vieron en Machine Learning; aquí el criterio es la pregunta.

```python
df = df.sort_values(["id_comuna", "anio"]).reset_index(drop=True)
df["ton_por_vehiculo"] = df["toneladas"] / df["vehiculos"]
df["pct_diesel"] = df["diesel"] / df["vehiculos"]
anterior = df.groupby("id_comuna")["toneladas"].shift(1)
df["variacion_ton"] = (df["toneladas"] - anterior) / anterior          # NaN en el primer año: correcto
df["alta_emision"] = df["ton_por_vehiculo"] > df["ton_por_vehiculo"].median()
```

## 7. Lo que ya vieron en Machine Learning (repaso aplicado, no clase nueva)

Nulos e imputación (`SimpleImputer`, `KNNImputer`), outliers (IQR, z-score), escalado (`StandardScaler`, `MinMaxScaler`, `RobustScaler`) y codificación (`OneHotEncoder`, `OrdinalEncoder`) se vieron en ML Clase 3; selección y extracción (filtros, PCA) en ML Clase 4. En el Informe 2 se aplican **a su dataset**, y lo que se evalúa es:

- **la decisión** (imputar con la mediana, eliminar, marcar) y **la alternativa descartada**;
- **el conteo** (cuántas filas o celdas afectó);
- **el momento**: escalar y codificar se hace *después* de separar entrenamiento y prueba (Informe 4), y con `fit` solo en entrenamiento. En el Informe 2 se deja decidido y justificado qué columnas se escalan y cómo; no hace falta ejecutarlo todavía.

## 8. El registro de decisiones (la tabla que sostiene el Informe 2)

| problema | evidencia | decisión | filas afectadas | justificación |
|---|---|---|---|---|
| 10.094 `id_comuna` con un espacio en blanco | `01-obtencion.ipynb`, celda 9 | convertir a NaN y recuperar desde el nombre de comuna | 10.094 | el nombre está completo en el 100 % de esas filas |
| 2024 sin coordenadas | `02-preprocesamiento.ipynb`, celda 4 | apilar con NaN; no usar lat/lon | 96 | las coordenadas no participan de la pregunta |
| duplicados exactos | `02-preprocesamiento.ipynb`, celda 7 | eliminar | 86.305 (24,1 %) | filas idénticas en todas las columnas, incluida la fecha |

Sin conteo no hay decisión: hay opinión. Y cada fila de esta tabla apunta a una celda que cualquiera puede ejecutar.
