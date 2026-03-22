# ============================================================
# FIGURA — CLIMATOLOGÍA MENSUAL (SERIE FINAL)
# Matoc vs Pocco
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 12

COLOR_MATOC = "#1b9e77"
COLOR_POCCO = "#d95f02"

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR = INPUT_DIR / "figuras"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

matoc = pd.read_csv(
    INPUT_DIR / "serie_final/Matoc_serie_mensual_2012_2022_completa.csv",
    parse_dates=["fecha_mensual"]
)

pocco = pd.read_csv(
    INPUT_DIR / "serie_final/Pocco_serie_mensual_2012_2022_completa.csv",
    parse_dates=["fecha_mensual"]
)

# Extraer mes
matoc["mes"] = matoc["fecha_mensual"].dt.month
pocco["mes"] = pocco["fecha_mensual"].dt.month

# Promedio mensual
clim_matoc = matoc.groupby("mes")["Precip_final"].mean()
clim_pocco = pocco.groupby("mes")["Precip_final"].mean()

# Crear figura
plt.figure(figsize=(10,6))

plt.plot(
    clim_matoc.index,
    clim_matoc.values,
    marker="o",
    linewidth=2,
    color=COLOR_MATOC,
    label="Matoc"
)

plt.plot(
    clim_pocco.index,
    clim_pocco.values,
    marker="o",
    linewidth=2,
    color=COLOR_POCCO,
    label="Pocco"
)

plt.xticks(range(1,13),
           ["Ene","Feb","Mar","Abr","May","Jun",
            "Jul","Ago","Sep","Oct","Nov","Dic"])

plt.ylabel("Precipitación promedio (mm)")
plt.xlabel("Mes")
plt.title("Climatología mensual 2012–2022 (Serie final)")
plt.legend(loc="upper right")
plt.grid(alpha=0.25)

plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "Figura1.2_fase7_Climatologia_Mensual_Final.png",
    dpi=600,
    bbox_inches="tight"
)

plt.close()

print("Figura climatología mensual generada.")