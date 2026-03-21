"""
Script: ndvi_trend_analysis.py

Descripción general
-------------------
Este script evalúa la presencia de tendencias temporales en las series
mensuales de NDVI mediante métodos estadísticos paramétricos y no
paramétricos.

Se aplican:

- Regresión lineal simple para estimar tendencia y coeficiente de determinación
- Test de Mann-Kendall para detección robusta de tendencia monotónica
- Análisis de correlación entre microcuencas
- Comparación temporal conjunta

Además, se generan tablas estadísticas y promedios climáticos mensuales
y anuales de NDVI.

Entradas
--------
- Series mensuales NDVI interpoladas

Salidas
-------
- Figura multipanel de tendencias y correlación
- Tabla CSV de estadísticas de tendencia
- Promedios anuales y mensuales de NDVI

Autor: Renzo Mendoza  
Año: 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress, pearsonr
import pymannkendall as mk
import os


# =====================================================
# CONFIGURACIÓN ESTÉTICA (FORMATO REVISTA CIENTÍFICA)
# =====================================================

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.linewidth": 0.6,
    "lines.linewidth": 1.2,
    "savefig.dpi": 600,
    "savefig.bbox": "tight"
})

# =====================================================
# COLORES
# =====================================================

COLOR_MATOC = "#4FA3D9"
COLOR_POCCO = "#F4A261"
COLOR_TREND = "#6E6E6E"
COLOR_CORR_POINTS = "#7A7A7A"
COLOR_CORR_LINE = "#4D4D4D"

# =====================================================
# CREACIÓN DE DIRECTORIOS
# =====================================================

os.makedirs("outputs/figuras", exist_ok=True)
os.makedirs("outputs/estadisticas", exist_ok=True)

# =====================================================
# CARGA Y PREPARACIÓN DE DATOS
# =====================================================

matoc = pd.read_csv("outputs/csv/NDVI_MATOC_interpolado.csv")
pocco = pd.read_csv("outputs/csv/NDVI_POCCO_interpolado.csv")

matoc["Fecha"] = pd.to_datetime(matoc[['Year','Month']].assign(DAY=1))
pocco["Fecha"] = pd.to_datetime(pocco[['Year','Month']].assign(DAY=1))

matoc = matoc.sort_values("Fecha")
pocco = pocco.sort_values("Fecha")

# Unión temporal para análisis comparativo
merged = pd.merge(
    matoc[["Fecha","NDVI"]],
    pocco[["Fecha","NDVI"]],
    on="Fecha",
    suffixes=("_Matoc","_Pocco")
)

# =====================================================
# ANÁLISIS DE TENDENCIA
# =====================================================

# Regresión lineal Matoc
x_m = np.arange(len(matoc))
slope_m, intercept_m, r_m, p_m, _ = linregress(x_m, matoc["NDVI"])

# Test Mann-Kendall Matoc
mk_m = mk.original_test(matoc["NDVI"])

# Regresión lineal Pocco
x_p = np.arange(len(pocco))
slope_p, intercept_p, r_p, p_p, _ = linregress(x_p, pocco["NDVI"])

# Test Mann-Kendall Pocco
mk_p = mk.original_test(pocco["NDVI"])

# Correlación entre microcuencas
r_c, p_c = pearsonr(
    merged["NDVI_Matoc"],
    merged["NDVI_Pocco"]
)

# =====================================================
# FIGURA MULTIPANEL
# =====================================================

fig, axs = plt.subplots(2, 2, figsize=(7, 5))

# Serie temporal Matoc
axs[0,0].plot(matoc["Fecha"], matoc["NDVI"], color=COLOR_MATOC)
axs[0,0].plot(matoc["Fecha"], intercept_m + slope_m*x_m,
              linestyle="--", color=COLOR_TREND)

axs[0,0].set_ylabel("NDVI")
axs[0,0].set_title("(a) Serie temporal Matoc", loc="left")

# Serie temporal Pocco
axs[0,1].plot(pocco["Fecha"], pocco["NDVI"], color=COLOR_POCCO)
axs[0,1].plot(pocco["Fecha"], intercept_p + slope_p*x_p,
              linestyle="--", color=COLOR_TREND)

axs[0,1].set_title("(b) Serie temporal Pocco", loc="left")

# Comparación temporal
axs[1,0].plot(merged["Fecha"], merged["NDVI_Matoc"],
              color=COLOR_MATOC, label="Matoc")
axs[1,0].plot(merged["Fecha"], merged["NDVI_Pocco"],
              color=COLOR_POCCO, label="Pocco")

axs[1,0].set_ylabel("NDVI")
axs[1,0].set_xlabel("Año")
axs[1,0].set_title("(c) Comparación temporal", loc="left")
axs[1,0].legend(frameon=False)

# Correlación
axs[1,1].scatter(
    merged["NDVI_Matoc"],
    merged["NDVI_Pocco"],
    facecolors="none",
    edgecolors=COLOR_CORR_POINTS,
    s=22
)

slope_c, intercept_c, _, _, _ = linregress(
    merged["NDVI_Matoc"],
    merged["NDVI_Pocco"]
)

x_line = np.linspace(
    merged["NDVI_Matoc"].min(),
    merged["NDVI_Matoc"].max(),
    100
)

axs[1,1].plot(
    x_line,
    intercept_c + slope_c*x_line,
    linestyle="--",
    color=COLOR_CORR_LINE
)

axs[1,1].set_xlabel("Matoc")
axs[1,1].set_ylabel("Pocco")
axs[1,1].set_title("(d) Correlación NDVI", loc="left")

for ax in axs.flat:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig("outputs/figuras/Figura_3_Tendencias_NDVI.png")
plt.close()

# =====================================================
# EXPORTACIÓN DE TABLAS
# =====================================================

estadisticas = pd.DataFrame({
    "Serie": ["Matoc", "Pocco", "Correlación"],
    "Pendiente": [slope_m, slope_p, slope_c],
    "R2": [r_m**2, r_p**2, r_c**2],
    "p_valor": [p_m, p_p, p_c],
    "MannKendall": [mk_m.trend, mk_p.trend, "NA"]
})

estadisticas.to_csv(
    "outputs/estadisticas/NDVI_estadisticas_tendencia.csv",
    index=False
)

# Promedios anuales
prom_anual = pd.concat([
    matoc.groupby("Year")["NDVI"].mean().reset_index().assign(Serie="Matoc"),
    pocco.groupby("Year")["NDVI"].mean().reset_index().assign(Serie="Pocco")
])

prom_anual.to_csv(
    "outputs/estadisticas/NDVI_promedio_anual.csv",
    index=False
)

# Promedios mensuales
prom_mensual = pd.concat([
    matoc.groupby("Month")["NDVI"].mean().reset_index().assign(Serie="Matoc"),
    pocco.groupby("Month")["NDVI"].mean().reset_index().assign(Serie="Pocco")
])

prom_mensual.to_csv(
    "outputs/estadisticas/NDVI_promedio_mensual.csv",
    index=False
)

print("Análisis de tendencias NDVI completado correctamente")
