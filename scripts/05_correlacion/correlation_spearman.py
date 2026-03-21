"""
Script: correlation_spearman.py

Descripción:
Correlación Spearman

Entradas:
Dataset

Salidas:
Matriz

Autor: Renzo Mendoza
Año: 2026
"""
# ======================================================
# SCRIPT 3
# Prueba de normalidad (Shapiro-Wilk + Q-Q plots)
# ======================================================

import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.stats import shapiro
import os

# ======================================
# Crear carpetas
# ======================================

os.makedirs("resultados/tablas", exist_ok=True)
os.makedirs("resultados/graficas", exist_ok=True)

# ======================================
# Cargar datos
# ======================================

matoc = pd.read_csv("resultados/tablas/matoc_datos.csv")
pocco = pd.read_csv("resultados/tablas/pocco_datos.csv")

# ======================================
# Variables
# ======================================

variables = ["P_mm","Tmed_c","ndvi","Q_mm"]
nombres = ["Precipitación","Temperatura","NDVI","Caudal"]

# ======================================
# Colores suaves
# ======================================

color_matoc = "#6BAED6"
color_pocco = "#FDAE6B"

# ======================================
# PRUEBA SHAPIRO
# ======================================

resultados = []

for var in variables:

    stat_m, p_m = shapiro(matoc[var].dropna())
    stat_p, p_p = shapiro(pocco[var].dropna())

    resultados.append([var,stat_m,p_m,stat_p,p_p])

tabla = pd.DataFrame(
    resultados,
    columns=["Variable","W_Matoc","p_Matoc","W_Pocco","p_Pocco"]
)

tabla.to_csv(
    "resultados/tablas/prueba_normalidad_shapiro.csv",
    index=False
)

# ======================================================
# FUNCIÓN PARA Q-Q PLOT
# ======================================================

def qqplot(ax, data, color, titulo, pvalue):

    (osm, osr), (slope, intercept, r) = stats.probplot(data, dist="norm")

    ax.scatter(osm, osr, color=color, alpha=0.8)
    ax.plot(osm, slope*osm + intercept, color="gray")

    ax.set_title(titulo, loc="left")
    ax.text(
        0.05,
        0.9,
        f"p = {pvalue:.3f}",
        transform=ax.transAxes,
        fontsize=10
    )

# ======================================================
# FIGURA 1 — MATOC
# ======================================================

fig, ax = plt.subplots(2,2, figsize=(9,8))

for i,var in enumerate(variables):

    fila = i//2
    col = i%2

    stat,p = shapiro(matoc[var].dropna())

    qqplot(
        ax[fila,col],
        matoc[var].dropna(),
        color_matoc,
        f"{chr(97+i)}) {nombres[i]}",
        p
    )

plt.suptitle("Normalidad – Matoc")

plt.tight_layout()

plt.savefig(
    "resultados/graficas/normalidad_matoc.png",
    dpi=400,
    bbox_inches="tight"
)

plt.close()

# ======================================================
# FIGURA 2 — POCCO
# ======================================================

fig, ax = plt.subplots(2,2, figsize=(9,8))

for i,var in enumerate(variables):

    fila = i//2
    col = i%2

    stat,p = shapiro(pocco[var].dropna())

    qqplot(
        ax[fila,col],
        pocco[var].dropna(),
        color_pocco,
        f"{chr(97+i)}) {nombres[i]}",
        p
    )

plt.suptitle("Normalidad – Pocco")

plt.tight_layout()

plt.savefig(
    "resultados/graficas/normalidad_pocco.png",
    dpi=400,
    bbox_inches="tight"
)

plt.close()

print("✔ Pruebas de normalidad completadas")
