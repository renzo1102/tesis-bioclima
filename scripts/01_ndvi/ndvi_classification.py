"""
Script: ndvi_classification.py
Descripción:
Clasifica NDVI en categorías cualitativas
Entradas:
NDVI mensual
Salidas:
NDVI clasificado

Autor: Renzo Mendoza
Año: 2026
"""
# =====================================================
# SCRIPT 6
# Clasificación cualitativa de NDVI por UH
# =====================================================

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# =====================================================
# ESTILO (igual que versión anterior)
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
# CARPETAS
# =====================================================

os.makedirs("outputs/clasificacion", exist_ok=True)
os.makedirs("outputs/figuras", exist_ok=True)

# =====================================================
# FUNCIÓN CLASIFICACIÓN NDVI
# =====================================================

def clasificar_ndvi(valor):
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
# PALETA NDVI CLÁSICA
# =====================================================

colores = {
    "Vegetación muy baja": "#d73027",
    "Vegetación baja": "#fdae61",
    "Vegetación moderada": "#a6d96a",
    "Vegetación alta": "#1a9850"
}

# =====================================================
# CARGAR DATOS
# =====================================================

matoc = pd.read_csv("outputs/csv/NDVI_MATOC_interpolado.csv")
pocco = pd.read_csv("outputs/csv/NDVI_POCCO_interpolado.csv")

for df in [matoc, pocco]:
    df["Fecha"] = pd.to_datetime(df[['Year','Month']].assign(DAY=1))
    df["Clase"] = df["NDVI"].apply(clasificar_ndvi)

# =====================================================
# EXPORTAR CSV CLASIFICADOS
# =====================================================

matoc.to_csv("outputs/clasificacion/NDVI_MATOC_clasificado.csv", index=False)
pocco.to_csv("outputs/clasificacion/NDVI_POCCO_clasificado.csv", index=False)

# =====================================================
# RESUMEN PORCENTUAL
# =====================================================

resumen = pd.DataFrame({
    "Clase": orden_clases,
    "Matoc (%)": matoc["Clase"].value_counts(normalize=True).reindex(orden_clases).values * 100,
    "Pocco (%)": pocco["Clase"].value_counts(normalize=True).reindex(orden_clases).values * 100
})

resumen.to_csv("outputs/clasificacion/NDVI_resumen_clases.csv", index=False)

# =====================================================
# FIGURA MULTIPANEL
# =====================================================

fig, axs = plt.subplots(
    2, 2,
    figsize=(7, 5),
    gridspec_kw={"height_ratios": [1.2, 1]}
)

# -----------------------
# (a) Matoc
# -----------------------

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

# Línea media
axs[0,0].axhline(
    matoc["NDVI"].mean(),
    color='gray',
    linestyle='--',
    linewidth=0.7,
    alpha=0.8
)

axs[0,0].set_title("(a) Clasificación NDVI – Matoc", loc="left")
axs[0,0].set_ylabel("NDVI")
axs[0,0].set_ylim(-0.05, 0.6)

# Leyenda compacta
axs[0,0].legend(
    frameon=False,
    loc="upper left",
    ncol=2,
    fontsize=6,
    handlelength=1.2,
    handletextpad=0.3,
    columnspacing=0.8,
    borderpad=0.2,
    markerscale=0.8
)

# -----------------------
# (b) Pocco
# -----------------------

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

# Línea media
axs[0,1].axhline(
    pocco["NDVI"].mean(),
    color='gray',
    linestyle='--',
    linewidth=0.7,
    alpha=0.8
)

axs[0,1].set_title("(b) Clasificación NDVI – Pocco", loc="left")
axs[0,1].set_ylim(-0.05, 0.6)

# -----------------------
# (c) Distribución Matoc
# -----------------------

axs[1,0].bar(
    resumen["Clase"],
    resumen["Matoc (%)"],
    color=[colores[c] for c in resumen["Clase"]],
    width=0.55
)

axs[1,0].set_title("(c) Distribución porcentual – Matoc", loc="left")
axs[1,0].set_ylabel("%")
axs[1,0].set_ylim(0, resumen["Matoc (%)"].max()*1.15)
axs[1,0].tick_params(axis="x", labelsize=6)

# -----------------------
# (d) Distribución Pocco
# -----------------------

axs[1,1].bar(
    resumen["Clase"],
    resumen["Pocco (%)"],
    color=[colores[c] for c in resumen["Clase"]],
    width=0.55
)

axs[1,1].set_title("(d) Distribución porcentual – Pocco", loc="left")
axs[1,1].set_ylim(0, resumen["Pocco (%)"].max()*1.15)
axs[1,1].tick_params(axis="x", labelsize=6)

# =====================================================
# ESTÉTICA FINAL
# =====================================================

for ax in axs.flat:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(width=0.6, length=3)

plt.subplots_adjust(hspace=0.35, wspace=0.25)

plt.savefig("outputs/figuras/Figura_Clasificacion_Cualitativa_NDVI.png")
plt.close()

print("Figura final exportada correctamente.")
