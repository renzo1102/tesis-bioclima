import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress, pearsonr
import pymannkendall as mk
import os

# =====================================================
# ESTILO REVISTA CIENTÍFICA
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

COLOR_MATOC = "#4FA3D9"      # celeste
COLOR_POCCO = "#F4A261"     # naranja claro
COLOR_TREND = "#6E6E6E"
COLOR_CORR_POINTS = "#7A7A7A"   # gris plomo
COLOR_CORR_LINE = "#4D4D4D"     # gris más notorio

# =====================================================
# DIRECTORIOS
# =====================================================

os.makedirs("outputs/figuras", exist_ok=True)
os.makedirs("outputs/estadisticas", exist_ok=True)

# =====================================================
# CARGA DE DATOS (INTERPOLADOS)
# =====================================================

matoc = pd.read_csv("outputs/csv/NDVI_MATOC_interpolado.csv")
pocco = pd.read_csv("outputs/csv/NDVI_POCCO_interpolado.csv")

matoc["Fecha"] = pd.to_datetime(matoc[['Year','Month']].assign(DAY=1))
pocco["Fecha"] = pd.to_datetime(pocco[['Year','Month']].assign(DAY=1))

matoc = matoc.sort_values("Fecha")
pocco = pocco.sort_values("Fecha")

# =====================================================
# UNIÓN TEMPORAL
# =====================================================

merged = pd.merge(
    matoc[["Fecha","NDVI"]],
    pocco[["Fecha","NDVI"]],
    on="Fecha",
    suffixes=("_Matoc","_Pocco")
)

# =====================================================
# TENDENCIAS Y TESTS
# =====================================================

# Matoc
x_m = np.arange(len(matoc))
slope_m, intercept_m, r_m, p_m, _ = linregress(x_m, matoc["NDVI"])
mk_m = mk.original_test(matoc["NDVI"])

# Pocco
x_p = np.arange(len(pocco))
slope_p, intercept_p, r_p, p_p, _ = linregress(x_p, pocco["NDVI"])
mk_p = mk.original_test(pocco["NDVI"])

# Correlación
r_c, p_c = pearsonr(
    merged["NDVI_Matoc"],
    merged["NDVI_Pocco"]
)

# =====================================================
# FIGURA MULTIPANEL
# =====================================================

fig, axs = plt.subplots(2, 2, figsize=(7, 5))

# (a) Serie Matoc
axs[0,0].plot(matoc["Fecha"], matoc["NDVI"], color=COLOR_MATOC)
axs[0,0].plot(matoc["Fecha"], intercept_m + slope_m*x_m,
              linestyle="--", color=COLOR_TREND)
axs[0,0].set_ylabel("NDVI")
axs[0,0].set_title("(a) Serie temporal Matoc", loc="left")
axs[0,0].text(
    0.02, 0.95,
    f"R² = {r_m**2:.3f}\np = {p_m:.3f}\nMK: {mk_m.trend}",
    transform=axs[0,0].transAxes,
    va="top",
    bbox=dict(facecolor="white", edgecolor="none")
)

# (b) Serie Pocco
axs[0,1].plot(pocco["Fecha"], pocco["NDVI"], color=COLOR_POCCO)
axs[0,1].plot(pocco["Fecha"], intercept_p + slope_p*x_p,
              linestyle="--", color=COLOR_TREND)
axs[0,1].set_title("(b) Serie temporal Pocco", loc="left")
axs[0,1].text(
    0.02, 0.95,
    f"R² = {r_p**2:.3f}\np = {p_p:.3f}\nMK: {mk_p.trend}",
    transform=axs[0,1].transAxes,
    va="top",
    bbox=dict(facecolor="white", edgecolor="none")
)

# (c) Comparación temporal
axs[1,0].plot(merged["Fecha"], merged["NDVI_Matoc"],
              color=COLOR_MATOC, label="Matoc")
axs[1,0].plot(merged["Fecha"], merged["NDVI_Pocco"],
              color=COLOR_POCCO, label="Pocco")
axs[1,0].set_ylabel("NDVI")
axs[1,0].set_xlabel("Año")
axs[1,0].set_title("(c) Comparación temporal", loc="left")
axs[1,0].legend(frameon=False)

# (d) Correlación
axs[1,1].scatter(
    merged["NDVI_Matoc"],
    merged["NDVI_Pocco"],
    facecolors="none",
    edgecolors=COLOR_CORR_POINTS,
    s=22,
    linewidths=0.8
)

x_line = np.linspace(
    merged["NDVI_Matoc"].min(),
    merged["NDVI_Matoc"].max(),
    100
)

slope_c, intercept_c, _, _, _ = linregress(
    merged["NDVI_Matoc"],
    merged["NDVI_Pocco"]
)

axs[1,1].plot(
    x_line,
    intercept_c + slope_c*x_line,
    linestyle="--",
    color=COLOR_CORR_LINE,
    linewidth=1.3
)

axs[1,1].set_xlabel("Matoc")
axs[1,1].set_ylabel("Pocco")
axs[1,1].set_title("(d) Correlación NDVI", loc="left")
axs[1,1].text(
    0.02, 0.95,
    f"r = {r_c:.2f}\np < 0.001",
    transform=axs[1,1].transAxes,
    va="top",
    bbox=dict(facecolor="white", edgecolor="none")
)

for ax in axs.flat:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(width=0.6, length=3)

plt.tight_layout()
plt.savefig("outputs/figuras/Figura_3_Tendencias_NDVI.png")
plt.close()

# =====================================================
# EXPORTAR TABLAS ESTADÍSTICAS
# =====================================================

# Tabla principal
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

# =====================================================
# PROMEDIO ANUAL
# =====================================================

matoc_anual = matoc.groupby("Year")["NDVI"].mean().reset_index()
matoc_anual["Serie"] = "Matoc"

pocco_anual = pocco.groupby("Year")["NDVI"].mean().reset_index()
pocco_anual["Serie"] = "Pocco"

prom_anual = pd.concat([matoc_anual, pocco_anual])
prom_anual.to_csv(
    "outputs/estadisticas/NDVI_promedio_anual.csv",
    index=False
)

# =====================================================
# PROMEDIO MENSUAL
# =====================================================

matoc_mensual = matoc.groupby("Month")["NDVI"].mean().reset_index()
matoc_mensual["Serie"] = "Matoc"

pocco_mensual = pocco.groupby("Month")["NDVI"].mean().reset_index()
pocco_mensual["Serie"] = "Pocco"

prom_mensual = pd.concat([matoc_mensual, pocco_mensual])
prom_mensual.to_csv(
    "outputs/estadisticas/NDVI_promedio_mensual.csv",
    index=False
)

print("Script 3 ejecutado correctamente")
print("Figura exportada")
print("Tablas estadísticas, mensuales y anuales exportadas")