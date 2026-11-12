# Guía para comunicar resultados — Clase 14 (material para estudiantes)

**Para qué sirve:** referencia técnica para contar un resultado de ciencia de datos a quien lo va a leer o escuchar: el resumen ejecutivo, las cifras con su origen, las figuras y tablas del informe, la página de resumen (y el dashboard, que es opcional), qué no se comparte, y cómo preparar la exposición final. Acompaña al notebook `lab14-comunicar-resultados.ipynb` y es la base del **Informe 5** y de la **exposición del 03-dic**.

Todas las cifras de ejemplo son del mini-caso sintético de los Labs 11 y 14: 6.000 pedidos de un servicio de reparto ficticio, 11,4 % con retraso. **Ninguna cifra describe a una empresa real.**

---

## 0. El caso y sus resultados

El modelado se hizo en el Lab 11; la celda de resultados del Lab 14 lo rehace igual:

- Test separado al inicio (20 %, 1.200 pedidos); validación cruzada con 5 folds estratificados sobre los 4.800 restantes, **los mismos folds** para todas las opciones.
- Costo declarado: no avisar un retraso (falso negativo) = 10; avisar de más (falso positivo) = 1. Umbral por costo = `C_FP / (C_FP + C_FN)` = **0,09**.

| Opción | Costo por pedido (media ± desv., 5 folds) | Sensibilidad | PR-AUC |
|---|---|---|---|
| Regresión logística | **0,616 ± 0,078** | 0,750 ± 0,075 | 0,351 ± 0,030 |
| Bosque aleatorio | 0,642 ± 0,042 | 0,798 ± 0,046 | 0,337 ± 0,028 |
| Árbol de decisión | 0,745 ± 0,084 | 0,638 ± 0,085 | 0,252 ± 0,021 |
| Avisar siempre | 0,886 ± 0,000 | 1,000 ± 0,000 | 0,114 ± 0,000 |
| Nunca avisar | 1,144 ± 0,005 | 0,000 ± 0,000 | 0,114 ± 0,000 |

Resultado final (test, una sola vez, regresión logística): costo **0,586** por pedido frente a **0,886** de "avisar siempre" (**−34 %**) y 1,142 de "nunca avisar"; avisa **106 de 137** retrasos (sensibilidad 0,774) con **499 avisos**, de los cuales **393** son de más.

## 1. El resumen ejecutivo: la conclusión primero

El lector tiene un minuto. **Pirámide invertida:** lo más importante arriba, el método después. Cinco partes, una o dos frases cada una:

| Parte | Responde | Ejemplo (mini-caso) |
|---|---|---|
| Pregunta | ¿Qué queríamos saber y por qué importa? | ¿Podemos anticipar qué pedidos llegarán con retraso para avisar antes del reclamo? |
| Hallazgo | ¿Qué encontramos? **Una** cifra con su comparación | Avisa a tiempo cerca de 8 de cada 10 retrasos (106 de 137) y, frente a avisar a todos, baja en un 34 % lo que cuestan los errores |
| Qué significa | ¿Qué implica, incluido el costo? | A cambio, de cada 5 avisos unos 4 son de más; como un aviso de más cuesta mucho menos que un retraso sin aviso, el balance es favorable |
| Qué se recomienda | ¿Qué decisión sugiere? | Una prueba piloto de un mes en una zona, midiendo reclamos y quejas por avisos innecesarios |
| Qué limita | ¿Qué podría hacer cambiar la conclusión? | Los costos 10 y 1 son supuestos; si un aviso de más molesta más de lo previsto, hay que recalcular el punto de corte |

**Mal:** "En este trabajo se utilizaron diversas técnicas de machine learning… se obtuvieron buenos resultados, con un PR-AUC de 0,35." Empieza por el método, la cifra no tiene comparación y está en una métrica que quien decide no conoce.

**Traducir una métrica:** "sensibilidad 0,774" → "avisa 8 de cada 10 retrasos"; "precisión 0,21" → "de cada 5 avisos, 1 es un retraso real"; "costo 0,586 frente a 0,886" → "un tercio menos de costo que avisar a todos". La traducción **no redondea a favor**: si son 77 %, es "cerca de 8 de cada 10", no "casi todos".

Prueba rápida: léanle el resumen a alguien que no trabajó en el proyecto, sin mostrárselo. Si no puede repetir el mensaje, reescriban.

## 2. Cada cifra con su origen

La regla del lector técnico (es la regla de trazabilidad que ya conocen desde el Informe 2):

> **cifra + incertidumbre + comparación + dónde se calculó**

1. Mal: "el modelo es muy bueno".
2. Mejor: "el modelo tiene un costo de 0,616 por pedido".
3. Bien: "costo de **0,616 ± 0,078** por pedido en validación cruzada (5 folds), frente a **0,886** de 'avisar siempre'; `notebooks/04-modelado.ipynb`, celda 31".

Una cifra sin origen no se puede verificar; una cifra sin comparación no dice si es buena; una cifra sin incertidumbre no dice si la diferencia es real. En el resumen no técnico va la cifra traducida y la comparación; la incertidumbre y el origen van en el cuerpo del informe.

## 3. Figuras que comunican

Checklist (el mismo del Ejercicio 2):

1. **Título = mensaje.** "Cerro de noche: 1 de cada 4 pedidos se retrasa", no "Tasa de retraso por zona".
2. **Una idea por figura.** Si hay dos mensajes, son dos figuras.
3. **Destacar lo importante,** el resto en gris.
4. **Etiquetas legibles** (ejes con unidades, tamaño de fuente que se lea desde el fondo de la sala en la exposición).
5. **Fuente y *n* al pie.**
6. **Incertidumbre y comparación a la vista** (barras de error, línea del baseline).

Recetas de Matplotlib:

```python
ax.set_ylim(0, None)                                   # barras: el eje parte en 0
ax.plot(x, y, color="0.75", lw=1)                      # serie de contexto, en gris
ax.plot(x, y_dest, color="tab:red", lw=2.5, zorder=3)  # la serie del mensaje
ax.text(x[-1] + 0.1, y_dest[-1], "Cerro", color="tab:red", va="center")  # etiqueta directa, sin leyenda
ax.barh(nombres, medias, xerr=desv, capsize=4)         # media ± desviación
ax.axvline(costo_baseline, color="0.2", ls="--")       # línea de referencia
ax.xaxis.set_major_formatter(lambda v, _: f"{v:.1f}".replace(".", ","))  # coma decimal
fig.text(0.01, -0.05, "Fuente: … · n = 4.800", fontsize=8, color="0.35")  # nota al pie
fig.savefig("figs/nombre.png", dpi=150, bbox_inches="tight")
```

Una figura buena se entiende sin leer el párrafo de al lado. Retomen el principio de la Clase 7: **figura → observación con número → decisión**.

## 4. Lo que engaña sin querer

| Problema | Por qué engaña | Corrección |
|---|---|---|
| Eje Y truncado en barras | La longitud de la barra codifica el valor: 11,6 % frente a 11,0 % parece "el doble" | Barras desde 0. (En una serie de tiempo o un gráfico de puntos el eje puede no partir en 0.) |
| Torta con muchas categorías | El ojo compara mal ángulos | Barras ordenadas |
| Doble eje Y | Las escalas se eligen para que las curvas "se muevan juntas" | Dos paneles, o índices con base común |
| Demasiadas series | No hay dónde mirar | Una destacada, el resto en gris; o paneles pequeños |
| Colores que no distingue una persona daltónica (rojo/verde) | Parte del público no ve la diferencia | Paleta accesible (`tab:blue` / `tab:orange`, *viridis*) y no depender solo del color: etiquetas, formas o patrones |
| Sin *n* ni incertidumbre | Una diferencia pequeña con *n* chico parece un hallazgo | Barras de error, intervalo o *n* en la nota |

## 5. Tablas para el informe

- **Media ± desviación** entre folds, con coma decimal y la misma cantidad de decimales en toda la tabla.
- **Orden con sentido** (por la métrica principal), no alfabético. Las políticas triviales se incluyen: son la comparación.
- **La mejor opción resaltada** (negrita) y una **nota al pie** que diga qué es cada número, sobre cuántos datos, y si mayor o menor es mejor.
- **Se genera con código** y se exporta a un archivo (`reports/tabla_resultados.md`, `.csv` o LaTeX con `tabla.to_latex()`): si hay que corregirla a mano, el proceso no es reproducible.
- **¿Tabla o gráfico?** Tabla si el lector necesita valores exactos; gráfico si necesita ver un patrón. En el informe suelen ir los dos.
- **Empate práctico** (regla del Lab 11): si la diferencia entre las dos mejores opciones es menor que la desviación entre folds, se informa como empate y se elige con otro criterio declarado (simplicidad, interpretabilidad, costo de mantener). En el caso: 0,616 frente a 0,642, diferencia 0,026 < 0,078 → empate; se elige la logística por ser más simple de explicar.

## 6. La página de resumen y los dashboards (opcional)

**El dashboard es opcional en este curso.** Un buen reporte con tres figuras bien elegidas lo reemplaza.

| Sí conviene un dashboard si… | No conviene si… |
|---|---|
| la audiencia necesita **explorar** (filtrar por zona, comparar períodos) | el mensaje es uno solo |
| el resultado se **actualiza** con datos nuevos | el lector tiene un minuto |
| hay muchas vistas posibles de lo mismo | tres figuras alcanzan |

Diseño de un panel para otra persona (el lector no estuvo en el análisis), en tres zonas: **arriba**, el mensaje y 2 a 3 cifras clave con su *n* y la fecha de los datos; **al centro**, una vista principal; **a un costado**, filtros mínimos con valores por defecto. Una pregunta por pantalla, jerarquía visual, texto de ayuda, colores coherentes y nada que exija saber programar.

Cómo compartirlo, del más simple al más complejo (el más simple que cumple la tarea es el correcto):

1. **Informe con figuras** (PDF): el mínimo siempre válido.
2. **HTML estático autocontenido** (Plotly: `fig.write_html("x.html", include_plotlyjs=True)`; pesa unos 5 MB porque lleva la librería adentro y por eso abre sin internet).
3. **App con servidor** (Streamlit, Panel; ver el Lab 08): más flexible, pero hay que alojarla y mantenerla.

## 7. Qué no se comparte: tres leyes, una lógica

Antes de publicar un dashboard, subir un HTML o compartir un enlace, repasen la Clase 13: **un archivo con datos de personas que sale de su computador es un tratamiento de datos.** Resumen general para criterio profesional, **no asesoría legal** (verificado el 11-nov-2026):

| | Chile: Ley 19.628, reformada por la Ley 21.719 | Unión Europea: RGPD / GDPR (Reglamento 2016/679) | California: CCPA, reformada por la CPRA |
|---|---|---|---|
| Rige desde | La reforma (Ley 21.719): **1-dic-2026** según la ley vigente. Hay un proyecto que la posterga al 15-oct-2027: aprobado por el Senado (28-oct) y en segundo trámite en la Cámara; **no es ley** a la fecha de esta guía | 25-may-2018 | CCPA desde 2020; reforma CPRA desde el 1-ene-2023 |
| A quién aplica | Quien trate datos en Chile, y también desde fuera si ofrece bienes o servicios a personas en Chile o monitorea su comportamiento | Quien esté establecido en la UE, y también desde fuera si ofrece bienes o servicios a personas en la UE o monitorea su comportamiento | Empresas con fines de lucro que hacen negocios en California y superan un umbral: ingresos anuales ≥ US$ 26,625 millones (ajustado en 2025), o datos de ≥ 100.000 residentes u hogares, o ≥ 50 % de ingresos por vender o compartir datos |
| Lógica de base | Necesita una **base de licitud** (consentimiento, contrato, obligación legal, interés legítimo, entre otras) | Necesita una **base de licitud** (seis bases del art. 6) | Modelo de **exclusión (*opt-out*)**: se puede tratar, pero la persona puede oponerse a la venta o al uso compartido (para menores de 16, se necesita autorización previa) |
| Datos sensibles | Protección reforzada (salud, biometría, origen, etc.) | "Categorías especiales" (art. 9), prohibidas salvo excepciones | "Información personal sensible": derecho a limitar su uso |
| Derechos | Acceso, rectificación, supresión, oposición, portabilidad, bloqueo; oponerse a decisiones automatizadas | Acceso, rectificación, supresión, limitación, portabilidad, oposición; no ser objeto de decisiones solo automatizadas (art. 22) | Saber, eliminar, corregir, excluirse de la venta o uso compartido, limitar el uso de datos sensibles, no ser discriminado por ejercerlos |
| Autoridad | Agencia de Protección de Datos Personales | Una autoridad de control por país, coordinadas por el Comité Europeo de Protección de Datos | Agencia de Privacidad de California (CPPA) y la Fiscalía General |
| Sanciones (tope) | Hasta 20.000 UTM (gravísimas); a empresas grandes reincidentes, hasta el 4 % de sus ingresos | Hasta € 20 millones o el 4 % de la facturación mundial anual, lo que sea mayor | Hasta US$ 2.663 por infracción, o US$ 7.988 si es intencional o afecta a menores de 16 (montos 2025) |

Tres diferencias que importan en un proyecto de datos:

- **"Es público" no es lo mismo en todas partes.** En Chile y en la UE un dato de una fuente pública **sigue siendo dato personal** y necesita base de licitud y finalidad. La CCPA, en cambio, excluye de su definición la información puesta a disposición pública legalmente.
- **Anonimizado de verdad queda fuera de las tres; seudonimizado no.** Reemplazar el RUT por un código (seudonimizar) no saca el dato de la ley. Generalizar y suprimir celdas pequeñas (Clase 13) es lo que acerca a la anonimización.
- **Una decisión automática sobre personas** (puntaje, priorización) activa derechos adicionales en Chile y en la UE: explicación y revisión humana.

Regla práctica para el proyecto: **publiquen agregados, no microdatos**; nada con identificadores ni cuasi-identificadores sin generalizar en un repositorio o un HTML público; y si dudan, el repositorio queda privado.

Fuentes: [Ley 21.719 (BCN)](https://www.bcn.cl/leychile/navegar?idNorma=1209272) · [estado del proyecto de postergación, Boletín 18.623-07 (Senado)](https://tramitacion.senado.cl/wspublico/tramitacion.php?boletin=18623) · [RGPD, texto oficial (EUR-Lex)](https://eur-lex.europa.eu/eli/reg/2016/679/oj) · [CCPA (Fiscalía General de California)](https://oag.ca.gov/ccpa) · [CPPA, preguntas frecuentes y montos ajustados](https://cppa.ca.gov/faq.html).

## 8. La exposición final

Formato (enunciado del curso): **12 minutos + 5 de preguntas**; primero para una **audiencia no técnica**, después para una **técnica**; **ambos integrantes exponen y responden**.

**Un reparto posible de los 12 minutos:** 1 min contexto y pregunta · 3 min hallazgo y qué significa (no técnico) · 1 min transición ("ahora, cómo lo hicimos") · 4 min datos, pipeline y evaluación (técnico) · 2 min limitaciones, ética y próximos pasos · 1 min cierre con el mensaje. El error más común: pasarse en la parte técnica y apurar las conclusiones.

**La parte no técnica.** Sí: una pregunta que el público entiende, **una** cifra principal con su comparación ("acierta 8 de cada 10, frente a…"), una analogía, qué decisión permite. No: nombres de algoritmos, métricas sin traducir, código.

**La parte técnica: lo que tienen que poder defender**, en el orden en que suelen preguntar: la **métrica** (por qué esa, según el costo del error; Clase 11) · el **baseline** · la **validación** (cómo se evitó la filtración) · los **hiperparámetros** (qué se buscó y con qué presupuesto) · la **reproducibilidad** (cómo se ejecuta de principio a fin; Clases 12 y 13). Para cada uno: una frase y la celda o el archivo donde está la evidencia.

**Diapositivas.** Una idea por diapositiva · título que dice la conclusión · figura legible desde el fondo · cero párrafos para leer en voz alta · alrededor de un minuto por diapositiva.

**Reparto de la voz.** Dos o tres cambios, con una frase de transición en cada uno. Ambos entienden todo el proyecto: no repartan por "quién hizo qué" si el otro no puede responder sobre esa parte.

**Control del tiempo.** Tres puntos de control: minuto 4 (¿ya mostré el hallazgo?), minuto 8 (¿ya empecé lo técnico?), minuto 11 (¿estoy cerrando?). Tengan una versión corta de la parte técnica por si van atrasados. Ensayen con cronómetro.

**Preguntas que pueden esperar:** ¿por qué esa métrica y no la exactitud? · ¿qué pasa si llegan datos de otro año? · ¿el modelo falla más con algún grupo? · ¿para qué **no** usarías este modelo? · ¿puedo ejecutarlo yo mañana? · ¿qué harías distinto con más tiempo?

**Cómo responder:** escuchar la pregunta completa → responder lo preguntado, primero la respuesta y después el detalle → apoyar con evidencia (una cifra, una figura, una celda) → reconocer límites: "eso no lo evaluamos; lo que sí vimos es…". **No inventar.**

## 9. Checklist de comunicación del Informe 5 (provisional, a contrastar con la pauta)

- [ ] Resumen ejecutivo de cinco partes al inicio
- [ ] Cada cifra con incertidumbre, comparación y origen (celda o archivo)
- [ ] Figuras con título-mensaje, legibles, accesibles, con fuente y *n*
- [ ] Tabla de resultados generada con código (media ± desviación, orden, mejor resaltado, nota)
- [ ] Limitaciones concretas y la sección de ética, privacidad y sesgo (Clase 13)
- [ ] Declaración de uso de IA
- [ ] Reproducibilidad: README con los comandos (Clase 13)
- [ ] Dashboard: **opcional**
