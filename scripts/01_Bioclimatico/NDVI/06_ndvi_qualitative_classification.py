# =====================================================
# SCRIPT 6
# Clasificación cualitativa de NDVI
# Generación de categorías de vegetación y análisis porcentual
# =====================================================

# =====================================================
# DESCRIPCIÓN GENERAL
# =====================================================
# Este script realiza la clasificación cualitativa de las series
# NDVI interpoladas en categorías de cobertura vegetal.
#
# Objetivos:
# - Clasificar valores NDVI en niveles de vegetación
# - Generar datasets clasificados
# - Calcular distribución porcentual por clase
# - Visualizar patrones temporales y distribución
#
# Salidas:
# - CSV clasificados por cuenca
# - Tabla resumen de porcentajes
# - Figura multipanel de clasificación

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# =====================================================
# CONFIGURACIÓN DE ESTILO
# =====================================================
# Se define un estilo gráfico consistente con figuras científicas.

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
# CREACIÓN DE CARPETAS
# =====================================================
# Se crean directorios para almacenar resultados.

os.makedirs("outputs/clasificacion", exist_ok=True)
os.makedirs("outputs/figuras", exist_ok=True)

# =====================================================
# FUNCIÓN: clasificar_ndvi
# =====================================================
# Clasifica valores NDVI en categorías cualitativas.
#
# Umbrales:
# - < 0.10 → Vegetación muy baja
# - 0.10–0.20 → Vegetación baja
# - 0.20–0.35 → Vegetación moderada
# - > 0.35 → Vegetación alta
#
# Entrada:
# - valor NDVI
#
# Salida:
# - Categoría de vegetación (string)

def clasificar_ndvi(valor):
    if valor < 0.10:
        return "Vegetación muy baja"
    elif valor < 0.20:
        return "Vegetación baja"
    elif valor < 0.35:
        return "Vegetación moderada"
    else:
        return "Vegetación alta"

# Orden de clases (importante para gráficos y tablas)
orden_clases = [
    "Vegetación muy baja",
    "Vegetación baja",
    "Vegetación moderada",
    "Vegetación alta"
]

# Abreviaturas para visualización compacta en gráficos
abreviaturas = {
    "Vegetación muy baja": "VMB",
    "Vegetación baja": "VB",
    "Vegetación moderada": "VM",
    "Vegetación alta": "VA"
}

# =====================================================
# PALETA DE COLORES
# =====================================================
# Escala clásica de NDVI (de baja a alta vegetación)

colores = {
    "Vegetación muy baja": "#d73027",
    "Vegetación baja": "#fdae61",
    "Vegetación moderada": "#a6d96a",
    "Vegetación alta": "#1a9850"
}

# =====================================================
# CARGA DE DATOS
# =====================================================
# Se leen las series interpoladas generadas previamente.

matoc = pd.read_csv("outputs/csv/NDVI_MATOC_interpolado.csv")
pocco = pd.read_csv("outputs/csv/NDVI_POCCO_interpolado.csv")

# Construcción de fecha y clasificación
for df in [matoc, pocco]:
    df["Fecha"] = pd.to_datetime(df[['Year','Month']].assign(DAY=1))
    df["Clase"] = df["NDVI"].apply(clasificar_ndvi)

# =====================================================
# EXPORTACIÓN DE DATOS CLASIFICADOS
# =====================================================
# Se generan archivos con la clase asignada a cada registro.

matoc.to_csv("outputs/clasificacion/NDVI_MATOC_clasificado.csv", index=False)
pocco.to_csv("outputs/clasificacion/NDVI_POCCO_clasificado.csv", index=False)

# =====================================================
# RESUMEN PORCENTUAL
# =====================================================
# Se calcula la proporción de cada clase en ambas cuencas.

resumen = pd.DataFrame({
    "Clase": orden_clases,
    "Matoc (%)": matoc["Clase"].value_counts(normalize=True).reindex(orden_clases).values * 100,
    "Pocco (%)": pocco["Clase"].value_counts(normalize=True).reindex(orden_clases).values * 100
})

resumen.to_csv("outputs/clasificacion/NDVI_resumen_clases.csv", index=False)

# =====================================================
# FIGURA MULTIPANEL
# =====================================================
# Se generan cuatro paneles:
# (a) Clasificación temporal Matoc
# (b) Clasificación temporal Pocco
# (c) Distribución porcentual Matoc
# (d) Distribución porcentual Pocco

fig, axs = plt.subplots(
    2, 2,
    figsize=(7, 5),
    gridspec_kw={"height_ratios": [1.2, 1]}
)

# -----------------------------------------------------
# (a) Matoc
# -----------------------------------------------------
# Dispersión temporal coloreada por clase

for clase in orden_clases:
    subset = matoc[matoc["Clase"] == clase]
    axs[0,0].scatter(
        subset["Fecha"],
        subset["NDVI"],
        s=12,
        color=colores[clase],
        alpha=0.9,
        edgecolors='none',
        label=abreviaturas[clase]
    )

# Línea de promedio
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

# -----------------------------------------------------
# (b) Pocco
# -----------------------------------------------------

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
    linewidth=0.7,
    alpha=0.8
)

axs[0,1].set_title("(b) Clasificación NDVI – Pocco", loc="left")
axs[0,1].set_ylim(-0.05, 0.6)

# -----------------------------------------------------
# (c) Distribución Matoc
# -----------------------------------------------------

axs[1,0].bar(
    resumen["Clase"],
    resumen["Matoc (%)"],
    color=[colores[c] for c in resumen["Clase"]],
    width=0.55
)

axs[1,0].set_xticks(range(len(resumen["Clase"])))
axs[1,0].set_xticklabels([abreviaturas[c] for c in resumen["Clase"]])

axs[1,0].set_title("(c) Distribución porcentual – Matoc", loc="left")
axs[1,0].set_ylabel("%")
axs[1,0].set_ylim(0, resumen["Matoc (%)"].max()*1.15)
axs[1,0].tick_params(axis="x", labelsize=6)

# -----------------------------------------------------
# (d) Distribución Pocco
# -----------------------------------------------------

axs[1,1].bar(
    resumen["Clase"],
    resumen["Pocco (%)"],
    color=[colores[c] for c in resumen["Clase"]],
    width=0.55
)

axs[1,1].set_xticks(range(len(resumen["Clase"])))
axs[1,1].set_xticklabels([abreviaturas[c] for c in resumen["Clase"]])

axs[1,1].set_title("(d) Distribución porcentual – Pocco", loc="left")
axs[1,1].set_ylim(0, resumen["Pocco (%)"].max()*1.15)
axs[1,1].tick_params(axis="x", labelsize=6)

# =====================================================
# AJUSTES ESTÉTICOS
# =====================================================

for ax in axs.flat:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(width=0.6, length=3)

plt.subplots_adjust(hspace=0.35, wspace=0.25)

plt.savefig("outputs/figuras/Figura_Clasificacion_Cualitativa_NDVI.png")
plt.close()

print("Figura final exportada correctamente.")

# =====================================================
# SALIDAS DEL SCRIPT
# =====================================================
# - outputs/clasificacion/NDVI_MATOC_clasificado.csv
# - outputs/clasificacion/NDVI_POCCO_clasificado.csv
# - outputs/clasificacion/NDVI_resumen_clases.csv
# - outputs/figuras/Figura_Clasificacion_Cualitativa_NDVI.png
#
# Este script permite interpretar el NDVI en términos ecológicos,
# facilitando su análisis cualitativo dentro del estudio.
# =====================================================
