"""
Script: ndvi_classification.py

Descripción general
-------------------
Este script realiza la clasificación cualitativa del NDVI mensual en
categorías de condición de cobertura vegetal para unidades hidrográficas.

Se asignan clases interpretativas de vigor vegetal a partir de umbrales
de NDVI y se generan:

- Series clasificadas en formato CSV
- Resumen porcentual por categoría
- Figura multipanel con evolución temporal y distribución de clases

Entradas
--------
- Series mensuales NDVI interpoladas por microcuenca

Salidas
-------
- CSV con NDVI clasificado
- CSV resumen porcentual de clases
- Figura científica multipanel

Autor: Renzo Mendoza  
Año: 2026
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# =====================================================
# CONFIGURACIÓN ESTÉTICA DE FIGURAS (FORMATO ARTÍCULO)
# =====================================================

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times"],
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.linewidth": 0.6,
    "savefig.dpi": 600,
    "savefig.bbox": "tight"
})

# =====================================================
# CREACIÓN DE CARPETAS DE SALIDA
# =====================================================

os.makedirs("outputs/clasificacion", exist_ok=True)
os.makedirs("outputs/figuras", exist_ok=True)

# =====================================================
# FUNCIÓN DE CLASIFICACIÓN NDVI
# =====================================================

def clasificar_ndvi(valor):
    """
    Clasifica un valor de NDVI en categorías cualitativas de cobertura vegetal.

    Umbrales utilizados:
    - NDVI < 0.10 → Vegetación muy baja
    - 0.10–0.20 → Vegetación baja
    - 0.20–0.35 → Vegetación moderada
    - > 0.35 → Vegetación alta

    Parámetros
    ----------
    valor : float
        Valor mensual de NDVI.

    Retorna
    -------
    str
        Clase cualitativa de vegetación.
    """
    if valor < 0.10:
        return "Vegetación muy baja"
    elif valor < 0.20:
        return "Vegetación baja"
    elif valor < 0.35:
        return "Vegetación moderada"
    else:
        return "Vegetación alta"


orden_clases = [
    "Vegetación muy baja",
    "Vegetación baja",
    "Vegetación moderada",
    "Vegetación alta"
]

# =====================================================
# PALETA CLÁSICA DE NDVI
# =====================================================

colores = {
    "Vegetación muy baja": "#d73027",
    "Vegetación baja": "#fdae61",
    "Vegetación moderada": "#a6d96a",
    "Vegetación alta": "#1a9850"
}

# =====================================================
# CARGA DE SERIES NDVI
# =====================================================

matoc = pd.read_csv("outputs/csv/NDVI_MATOC_interpolado.csv")
pocco = pd.read_csv("outputs/csv/NDVI_POCCO_interpolado.csv")

for df in [matoc, pocco]:
    df["Fecha"] = pd.to_datetime(df[['Year','Month']].assign(DAY=1))
    df["Clase"] = df["NDVI"].apply(clasificar_ndvi)

# =====================================================
# EXPORTACIÓN DE SERIES CLASIFICADAS
# =====================================================

matoc.to_csv("outputs/clasificacion/NDVI_MATOC_clasificado.csv", index=False)
pocco.to_csv("outputs/clasificacion/NDVI_POCCO_clasificado.csv", index=False)

# =====================================================
# RESUMEN PORCENTUAL DE CLASES
# =====================================================

resumen = pd.DataFrame({
    "Clase": orden_clases,
    "Matoc (%)": matoc["Clase"].value_counts(normalize=True).reindex(orden_clases).values * 100,
    "Pocco (%)": pocco["Clase"].value_counts(normalize=True).reindex(orden_clases).values * 100
})

resumen.to_csv("outputs/clasificacion/NDVI_resumen_clases.csv", index=False)

# =====================================================
# GENERACIÓN DE FIGURA MULTIPANEL
# =====================================================

fig, axs = plt.subplots(
    2, 2,
    figsize=(7, 5),
    gridspec_kw={"height_ratios": [1.2, 1]}
)

# Evolución temporal Matoc
for clase in orden_clases:
    subset = matoc[matoc["Clase"] == clase]
    axs[0,0].scatter(
        subset["Fecha"],
        subset["NDVI"],
        s=12,
        color=colores[clase],
        alpha=0.9,
        edgecolors='none',
        label=clase
    )

axs[0,0].axhline(
    matoc["NDVI"].mean(),
    color='gray',
    linestyle='--',
    linewidth=0.7
)

axs[0,0].set_title("(a) Clasificación NDVI – Matoc", loc="left")
axs[0,0].set_ylabel("NDVI")
axs[0,0].set_ylim(-0.05, 0.6)

axs[0,0].legend(frameon=False, loc="upper left", ncol=2, fontsize=6)

# Evolución temporal Pocco
for clase in orden_clases:
    subset = pocco[pocco["Clase"] == clase]
    axs[0,1].scatter(
        subset["Fecha"],
        subset["NDVI"],
        s=12,
        color=colores[clase],
        alpha=0.9,
        edgecolors='none'
    )

axs[0,1].axhline(
    pocco["NDVI"].mean(),
    color='gray',
    linestyle='--',
    linewidth=0.7
)

axs[0,1].set_title("(b) Clasificación NDVI – Pocco", loc="left")
axs[0,1].set_ylim(-0.05, 0.6)

# Distribución Matoc
axs[1,0].bar(
    resumen["Clase"],
    resumen["Matoc (%)"],
    color=[colores[c] for c in resumen["Clase"]],
    width=0.55
)

axs[1,0].set_title("(c) Distribución porcentual – Matoc", loc="left")
axs[1,0].set_ylabel("%")

# Distribución Pocco
axs[1,1].bar(
    resumen["Clase"],
    resumen["Pocco (%)"],
    color=[colores[c] for c in resumen["Clase"]],
    width=0.55
)

axs[1,1].set_title("(d) Distribución porcentual – Pocco", loc="left")

# Estética final
for ax in axs.flat:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

plt.subplots_adjust(hspace=0.35, wspace=0.25)

plt.savefig("outputs/figuras/Figura_Clasificacion_Cualitativa_NDVI.png")
plt.close()

print("Figura de clasificación NDVI exportada correctamente.")
