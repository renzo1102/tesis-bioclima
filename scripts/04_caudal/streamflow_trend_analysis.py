"""
Script: streamflow_trend_analysis.py

Descripción:
Tendencias del caudal

Entradas:
Serie caudal

Salidas:
Tendencias

Autor: Renzo Mendoza
Año: 2026
"""
# ======================================================
# SCRIPT 14
# FASE 8
# CALIBRACIÓN MODELO HIDROLÓGICO GR2M
# ======================================================

import pandas as pd
import numpy as np
import os
import json
from scipy.optimize import minimize

print("\n====================================")
print("FASE 8 - CALIBRACIÓN MODELO GR2M")
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

ESTACIONES = ["Matoc", "Pocco"]

# rezago precipitación
LAG = 0

# ======================================================
# MODELO GR2M
# ======================================================

def modelo_hidrologico(df, params):

    X1, X2 = params

    S = 0.5 * X1
    R = 30

    Qsim = []

    for _, row in df.iterrows():

        P = row["P_lag"]
        E = row["PET_mm"]

        if np.isnan(P):

            Qsim.append(np.nan)
            continue

        # PRODUCCIÓN

        if P >= E:

            Pn = P - E

            Ps = (X1 * (1 - (S/X1)**2) * np.tanh(Pn/X1)) / \
                 (1 + (S/X1) * np.tanh(Pn/X1))

            S = S + Ps
            Pe = Pn - Ps

        else:

            En = E - P

            Es = (S * (2 - S/X1) * np.tanh(En/X1)) / \
                 (1 + (1 - S/X1) * np.tanh(En/X1))

            S = S - Es
            Pe = 0

        # PERCOLACIÓN

        Perc = S * (1 - (1 + (4/9)*(S/X1)**4)**(-0.25))

        S = S - Perc

        if S < 0:
            S = 0

        # RESERVORIO DE ENRUTAMIENTO

        R = R + Perc + Pe

        Q = R * (1 - (1 + (R/X2)**4)**(-0.25))

        R = R - Q

        if R < 0:
            R = 0

        Qsim.append(Q)

    return np.array(Qsim)


# ======================================================
# MÉTRICAS
# ======================================================

def calcular_metricas(Qobs, Qsim):

    mask = ~np.isnan(Qobs)

    Qobs = Qobs[mask]
    Qsim = Qsim[mask]

    if len(Qobs) < 5:
        return np.nan, np.nan, np.nan, np.nan

    NSE = 1 - np.sum((Qobs - Qsim)**2) / np.sum((Qobs - np.mean(Qobs))**2)

    R2 = np.corrcoef(Qobs, Qsim)[0,1]**2

    RMSE = np.sqrt(np.mean((Qobs - Qsim)**2))

    PBIAS = 100 * (np.sum(Qsim - Qobs) / np.sum(Qobs))

    return NSE, R2, RMSE, PBIAS


# ======================================================
# FUNCIÓN OBJETIVO
# ======================================================

def objetivo(params, df):

    Qsim = modelo_hidrologico(df, params)

    df_temp = df.copy()
    df_temp["Q_sim"] = Qsim

    df_cal = df_temp[(df_temp["usar_calibracion"] == True) &
                     (df_temp["Q_mm"].notna())]

    NSE, _, _, _ = calcular_metricas(
        df_cal["Q_mm"].values,
        df_cal["Q_sim"].values
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
    print("Calibrando estación:", estacion)
    print("------------------------------------")

    archivo = os.path.join(DATA_MODEL, f"modelo_{estacion}.csv")

    if not os.path.exists(archivo):

        print("⚠ Archivo no encontrado:", archivo)
        continue

    df = pd.read_csv(archivo)

    df["fecha"] = pd.to_datetime(df["fecha"])

    df = df.sort_values("fecha").reset_index(drop=True)

    # aplicar rezago precipitación

    df["P_lag"] = df["P_mm"].shift(LAG)

    # --------------------------------------------------
    # optimización
    # --------------------------------------------------

    x0 = [300, 2]

    bounds = [(50,1500),(0.1,10)]

    resultado = minimize(
        objetivo,
        x0,
        args=(df,),
        bounds=bounds,
        method="L-BFGS-B"
    )

    X1, X2 = resultado.x

    print("\nParámetros encontrados")

    print("X1:", round(X1,2))
    print("X2:", round(X2,3))

    # --------------------------------------------------
    # simulación completa
    # --------------------------------------------------

    Qsim_full = modelo_hidrologico(df, resultado.x)

    df["Q_sim"] = Qsim_full

    df_cal = df[(df["usar_calibracion"] == True) &
                (df["Q_mm"].notna())]

    NSE, R2, RMSE, PBIAS = calcular_metricas(
        df_cal["Q_mm"].values,
        df_cal["Q_sim"].values
    )

    print("\nMétricas calibración")

    print("NSE :", round(NSE,3))
    print("R2  :", round(R2,3))
    print("RMSE:", round(RMSE,3))
    print("PBIAS:", round(PBIAS,2))

    # --------------------------------------------------
    # guardar serie calibración
    # --------------------------------------------------

    archivo_cal = os.path.join(OUTPUTS,
                               f"serie_calibracion_{estacion}.csv")

    df_cal.to_csv(archivo_cal, index=False)

    print("Serie guardada:", archivo_cal)

    # --------------------------------------------------

    metricas_totales.append({

        "estacion": estacion,
        "NSE": NSE,
        "R2": R2,
        "RMSE": RMSE,
        "PBIAS": PBIAS

    })

    parametros_totales[estacion] = {

        "X1": float(X1),
        "X2": float(X2)

    }


# ======================================================
# GUARDAR RESULTADOS
# ======================================================

df_metricas = pd.DataFrame(metricas_totales)

archivo_metricas = os.path.join(
    OUTPUTS,
    "metricas_calibracion_GR2M.csv"
)

df_metricas.to_csv(archivo_metricas, index=False)

print("\n✔ Métricas guardadas:", archivo_metricas)

archivo_param = os.path.join(
    OUTPUTS,
    "parametros_modelo.json"
)

with open(archivo_param, "w") as f:

    json.dump(parametros_totales, f, indent=4)

print("✔ Parámetros guardados:", archivo_param)

print("\n====================================")
print("FASE 8 COMPLETADA")
print("====================================")

