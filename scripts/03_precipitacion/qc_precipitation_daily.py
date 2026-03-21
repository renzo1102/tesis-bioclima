"""
Script: qc_precipitation_daily.py

Descripción general
-------------------
Este script implementa un control de calidad multietapa para
series diarias de precipitación provenientes de estaciones
pluviométricas ubicadas en las unidades hidrográficas de estudio
y estaciones regionales de referencia.

El procedimiento combina criterios:

- Plausibilidad física del dato
- Detección de outliers mediante IQR por época hidrológica
- Identificación de ceros inconsistentes dentro de eventos lluviosos
- Evaluación de coherencia temporal
- Consistencia climática respecto a fase ENSO

Cada observación diaria es clasificada como:
- Aceptado: registro consistente
- Revisar: posible outlier o inconsistencia
- Completar: dato físicamente inválido o faltante

Entradas
--------
Archivos Excel diarios por estación ubicados en data/raw/

Salidas
-------
- Series clasificadas según QC
- Figuras tipo panel estilo publicación científica

Autor: Renzo Mendoza
Año: 2026
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ==========================================================
# 1. CONFIGURACIÓN DE RUTAS
# ==========================================================
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_RAW = BASE_DIR / "data" / "raw"
OUTPUTS = BASE_DIR / "outputs" / "qc_individual"
TABLAS = OUTPUTS / "tablas"
FIGURAS = OUTPUTS / "figuras"

TABLAS.mkdir(parents=True, exist_ok=True)
FIGURAS.mkdir(parents=True, exist_ok=True)


# ==========================================================
# 2. CONFIGURACIÓN GRÁFICA
# ==========================================================
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11
})

COLOR_SERIE_ANA = "#238b45"
COLOR_SERIE_UH  = "#1f78b4"

COLOR_OK   = "#fdae61"
COLOR_REV  = "#d73027"
COLOR_COMP = "#bdbdbd"


# ==========================================================
# 3. INFORMACIÓN CLIMÁTICA ENSO
# ==========================================================
ENSO = {
    2011: "Neutro", 2012: "Niño", 2013: "Niña",
    2014: "Niño", 2015: "Niño", 2016: "Niño",
    2017: "Niño", 2018: "Niña", 2019: "Neutro",
    2020: "Niña", 2021: "Niña", 2022: "Niña",
    2023: "Niño", 2024: "Niño"
}


# ==========================================================
# 4. FUNCIONES DE CONTROL DE CALIDAD
# ==========================================================

def clasificar_epoca(fecha):
    """
    Clasifica la fecha según época hidrológica.
    Lluviosa: octubre – abril
    Seca: mayo – septiembre
    """
    return "Lluviosa" if fecha.month in [10,11,12,1,2,3,4] else "Seca"


def qc_fisico(p):
    """
    Verifica plausibilidad física de la precipitación diaria.
    """
    return (p >= 0) & (p <= 300)


def qc_iqr_por_epoca(df):
    """
    Detecta outliers usando el método IQR
    aplicado separadamente por época hidrológica.
    """
    df = df.copy()
    df["Epoca"] = df["fecha"].apply(clasificar_epoca)
    flag = pd.Series(True, index=df.index)

    for epoca in ["Lluviosa", "Seca"]:
        sub = df.loc[df["Epoca"] == epoca, "precipitacion_mm"]
        if sub.count() < 10:
            continue

        q1, q3 = sub.quantile([0.25, 0.75])
        iqr = q3 - q1
        li, ls = q1 - 1.5 * iqr, q3 + 1.5 * iqr

        idx = df[df["Epoca"] == epoca].index
        flag.loc[idx] = df.loc[idx, "precipitacion_mm"].between(li, ls)

    return flag


def qc_ceros(series):
    """
    Identifica ceros inconsistentes dentro de eventos lluviosos.
    """
    flag = []
    for i in range(len(series)):
        if series.iloc[i] == 0 and 0 < i < len(series)-1:
            flag.append(not (series.iloc[i-1] > 1 and series.iloc[i+1] > 1))
        else:
            flag.append(True)
    return pd.Series(flag, index=series.index)


def qc_temporal(series):
    """
    Evalúa coherencia temporal mediante cambios extremos diarios.
    """
    return series.diff().abs() <= series.diff().abs().quantile(0.99)


def qc_enso(df):
    """
    Evalúa consistencia climática considerando la fase ENSO.
    """
    df = df.copy()
    df["ENSO"] = df["fecha"].dt.year.map(ENSO)
    p95 = df["precipitacion_mm"].quantile(0.95)
    return ~((df["ENSO"] == "Neutro") & (df["precipitacion_mm"] > p95))


# ==========================================================
# 5. FUNCIÓN EJECUCIÓN QC COMPLETO
# ==========================================================

def ejecutar_qc(df, uh, estacion):
    """
    Ejecuta control de calidad combinando todos los criterios.
    """
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha")

    p = df["precipitacion_mm"]

    df["QC_Fisico"] = qc_fisico(p)
    df["QC_IQR"] = qc_iqr_por_epoca(df)
    df["QC_Ceros"] = qc_ceros(p)
    df["QC_Temporal"] = qc_temporal(p)
    df["QC_ENSO"] = qc_enso(df)

    def decision(r):
        if not r["QC_Fisico"]:
            return "Completar"
        elif not (r["QC_IQR"] and r["QC_Ceros"] and r["QC_Temporal"] and r["QC_ENSO"]):
            return "Revisar"
        else:
            return "Aceptado"

    df["Decision"] = df.apply(decision, axis=1)
    df["UH"] = uh
    df["Estacion"] = estacion

    return df


# ==========================================================
# 6. LECTURA Y APLICACIÓN QC
# ==========================================================

qc_total = []

for archivo in DATA_RAW.glob("*.xlsx"):
    uh = archivo.stem.split("_")[0]
    estacion = archivo.stem
    df = pd.read_excel(archivo)[["fecha", "precipitacion_mm"]]
    qc = ejecutar_qc(df, uh, estacion)
    qc_total.append(qc)

qc_total = pd.concat(qc_total, ignore_index=True)


# ==========================================================
# 7. FUNCIÓN PARA GENERAR PANELES GRÁFICOS
# ==========================================================

def panel_series(df, estaciones, titulo, color_linea, nombre):
    """
    Genera paneles gráficos mostrando resultados del QC.
    """
    n = len(estaciones)
    fig, axes = plt.subplots(n, 1, figsize=(18, 4*n), sharex=True)

    if n == 1:
        axes = [axes]

    for ax, est in zip(axes, estaciones):
        d = df[df["Estacion"] == est].sort_values("fecha")

        ax.plot(d["fecha"], d["precipitacion_mm"],
                color=color_linea, lw=0.9, alpha=0.6)

        a = d[d["Decision"] == "Aceptado"]
        ax.scatter(a["fecha"], a["precipitacion_mm"], s=14)

        ax.set_title(est, loc="left")
        ax.set_ylabel("Precipitación (mm)")
        ax.grid(True, linestyle="--", alpha=0.25)

    axes[-1].set_xlabel("Año")

    fig.suptitle(titulo)
    fig.tight_layout()
    fig.savefig(FIGURAS / nombre, dpi=600)
    plt.close()


# ==========================================================
# 8. GENERACIÓN DE FIGURAS
# ==========================================================

panel_series(
    qc_total,
    qc_total["Estacion"].unique(),
    "Series de precipitación diaria y control de calidad",
    COLOR_SERIE_UH,
    "Panel_QC.png"
)

print("Figuras generadas correctamente.")
