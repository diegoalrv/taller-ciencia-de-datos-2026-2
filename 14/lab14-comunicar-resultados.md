# Laboratorio 14 — Comunicar resultados: reporte, figuras y exposición

**EIN146A25 · 2026-2 · Jueves 12-nov · Lab. Central 114**
Notebook: [`lab14-comunicar-resultados.ipynb`](lab14-comunicar-resultados.ipynb) · Referencia técnica: [`lab14-guia-comunicar-resultados.md`](lab14-guia-comunicar-resultados.md)

## Objetivo

Pasar de "tengo resultados" a "el lector entiende qué hacer con ellos". Tres preguntas: **¿qué digo primero?** (el resumen ejecutivo: el hallazgo con una cifra comparada y traducida, antes que el método), **¿qué muestro?** (figuras con título-mensaje, sin ejes que engañen, con la incertidumbre y la comparación a la vista; tablas que se copian al informe sin editarlas) y **¿cómo lo digo en voz alta?** (un *pitch* de 3 minutos para una audiencia no técnica). Es la base del **resumen ejecutivo, las figuras y la tabla de resultados del Informe 5** y de la **exposición final**.

## Antes de empezar

```bash
git pull                     # en el repositorio del curso
pip install -r requirements.txt
```

`scikit-learn` es obligatorio (solo para rehacer los resultados del Lab 11 en el Setup). `plotly` es **opcional**: lo usa únicamente la parte B del extra 3.3; si no está, el Setup lo avisa y el lab funciona completo. `seaborn` no se usa.

**Datos sintéticos generados para el lab: ninguna cifra describe a una empresa, un comercio o un reparto real.**

Abran el notebook y ejecuten las celdas de *Setup*, de generación de datos y de resultados. Es el mismo mini-caso del Lab 11 (6.000 pedidos de un servicio de reparto a domicilio; **"¿este pedido llegará con retraso?"**): el modelo ya está elegido y evaluado, y la celda de resultados lo rehace en unos segundos. **Hoy no se modela: se comunica.** Traigan también el **resultado principal de su proyecto y la figura que lo muestra** (el encargo de la Clase 13): los usan en la parte de proyecto.

## Mecánica

| # | Qué | Duración |
|---|---|---|
| 1 | `git pull`, Setup, datos y resultados | 5 min |
| 2 | **Ej. 1 — Reescribir un resumen ejecutivo** | 20 min |
| 3 | **Ej. 2 — Arreglar tres figuras engañosas** | 25 min |
| 4 | Recreo | 10 min |
| 5 | **Ej. 3 — Tabla de resultados lista para el informe** (el extra 3.3 es opcional) | 25 min |
| 6 | **Proyecto:** resumen ejecutivo de su proyecto y guion del *pitch* | 10 min |
| 7 | **Pitch de 3 minutos** por equipo + preguntas + hoja de retroalimentación | 30 min |
| 8 | Checklist de salida y encargo | 10 min |

## Ejercicios

**1 · Reescribir un resumen ejecutivo.** Un equipo ficticio resumió su trabajo así: "se usaron diversas técnicas… se obtuvieron buenos resultados, con un PR-AUC de 0,35". Todo es cierto y nadie puede decidir nada con eso. Lo reescriben en cinco partes (pregunta, hallazgo, qué significa, qué se recomienda, qué limita), sin jerga y con una cifra comparada, y escriben además **una** frase para el lector técnico con la regla completa: cifra ± incertidumbre, comparación y origen.

**2 · Arreglar tres figuras engañosas.** Tres figuras del mismo borrador, cada una con un problema distinto. Las rehacen con Matplotlib aplicando el checklist (título = mensaje, una idea por figura, destacar lo importante, fuente y *n* al pie, incertidumbre y comparación a la vista). La verificación revisa la figura misma, no solo el archivo.

**3 · Tabla de resultados lista para el informe.** De la tabla copiada de la consola a una tabla que se pega en el informe sin tocarla: media ± desviación, orden con sentido, la mejor opción resaltada, nota al pie, exportada a `reports/`. Y una decisión que hay que saber escribir: ¿hay un ganador o un empate práctico? **Extra 3.3 (opcional):** una página de resumen de una pantalla (todos) y, si tienen `plotly`, su versión HTML autocontenida con un filtro. **El dashboard es opcional en este curso**: una buena página de resumen vale lo mismo.

## Proyecto (40 min)

1. **Preparar (10 min).** Con la plantilla del notebook, escriban el resumen ejecutivo de **su** proyecto (cinco partes, cada cifra con la celda de donde sale) y el guion de un *pitch* no técnico de 3 minutos alrededor de su figura principal.
2. **Pitch (30 min).** Cada equipo presenta 3 minutos (ambos integrantes hablan), responde 2 minutos de preguntas del público y recibe la hoja de retroalimentación. El orden se sortea. **No se califica hoy:** es el primer ensayo de la versión no técnica de la exposición final.

## Checklist de salida

- [ ] Ejercicios 1 y 2 pasan su verificación automática (el 3 y el extra pueden quedar para la casa)
- [ ] Resumen ejecutivo del proyecto en cinco partes, con el origen de cada cifra
- [ ] *Pitch* de 3 minutos presentado y hoja de retroalimentación recibida
- [ ] Figura principal del proyecto rehecha con el checklist del Ejercicio 2
- [ ] **Para la próxima clase (jueves 19-nov): ensayo cronometrado.** Traer un guion borrador de 12 minutos (primero la versión no técnica, después la técnica) y las diapositivas en el estado en que estén
- [ ] Recordatorio: **Informe 5 y exposición final, jueves 03-dic**
