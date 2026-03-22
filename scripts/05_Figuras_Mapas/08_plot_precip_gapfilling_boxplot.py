# ============================================================
# FIGURA — CLIMATOLOGÍA MENSUAL COMPARATIVA
# Proporción corregida + leyenda limpia
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from pathlib import Path

# ------------------------------------------------------------
# CONFIGURACIÓN VISUAL
# ------------------------------------------------------------

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 12

COLOR_OBS    = "#6baed6"
COLOR_MATOC  = "#66c2a4"
COLOR_POCCO  = "#fdae6b"

# ------------------------------------------------------------
# RUTAS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "outputs/serie_final"
OUTPUT_DIR = BASE_DIR / "outputs/figuras"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# CARGAR DATOS
# ------------------------------------------------------------

matoc = pd.read_csv(
    INPUT_DIR / "Matoc_serie_mensual_2012_2022_completa.csv",
    parse_dates=["fecha_mensual"]
)

pocco = pd.read_csv(
    INPUT_DIR / "Pocco_serie_mensual_2012_2022_completa.csv",
    parse_dates=["fecha_mensual"]
)

# ------------------------------------------------------------
# CREAR FIGURA (MEJOR PROPORCIÓN)
# ------------------------------------------------------------

fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

for ax, df, titulo, color_final in zip(
    axes,
    [matoc, pocco],
    ["(a) Matoc — Climatología mensual",
     "(b) Pocco — Climatología mensual"],
    [COLOR_MATOC, COLOR_POCCO]
):

    df["mes"] = df["fecha_mensual"].dt.month

    data_obs = [df[df["mes"] == m]["Prec_UH_OBS"].dropna()
                for m in range(1, 13)]

    data_final = [df[df["mes"] == m]["Precip_final"]
                  for m in range(1, 13)]

    bp1 = ax.boxplot(
        data_obs,
        positions=[m - 0.2 for m in range(1, 13)],
        widths=0.35,
        patch_artist=True
    )

    bp2 = ax.boxplot(
        data_final,
        positions=[m + 0.2 for m in range(1, 13)],
        widths=0.35,
        patch_artist=True
    )

    # Colores suaves
    for patch in bp1["boxes"]:
        patch.set_facecolor(COLOR_OBS)
        patch.set_alpha(0.85)

    for patch in bp2["boxes"]:
        patch.set_facecolor(color_final)
        patch.set_alpha(0.85)

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(
        ["Ene","Feb","Mar","Abr","May","Jun",
         "Jul","Ago","Sep","Oct","Nov","Dic"]
    )

    ax.set_ylabel("Precipitación (mm)")
    ax.set_title(titulo)
    ax.grid(alpha=0.25)

    # Leyenda clara y limpia
    legend_elements = [
        Patch(facecolor=COLOR_OBS, label="Observada", alpha=0.85),
        Patch(facecolor=color_final, label="Serie final", alpha=0.85)
    ]

    ax.legend(
        handles=legend_elements,
        loc="upper right",
        fontsize=10,
        frameon=False
    )

axes[1].set_xlabel("Mes")

plt.tight_layout(pad=2.0)

plt.savefig(
    OUTPUT_DIR / "Figura1.3_fase7_Climatologia_Mensual_Proporcion_Corregida.png",
    dpi=600,
    bbox_inches="tight"
)

plt.close()

print("Figura con mejor proporción generada correctamente.")