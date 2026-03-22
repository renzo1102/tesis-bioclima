# ============================================================
# FASE 9 — FIGURA F9-1
# Climatología mensual + Totales anuales (CURVAS SUAVIZADAS)
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy.interpolate import make_interp_spline

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 11

COLOR_MATOC = "#1b9e77"
COLOR_POCCO = "#d95f02"

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
matoc["mes"] = matoc["fecha_mensual"].dt.month

pocco["anio"] = pocco["fecha_mensual"].dt.year
pocco["mes"] = pocco["fecha_mensual"].dt.month

# ------------------------------------------------------------
# CLIMATOLOGÍA
# ------------------------------------------------------------

clim_matoc = matoc.groupby("mes")["Precip_final"].mean()
clim_pocco = pocco.groupby("mes")["Precip_final"].mean()

# ------------------------------------------------------------
# TOTALES ANUALES
# ------------------------------------------------------------

anual_matoc = matoc.groupby("anio")["Precip_final"].sum()
anual_pocco = pocco.groupby("anio")["Precip_final"].sum()

# ------------------------------------------------------------
# FUNCIÓN PARA SUAVIZAR CURVAS
# ------------------------------------------------------------

def suavizar_curva(x, y, puntos=300):
    x = np.array(x)
    y = np.array(y)
    x_new = np.linspace(x.min(), x.max(), puntos)
    spline = make_interp_spline(x, y, k=3)
    y_smooth = spline(x_new)
    return x_new, y_smooth

# ------------------------------------------------------------
# FIGURA
# ------------------------------------------------------------

fig, axes = plt.subplots(2, 1, figsize=(10, 8))

# (a) Climatología mensual suavizada
x_m_matoc, y_m_matoc = suavizar_curva(clim_matoc.index, clim_matoc.values)
x_m_pocco, y_m_pocco = suavizar_curva(clim_pocco.index, clim_pocco.values)

axes[0].plot(x_m_matoc, y_m_matoc,
             linewidth=2, color=COLOR_MATOC, label="Matoc")

axes[0].plot(x_m_pocco, y_m_pocco,
             linewidth=2, color=COLOR_POCCO, label="Pocco")

axes[0].set_title("(a) Climatología mensual (2012–2022)")
axes[0].set_ylabel("Precipitación (mm)")
axes[0].set_xticks(range(1,13))
axes[0].legend(frameon=False)

# (b) Totales anuales suavizados
x_a_matoc, y_a_matoc = suavizar_curva(anual_matoc.index, anual_matoc.values)
x_a_pocco, y_a_pocco = suavizar_curva(anual_pocco.index, anual_pocco.values)

axes[1].plot(x_a_matoc, y_a_matoc,
             linewidth=2, color=COLOR_MATOC, label="Matoc")

axes[1].plot(x_a_pocco, y_a_pocco,
             linewidth=2, color=COLOR_POCCO, label="Pocco")

axes[1].set_title("(b) Totales anuales (2012–2022)")
axes[1].set_ylabel("Precipitación anual (mm)")
axes[1].set_xlabel("Año")
axes[1].legend(frameon=False)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "Figura_F9_1_Climatologia_Totales.png",
    dpi=600,
    bbox_inches="tight"
)

plt.close()

print("Figura F9-1 generada correctamente.")
