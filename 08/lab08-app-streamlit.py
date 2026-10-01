"""Lab 08 · Ejemplo de dashboard nivel 3 (Streamlit). Opcional: no es parte de la verificación del lab.

Requisitos: haber ejecutado el Setup y la celda de generación del notebook (crea data_practica/).
Correr desde la carpeta 08/:

    streamlit run lab08-app-streamlit.py

y abrir http://localhost:8501. Se detiene con Ctrl+C en la terminal.
Datos sintéticos: ninguna cifra describe a una comuna o establecimiento real.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

RUTA = Path(__file__).parent / "data_practica" / "asistencia_mensual.csv"
MESES = {3: "mar", 4: "abr", 5: "may", 6: "jun", 7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"}

st.set_page_config(page_title="Asistencia escolar · Lab 08", layout="wide")


@st.cache_data                     # lee y limpia una sola vez, no en cada clic
def cargar(ruta):
    df = pd.read_csv(ruta, dtype={"rbd": str, "cod_comuna": str}, parse_dates=["fecha"])
    df.loc[df.asistencia_pct == 0.0, "asistencia_pct"] = float("nan")   # los 40 ceros son faltantes (Ej. 2)
    return df


if not RUTA.exists():
    st.error(f"No encuentro {RUTA}. Ejecuten primero el Setup y la generación de datos del notebook.")
    st.stop()
df = cargar(RUTA)

# --- Filtros ------------------------------------------------------------------
st.sidebar.header("Filtros")
comuna = st.sidebar.selectbox("Comuna", ["Todas"] + sorted(df.comuna.unique()))
deps = st.sidebar.multiselect("Dependencia", sorted(df.dependencia.unique()), default=sorted(df.dependencia.unique()))
if not deps:
    st.warning("Elijan al menos una dependencia.")
    st.stop()

d = df[df.dependencia.isin(deps)]
if comuna != "Todas":
    d = d[d.comuna == comuna]

# --- Tarjetas -----------------------------------------------------------------
st.title(f"Asistencia escolar — {comuna}")
st.caption("Datos sintéticos del Lab 08 · 2023–2025 · ceros reemplazados por faltantes")

p23 = d.loc[d.anio == 2023, "asistencia_pct"].mean()
p25 = d.loc[d.anio == 2025, "asistencia_pct"].mean()
estac = d.groupby("mes").asistencia_pct.mean()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Asistencia 2025", f"{p25:.1f} %")
c2.metric("Cambio vs. 2023", f"{p25 - p23:+.1f} pp")
c3.metric("Mes más bajo", MESES[estac.idxmin()], f"{estac.min():.1f} %", delta_color="off")
c4.metric("Establecimientos (n)", d.rbd.nunique())

# --- Vistas (todas usan el mismo d filtrado) ----------------------------------
izq, der = st.columns([2, 1])
izq.subheader("Serie mensual por dependencia (%)")
izq.line_chart(d.pivot_table(index="fecha", columns="dependencia", values="asistencia_pct"))
der.subheader("Promedio por mes calendario (%)")
der.bar_chart(estac.rename(index=lambda m: f"{m:02d}-{MESES[m]}"))   # "03-mar": así el orden alfabético es el del calendario

st.subheader("Cambio 2023 → 2025 por comuna (pp), con los filtros de dependencia")
cambio = (df[df.dependencia.isin(deps)]
          .pivot_table(index="comuna", columns="anio", values="asistencia_pct")
          .assign(cambio_pp=lambda t: t[2025] - t[2023])
          .sort_values("cambio_pp")[["cambio_pp"]])
st.dataframe(cambio.style.format("{:+.1f}"))

with st.expander("Ver datos filtrados"):
    st.dataframe(d)
