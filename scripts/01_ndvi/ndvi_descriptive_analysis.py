"""
Script: ndvi_descriptive_analysis.py

Descripción general
-------------------
Este script realiza el análisis estadístico descriptivo de las series
mensuales de NDVI para unidades hidrográficas.

Se calculan métricas básicas de tendencia central, dispersión y
completitud temporal, y se generan gráficos diagnósticos que permiten
evaluar:

- Variabilidad temporal del NDVI
- Distribución de valores
- Comparación estadística entre microcuencas

Entradas
--------
- Series mensuales de NDVI sin interpolación

Salidas
-------
- Tabla CSV con estadísticos descriptivos
- Figura multipanel diagnóstica

Autor: Renzo Mendoza  
Año: 2026
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


# =====================================================
# CONFIGURACIÓN DE ESTILO (FORMATO ARTÍCULO CIENTÍFICO)
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
    "lines.linewidth": 1.4,
    "savefig.dpi": 600,
    "savefig.bbox": "tight"
})

# =====================================================
# DEFINICIÓN DE COLORES
# =====================================================

COLOR_MATOC = "#4FA3D9"
COLOR_POCCO = "#F4A261"
COLOR_BOX = "#B0B0B0"

# =====================================================
# CREACIÓN DE CARPETAS DE SALIDA
# =====================================================

os.makedirs("outputs/figuras", exist_ok=True)
os.makedirs("outputs/estadisticas", exist_ok=True)

# =====================================================
# CARGA DE SERIES NDVI
# =====================================================

matoc = pd.read_csv("outputs/csv/NDVI_MATOC.csv")
pocco = pd.read_csv("outputs/csv/NDVI_POCCO.csv")

matoc["Fecha"] = pd.to_datetime(matoc[['Year','Month']].assign(DAY=1))
pocco["Fecha"] = pd.to_datetime(pocco[['Year','Month']].assign(DAY=1))


# =====================================================
# FUNCIÓN DE RESUMEN ESTADÍSTICO
# =====================================================

def resumen(df, nombre):
    """
    Calcula estadísticos descriptivos básicos para una serie de NDVI.

    Parámetros
    ----------
    df : pandas.DataFrame
        DataFrame que contiene la columna NDVI.

    nombre : str
        Nombre identificador de la serie (microcuenca).

    Retorna
    -------
    dict
        Diccionario con métricas descriptivas.
    """
    return {
        "Serie": nombre,
        "N": df["NDVI"].count(),
        "Media": df["NDVI"].mean(),
        "Mediana": df["NDVI"].median(),
        "Desv_std": df["NDVI"].std(),
        "Min": df["NDVI"].min(),
        "Max": df["NDVI"].max(),
        "Meses_vacios": df["NDVI"].isna().sum()
    }


# =====================================================
# CONSTRUCCIÓN DE TABLA DESCRIPTIVA
# =====================================================

tabla = pd.DataFrame([
    resumen(matoc, "Matoc"),
    resumen(pocco, "Pocco")
])

tabla.to_csv(
    "outputs/estadisticas/NDVI_resumen_descriptivo.csv",
    index=False
)

print("\nResumen estadístico NDVI")
print(tabla)
print("\nDistribución lista para inspección visual")


# =====================================================
# GENERACIÓN DE FIGURA DIAGNÓSTICA MULTIPANEL
# =====================================================

fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.6))

# (a) Serie temporal
axs[0].plot(
    matoc["Fecha"], matoc["NDVI"],
    color=COLOR_MATOC, label="Matoc"
)
axs[0].plot(
    pocco["Fecha"], pocco["NDVI"],
    color=COLOR_POCCO, label="Pocco"
)

axs[0].set_ylabel("NDVI")
axs[0].set_title("(a) Serie temporal mensual", loc="left")
axs[0].legend(frameon=False)

# (b) Distribución de frecuencias
axs[1].hist(
    matoc["NDVI"].dropna(),
    bins=18, color=COLOR_MATOC, alpha=0.6
)
axs[1].hist(
    pocco["NDVI"].dropna(),
    bins=18, color=COLOR_POCCO, alpha=0.6
)

axs[1].set_xlabel("NDVI")
axs[1].set_ylabel("Frecuencia")
axs[1].set_title("(b) Distribución NDVI", loc="left")

# (c) Comparación estadística
axs[2].boxplot(
    [matoc["NDVI"].dropna(), pocco["NDVI"].dropna()],
    labels=["Matoc", "Pocco"],
    patch_artist=True,
    boxprops=dict(facecolor=COLOR_BOX, color="black", linewidth=0.8),
    medianprops=dict(color="black", linewidth=1.1),
    whiskerprops=dict(linewidth=0.8),
    capprops=dict(linewidth=0.8)
)

axs[2].set_ylabel("NDVI")
axs[2].set_title("(c) Comparación estadística", loc="left")

# Limpieza estética
for ax in axs:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(width=0.6, length=3)

plt.tight_layout()
plt.savefig("outputs/figuras/Figura_2a_Diagnostico_NDVI.png")
plt.close()

print("\nFigura diagnóstica NDVI exportada correctamente")
