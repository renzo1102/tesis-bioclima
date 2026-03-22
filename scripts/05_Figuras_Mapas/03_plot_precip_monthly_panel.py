# ============================================================
# FIGURA FASE 3 — ESTILO REVISTA HIDROLÓGICA
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from pathlib import Path

# ============================================================
# CONFIGURACIÓN ESTÉTICA SOBRIA
# ============================================================

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 11
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["axes.edgecolor"] = "#333333"

COLOR_MATOC = "#2f6f4f"
COLOR_POCCO = "#8c5a2b"

cmap_disp = ListedColormap(["#f5f5f5", "#4c78a8"])

# ============================================================
# RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "outputs/mensuales"
OUTPUT_DIR = BASE_DIR / "outputs/figuras"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CARGAR DATOS
# ============================================================

matoc = pd.read_csv(
    INPUT_DIR / "4_Matoc_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

pocco = pd.read_csv(
    INPUT_DIR / "4_Pocco_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

for df in [matoc, pocco]:
    df["año"] = df["fecha_mensual"].dt.year
    df["mes"] = df["fecha_mensual"].dt.month

# ============================================================
# CREAR PANEL
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

# ------------------------------------------------------------
# (a) Serie mensual Matoc
# ------------------------------------------------------------

axes[0,0].plot(
    matoc["fecha_mensual"],
    matoc["Prec_UH_OBS"],
    color=COLOR_MATOC,
    linewidth=1.5
)

axes[0,0].set_title("(a) Monthly observed series – Matoc")
axes[0,0].set_ylabel("Precipitation (mm)")
axes[0,0].grid(alpha=0.15)

# ------------------------------------------------------------
# (b) Serie mensual Pocco
# ------------------------------------------------------------

axes[0,1].plot(
    pocco["fecha_mensual"],
    pocco["Prec_UH_OBS"],
    color=COLOR_POCCO,
    linewidth=1.5
)

axes[0,1].set_title("(b) Monthly observed series – Pocco")
axes[0,1].grid(alpha=0.15)

# ------------------------------------------------------------
# Heatmap función
# ------------------------------------------------------------

def heatmap_disponibilidad(df, ax, titulo):

    pivot = df.pivot(index="año", columns="mes",
                     values="Prec_UH_OBS")

    disponibilidad = pivot.notna().astype(int)

    im = ax.imshow(
        disponibilidad,
        aspect="auto",
        cmap=cmap_disp
    )

    ax.set_title(titulo)
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")
    ax.set_xticks(range(12))
    ax.set_xticklabels(range(1,13))
    ax.set_yticks(range(len(disponibilidad.index)))
    ax.set_yticklabels(disponibilidad.index)

    ax.set_xticks(np.arange(-.5, 12, 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(disponibilidad.index), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.4)
    ax.tick_params(which="minor", bottom=False, left=False)

# ------------------------------------------------------------
# (c) Heatmap Matoc
# ------------------------------------------------------------

heatmap_disponibilidad(
    matoc,
    axes[1,0],
    "(c) Monthly data availability – Matoc"
)

# ------------------------------------------------------------
# (d) Heatmap Pocco
# ------------------------------------------------------------

heatmap_disponibilidad(
    pocco,
    axes[1,1],
    "(d) Monthly data availability – Pocco"
)

# ============================================================
# LEYENDA
# ============================================================

legend_elements = [
    Patch(facecolor="#4c78a8", label="Available"),
    Patch(facecolor="#f5f5f5", label="Missing")
]

fig.legend(
    handles=legend_elements,
    loc="lower center",
    ncol=2,
    frameon=False
)

plt.tight_layout(rect=[0,0.05,1,1])

plt.savefig(
    OUTPUT_DIR / "Figure_Phase3_HydrologyStyle.png",
    dpi=600,
    bbox_inches="tight"
)

plt.close()

print("Figura FASE 3 estilo revista hidrológica generada.")