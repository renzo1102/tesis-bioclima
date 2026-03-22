# ============================================================
# FIGURA FASE 4 — ANÁLISIS REGIONAL (VERSIÓN FINAL TESIS)
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# ============================================================
# CONFIGURACIÓN VISUAL
# ============================================================

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 12

COLOR_MATOC = "#1b9e77"
COLOR_POCCO = "#d95f02"
COLOR_ANA = "#377eb8"
COLOR_REG = "#666666"

# ============================================================
# RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_MENS = BASE_DIR / "outputs/mensuales"
OUTPUT_DIR = BASE_DIR / "outputs/figuras"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CARGAR DATOS
# ============================================================

matoc = pd.read_csv(
    INPUT_MENS / "4_Matoc_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

pocco = pd.read_csv(
    INPUT_MENS / "4_Pocco_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

estaciones = pd.read_csv(
    INPUT_MENS / "mensual_estaciones_2012_2022.csv",
    parse_dates=["fecha_mensual"]
)

ana1 = estaciones[estaciones["Estacion"] == "ANA 1"][
    ["fecha_mensual", "Prec_mensual"]
].rename(columns={"Prec_mensual": "ANA1"})

# Merge
matoc = matoc.merge(ana1, on="fecha_mensual", how="left")
pocco = pocco.merge(ana1, on="fecha_mensual", how="left")

# ============================================================
# PREPARAR DATOS SIN NA
# ============================================================

matoc_reg = matoc.dropna(subset=["Prec_UH_OBS", "ANA1"]).copy()
pocco_reg = pocco.dropna(subset=["Prec_UH_OBS", "ANA1"]).copy()

# Ajuste regresión
model_m = LinearRegression().fit(
    matoc_reg[["ANA1"]],
    matoc_reg["Prec_UH_OBS"]
)

model_p = LinearRegression().fit(
    pocco_reg[["ANA1"]],
    pocco_reg["Prec_UH_OBS"]
)

r2_m = r2_score(
    matoc_reg["Prec_UH_OBS"],
    model_m.predict(matoc_reg[["ANA1"]])
)

r2_p = r2_score(
    pocco_reg["Prec_UH_OBS"],
    model_p.predict(pocco_reg[["ANA1"]])
)

x_line = np.linspace(
    0,
    max(matoc_reg["ANA1"].max(),
        pocco_reg["ANA1"].max()),
    100
)

# ============================================================
# CREAR PANEL
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

# ------------------------------------------------------------
# (a) Scatter Matoc vs ANA1
# ------------------------------------------------------------

axes[0,0].scatter(
    matoc_reg["ANA1"],
    matoc_reg["Prec_UH_OBS"],
    color=COLOR_MATOC,
    alpha=0.7
)

axes[0,0].plot(
    x_line,
    model_m.predict(x_line.reshape(-1,1)),
    color=COLOR_REG,
    linestyle="--",
    linewidth=1.4
)

axes[0,0].text(
    0.05, 0.90,
    f"$R^2$ = {r2_m:.2f}",
    transform=axes[0,0].transAxes,
    fontsize=11
)

axes[0,0].set_title("(a) Matoc vs ANA1")
axes[0,0].set_xlabel("ANA1 (mm)")
axes[0,0].set_ylabel("Matoc (mm)")
axes[0,0].grid(alpha=0.25)

# ------------------------------------------------------------
# (b) Scatter Pocco vs ANA1
# ------------------------------------------------------------

axes[0,1].scatter(
    pocco_reg["ANA1"],
    pocco_reg["Prec_UH_OBS"],
    color=COLOR_POCCO,
    alpha=0.7
)

axes[0,1].plot(
    x_line,
    model_p.predict(x_line.reshape(-1,1)),
    color=COLOR_REG,
    linestyle="--",
    linewidth=1.4
)

axes[0,1].text(
    0.05, 0.90,
    f"$R^2$ = {r2_p:.2f}",
    transform=axes[0,1].transAxes,
    fontsize=11
)

axes[0,1].set_title("(b) Pocco vs ANA1")
axes[0,1].set_xlabel("ANA1 (mm)")
axes[0,1].grid(alpha=0.25)

# ------------------------------------------------------------
# (c) Climatología mensual (líneas suavizadas)
# ------------------------------------------------------------

matoc["mes"] = matoc["fecha_mensual"].dt.month
pocco["mes"] = pocco["fecha_mensual"].dt.month
ana1["mes"] = ana1["fecha_mensual"].dt.month

clim_m = matoc.groupby("mes")["Prec_UH_OBS"].mean()
clim_p = pocco.groupby("mes")["Prec_UH_OBS"].mean()
clim_a = ana1.groupby("mes")["ANA1"].mean()

axes[1,0].plot(
    clim_m.index, clim_m,
    color=COLOR_MATOC,
    linewidth=1.6,
    alpha=0.85,
    label="Matoc"
)

axes[1,0].plot(
    clim_p.index, clim_p,
    color=COLOR_POCCO,
    linewidth=1.6,
    alpha=0.85,
    label="Pocco"
)

axes[1,0].plot(
    clim_a.index, clim_a,
    color=COLOR_ANA,
    linewidth=1.6,
    alpha=0.85,
    label="ANA1"
)

axes[1,0].set_title("(c) Climatología mensual")
axes[1,0].set_xlabel("Mes")
axes[1,0].set_ylabel("Precipitación (mm)")
axes[1,0].legend()
axes[1,0].grid(alpha=0.18)

# ------------------------------------------------------------
# (d) Residuales vs mes
# ------------------------------------------------------------

matoc_reg["residual"] = matoc_reg["Prec_UH_OBS"] - model_m.predict(matoc_reg[["ANA1"]])
pocco_reg["residual"] = pocco_reg["Prec_UH_OBS"] - model_p.predict(pocco_reg[["ANA1"]])

matoc_reg["mes"] = matoc_reg["fecha_mensual"].dt.month
pocco_reg["mes"] = pocco_reg["fecha_mensual"].dt.month

axes[1,1].scatter(
    matoc_reg["mes"],
    matoc_reg["residual"],
    color=COLOR_MATOC,
    alpha=0.6,
    label="Matoc"
)

axes[1,1].scatter(
    pocco_reg["mes"],
    pocco_reg["residual"],
    color=COLOR_POCCO,
    alpha=0.6,
    label="Pocco"
)

axes[1,1].axhline(0, color="#555555", linestyle="--", linewidth=1.2)
axes[1,1].set_title("(d) Residuales vs mes")
axes[1,1].set_xlabel("Mes")
axes[1,1].set_ylabel("Residual (mm)")
axes[1,1].legend()
axes[1,1].grid(alpha=0.25)

# ============================================================
# GUARDAR FIGURA
# ============================================================

plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "Figura_Fase4_Panel_Final.png",
    dpi=600,
    bbox_inches="tight"
)

plt.close()

print("Figura FASE 4 final generada correctamente.")