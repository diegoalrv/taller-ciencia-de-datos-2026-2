# Guía de recolección de datos — Clase 2 (material para estudiantes)

**Para qué sirve:** referencia técnica de las tres vías de acceso a datos que se practican hoy (archivos planos, SQL, APIs), más el estándar de **obtención reproducible** que exige el Informe 1. Acompaña al notebook `lab02-recoleccion-datos.ipynb`.

---

## 1. Archivos planos (CSV y parientes)

La vía más común — y la más traicionera. Un CSV "estándar" no existe: cada fuente decide separador, codificación y formato de números. Los portales chilenos (datos.gob.cl, DEIS, MINEDUC) suelen venir con esta combinación:

| Trampa | Síntoma | Solución |
|---|---|---|
| Codificación `latin-1` (no UTF-8) | `UnicodeDecodeError` o "Ã±" donde va "ñ" | `pd.read_csv(..., encoding="latin-1")` |
| Separador `;` (no `,`) | Todo queda en una sola columna | `sep=";"` |
| Decimal con coma (`3,14`) | Números leídos como texto (`object`) | `decimal=","` |
| Miles con punto (`1.234.567`) | Ídem | `thousands="."` |
| Filas de título/notas antes del header | Columnas `Unnamed: 0, Unnamed: 1...` | `skiprows=N` |
| Códigos con ceros a la izquierda (comunas, RBD) | `05101` se convierte en `5101` | `dtype={"codigo_comuna": str}` |
| Valores nulos escritos como texto | `"S/I"`, `"-"`, `"NA"` no son detectados | `na_values=["S/I", "-", "NA"]` |

**Rutina recomendada al recibir cualquier CSV:** mirar las primeras líneas crudas (`head -5 archivo.csv` o abrirlo como texto), recién después llamar a `read_csv` con los parámetros correctos, y verificar con `df.info()` que cada columna tenga el dtype que corresponde. Un `object` donde esperabas números es una lectura fallida silenciosa.

Otros formatos de archivo que pueden aparecer: Excel (`pd.read_excel`, requiere `openpyxl`), SPSS/Stata de la CASEN (`pyreadstat`), Parquet (`pd.read_parquet`), JSON de archivo (`pd.read_json`).

## 2. Bases de datos SQL

Cuando los datos ya viven en una base relacional (o son demasiado grandes para abrirlos enteros), conviene **filtrar y agregar en SQL** y traer a pandas solo lo necesario.

```python
import sqlite3
import pandas as pd

con = sqlite3.connect("ventas.db")
df = pd.read_sql("""
    SELECT c.comuna, COUNT(*) AS n_ventas, SUM(v.monto) AS monto_total
    FROM ventas v
    JOIN clientes c ON c.id_cliente = v.id_cliente
    WHERE v.fecha >= '2026-01-01'
    GROUP BY c.comuna
    ORDER BY monto_total DESC
""", con)
```

Ideas clave: la conexión es un recurso (cerrarla o usar `with`); `read_sql` devuelve un DataFrame normal; el criterio de dónde hacer cada cosa es simple — **reducción de volumen en SQL, análisis fino en pandas**. Para el proyecto, SQLite es suficiente como formato de trabajo local; nadie exige un servidor.

## 3. APIs públicas

Una API entrega datos a pedido vía HTTP, casi siempre en JSON. Es la vía correcta cuando los datos cambian en el tiempo o cuando la descarga masiva no está disponible.

```python
import requests

r = requests.get("https://mindicador.cl/api/uf/2025", timeout=30)
r.raise_for_status()          # error explícito si la API falló
datos = r.json()              # dict de Python
df = pd.DataFrame(datos["serie"])
```

Checklist al usar una API: leer la documentación (endpoints, parámetros, formato de respuesta); revisar si exige **API key** (guardarla fuera del código — variable de entorno, nunca al repo); respetar **rate limits** (pausas con `time.sleep` si se hacen muchas llamadas); manejar errores (`status_code`, `raise_for_status`); y **guardar la respuesta cruda a disco** — la API de hoy puede no responder lo mismo mañana.

APIs sin registro para partir: [Mindicador.cl](https://mindicador.cl) (indicadores económicos chilenos) y [Open-Meteo](https://open-meteo.com) (clima histórico). Con registro gratuito: Banco Central (BDE), GitHub API, OpenWeatherMap.

## 4. Web scraping (mención con advertencias)

Extraer datos de páginas HTML es el último recurso, cuando no hay descarga ni API. Antes de scrapear: revisar `robots.txt` y los términos del sitio, no bombardear el servidor, y preferir siempre una fuente estructurada si existe. Para este taller, **scraping solo con aprobación previa del profesor** — suele consumir semanas que el calendario no tiene.

## 5. Obtención reproducible (lo que exige el Informe 1)

Regla de oro: **cualquier persona con tu repositorio debe poder regenerar `data/raw/` ejecutando un solo script o notebook.** Los datos crudos son intocables: nunca se editan a mano; toda corrección ocurre después, en código (eso es la U2).

Estructura mínima del repositorio:

```
proyecto/
├── README.md            ← qué es el proyecto, cómo regenerar los datos
├── data/
│   └── raw/             ← datos crudos tal como llegaron (no se tocan)
├── notebooks/
│   └── 01-obtencion.ipynb   ← descarga y verificación
└── src/
    └── descargar.py     ← (opcional) script de descarga
```

Metadata mínima a documentar por cada fuente (va en el README y en el Informe 1):

| Campo | Ejemplo |
|---|---|
| Fuente y URL exacta | DEIS — Listas de espera GLOSA, https://deis.minsal.cl/... |
| Fecha de descarga | 2026-08-13 |
| Licencia / condiciones de uso | Datos abiertos, uso libre con cita |
| Versión o período cubierto | Corte junio 2026; años 2020–2026 |
| Formato y tamaño | CSV latin-1, 480 MB, 2,1 M filas × 14 columnas |
| Procedimiento | Script `01-obtencion.ipynb`, sección 2 |

**Checklist de salida de la Clase 2** (esto es lo que se revisa en la sección de obtención del Informe 1):

- [ ] Dataset principal descargado y guardado en `data/raw/` sin modificaciones
- [ ] Obtención automatizada (script o notebook que descarga, o instrucciones exactas si la fuente exige clic manual — con URL, fecha y pasos)
- [ ] Metadata de la fuente documentada (tabla de arriba)
- [ ] Verificación básica ejecutada: dimensiones, `df.info()`, conteo de nulos
- [ ] Si hay API: respuesta cruda guardada a disco (JSON), no solo el DataFrame
