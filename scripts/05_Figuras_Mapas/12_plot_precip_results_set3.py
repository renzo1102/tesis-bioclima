# ============================================================
# FASE 9 — FIGURA F9-3
# Anomalías estandarizadas (Z-score)
# Versión final con leyenda horizontal compacta
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 11

# ------------------------------------------------------------
# COLORES (estilo SPI paper)
# ------------------------------------------------------------

COLOR_HUMEDO = "#2166ac"   # azul
COLOR_SECO = "#b2182b"     # rojo
COLOR_NEUTRO = "#bdbdbd"   # gris

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

# ------------------------------------------------------------
# CÁLCULO Z-SCORE
# ------------------------------------------------------------

def calcular_zscore(serie):
    media = serie.mean()
    std = serie.std()
    return (serie - media) / std

matoc["Z"] = calcular_zscore(matoc["Precip_final"])
pocco["Z"] = calcular_zscore(pocco["Precip_final"])

# ------------------------------------------------------------
# ASIGNACIÓN DE COLORES SEGÚN CLASIFICACIÓN
# ------------------------------------------------------------

def asignar_color(z):
    if z >= 1:
        return COLOR_HUMEDO
    elif z <= -1:
        return COLOR_SECO
    else:
        return COLOR_NEUTRO

matoc["color"] = matoc["Z"].apply(asignar_color)
pocco["color"] = pocco["Z"].apply(asignar_color)

# ------------------------------------------------------------
# CREACIÓN FIGURA
# ------------------------------------------------------------

fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

for ax, df, titulo in zip(
        axes,
        [matoc, pocco],
        ["(a) Anomalías estandarizadas - Matoc",
         "(b) Anomalías estandarizadas - Pocco"]):

    ax.bar(df["fecha_mensual"], df["Z"],
           color=df["color"], width=20)

    # Líneas de referencia
    ax.axhline(0, color="black", linewidth=1)
    ax.axhline(1, color="gray", linestyle="--", linewidth=1)
    ax.axhline(-1, color="gray", linestyle="--", linewidth=1)
    ax.axhline(2, color="gray", linestyle=":", linewidth=1)
    ax.axhline(-2, color="gray", linestyle=":", linewidth=1)

    ax.set_title(titulo)
    ax.set_ylabel("Z-score")

# ------------------------------------------------------------
# LEYENDA HORIZONTAL COMPACTA
# ------------------------------------------------------------

legend_elements = [
    Patch(facecolor=COLOR_HUMEDO, label="Z ≥ 1"),
    Patch(facecolor=COLOR_NEUTRO, label="-1 < Z < 1"),
    Patch(facecolor=COLOR_SECO, label="Z ≤ -1"),
    Line2D([0], [0], color="black", lw=1, label="Z = 0"),
    Line2D([0], [0], color="gray", lw=1, linestyle="--", label="±1"),
    Line2D([0], [0], color="gray", lw=1, linestyle=":", label="±2"),
]

axes[0].legend(
    handles=legend_elements,
    loc="upper right",
    ncol=3,                 # horizontal
    fontsize=9,             # tamaño pequeño
    frameon=False,          # sin caja
    handlelength=1.5,
    columnspacing=1
)

axes[1].set_xlabel("Fecha")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "Figura_F9_3_Anomalias_Estandarizadas.png",
    dpi=600,
    bbox_inches="tight"
)

plt.close()

print("Figura F9-3 generada correctamente.")
