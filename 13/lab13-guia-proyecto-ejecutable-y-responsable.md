# Guía de proyecto ejecutable y responsable — Clase 13 (material para estudiantes)

**Para qué sirve:** referencia técnica para convertir un análisis en un proyecto que otra persona puede ejecutar (estructura, scripts, pruebas, requisitos) y para revisar si debería existir con los datos que usa (datos personales, reidentificación, sesgo, ficha del modelo). Acompaña al notebook `lab13-proyecto-ejecutable-y-responsable.ipynb` y es la base de las secciones de **reproducibilidad** y de **ética, privacidad y sesgo** del Informe 5.

Todas las cifras de ejemplo son del mini-caso sintético del lab: 6.000 solicitudes de microcrédito de una institución ficticia, 19,7 % de incumplimiento. **Ninguna persona, nombre ni correo es real.**

---

## 0. Las dos preguntas de la clase

| Pregunta | Qué revisa | Secciones |
|---|---|---|
| **¿Lo puede ejecutar otra persona?** | Estructura, scripts con parámetros, semillas y versiones, datos documentados, pruebas, un comando, README | §1 a §7 |
| **¿Debería existir con estos datos?** | Datos personales, principios y derechos, reidentificación, sesgo por subgrupo, ficha del modelo, uso de IA y seguridad | §8 a §12 |

Herramientas del Setup del notebook que se usan en toda la guía:

| Nombre | Qué hace |
|---|---|
| `crear_proyecto_ejemplo()` | Crea (o recrea) `proyecto_ejemplo/` con `data/raw/`, `src/`, `tests/`, `models/` y un `requirements.txt` de partida |
| `ejecutar(args, cwd)` | Corre un comando con `subprocess` desde la raíz del proyecto, como en la terminal |
| `pipeline_generico(num, cat)` | Pipeline del caso: escalado + one-hot + regresión logística |
| `partir(df)` | Partición 70/30 estratificada con `SEED = 2026`: `X_tr, X_te, y_tr, y_te, sexo_te` |
| `auc_modelo(df, num, cat)` | ROC-AUC en test del pipeline con esas columnas |
| `intervalo_wilson(k, n)` | Intervalo de confianza del 95 % para una tasa (§11) |
| `pipeline_ref` | Pipeline de referencia ya ajustado (no usa `sexo`) |

## 1. Estructura de un repositorio

Una estructura que cualquiera reconoce:

```
proyecto/
├── README.md            qué hace, cómo se instala y cómo se ejecuta
├── requirements.txt     paquetes con versión
├── run_all.py           el comando único
├── data/
│   ├── raw/             datos originales: no se modifican nunca
│   └── processed/       datos derivados: se regeneran con el código
├── notebooks/           exploración y narración (01-..., 02-..., en orden)
├── src/                 funciones reutilizables (__init__.py, datos.py, modelo.py, entrenar.py)
├── models/              modelos y métricas generados (no se versionan)
├── reports/             figuras y tablas finales
└── tests/               pruebas (__init__.py, test_pipeline.py)
```

**¿Script o notebook?**

| Va a un script (`src/`) | Se queda en un notebook |
|---|---|
| Lo que se repite: cargar, validar, limpiar, entrenar, evaluar | La exploración y las preguntas |
| Lo que tiene que dar siempre lo mismo | Los gráficos que cuentan la historia |
| Lo que otra persona tiene que poder ejecutar sin abrir Jupyter | La interpretación de los resultados |
| Lo que se prueba con `tests/` | — |

Regla práctica: si copiaron la misma celda en dos notebooks, esa celda es una función de `src/`. El notebook la importa (`from src.datos import cargar_datos`) en vez de repetirla.

## 2. Parámetros fuera del código: `argparse`, `pathlib` y `python -m`

Un script no debería tener que editarse para cambiar la ruta de los datos, la carpeta de salida o la semilla: eso se le pasa desde la terminal.

```python
import argparse
from pathlib import Path

ap = argparse.ArgumentParser(description="Entrena el modelo")
ap.add_argument("--datos", required=True, type=Path)
ap.add_argument("--salida", required=True, type=Path)
ap.add_argument("--semilla", type=int, default=2026)
a = ap.parse_args()
```

```bash
python -m src.entrenar --datos data/raw/solicitudes_microcredito.csv --salida models/ --semilla 2026
python -m src.entrenar --help        # argparse genera la ayuda solo
```

**`pathlib` en vez de rutas escritas como texto.** `Path("data") / "raw" / "archivo.csv"` funciona igual en Windows, macOS y Linux. Una ruta como `C:/Users/alguien/Desktop/archivo.csv` solo existe en un computador. Las rutas van **relativas a la raíz del proyecto**.

| Evitar | Usar |
|---|---|
| `"C:\\Users\\yo\\datos.csv"`, `"/Users/yo/datos.csv"` | `Path("data/raw/datos.csv")`, recibida por `--datos` |
| `os.path.join("data", "raw")` | `Path("data") / "raw"` |
| `open(ruta)` sin encoding | `ruta.read_text(encoding="utf-8")`, `to_csv(..., encoding="utf-8")` |
| `os.makedirs(..., exist_ok=True)` | `ruta.mkdir(parents=True, exist_ok=True)` |

**`python -m paquete.modulo` y `src/__init__.py`.** `python -m src.entrenar` ejecuta `src/entrenar.py` **como parte del paquete `src`** y agrega la carpeta actual al camino de importación, así que `from src.datos import ...` funciona. Para eso hay que ejecutarlo **desde la raíz del proyecto**, y `src/` debe tener un `__init__.py` (puede estar vacío). Con `python src/entrenar.py`, en cambio, Python busca los módulos dentro de `src/` y `from src.datos import ...` falla.

El bloque final hace que el archivo sirva tanto para importarlo como para ejecutarlo:

```python
if __name__ == "__main__":
    main()
```

## 3. Semillas, versiones y entorno

**Semillas.** Todo lo que tiene azar recibe la semilla: la partición (`train_test_split(..., random_state=semilla)`), los modelos (`random_state=semilla`), la generación de datos (`np.random.default_rng(semilla)`). En el lab, la misma celda sin semilla dio tres ROC-AUC distintos. Con semilla, el script da siempre 0,802. La semilla se declara **una vez** y se pasa como parámetro, no se repite como número suelto.

**Versiones.** Dos formas de escribir `requirements.txt`:

| | `pip freeze > requirements.txt` | Escrito a mano con `>=` |
|---|---|---|
| Qué guarda | Todo lo instalado en el entorno, con `==` exacto | Solo lo que el proyecto importa, con versión mínima |
| Ventaja | Reproduce el entorno exacto | Corto, legible, instala en otros sistemas |
| Riesgo | Arrastra paquetes que no se usan y versiones que no existen en otro sistema operativo | Una versión futura puede cambiar resultados |
| Cuándo | Para archivar el entorno exacto de una entrega | Para un repositorio que otra persona va a instalar |

Una práctica razonable: `requirements.txt` a mano con `>=` (todo lo que importan `src/`, `tests/` y los notebooks) y, si quieren dejar constancia exacta, un `requirements-lock.txt` generado con `pip freeze`. Declaren también la versión de Python en el README.

```text
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
matplotlib>=3.7
pytest>=7
```

**Entorno virtual.** Cada proyecto con sus paquetes, sin mezclar con los de otros:

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate      macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

`.venv/` va en `.gitignore`.

## 4. Los datos: qué se sube y qué se documenta

| Se sube al repositorio | No se sube |
|---|---|
| Datos pequeños, públicos y sin datos personales | Archivos grandes (como referencia, más de unos 50 MB) |
| Una **muestra pequeña** para las pruebas | Datos con información personal o sensible |
| `data/README.md` con la documentación | Datos con licencia que no permite redistribuirlos |
| El código que genera `data/processed/` | `data/processed/` y `models/` (se regeneran) |

`data/README.md` mínimo: **fuente** (institución, enlace), **fecha de descarga**, **licencia o condiciones de uso**, **cómo obtenerlos** (pasos exactos o script de descarga), **diccionario de columnas** y **qué datos personales contienen** (§8).

```text
# .gitignore
data/raw/*
!data/raw/README.md
data/processed/
models/
.venv/
__pycache__/
```

Si los datos no se pueden subir, el README dice exactamente cómo conseguirlos y dónde dejarlos. Una **muestra pequeña** sintética o anonimizada permite que las pruebas corran en un clon vacío.

## 5. Fallar temprano y `logging` en vez de `print`

Un script que recibe datos malos debería **detenerse al inicio con un mensaje claro**, no entregar un número equivocado al final.

```python
def validar_columnas(df):
    """Comprueba columnas esperadas, rangos básicos y objetivo binario."""
    for col in NUMERICAS + CATEGORICAS + [OBJETIVO]:
        if col not in df.columns:
            raise ValueError(f"Falta la columna '{col}'")
    if not df[OBJETIVO].isin([0, 1]).all():
        raise ValueError(f"'{OBJETIVO}' debe ser 0/1")
    if (df["edad"] < 18).any():
        raise ValueError("Hay edades menores de 18")
    return df
```

| Qué validar | Ejemplo |
|---|---|
| Que el archivo exista | `FileNotFoundError(f"No existe el archivo de datos: {ruta}")` |
| Columnas esperadas | `ValueError("Falta la columna 'ocupacion'")` |
| Tipos y valores posibles | objetivo 0/1, categorías conocidas |
| Rangos | edades ≥ 18, montos positivos |
| Tamaño mínimo | al menos *n* filas después de filtrar |

Un error con mensaje claro termina el script con **código de salida distinto de 0**: así `run_all.py` sabe que el paso falló.

**`logging`** registra qué pasó, con hora y nivel, y se puede silenciar o enviar a un archivo sin tocar el código:

```python
import logging
log = logging.getLogger(__name__)          # en cada módulo
log.info("Datos cargados: %d filas x %d columnas", *df.shape)

logging.basicConfig(level=logging.INFO,    # una sola vez, en el script principal
                    format="%(asctime)s %(levelname)s %(message)s")
```

Niveles: `debug` (detalle para depurar) · `info` (lo normal) · `warning` (algo raro, pero sigue) · `error` (falló algo). `print` queda para la salida que el usuario pidió.

## 6. README, docstrings y nombres

**Plantilla de README (nueve secciones):**

| Sección | Qué lleva |
|---|---|
| **Qué hace** | Dos líneas: la pregunta y el resultado |
| **Requisitos** | Versión de Python y `requirements.txt` |
| **Instalación** | Comandos exactos (`venv`, `pip install -r requirements.txt`) |
| **Cómo ejecutar** | Comandos exactos, en orden (`python run_all.py`) |
| **Estructura** | Qué hay en cada carpeta |
| **Datos** | Fuente, fecha, licencia, cómo obtenerlos, datos personales (§4) |
| **Resultados principales** | Cada cifra con el archivo o la celda que la produce |
| **Limitaciones** | Lo que el análisis no permite afirmar, y lo que no se alcanzó a corregir |
| **Uso de IA** | Qué herramienta, para qué parte y cómo se verificó |

**Docstrings.** Cada función pública dice qué hace, qué recibe y qué devuelve o cuándo falla. Una línea basta si la función es simple:

```python
def calcular_tasa_incumplimiento(solicitudes, umbral):
    """Proporción de solicitudes con probabilidad de incumplimiento >= umbral.

    solicitudes: DataFrame con la columna 'prob'. Devuelve un float entre 0 y 1.
    """
```

**Nombres.** Que digan lo que son: `calcular_tasa_incumplimiento(solicitudes, umbral)` y no `f(d, x)`; `tam_grupo` y no `aux2`. Un **comentario** explica el **porqué** (`# test_size=0.3 para tener al menos 100 incumplimientos por sexo en test`), no el **qué** (`# divide los datos`).

## 7. Pruebas mínimas y el comando único

Una prueba es una función que **falla si algo se rompe**. Tres pruebas mínimas de un pipeline:

| Prueba | Qué protege |
|---|---|
| La salida del preprocesamiento no tiene nulos | Que el escalado o la codificación no se rompan con datos nuevos |
| Una predicción por fila | Que el pipeline no pierda ni duplique filas |
| Supera a un baseline (`DummyClassifier`) | Que el modelo aprenda algo: si no le gana a lo trivial, algo cambió |

```python
def test_supera_al_baseline():
    Xtr, Xte, ytr, yte = _partir()
    pipe = construir_pipeline(2026).fit(Xtr, ytr)
    base = DummyClassifier(strategy="prior").fit(Xtr, ytr)
    auc_m = roc_auc_score(yte, pipe.predict_proba(Xte)[:, 1])
    auc_b = roc_auc_score(yte, base.predict_proba(Xte)[:, 1])
    assert auc_m > auc_b + 0.10
```

**Con `pytest`:** `pytest` busca los archivos `test_*.py` y ejecuta cada función `test_…`. Se ejecuta desde la raíz con

```bash
python -m pytest -q tests
```

y **no** con `pytest` a secas: `python -m` agrega la carpeta actual al camino de importación, y así `from src.datos import ...` funciona dentro de las pruebas.

**Sin `pytest`:** las mismas funciones con `assert`, llamadas desde un bloque final (requiere `tests/__init__.py`):

```python
if __name__ == "__main__":   # python -m tests.test_pipeline
    for prueba in (test_preprocesamiento_sin_nulos, test_una_prediccion_por_fila, test_supera_al_baseline):
        prueba()
        print("OK", prueba.__name__)
```

**El comando único.** Todo el proceso, en orden, con un solo comando que termina con error si algún paso falla:

```python
# run_all.py
import subprocess, sys

PASOS = [
    [sys.executable, "-m", "src.entrenar", "--datos", "data/raw/solicitudes_microcredito.csv",
     "--salida", "models/", "--semilla", "2026"],
    [sys.executable, "-m", "pytest", "-q", "tests"],
]
for paso in PASOS:
    if subprocess.run(paso).returncode != 0:
        sys.exit("Falló el paso anterior")
```

`sys.executable` es el Python que está corriendo (el del entorno virtual); escribir `"python"` puede llamar a otro. Equivalentes en otros sistemas (no funcionan en Windows sin herramientas extra):

```make
# Makefile  →  make all
all:
	python -m src.entrenar --datos data/raw/solicitudes_microcredito.csv --salida models/ --semilla 2026
	python -m pytest -q tests
```

```bash
# run_all.sh  →  bash run_all.sh
set -e
python -m src.entrenar --datos data/raw/solicitudes_microcredito.csv --salida models/ --semilla 2026
python -m pytest -q tests
```

**La prueba del clon vacío.** Clonar el repositorio en una carpeta nueva, crear el entorno, seguir el README al pie de la letra y ejecutar todo. Si algo falla, falta algo en el repositorio o en el README.

## 8. Datos personales

> **Resumen en términos generales, a confirmar contra el texto oficial de la Ley 21.719 y el sitio de la Biblioteca del Congreso Nacional (leychile.cl). La ley entra en vigor el 1 de diciembre de 2026. Esta guía no es asesoría legal.**

| Concepto | En términos generales |
|---|---|
| **Dato personal** | Información sobre una persona natural **identificada o identificable** |
| **Identificable** | Se puede determinar quién es, directa o indirectamente, **incluso combinando datos** que por separado no la identifican (comuna + edad + sexo + fecha) |
| **Dato sensible** | Categorías que la ley protege con más fuerza (por ejemplo, salud, origen étnico, opiniones políticas, creencias, vida y orientación sexual, datos biométricos). Revisen la lista exacta en el texto oficial |
| **Datos de niñas, niños y adolescentes** | Tienen protección reforzada: se tratan atendiendo a su interés superior |

**Tres planos para revisar un uso de datos:**

| Plano | Pregunta | Ejemplo en el caso |
|---|---|---|
| **Legal** | ¿Está permitido? ¿Con qué base y para qué fin? | ¿Los datos de las solicitudes se pueden usar para entrenar un modelo de riesgo? |
| **Ético** | ¿Es correcto, aunque esté permitido? ¿A quién puede perjudicar? | ¿Es aceptable negar más créditos a un grupo por variables que se le asocian? |
| **Técnico** | ¿Qué se hace para proteger a las personas? | Quitar identificadores, generalizar, medir el riesgo de reidentificación y el sesgo |

En el lab, las columnas se clasifican en: **identificador directo** (identifica por sí solo: nombre, correo, número de solicitud) · **cuasi-identificador** (identifica al combinarse: comuna, edad, sexo, fecha) · **financiera** (situación económica de la persona: se trata con cuidado reforzado, sin afirmar aquí su categoría legal) · **neutra** · **objetivo**.

## 9. Principios y derechos

> **Mismo aviso de §8: resumen general, a confirmar contra el texto oficial; no es asesoría legal.**

**Principios** (en términos generales):

| Principio | Qué pide | Pregunta práctica |
|---|---|---|
| **Licitud** | Tratar datos con una base válida (consentimiento, ley, contrato u otra que la ley reconozca) | ¿Con qué base tenemos estos datos? |
| **Finalidad** | Usarlos para fines determinados y no para otros incompatibles | ¿Para qué se recolectaron y para qué los usamos? |
| **Proporcionalidad** | Usar solo los datos necesarios para ese fin | ¿Necesitamos el nombre, el correo o la fecha exacta? |
| **Calidad** | Que sean exactos y estén actualizados | ¿Están bien registrados? ¿Qué limitaciones tienen (por ejemplo, sexo en solo dos categorías)? |
| **Seguridad** | Protegerlos contra accesos indebidos, pérdida o filtración | ¿Quién tiene acceso? ¿Están en un repositorio público? |
| **Transparencia** | Que las personas sepan qué se hace con sus datos | ¿Podríamos explicarle a una persona qué hicimos con su solicitud? |

**Derechos de la persona** (en términos generales): **acceso** (saber qué datos suyos se tratan) · **rectificación** (corregirlos) · **supresión** (pedir que se eliminen) · **oposición** (oponerse a ciertos tratamientos) · **portabilidad** (recibirlos para llevarlos a otro responsable).

**"Publicado ≠ libre de usar para cualquier fin."** Que un dato esté en internet o en un portal abierto no autoriza cualquier uso: hay que revisar la finalidad con que se publicó, su licencia y si permite identificar a alguien.

## 10. Anonimización: seudonimizar, generalizar y suprimir

| Técnica | Qué hace | Ejemplo | Ojo |
|---|---|---|---|
| **Eliminar** | Quitar la columna | `nombre`, `correo` | No basta: los cuasi-identificadores siguen ahí |
| **Seudonimizar** | Reemplazar el identificador por una clave sin significado | `S0001` → `a83f…` | Sigue siendo dato personal si alguien guarda la tabla de equivalencias |
| **Generalizar** | Reducir el detalle | edad → tramo; comuna → provincia; fecha → trimestre | Se pierde detalle: hay que medir cuánto |
| **Suprimir celdas pequeñas** | Quitar las filas de grupos con menos de *k* personas | grupos con menos de 5 | Se pierden filas: declararlo |

**k-anonimato.** Un conjunto es *k*-anónimo si cada combinación de cuasi-identificadores la comparten **al menos *k* filas**: nadie se distingue de otras *k* − 1 personas. Se mide con el tamaño de cada grupo:

```python
CUASI = ["comuna", "edad", "sexo", "fecha_solicitud"]
tam = df.groupby(CUASI).size()                         # una fila por grupo
k_min = tam.min()                                      # el grupo más pequeño
unicas = (tam == 1).sum()                              # personas que nadie más comparte

tam_fila = df.groupby(CUASI).transform("size")         # el tamaño de su grupo, en cada fila
df_k = df[tam_fila >= 5]                               # suprime los grupos con menos de 5
```

En el lab:

| Paso | Grupos | Tamaño mínimo | Filas en riesgo | ROC-AUC |
|---|---|---|---|---|
| Sin nombre, correo ni id (crudo) | 5.938 | 1 | 5.876 filas únicas (97,9 %) | 0,802 |
| Generalizado (tramo de edad, provincia, trimestre) | 120 | 2 | 20 filas en grupos de menos de 5 | 0,801 |
| Generalizado + supresión con *k* = 5 | 113 | 5 | 0 (se suprimieron 20 filas) | — |

En este caso, proteger casi no costó utilidad. No siempre es así: hay que **medir antes y después**. El k-anonimato no protege contra todo (si todas las personas de un grupo comparten el mismo valor sensible, igual se revela). Técnicas más fuertes, como la privacidad diferencial, quedan fuera del curso.

## 11. Sesgo: de dónde viene, cómo se mide y la ficha del modelo

**De dónde viene.**

| Origen | Qué pasa | Ejemplo |
|---|---|---|
| **Datos históricos** | El modelo aprende decisiones o desigualdades del pasado | Si antes se aprobaba menos a un grupo, hay menos datos de cómo pagan |
| **Muestreo** | Un grupo está poco representado | Pocas solicitudes de una comuna: estimaciones inestables |
| **Etiquetas** | Lo que se predice no mide lo que se quiere | "Incumple" registrado distinto según el canal de cobranza |
| **Proxies** | Una variable permitida reproduce una variable sensible | En el lab, `servicios_domesticos` es 93 % mujeres y tiene ingreso más bajo |

**Quitar la columna sensible no basta.** En el lab, el modelo no usa `sexo` y aun así niega el crédito a más mujeres que sí habrían pagado: la ocupación y el ingreso llevan esa información. Agregar `sexo` al modelo casi no cambia la brecha (0,080 en ambos casos).

**Medir por subgrupo.** Con la decisión del caso (negar si *p* ≥ 0,25):

| Tasa | Definición | Quién la sufre |
|---|---|---|
| **Falsos positivos** (`fpr`) | Negados entre quienes **sí habrían pagado** = FP / (FP + VN) | La persona |
| **Falsos negativos** (`fnr`) | Aprobados entre quienes **incumplen** = FN / (FN + VP) | La institución |

Cada tasa se reporta con su ***n*** (el denominador) y su **intervalo de confianza**. Con pocas personas en un subgrupo, una diferencia grande puede ser solo ruido.

**Intervalo de Wilson** (95 %, *z* = 1,96) para una tasa *p* = *k*/*n*:

```python
def intervalo_wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d                                  # centro, corrido hacia 0,5
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d     # semiancho
    return c - h, c + h
```

A diferencia del intervalo "normal" (*p* ± 1,96·√(*p*(1−*p*)/*n*)), el de Wilson no se sale de [0, 1] y funciona bien con *n* pequeño o tasas cercanas a 0 o a 1. En el lab:

| Sexo | *n* en test | Falsos positivos [IC 95 %] | Falsos negativos [IC 95 %] |
|---|---|---|---|
| F | 962 (727 pagan, 235 incumplen) | 0,248 [0,218; 0,280] | 0,294 [0,239; 0,355] |
| M | 838 (719 pagan, 119 incumplen) | 0,168 [0,143; 0,197] | 0,412 [0,327; 0,502] |

Los intervalos de falsos positivos **no se solapan**: la diferencia no se explica por azar. (Que dos intervalos se solapen no prueba que no haya diferencia; que no se solapen es evidencia fuerte de que la hay.)

**No hay una sola definición de "justo".** Igualar la tasa de aprobación, igualar los falsos positivos o igualar los falsos negativos son criterios distintos, y en general **no se pueden cumplir todos a la vez** cuando las tasas base difieren entre grupos. Elegir cuál importa más es una decisión que se explica, no un cálculo.

**Mitigar.** Medir **antes y después** de cada cambio · revisar las variables que actúan como proxy · revisión humana de las decisiones desfavorables · umbrales o ajustes por grupo y técnicas como la reponderación (se nombran aquí; el lab solo mide) · declarar lo que no se corrigió como limitación.

**Ficha del modelo (*model card*), seis campos:**

| Campo | Qué lleva |
|---|---|
| **Uso previsto y usos no recomendados** | Para qué sirve y para qué **no** debe usarse |
| **Datos** | Fuente, fecha, qué incluyen y qué no |
| **Desempeño** | Métrica global y **por subgrupo**, con intervalos, y la celda o archivo de origen |
| **Limitaciones** | Concretas: qué no se evaluó, qué brecha quedó, qué supuestos tiene |
| **Consideraciones éticas** | Datos sensibles, quién puede verse perjudicado, qué control humano hay |
| **Versión y fecha** | Versión del modelo, fecha, parámetros clave (umbral, semilla) |

## 12. IA generativa, datos y seguridad en el repositorio

**IA generativa y datos.**

| Siempre | Nunca |
|---|---|
| Declarar qué herramienta se usó, para qué y cómo se verificó | Pegar datos personales o sensibles en un asistente externo |
| Verificar ejecutando el código y revisando las cifras | Copiar una cifra o una cita que no se comprobó |
| Usar datos sintéticos o una muestra anonimizada para pedir ayuda | Subir credenciales o claves a un asistente |

**Seguridad en el repositorio: cinco hábitos.**

1. **`.gitignore` desde el primer commit:** `data/raw/`, `models/`, `.venv/`, `.env`.
2. **Credenciales fuera del código:** en variables de entorno o en un `.env` que no se sube.
3. **Revisar antes de cada commit:** `git status` y `git diff --staged`.
4. **Repositorio privado** mientras haya datos o resultados sin revisar.
5. **Si se subió algo que no debía, no basta con borrarlo en el siguiente commit:** queda en el historial. Hay que reescribir el historial (o rehacer el repositorio) y cambiar cualquier credencial expuesta.

## 13. Glosario

| Término | Definición |
|---|---|
| **Reproducible** | Otra persona, con el repositorio y las instrucciones, obtiene los mismos resultados |
| **Script** | Archivo `.py` que se ejecuta de principio a fin con un comando |
| **Módulo** | Archivo `.py` que se importa (`src/datos.py` → `from src.datos import ...`) |
| **Docstring** | Texto entre comillas triples al inicio de una función que explica qué hace |
| **Cuasi-identificador** | Atributo que no identifica solo, pero sí combinado con otros (comuna, edad, sexo, fecha) |
| **k-anonimato** | Cada combinación de cuasi-identificadores la comparten al menos *k* filas |
| **Proxy** | Variable permitida que lleva información de una variable sensible |
| **Falso positivo** | El modelo predice el evento y no ocurre (en el caso: negar a quien sí pagaría) |
| **Falso negativo** | El modelo no predice el evento y sí ocurre (en el caso: aprobar a quien incumple) |
| **Ficha del modelo** | Documento de una página con uso previsto, datos, desempeño, limitaciones, ética y versión |
