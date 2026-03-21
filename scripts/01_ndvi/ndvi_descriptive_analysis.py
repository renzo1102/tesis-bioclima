"""
Script: ndvi_descriptive_analysis.py
Descripción:
Calcula estadísticas descriptivas del NDVI
Entradas:
NDVI mensual

Salidas:
Estadísticos, gráficos

Autor: Renzo Mendoza
Año: 2026
"""
# =====================================================
# SCRIPT 3
# Exporta CSV originales (sin interpolar)
# =====================================================

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


# =====================================================
# CONFIGURACIÓN DE ESTILO (ARTÍCULO CIENTÍFICO)
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
# COLORES
# =====================================================

COLOR_MATOC = "#4FA3D9"   # celeste
COLOR_POCCO = "#F4A261"   # naranja claro
COLOR_BOX = "#B0B0B0"     # gris científico

# =====================================================
# CARPETAS
# =====================================================

os.makedirs("outputs/figuras", exist_ok=True)
os.makedirs("outputs/estadisticas", exist_ok=True)

# =====================================================
# CARGAR SERIES
# =====================================================

matoc = pd.read_csv("outputs/csv/NDVI_MATOC.csv")
pocco = pd.read_csv("outputs/csv/NDVI_POCCO.csv")

matoc["Fecha"] = pd.to_datetime(matoc[['Year','Month']].assign(DAY=1))
pocco["Fecha"] = pd.to_datetime(pocco[['Year','Month']].assign(DAY=1))

# =====================================================
# ESTADÍSTICA DESCRIPTIVA
# =====================================================

def resumen(df, nombre):
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

tabla = pd.DataFrame([
    resumen(matoc, "Matoc"),
    resumen(pocco, "Pocco")
])

tabla.to_csv(
    "outputs/estadisticas/NDVI_resumen_descriptivo.csv",
    index=False
)

# =====================================================
# MENSAJES EN TERMINAL
# =====================================================

print("\nResumen estadístico NDVI")
print(tabla)
print("\nDistribución lista para inspección visual")

# =====================================================
# FIGURA MULTIPANEL
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

# (b) Distribución
axs[1].hist(
    matoc["NDVI"].dropna(),
    bins=18, color=COLOR_MATOC, alpha=0.6, label="Matoc"
)
axs[1].hist(
    pocco["NDVI"].dropna(),
    bins=18, color=COLOR_POCCO, alpha=0.6, label="Pocco"
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

print("\nFigura diagnóstica exportada correctamente")
