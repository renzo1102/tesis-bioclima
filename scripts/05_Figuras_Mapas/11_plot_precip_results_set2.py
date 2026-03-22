# ============================================================
# FASE 9 — FIGURA F9-2
# Tendencia anual con regresión y significancia
# Línea gris punteada
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy import stats

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 11

COLOR_MATOC = "#1b9e77"
COLOR_POCCO = "#d95f02"
COLOR_TENDENCIA = "#555555"  # gris científico

# ------------------------------------------------------------
# RUTAS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "outputs" / "serie_final"
OUTPUT_DIR = BASE_DIR / "outputs" / "figuras"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

matoc = pd.read_csv(INPUT_DIR / "Matoc_serie_mensual_2012_2022_completa.csv")
pocco = pd.read_csv(INPUT_DIR / "Pocco_serie_mensual_2012_2022_completa.csv")

matoc["fecha_mensual"] = pd.to_datetime(matoc["fecha_mensual"])
pocco["fecha_mensual"] = pd.to_datetime(pocco["fecha_mensual"])

matoc["anio"] = matoc["fecha_mensual"].dt.year
pocco["anio"] = pocco["fecha_mensual"].dt.year

# ------------------------------------------------------------
# TOTALES ANUALES
# ------------------------------------------------------------

anual_matoc = matoc.groupby("anio")["Precip_final"].sum()
anual_pocco = pocco.groupby("anio")["Precip_final"].sum()

# ------------------------------------------------------------
# FUNCIÓN REGRESIÓN
# ------------------------------------------------------------

def calcular_tendencia(x, y):
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    y_fit = intercept + slope * x
    return slope, intercept, r_value**2, p_value, y_fit

# ------------------------------------------------------------
# CÁLCULO TENDENCIAS
# ------------------------------------------------------------

x_matoc = anual_matoc.index.values
y_matoc = anual_matoc.values

x_pocco = anual_pocco.index.values
y_pocco = anual_pocco.values

slope_m, int_m, r2_m, p_m, yfit_m = calcular_tendencia(x_matoc, y_matoc)
slope_p, int_p, r2_p, p_p, yfit_p = calcular_tendencia(x_pocco, y_pocco)

# ------------------------------------------------------------
# FIGURA
# ------------------------------------------------------------

fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# -------- MATOC --------
axes[0].scatter(x_matoc, y_matoc, color=COLOR_MATOC, s=45)
axes[0].plot(x_matoc, yfit_m,
             color=COLOR_TENDENCIA,
             linestyle="--",
             linewidth=1.8)

axes[0].set_title("(a) Tendencia anual - Matoc")
axes[0].set_ylabel("Precipitación anual (mm)")

texto_m = (
    f"Pendiente = {slope_m:.2f} mm/año\n"
    f"R² = {r2_m:.3f}\n"
    f"p = {p_m:.3f}"
)

axes[0].text(0.03, 0.95, texto_m,
             transform=axes[0].transAxes,
             verticalalignment='top')

# -------- POCCO --------
axes[1].scatter(x_pocco, y_pocco, color=COLOR_POCCO, s=45)
axes[1].plot(x_pocco, yfit_p,
             color=COLOR_TENDENCIA,
             linestyle="--",
             linewidth=1.8)

axes[1].set_title("(b) Tendencia anual - Pocco")
axes[1].set_ylabel("Precipitación anual (mm)")
axes[1].set_xlabel("Año")

texto_p = (
    f"Pendiente = {slope_p:.2f} mm/año\n"
    f"R² = {r2_p:.3f}\n"
    f"p = {p_p:.3f}"
)

axes[1].text(0.03, 0.95, texto_p,
             transform=axes[1].transAxes,
             verticalalignment='top')

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "Figura_F9_2_Tendencia_Anual.png",
    dpi=600,
    bbox_inches="tight"
)

plt.close()

print("Figura F9-2 generada correctamente.")
