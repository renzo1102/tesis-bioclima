"""
Script: streamflow_comparison_observed_vs_simulated.py

Descripción:
Realiza la validación hidrológica del modelo GR2M mediante
comparación entre caudales observados y simulados.

Entradas:
Series mensuales de precipitación, PET y caudal observado.

Salidas:
Series simuladas, métricas de desempeño hidrológico y
archivos de validación.

Autor: Renzo Mendoza
Año: 2026
"""

# ======================================================
# SCRIPT 17
# FASE 9
# VALIDACIÓN MODELO HIDROLÓGICO GR2M
# ======================================================

import pandas as pd
import numpy as np
import os
import json

print("\n====================================")
print("FASE 9 - VALIDACIÓN MODELO GR2M")
print("====================================")

# ======================================================
# RUTAS
# ======================================================
# Se define el directorio base del proyecto para asegurar
# ejecución reproducible en cualquier entorno.

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_MODEL = os.path.join(BASE_DIR, "data_model")
OUTPUTS = os.path.join(BASE_DIR, "outputs")

# estaciones hidrológicas analizadas
ESTACIONES = ["Matoc", "Pocco"]

# rezago hidrológico aplicado a precipitación
LAG = 0

# ======================================================
# MODELO GR2M
# ======================================================
# Implementación del modelo lluvia–escorrentía GR2M.
#
# X1 → capacidad máxima del reservorio de producción (mm)
# X2 → coeficiente del reservorio de enrutamiento
#
# El modelo representa:
# ✔ balance hídrico en el suelo
# ✔ percolación
# ✔ almacenamiento subsuperficial
# ✔ generación de caudal mensual

def modelo_hidrologico(df, X1, X2):

    # almacenamiento inicial en reservorio de producción
    S = 0.5 * X1

    # almacenamiento inicial en reservorio de enrutamiento
    R = 30

    Qsim = []

    for _, row in df.iterrows():

        P = row["P_lag"]
        E = row["PET_mm"]

        # si no hay precipitación válida no se simula
        if np.isnan(P):

            Qsim.append(np.nan)
            continue

        # ==================================================
        # PRODUCCIÓN
        # ==================================================
        # Determina infiltración, evaporación real y exceso.

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

        # ==================================================
        # PERCOLACIÓN
        # ==================================================
        # Representa transferencia hacia almacenamiento profundo.

        Perc = S * (1 - (1 + (4/9)*(S/X1)**4)**(-0.25))

        S = S - Perc

        if S < 0:
            S = 0

        # ==================================================
        # RESERVORIO DE ENRUTAMIENTO
        # ==================================================
        # Simula propagación del flujo hasta la salida de la cuenca.

        R = R + Perc + Pe

        Q = R * (1 - (1 + (R/X2)**4)**(-0.25))

        R = R - Q

        if R < 0:
            R = 0

        Qsim.append(Q)

    return np.array(Qsim)


# ======================================================
# MÉTRICAS HIDROLÓGICAS
# ======================================================
# Evalúan desempeño del modelo comparando Q observado vs simulado.

def calcular_metricas(Qobs, Qsim):

    # eliminar pares sin datos observados
    mask = ~np.isnan(Qobs)

    Qobs = Qobs[mask]
    Qsim = Qsim[mask]

    # control de tamaño mínimo de muestra
    if len(Qobs) < 5:
        return np.nan, np.nan, np.nan, np.nan

    # eficiencia Nash–Sutcliffe
    NSE = 1 - np.sum((Qobs - Qsim)**2) / \
              np.sum((Qobs - np.mean(Qobs))**2)

    # coeficiente de determinación
    R2 = np.corrcoef(Qobs, Qsim)[0,1]**2

    # error cuadrático medio
    RMSE = np.sqrt(np.mean((Qobs - Qsim)**2))

    # sesgo porcentual
    PBIAS = 100 * (np.sum(Qsim - Qobs) /
                   np.sum(Qobs))

    return NSE, R2, RMSE, PBIAS


# ======================================================
# CARGAR PARÁMETROS CALIBRADOS
# ======================================================

archivo_param = os.path.join(
    OUTPUTS,
    "parametros_modelo.json"
)

with open(archivo_param) as f:
    parametros = json.load(f)


# ======================================================
# VALIDACIÓN HIDROLÓGICA
# ======================================================

resultados = []

for estacion in ESTACIONES:

    print("\n------------------------------------")
    print("Validando estación:", estacion)
    print("------------------------------------")

    archivo = os.path.join(
        DATA_MODEL,
        f"modelo_{estacion}.csv"
    )

    if not os.path.exists(archivo):

        print("⚠ Archivo no encontrado:", archivo)
        continue

    df = pd.read_csv(archivo)

    df["fecha"] = pd.to_datetime(df["fecha"])

    df = df.sort_values("fecha").reset_index(drop=True)

    # aplicar rezago a precipitación
    df["P_lag"] = df["P_mm"].shift(LAG)

    # parámetros calibrados del modelo
    X1 = parametros[estacion]["X1"]
    X2 = parametros[estacion]["X2"]

    print("X1:", round(X1,2))
    print("X2:", round(X2,3))

    # simulación completa del periodo
    Qsim_full = modelo_hidrologico(df, X1, X2)

    df["Q_sim"] = Qsim_full

    # seleccionar solo periodo de validación
    df_val = df[(df["usar_validacion"] == True) &
                (df["Q_mm"].notna())]

    print("Meses validación:", len(df_val))

    NSE, R2, RMSE, PBIAS = calcular_metricas(
        df_val["Q_mm"].values,
        df_val["Q_sim"].values
    )

    print("\nMétricas validación")

    print("NSE :", round(NSE,3))
    print("R2  :", round(R2,3))
    print("RMSE:", round(RMSE,3))
    print("PBIAS:", round(PBIAS,2))

    # guardar serie validada
    archivo_val = os.path.join(
        OUTPUTS,
        f"serie_validacion_{estacion}.csv"
    )

    df_val.to_csv(archivo_val, index=False)

    print("Serie guardada:", archivo_val)

    resultados.append({

        "estacion": estacion,
        "NSE": NSE,
        "R2": R2,
        "RMSE": RMSE,
        "PBIAS": PBIAS

    })


# ======================================================
# GUARDAR TABLA FINAL DE MÉTRICAS
# ======================================================

df_result = pd.DataFrame(resultados)

archivo_out = os.path.join(
    OUTPUTS,
    "metricas_validacion_GR2M.csv"
)

df_result.to_csv(archivo_out, index=False)

print("\n====================================")
print("VALIDACIÓN COMPLETADA")
print("Tabla guardada:", archivo_out)
print("====================================")
