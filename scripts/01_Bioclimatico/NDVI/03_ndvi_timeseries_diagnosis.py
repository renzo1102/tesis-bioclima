# =====================================================
# SCRIPT 3
# Diagnóstico de series temporales NDVI
# Generación de estadísticos descriptivos y figura multipanel
# =====================================================

# =====================================================
# DESCRIPCIÓN GENERAL
# =====================================================
# Este script realiza un diagnóstico exploratorio de las series
# temporales de NDVI previamente generadas (Script 2).
#
# Objetivos:
# - Evaluar la calidad y comportamiento de las series NDVI
# - Calcular estadísticos descriptivos
# - Visualizar patrones temporales y distribuciones
#
# Salidas:
# - Tabla de estadísticos descriptivos (CSV)
# - Figura multipanel con:
#     (a) Serie temporal
#     (b) Histograma de distribución
#     (c) Boxplot comparativo

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# =====================================================
# CONFIGURACIÓN DE ESTILO (ARTÍCULO CIENTÍFICO)
# =====================================================
# Se define un estilo gráfico consistente con publicaciones científicas.

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
# Colores diferenciados para cada cuenca y elementos gráficos.

COLOR_MATOC = "#4FA3D9"   # Matoc
COLOR_POCCO = "#F4A261"   # Pocco
COLOR_BOX = "#B0B0B0"     # Boxplot

# =====================================================
# CREACIÓN DE CARPETAS DE SALIDA
# =====================================================
# Se crean carpetas necesarias si no existen.

os.makedirs("outputs/figuras", exist_ok=True)
os.makedirs("outputs/estadisticas", exist_ok=True)

# =====================================================
# CARGA DE SERIES NDVI
# =====================================================
# Se leen los archivos generados en el Script 2.

matoc = pd.read_csv("outputs/csv/NDVI_MATOC.csv")
pocco = pd.read_csv("outputs/csv/NDVI_POCCO.csv")

# Conversión a formato de fecha (primer día del mes)
matoc["Fecha"] = pd.to_datetime(matoc[['Year','Month']].assign(DAY=1))
pocco["Fecha"] = pd.to_datetime(pocco[['Year','Month']].assign(DAY=1))

# =====================================================
# FUNCIÓN: resumen
# =====================================================
# Calcula estadísticos descriptivos para una serie NDVI.
#
# Parámetros:
# - df: DataFrame con columna NDVI
# - nombre: identificador de la serie
#
# Retorna:
# - Diccionario con métricas estadísticas

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

# Construcción de tabla comparativa
tabla = pd.DataFrame([
    resumen(matoc, "Matoc"),
    resumen(pocco, "Pocco")
])

# Exportación de estadísticos
tabla.to_csv(
    "outputs/estadisticas/NDVI_resumen_descriptivo.csv",
    index=False
)

# =====================================================
# MENSAJES EN TERMINAL
# =====================================================
# Se imprime resumen para verificación rápida.

print("\nResumen estadístico NDVI")
print(tabla)
print("\nDistribución lista para inspección visual")

# =====================================================
# FIGURA MULTIPANEL
# =====================================================
# Se construye una figura con tres paneles:
# (a) Serie temporal
# (b) Histograma
# (c) Boxplot

fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.6))

# -----------------------------------------------------
# (a) Serie temporal
# -----------------------------------------------------
# Visualiza evolución mensual del NDVI

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

# -----------------------------------------------------
# (b) Distribución (histograma)
# -----------------------------------------------------
# Permite evaluar frecuencia y dispersión de valores NDVI

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

# -----------------------------------------------------
# (c) Boxplot comparativo
# -----------------------------------------------------
# Resume distribución estadística y posibles valores extremos

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

# =====================================================
# AJUSTES ESTÉTICOS
# =====================================================
# Mejora visual eliminando bordes innecesarios

for ax in axs:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(width=0.6, length=3)

plt.tight_layout()

# Exportación de figura
plt.savefig("outputs/figuras/Figura_2a_Diagnostico_NDVI.png")
plt.close()

print("\nFigura diagnóstica exportada correctamente")

# =====================================================
# SALIDAS DEL SCRIPT
# =====================================================
# - outputs/estadisticas/NDVI_resumen_descriptivo.csv
# - outputs/figuras/Figura_2a_Diagnostico_NDVI.png
#
# Este script permite validar visual y estadísticamente
# las series NDVI antes de su uso en análisis posteriores.
# =====================================================
