"""
Script: streamflow_extreme_events.py

Descripción:
Eventos extremos

Entradas:
Serie caudal

Salidas:
Eventos

Autor: Renzo Mendoza
Año: 2026
"""
# ======================================================
# SCRIPT 16
# COMPARACIÓN MODELOS HIDROLÓGICOS
# GR2M vs LUTZ-SCHOLZ
# Matoc y Pocco
# ======================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ======================================================
# RUTAS AUTOMÁTICAS
# ======================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_MODEL = os.path.join(BASE_DIR, "data_model")
OUTPUTS = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUTS, exist_ok=True)

# ======================================================
# ARCHIVOS
# ======================================================

archivo_gr2m_matoc = os.path.join(OUTPUTS, "serie_calibracion_Matoc.csv")
archivo_gr2m_pocco = os.path.join(OUTPUTS, "serie_calibracion_Pocco.csv")

archivo_lutz_matoc = os.path.join(OUTPUTS, "serie_calibracion_lutz_Matoc.csv")
archivo_lutz_pocco = os.path.join(OUTPUTS, "serie_calibracion_lutz_Pocco.csv")

print("Cargando datos...")

gr2m_matoc = pd.read_csv(archivo_gr2m_matoc)
gr2m_pocco = pd.read_csv(archivo_gr2m_pocco)

lutz_matoc = pd.read_csv(archivo_lutz_matoc)
lutz_pocco = pd.read_csv(archivo_lutz_pocco)

# ======================================================
# FUNCIÓN MÉTRICAS
# ======================================================

def metricas(obs, sim):

    obs = np.array(obs)
    sim = np.array(sim)

    mask = ~np.isnan(obs) & ~np.isnan(sim)

    obs = obs[mask]
    sim = sim[mask]

    nse = 1 - (np.sum((obs - sim) ** 2) /
               np.sum((obs - np.mean(obs)) ** 2))

    rmse = np.sqrt(np.mean((obs - sim) ** 2))

    r2 = np.corrcoef(obs, sim)[0,1] ** 2

    pbias = 100 * np.sum(sim - obs) / np.sum(obs)

    return nse, rmse, r2, pbias


# ======================================================
# MATOC
# ======================================================

obs_matoc = gr2m_matoc["Q_mm"].values

sim_gr2m_matoc = gr2m_matoc["Q_sim"].values
sim_lutz_matoc = lutz_matoc["Q_sim_lutz"].values

nse_g, rmse_g, r2_g, pbias_g = metricas(obs_matoc, sim_gr2m_matoc)
nse_l, rmse_l, r2_l, pbias_l = metricas(obs_matoc, sim_lutz_matoc)


# ======================================================
# POCCO
# ======================================================

obs_pocco = gr2m_pocco["Q_mm"].values

sim_gr2m_pocco = gr2m_pocco["Q_sim"].values
sim_lutz_pocco = lutz_pocco["Q_sim_lutz"].values

nse_g_p, rmse_g_p, r2_g_p, pbias_g_p = metricas(obs_pocco, sim_gr2m_pocco)
nse_l_p, rmse_l_p, r2_l_p, pbias_l_p = metricas(obs_pocco, sim_lutz_pocco)


# ======================================================
# TABLA RESULTADOS
# ======================================================

tabla = pd.DataFrame({

"Cuenca":[
"Matoc_GR2M","Matoc_Lutz",
"Pocco_GR2M","Pocco_Lutz"
],

"NSE":[
nse_g,nse_l,
nse_g_p,nse_l_p
],

"RMSE":[
rmse_g,rmse_l,
rmse_g_p,rmse_l_p
],

"R2":[
r2_g,r2_l,
r2_g_p,r2_l_p
],

"PBIAS":[
pbias_g,pbias_l,
pbias_g_p,pbias_l_p
]

})

tabla = tabla.round(3)

ruta_tabla = os.path.join(OUTPUTS,"comparacion_modelos.csv")

tabla.to_csv(ruta_tabla,index=False)

print("\nResultados:")
print(tabla)


# ======================================================
# FIGURA MATOC
# ======================================================

fig, ax = plt.subplots(figsize=(12,6))

fecha = pd.to_datetime(gr2m_matoc["fecha"])

ax.plot(fecha, obs_matoc, label="Observado", linewidth=2)
ax.plot(fecha, sim_gr2m_matoc, label="GR2M", linestyle="--")
ax.plot(fecha, sim_lutz_matoc, label="Lutz-Scholz", linestyle=":")

ax.set_title("Comparación de modelos hidrológicos - UH Matoc")
ax.set_ylabel("Caudal (mm)")
ax.set_xlabel("Fecha")

ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(os.path.join(OUTPUTS,"comparacion_matoc.png"),dpi=300)

plt.show()


# ======================================================
# FIGURA POCCO
# ======================================================

fig, ax = plt.subplots(figsize=(12,6))

fecha = pd.to_datetime(gr2m_pocco["fecha"])

ax.plot(fecha, obs_pocco, label="Observado", linewidth=2)
ax.plot(fecha, sim_gr2m_pocco, label="GR2M", linestyle="--")
ax.plot(fecha, sim_lutz_pocco, label="Lutz-Scholz", linestyle=":")

ax.set_title("Comparación de modelos hidrológicos - UH Pocco")
ax.set_ylabel("Caudal (mm)")
ax.set_xlabel("Fecha")

ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(os.path.join(OUTPUTS,"comparacion_pocco.png"),dpi=300)

plt.show()

print("\nComparación finalizada.")
