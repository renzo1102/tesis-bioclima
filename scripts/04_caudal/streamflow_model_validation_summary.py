"""
Script: streamflow_model_validation_summary.py

Descripción:
Resumen validación modelo

Entradas:
Resultados

Salidas:
Reporte

Autor: Renzo Mendoza
Año: 2026
"""
# ======================================================
# SCRIPT 18
# FASE 10
# SIMULACIÓN FINAL MODELO GR2M
# ======================================================

import pandas as pd
import numpy as np
import os
import json

print("\n====================================")
print("FASE 10 - SIMULACIÓN FINAL GR2M")
print("====================================")

# ======================================================
# RUTAS
# ======================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_MODEL = os.path.join(BASE_DIR, "data_model")
OUTPUTS = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUTS, exist_ok=True)

# ======================================================
# CARGAR PARÁMETROS CALIBRADOS
# ======================================================

param_file = os.path.join(OUTPUTS, "parametros_modelo.json")

with open(param_file, "r") as f:
    PARAMS = json.load(f)

# ======================================================
# ESTACIONES
# ======================================================

ESTACIONES = ["Matoc", "Pocco"]

# ======================================================
# MODELO GR2M
# ======================================================

def modelo_hidrologico(df, X1, X2):

    S = 0.5 * X1
    R = 30

    Qsim = []

    for _, row in df.iterrows():

        P = row["P_mm"]
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

        # RESERVORIO ENRUTAMIENTO

        R = R + Perc + Pe

        Q = R * (1 - (1 + (R/X2)**4)**(-0.25))

        R = R - Q

        if R < 0:
            R = 0

        Qsim.append(Q)

    return np.array(Qsim)


# ======================================================
# SIMULACIÓN
# ======================================================

for estacion in ESTACIONES:

    print("\n--------------------------------")
    print("Simulando estación:", estacion)
    print("--------------------------------")

    archivo = os.path.join(DATA_MODEL, f"modelo_{estacion}.csv")

    df = pd.read_csv(archivo)

    df["fecha"] = pd.to_datetime(df["fecha"])

    df = df.sort_values("fecha")

    X1 = PARAMS[estacion]["X1"]
    X2 = PARAMS[estacion]["X2"]

    print("X1:", round(X1,2))
    print("X2:", round(X2,2))

    # simular

    df["Q_sim"] = modelo_hidrologico(df, X1, X2)

    # guardar serie completa

    archivo_out = os.path.join(
        OUTPUTS,
        f"simulacion_GR2M_{estacion}.csv"
    )

    df.to_csv(archivo_out, index=False)

    print("Serie guardada:", archivo_out)

    # ==================================================
    # RÉGIMEN MENSUAL
    # ==================================================

    df["mes"] = df["fecha"].dt.month

    regimen = df.groupby("mes")[["Q_mm", "Q_sim"]].mean()

    archivo_regimen = os.path.join(
        OUTPUTS,
        f"regimen_mensual_{estacion}.csv"
    )

    regimen.to_csv(archivo_regimen)

    print("Régimen mensual guardado:", archivo_regimen)

print("\n====================================")
print("SIMULACIÓN COMPLETADA")
print("====================================")
