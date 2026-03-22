# ======================================================
# FASE 8B
# CALIBRACIÓN MODELO HIDROLÓGICO LUTZ-SCHOLZ (REAL)
# ======================================================

import pandas as pd
import numpy as np
import os
import json
from scipy.optimize import minimize

print("\n====================================")
print("CALIBRACIÓN MODELO LUTZ-SCHOLZ")
print("====================================")

# ======================================================
# RUTAS
# ======================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_MODEL = os.path.join(BASE_DIR, "data_model")
OUTPUTS = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUTS, exist_ok=True)

# ======================================================
# ESTACIONES
# ======================================================

ESTACIONES = ["Matoc","Pocco"]

# ======================================================
# MODELO LUTZ-SCHOLZ
# ======================================================

def modelo_lutz(df, params):

    Smax, k = params

    S = Smax * 0.5

    Qsim = []

    for _, row in df.iterrows():

        P = row["P_mm"]
        PET = row["PET_mm"]

        if np.isnan(P) or np.isnan(PET):
            Qsim.append(np.nan)
            continue

        # ------------------------------------------------
        # Evapotranspiración real
        # ------------------------------------------------

        ETR = PET * (S / Smax)

        if ETR > S:
            ETR = S

        # ------------------------------------------------
        # Balance hídrico
        # ------------------------------------------------

        S = S + P - ETR

        excedente = 0

        if S > Smax:

            excedente = S - Smax
            S = Smax

        # ------------------------------------------------
        # Escorrentía
        # ------------------------------------------------

        Q = k * excedente

        Qsim.append(Q)

    return np.array(Qsim)

# ======================================================
# MÉTRICAS HIDROLÓGICAS
# ======================================================

def calcular_metricas(Qobs, Qsim):

    mask = (~np.isnan(Qobs)) & (~np.isnan(Qsim))

    Qobs = Qobs[mask]
    Qsim = Qsim[mask]

    if len(Qobs) < 5:
        return np.nan,np.nan,np.nan,np.nan

    NSE = 1 - np.sum((Qobs-Qsim)**2)/np.sum((Qobs-np.mean(Qobs))**2)

    R2 = np.corrcoef(Qobs,Qsim)[0,1]**2

    RMSE = np.sqrt(np.mean((Qobs-Qsim)**2))

    PBIAS = 100*(np.sum(Qsim-Qobs)/np.sum(Qobs))

    return NSE,R2,RMSE,PBIAS

# ======================================================
# FUNCIÓN OBJETIVO
# ======================================================

def objetivo(params,df):

    Qsim = modelo_lutz(df,params)

    df_temp = df.copy()
    df_temp["Q_sim_lutz"] = Qsim

    df_cal = df_temp[(df_temp["usar_calibracion"]==True) &
                     (df_temp["Q_mm"].notna())]

    NSE,_,_,_ = calcular_metricas(
        df_cal["Q_mm"].values,
        df_cal["Q_sim_lutz"].values
    )

    if np.isnan(NSE):
        return 9999

    return -NSE

# ======================================================
# RESULTADOS
# ======================================================

metricas_totales = []
parametros_totales = {}

# ======================================================
# CALIBRACIÓN
# ======================================================

for estacion in ESTACIONES:

    print("\n------------------------------------")
    print("Calibrando estación:",estacion)
    print("------------------------------------")

    archivo = os.path.join(DATA_MODEL,f"modelo_{estacion}.csv")

    if not os.path.exists(archivo):

        print("Archivo no encontrado:",archivo)
        continue

    df = pd.read_csv(archivo)

    df["fecha"] = pd.to_datetime(df["fecha"])

    df = df.sort_values("fecha").reset_index(drop=True)

    # --------------------------------------------------
    # valores iniciales y límites hidrológicos
    # --------------------------------------------------

    x0 = [180,0.5]

    bounds = [

        (80,300),   # Smax
        (0.2,0.8)   # k

    ]

    resultado = minimize(

        objetivo,
        x0,
        args=(df,),
        bounds=bounds,
        method="L-BFGS-B"

    )

    Smax,k = resultado.x

    print("\nParámetros encontrados")

    print("Smax:",round(Smax,2))
    print("k:",round(k,3))

    # --------------------------------------------------
    # simulación completa
    # --------------------------------------------------

    Qsim_full = modelo_lutz(df,resultado.x)

    df["Q_sim_lutz"] = Qsim_full

    df_cal = df[(df["usar_calibracion"]==True) &
                (df["Q_mm"].notna())]

    NSE,R2,RMSE,PBIAS = calcular_metricas(

        df_cal["Q_mm"].values,
        df_cal["Q_sim_lutz"].values

    )

    print("\nMétricas calibración")

    print("NSE :",round(NSE,3))
    print("R2  :",round(R2,3))
    print("RMSE:",round(RMSE,3))
    print("PBIAS:",round(PBIAS,2))

    # --------------------------------------------------
    # guardar serie calibración
    # --------------------------------------------------

    archivo_cal = os.path.join(

        OUTPUTS,
        f"serie_calibracion_lutz_{estacion}.csv"

    )

    df_cal.to_csv(archivo_cal,index=False)

    print("Serie guardada:",archivo_cal)

    metricas_totales.append({

        "estacion":estacion,
        "NSE":NSE,
        "R2":R2,
        "RMSE":RMSE,
        "PBIAS":PBIAS

    })

    parametros_totales[estacion]={

        "Smax":float(Smax),
        "k":float(k)

    }

# ======================================================
# GUARDAR MÉTRICAS
# ======================================================

df_metricas = pd.DataFrame(metricas_totales)

archivo_metricas = os.path.join(
    OUTPUTS,
    "metricas_calibracion_LUTZ_REAL.csv"
)

df_metricas.to_csv(archivo_metricas,index=False)

print("\n✔ Métricas guardadas:",archivo_metricas)

# ======================================================
# GUARDAR PARÁMETROS
# ======================================================

archivo_param = os.path.join(
    OUTPUTS,
    "parametros_lutz_real.json"
)

with open(archivo_param,"w") as f:

    json.dump(parametros_totales,f,indent=4)

print("✔ Parámetros guardados:",archivo_param)

print("\n====================================")
print("MODELO LUTZ-SCHOLZ CALIBRADO")
print("====================================")