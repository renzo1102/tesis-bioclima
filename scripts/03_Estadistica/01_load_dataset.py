# ======================================================
# SCRIPT 01
# Carga de datos + figura comparativa Matoc vs Pocco
# ======================================================

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# ======================================
# Crear carpetas
# ======================================

os.makedirs("resultados/tablas", exist_ok=True)
os.makedirs("resultados/graficas", exist_ok=True)

# ======================================
# Cargar datos
# ======================================

matoc = pd.read_csv("Data_Variables_Matoc.csv", sep=";")
pocco = pd.read_csv("Data_Variables_Pocco.csv", sep=";")

# convertir fecha
matoc["fecha"] = pd.to_datetime(matoc["fecha"], dayfirst=True)
pocco["fecha"] = pd.to_datetime(pocco["fecha"], dayfirst=True)

# ordenar
matoc = matoc.sort_values("fecha")
pocco = pocco.sort_values("fecha")

# ======================================
# Guardar copia de datos
# ======================================

matoc.to_csv("resultados/tablas/matoc_datos.csv", index=False)
pocco.to_csv("resultados/tablas/pocco_datos.csv", index=False)

# ======================================
# Colores recomendados (artículo)
# ======================================

color_matoc = "#2C7FB8"   # azul
color_pocco = "#F28E2B"   # naranja

# ======================================
# Crear panel
# ======================================

fig, ax = plt.subplots(4,1, figsize=(12,10), sharex=True)

x = np.arange(len(matoc))
width = 0.4

# ==========================
# a) Precipitación
# ==========================

ax[0].bar(x - width/2, matoc["P_mm"], width=width, color=color_matoc, alpha=0.9, label="Matoc")
ax[0].bar(x + width/2, pocco["P_mm"], width=width, color=color_pocco, alpha=0.9, label="Pocco")

ax[0].set_ylabel("P (mm)")
ax[0].set_title("a) Precipitación", loc="left")
ax[0].grid(alpha=0.25)

# leyenda dentro del panel
ax[0].legend(loc="upper right")

# ==========================
# b) Temperatura
# ==========================

ax[1].plot(x, matoc["Tmed_c"], color=color_matoc, linewidth=1.6)
ax[1].plot(x, pocco["Tmed_c"], color=color_pocco, linewidth=1.6)

ax[1].set_ylabel("T (°C)")
ax[1].set_title("b) Temperatura media", loc="left")
ax[1].grid(alpha=0.25)

# ==========================
# c) NDVI
# ==========================

ax[2].plot(x, matoc["ndvi"], color=color_matoc, linewidth=1.6)
ax[2].plot(x, pocco["ndvi"], color=color_pocco, linewidth=1.6)

ax[2].set_ylabel("NDVI")
ax[2].set_title("c) Índice NDVI", loc="left")
ax[2].grid(alpha=0.25)

# ==========================
# d) Caudal
# ==========================

ax[3].plot(x, matoc["Q_mm"], color=color_matoc, linewidth=1.8)
ax[3].plot(x, pocco["Q_mm"], color=color_pocco, linewidth=1.8)

ax[3].set_ylabel("Q (mm)")
ax[3].set_title("d) Caudal", loc="left")
ax[3].grid(alpha=0.25)

# ======================================
# Eje temporal (marcas por año)
# ======================================

years = matoc["fecha"].dt.year
year_positions = np.where(years.diff()!=0)[0]

ax[3].set_xticks(year_positions)
ax[3].set_xticklabels(years.iloc[year_positions])

ax[3].set_xlabel("Año")

# ======================================
# Ajustar figura
# ======================================

plt.tight_layout()

plt.savefig(
    "resultados/graficas/series_temporales_matoc_pocco.png",
    dpi=400,
    bbox_inches="tight"
)

plt.close()

print("✔ Figura generada correctamente")