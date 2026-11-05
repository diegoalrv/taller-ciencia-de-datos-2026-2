# Laboratorio 13 — Proyecto ejecutable y responsable

**EIN146A25 · 2026-2 · Jueves 05-nov, 10:00–12:15 · Lab. Central 114**
Notebook: [`lab13-proyecto-ejecutable-y-responsable.ipynb`](lab13-proyecto-ejecutable-y-responsable.ipynb) · Referencia técnica: [`lab13-guia-proyecto-ejecutable-y-responsable.md`](lab13-guia-proyecto-ejecutable-y-responsable.md)

## Objetivo

Responder dos preguntas sobre un análisis de datos: **¿lo puede ejecutar otra persona?** (scripts que reciben sus parámetros desde afuera, validan sus entradas, tienen pruebas y se ejecutan con un solo comando) y **¿debería existir con estos datos?** (qué columnas identifican a una persona, qué riesgo de reidentificación hay y si el modelo se equivoca más con un grupo que con otro). Es la base de las secciones de **reproducibilidad** y de **ética, privacidad y sesgo** del Informe 5.

## Antes de empezar

```bash
git pull                     # en el repositorio del curso
pip install -r requirements.txt
pip install pytest           # opcional: sin pytest, el Ejercicio 2 usa la versión con assert
```

`scikit-learn` es **obligatorio**. `pytest` es **opcional**: si no está, el Setup lo avisa y el Ejercicio 2 corre las mismas pruebas con `assert`.

**Datos sintéticos generados para el lab: todas las personas, nombres y correos son inventados; ninguna cifra describe a una institución ni a una persona real.**

Abran el notebook y ejecuten las celdas de *Setup*. El archivo de práctica (6.000 solicitudes de microcrédito de una institución ficticia; la pregunta es **"¿esta persona incumplirá el pago en 12 meses?"**) **se genera solo** en `data_practica/`, y la carpeta `proyecto_ejemplo/` (la estructura de un repositorio) se crea al lado. No hay que descargar nada y el lab no usa internet.

## Mecánica

| Hora | Qué |
|---|---|
| 10:00 | `git pull`, Setup y generación de datos |
| 10:05 | **Ej. 1 — De notebook a script que se ejecuta** (~25 min) |
| 10:30 | **Ej. 2 — Pruebas, un comando y requisitos** (~20 min; el extra 2.3 es opcional) |
| 10:50 | Recreo |
| 11:00 | **Ej. 3 — Clasificar columnas y medir el riesgo de reidentificación** (~25 min) |
| 11:25 | **Ej. 4 — Auditar el sesgo y completar la ficha** (~30 min; el extra 4.3 es opcional) |
| 11:55 | **Proyecto:** prueba del clon vacío + última ronda de consulta de los Informes 3+4 |
| 12:10 | Checklist de salida |

## Ejercicios

En los Ejercicios 1 y 2 las celdas ✏️ TU TURNO son celdas `%%writefile`: se completa el esqueleto y se **ejecuta la celda**, que escribe el archivo dentro de `proyecto_ejemplo/`. Las verificaciones ejecutan esos archivos de verdad, como lo haría otra persona en la terminal. Si vuelven a ejecutar el Setup, `proyecto_ejemplo/` se recrea: vuelvan a ejecutar sus celdas `%%writefile`.

**1 · De notebook a script que se ejecuta.** Un análisis que quedó en una sola celda de notebook da un número distinto cada vez que se ejecuta, y en otro computador ni siquiera corre. Lo convierten en tres módulos (`src/datos.py`, `src/modelo.py`, `src/entrenar.py`) que se ejecutan con `python -m src.entrenar --datos ... --salida ... --semilla 2026`, fallan con un mensaje claro si el dato no es el esperado y dejan el modelo y sus métricas en `models/`.

**2 · Pruebas, un comando y requisitos.** Una copia del proyecto "recién clonada" no corre. Escriben tres pruebas mínimas del pipeline, un `run_all.py` que entrena y prueba en orden, y un `requirements.txt` con versiones; la verificación final ejecuta todo en una copia limpia. **Extra (opcional):** el README del proyecto de ejemplo con la plantilla de nueve secciones.

**3 · Clasificar columnas y medir el riesgo de reidentificación.** Se quitan el nombre, el correo y el identificador: ¿el archivo ya es anónimo? Clasifican cada columna, deciden qué hacer con ella, miden cuántas personas comparten cada combinación de atributos y prueban qué se gana y qué se pierde al proteger los datos.

**4 · Auditar el sesgo y completar la ficha.** El modelo tiene un ROC-AUC de 0,80. Miden sus errores por subgrupo, con su tamaño y su intervalo de confianza, comparan con un modelo que sí usa la variable sensible, buscan qué columnas explican lo que encuentren y completan la **ficha del modelo** de la S14. **Extra (opcional):** el gráfico de tasas por subgrupo.

Cada ejercicio trae su celda de **verificación automática** (debe imprimir todos los ✓). El notebook **no trae las soluciones**: se revisan en clase al cierre de cada bloque, y la guía tiene la referencia técnica de cada paso. Las verificaciones de los extras imprimen `⊘` si no los hicieron, y no cuentan como falla.

## Parte de proyecto (11:55)

Al final del notebook hay dos tablas vacías para copiar al informe o al README de su repositorio:

- **Prueba del clon vacío (reproducibilidad).** Clonen su repositorio en una **carpeta nueva**, sigan **su propio README** y corran los **cuatro notebooks en orden**. Para cada uno de los nueve puntos de la S16 (clon vacío según el README · `requirements.txt` con versiones · semilla fija · un comando · datos documentados · tres pruebas que pasan · README con resultados, origen y limitaciones · declaración de uso de IA · commits claros): `cumple` / `no cumple` y `qué hago`. Es el gate de los Informes 3+4.
- **Borrador de ética, privacidad y sesgo (para la casa).** Las cinco preguntas de la S16, con una a tres frases y la evidencia (celda o cifra) de cada una. *"No aplica, porque…"* es una respuesta válida.

> **Informes 3+4 (documento único): domingo 08-nov, 23:59, AULA-USM.** −10 por día de atraso, máx. 3, aplicado a las dos notas. Hoy es la última ronda de consulta.

## Checklist de salida

- [ ] Ejercicios 1, 2 y 3 pasan su verificación automática (el 4, la ficha y los extras pueden quedar para la casa)
- [ ] Tabla de reproducibilidad completa sobre el repositorio del proyecto: cada punto con `cumple` y `qué hago`
- [ ] Borrador de las cinco respuestas de ética, privacidad y sesgo (para la casa)
- [ ] Lo que no se alcanza a corregir hoy, anotado como limitación para el informe
- [ ] Informes 3+4 (documento único): **domingo 8-nov, 23:59, AULA-USM**
- [ ] Para la clase de reportes y comunicación: traer el resultado principal del proyecto y la figura que lo muestra
- [ ] Recordatorio: **Informe 5 y exposición, 03-dic**

## Entrega

El laboratorio **no se entrega por separado**: alimenta el repositorio del proyecto y el **Informe 5** (reproducibilidad; ética, privacidad y sesgo). La prueba del clon vacío de hoy se aplica al repositorio de los **Informes 3+4**, que se entregan el **domingo 8-nov a las 23:59** por AULA-USM.
