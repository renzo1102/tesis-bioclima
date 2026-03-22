# ============================================================
# FIGURA FASE 5–6 — VALIDACIÓN Y CORRECCIÓN CHIRPS
# VERSIÓN AJUSTADA FINAL TESIS
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# CONFIGURACIÓN VISUAL
# ============================================================

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 12

COLOR_ORIG = "#377eb8"
COLOR_CORR = "#1b9e77"
COLOR_OBS = "black"
COLOR_REG = "#666666"

# ============================================================
# RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR = INPUT_DIR / "figuras"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CARGAR DATOS
# ============================================================

df = pd.read_csv(
    INPUT_DIR / "chirps_corregido/CHIRPS_ANA1_corregido.csv",
    parse_dates=["fecha_mensual"]
)

obs = pd.read_csv(
    INPUT_DIR / "mensuales/4_Matoc_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

df = df.merge(
    obs[["fecha_mensual", "Prec_UH_OBS"]],
    on="fecha_mensual",
    how="left"
)

df = df.rename(columns={
    "Prec_UH_OBS": "OBS",
    "CHIRPS_ANA1": "ORIG",
    "CHIRPS_ANA1_CORR": "CORR"
})

metricas_pre = pd.read_csv(
    INPUT_DIR / "validacion_chirps/7_fase5_validacion_chirps_integral.csv"
)

metricas_post = pd.read_csv(
    INPUT_DIR / "chirps_corregido/metricas_post_correccion_ANA1.csv"
)

r2_pre = metricas_pre["R2"].values[0]
rmse_pre = metricas_pre["RMSE"].values[0]

r2_post = metricas_post["R2"].values[0]
rmse_post = metricas_post["RMSE"].values[0]

factores = pd.read_csv(
    INPUT_DIR / "chirps_corregido/factores_mensuales_base_ANA1.csv"
)

# ============================================================
# CREAR FIGURA
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

# ------------------------------------------------------------
# (a) Serie original
# ------------------------------------------------------------

axes[0,0].plot(df["fecha_mensual"], df["OBS"],
               color=COLOR_OBS, linewidth=1.6, label="OBS")

axes[0,0].plot(df["fecha_mensual"], df["ORIG"],
               color=COLOR_ORIG, linewidth=1.6, label="CHIRPS original")

axes[0,0].set_title("(a) ANA1 vs CHIRPS original")
axes[0,0].legend(fontsize=9)
axes[0,0].grid(alpha=0.25)

axes[0,0].text(
    0.02, 0.95,
    f"R² = {r2_pre:.2f}\nRMSE = {rmse_pre:.1f} mm",
    transform=axes[0,0].transAxes,
    verticalalignment="top",
    bbox=dict(facecolor="white", alpha=0.85, edgecolor="none")
)

# ------------------------------------------------------------
# (b) Serie corregida
# ------------------------------------------------------------

axes[0,1].plot(df["fecha_mensual"], df["OBS"],
               color=COLOR_OBS, linewidth=1.6, label="OBS")

axes[0,1].plot(df["fecha_mensual"], df["CORR"],
               color=COLOR_CORR, linewidth=1.6, label="CHIRPS corregido")

axes[0,1].set_title("(b) ANA1 vs CHIRPS corregido")
axes[0,1].legend(fontsize=9)
axes[0,1].grid(alpha=0.25)

axes[0,1].text(
    0.02, 0.95,
    f"R² = {r2_post:.2f}\nRMSE = {rmse_post:.1f} mm",
    transform=axes[0,1].transAxes,
    verticalalignment="top",
    bbox=dict(facecolor="white", alpha=0.85, edgecolor="none")
)

# ------------------------------------------------------------
# (c) Factores mensuales
# ------------------------------------------------------------

axes[1,0].plot(factores["mes"],
               factores["Factor_correccion"],
               marker="o",
               color=COLOR_CORR,
               linewidth=1.6)

axes[1,0].set_title("(c) Factores de corrección mensuales")
axes[1,0].set_xlabel("Mes")
axes[1,0].set_ylabel("Factor")
axes[1,0].grid(alpha=0.25)

# ------------------------------------------------------------
# (d) Comparación métricas oficiales
# ------------------------------------------------------------

ax1 = axes[1,1]
x_labels = ["Original", "Corregido"]
x_pos = [0, 1]

ax1.plot(x_pos, [r2_pre, r2_post],
         marker="o", color=COLOR_CORR,
         linewidth=1.8, label="R²")

ax1.set_ylabel("R²")
ax1.set_ylim(0, 1)
ax1.set_xticks(x_pos)
ax1.set_xticklabels(x_labels)
ax1.grid(alpha=0.25)

ax2 = ax1.twinx()
ax2.plot(x_pos, [rmse_pre, rmse_post],
         marker="s", color=COLOR_ORIG,
         linewidth=1.8, label="RMSE")

ax2.set_ylabel("RMSE (mm)")

ax1.set_title("(d) Mejora estadística tras corrección")

# Anotaciones
ax1.annotate(f"{r2_pre:.2f} → {r2_post:.2f}",
             xy=(1, r2_post),
             xytext=(0.4, r2_post + 0.08),
             arrowprops=dict(arrowstyle="->", color=COLOR_CORR),
             fontsize=10)

ax2.annotate(f"{rmse_pre:.1f} → {rmse_post:.1f}",
             xy=(1, rmse_post),
             xytext=(0.4, rmse_post + (rmse_pre*0.05)),
             arrowprops=dict(arrowstyle="->", color=COLOR_ORIG),
             fontsize=10)

# Leyenda inferior izquierda
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2,
           labels1 + labels2,
           loc="lower left",
           fontsize=9)

# ============================================================
# GUARDAR
# ============================================================

plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "Figura_Fase5_6_Final_Tesis_Ajustada.png",
    dpi=600,
    bbox_inches="tight"
)

plt.close()

print("Figura FASE 5–6 ajustada correctamente.")