# ==========================================================
# FASE 6
# CALCULO DE PET (ETP) - METODO THORNTHWAITE
# + FIGURAS TIPO ARTICULO
# ==========================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ----------------------------------------------------------
# ESTILO GRAFICO (tipo articulo)
# ----------------------------------------------------------

plt.rcParams.update({

    "font.family": "serif",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "figure.titlesize": 13

})

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_DIR = BASE_DIR / "data_mensual"
OUTPUT_DIR = BASE_DIR / "data_model"
FIG_DIR = BASE_DIR / "figuras_pet"

OUTPUT_DIR.mkdir(exist_ok=True)
FIG_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------
# LATITUD
# ----------------------------------------------------------

LATITUD = -9.68

# ----------------------------------------------------------
# COLORES
# ----------------------------------------------------------

COLOR_MATOC = "#1f77b4"
COLOR_POCCO = "#d62728"

# ----------------------------------------------------------
# DIAS POR MES
# ----------------------------------------------------------

dias_mes = np.array([
31,28,31,30,31,30,
31,31,30,31,30,31
])

# ----------------------------------------------------------
# HORAS DE LUZ
# ----------------------------------------------------------

def horas_luz(mes, lat):

    J = (mes - 0.5) * 30.4

    delta = 23.45 * np.sin(np.deg2rad((360/365)*(284 + J)))

    ws = np.arccos(-np.tan(np.deg2rad(lat)) * np.tan(np.deg2rad(delta)))

    return 24/np.pi * ws


# ----------------------------------------------------------
# THORNTHWAITE
# ----------------------------------------------------------

def calcular_pet(df):

    df["Tcorr"] = df["Tmed"].clip(lower=0)

    df["I_mensual"] = (df["Tcorr"]/5)**1.514

    I_anual = df.groupby("anio")["I_mensual"].sum()

    a = (
        6.75e-7 * I_anual**3
        - 7.71e-5 * I_anual**2
        + 1.79e-2 * I_anual
        + 0.492
    )

    pet = []

    for _, row in df.iterrows():

        anio = row["anio"]
        mes = row["mes"]
        T = row["Tcorr"]

        I = I_anual.loc[anio]
        a_val = a.loc[anio]

        if T <= 0 or I == 0:
            pet.append(0)
            continue

        pet_base = 16*((10*T/I)**a_val)

        L = horas_luz(mes, LATITUD)

        pet_corr = pet_base*(L/12)*(dias_mes[mes-1]/30)

        pet.append(pet_corr)

    df["PET_mm"] = pet

    return df


# ----------------------------------------------------------
# CARGAR DATOS
# ----------------------------------------------------------

df_matoc = pd.read_csv(INPUT_DIR / "T_Matoc_mensual.csv")
df_pocco = pd.read_csv(INPUT_DIR / "T_Pocco_mensual.csv")

for df in [df_matoc, df_pocco]:

    df["fecha"] = pd.to_datetime(df["fecha"])
    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month


# ----------------------------------------------------------
# CALCULAR PET
# ----------------------------------------------------------

df_matoc = calcular_pet(df_matoc)
df_pocco = calcular_pet(df_pocco)


# ----------------------------------------------------------
# GUARDAR SERIES
# ----------------------------------------------------------

df_matoc[["fecha","PET_mm"]].to_csv(
OUTPUT_DIR / "PET_Matoc_mensual.csv",
index=False)

df_pocco[["fecha","PET_mm"]].to_csv(
OUTPUT_DIR / "PET_Pocco_mensual.csv",
index=False)


# ----------------------------------------------------------
# RESUMEN PET
# ----------------------------------------------------------

resumen = pd.DataFrame({

"Estacion":[
"Matoc",
"Pocco"
],

"PET_media_mm":[
round(df_matoc["PET_mm"].mean(),2),
round(df_pocco["PET_mm"].mean(),2)
],

"PET_max_mm":[
round(df_matoc["PET_mm"].max(),2),
round(df_pocco["PET_mm"].max(),2)
],

"PET_min_mm":[
round(df_matoc["PET_mm"].min(),2),
round(df_pocco["PET_mm"].min(),2)
]

})

resumen.to_csv(
OUTPUT_DIR / "resumen_pet.csv",
index=False
)


# ----------------------------------------------------------
# FIGURA 1 — SERIE TEMPORAL (PANEL A-B)
# ----------------------------------------------------------

fig,ax = plt.subplots(2,1,figsize=(10,6),sharex=True)

ax[0].plot(df_matoc["fecha"],df_matoc["PET_mm"],
color=COLOR_MATOC)

ax[0].set_ylabel("PET (mm/mes)")
ax[0].set_title("A) Unidad Hidrográfica Matoc")

ax[1].plot(df_pocco["fecha"],df_pocco["PET_mm"],
color=COLOR_POCCO)

ax[1].set_ylabel("PET (mm/mes)")
ax[1].set_title("B) Unidad Hidrográfica Pocco")

plt.xlabel("Año")

plt.tight_layout()

plt.savefig(
FIG_DIR / "serie_pet_panel.png",
dpi=300)

plt.close()


# ----------------------------------------------------------
# FIGURA 2 — CICLO CLIMATOLOGICO
# ----------------------------------------------------------

clim_matoc = df_matoc.groupby("mes")["PET_mm"].mean()
clim_pocco = df_pocco.groupby("mes")["PET_mm"].mean()

fig,ax = plt.subplots(1,2,figsize=(10,4),sharey=True)

ax[0].plot(range(1,13),clim_matoc,
marker="o",
color=COLOR_MATOC)

ax[0].set_title("A) Matoc")
ax[0].set_xlabel("Mes")
ax[0].set_ylabel("PET (mm)")

ax[1].plot(range(1,13),clim_pocco,
marker="o",
color=COLOR_POCCO)

ax[1].set_title("B) Pocco")
ax[1].set_xlabel("Mes")

plt.tight_layout()

plt.savefig(
FIG_DIR / "climatologia_pet_panel.png",
dpi=300)

plt.close()


# ----------------------------------------------------------
# FIGURA 3 — BOXPLOT
# ----------------------------------------------------------

fig,ax = plt.subplots(1,2,figsize=(10,4),sharey=True)

data_matoc = [df_matoc[df_matoc["mes"]==m]["PET_mm"] for m in range(1,13)]
data_pocco = [df_pocco[df_pocco["mes"]==m]["PET_mm"] for m in range(1,13)]

ax[0].boxplot(data_matoc)
ax[0].set_title("A) Matoc")
ax[0].set_xlabel("Mes")
ax[0].set_ylabel("PET (mm)")

ax[1].boxplot(data_pocco)
ax[1].set_title("B) Pocco")
ax[1].set_xlabel("Mes")

plt.tight_layout()

plt.savefig(
FIG_DIR / "boxplot_pet_panel.png",
dpi=300)

plt.close()


print("\n====================================")
print("PET CALCULADO Y FIGURAS GENERADAS")
print("====================================")