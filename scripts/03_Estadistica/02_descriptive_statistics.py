# ======================================================
# SCRIPT 02
# Estadística descriptiva con distribución
# ======================================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ======================================
# Crear carpetas
# ======================================

os.makedirs("resultados/tablas", exist_ok=True)
os.makedirs("resultados/graficas", exist_ok=True)

# ======================================
# Cargar datos
# ======================================

matoc = pd.read_csv("resultados/tablas/matoc_datos.csv")
pocco = pd.read_csv("resultados/tablas/pocco_datos.csv")

# ======================================
# Variables
# ======================================

variables = ["P_mm", "Tmed_c", "ndvi", "Q_mm"]

# ======================================
# Estadística descriptiva
# ======================================

desc_matoc = matoc[variables].describe()
desc_pocco = pocco[variables].describe()

desc_matoc.to_csv("resultados/tablas/estadistica_descriptiva_matoc.csv")
desc_pocco.to_csv("resultados/tablas/estadistica_descriptiva_pocco.csv")

# ======================================
# Colores
# ======================================

color_matoc = "#2C7FB8"
color_pocco = "#F28E2B"

# ======================================
# Crear figura
# ======================================

fig, ax = plt.subplots(2,2, figsize=(11,8))

# ==========================
# a) Precipitación
# ==========================

sns.histplot(matoc["P_mm"], kde=True, color=color_matoc, ax=ax[0,0], label="Matoc", stat="density", alpha=0.5)
sns.histplot(pocco["P_mm"], kde=True, color=color_pocco, ax=ax[0,0], label="Pocco", stat="density", alpha=0.5)

ax[0,0].set_title("a) Precipitación", loc="left")
ax[0,0].set_xlabel("P (mm)")
ax[0,0].legend()

# ==========================
# b) Temperatura
# ==========================

sns.histplot(matoc["Tmed_c"], kde=True, color=color_matoc, ax=ax[0,1], stat="density", alpha=0.5)
sns.histplot(pocco["Tmed_c"], kde=True, color=color_pocco, ax=ax[0,1], stat="density", alpha=0.5)

ax[0,1].set_title("b) Temperatura", loc="left")
ax[0,1].set_xlabel("T (°C)")

# ==========================
# c) NDVI
# ==========================

sns.histplot(matoc["ndvi"], kde=True, color=color_matoc, ax=ax[1,0], stat="density", alpha=0.5)
sns.histplot(pocco["ndvi"], kde=True, color=color_pocco, ax=ax[1,0], stat="density", alpha=0.5)

ax[1,0].set_title("c) NDVI", loc="left")
ax[1,0].set_xlabel("NDVI")

# ==========================
# d) Caudal
# ==========================

sns.histplot(matoc["Q_mm"], kde=True, color=color_matoc, ax=ax[1,1], stat="density", alpha=0.5)
sns.histplot(pocco["Q_mm"], kde=True, color=color_pocco, ax=ax[1,1], stat="density", alpha=0.5)

ax[1,1].set_title("d) Caudal", loc="left")
ax[1,1].set_xlabel("Q (mm)")

# ======================================
# Ajustar
# ======================================

plt.tight_layout()

plt.savefig(
    "resultados/graficas/distribucion_variables_matoc_pocco.png",
    dpi=400,
    bbox_inches="tight"
)

plt.close()

print("✔ Distribuciones generadas")