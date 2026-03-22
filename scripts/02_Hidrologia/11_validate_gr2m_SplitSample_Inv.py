# ======================================================
# FASE 9
# VALIDACIÓN MODELO HIDROLÓGICO GR2M
# + SPLIT-SAMPLE INVERSO (VALIDACIÓN RIGUROSA)
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

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_MODEL = os.path.join(BASE_DIR, "data_model")
OUTPUTS = os.path.join(BASE_DIR, "outputs")

ESTACIONES = ["Matoc", "Pocco"]

LAG = 0

# ======================================================
# MODELO GR2M
# ======================================================

def modelo_hidrologico(df, X1, X2):

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

        # RESERVORIO
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
# CARGAR PARÁMETROS
# ======================================================

archivo_param = os.path.join(OUTPUTS, "parametros_modelo.json")

with open(archivo_param) as f:
    parametros = json.load(f)


# ======================================================
# VALIDACIÓN
# ======================================================

resultados = []

for estacion in ESTACIONES:

    print("\n------------------------------------")
    print("Validando estación:", estacion)
    print("------------------------------------")

    archivo = os.path.join(DATA_MODEL, f"modelo_{estacion}.csv")

    if not os.path.exists(archivo):
        print("⚠ Archivo no encontrado:", archivo)
        continue

    df = pd.read_csv(archivo)

    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha").reset_index(drop=True)

    # aplicar rezago
    df["P_lag"] = df["P_mm"].shift(LAG)

    # parámetros calibrados
    X1 = parametros[estacion]["X1"]
    X2 = parametros[estacion]["X2"]

    print("X1:", round(X1,2))
    print("X2:", round(X2,3))

    # simulación
    Qsim_full = modelo_hidrologico(df, X1, X2)
    df["Q_sim"] = Qsim_full

    # ======================================================
    # VALIDACIÓN ORIGINAL
    # ======================================================

    df_val = df[(df["usar_validacion"] == True) &
                (df["Q_mm"].notna())]

    print("\n--- VALIDACIÓN ORIGINAL ---")
    print("Meses:", len(df_val))

    NSE, R2, RMSE, PBIAS = calcular_metricas(
        df_val["Q_mm"].values,
        df_val["Q_sim"].values
    )

    print("NSE :", round(NSE,3))
    print("R2  :", round(R2,3))
    print("RMSE:", round(RMSE,3))
    print("PBIAS:", round(PBIAS,2))

    # guardar serie original
    archivo_val = os.path.join(
        OUTPUTS,
        f"serie_validacion_{estacion}.csv"
    )

    df_val.to_csv(archivo_val, index=False)

    # ======================================================
    # VALIDACIÓN INVERSA
    # ======================================================

    df_val_inv = df[(df["usar_calibracion"] == True) &
                    (df["Q_mm"].notna())]

    print("\n--- VALIDACIÓN INVERSA ---")
    print("Meses:", len(df_val_inv))

    NSE_i, R2_i, RMSE_i, PBIAS_i = calcular_metricas(
        df_val_inv["Q_mm"].values,
        df_val_inv["Q_sim"].values
    )

    print("NSE :", round(NSE_i,3))
    print("R2  :", round(R2_i,3))
    print("RMSE:", round(RMSE_i,3))
    print("PBIAS:", round(PBIAS_i,2))

    # guardar serie inversa
    archivo_val_inv = os.path.join(
        OUTPUTS,
        f"serie_validacion_inversa_{estacion}.csv"
    )

    df_val_inv.to_csv(archivo_val_inv, index=False)

    # ======================================================
    # GUARDAR RESULTADOS
    # ======================================================

    resultados.append({

        "estacion": estacion,

        "NSE_val": NSE,
        "R2_val": R2,
        "RMSE_val": RMSE,
        "PBIAS_val": PBIAS,

        "NSE_inv": NSE_i,
        "R2_inv": R2_i,
        "RMSE_inv": RMSE_i,
        "PBIAS_inv": PBIAS_i
    })


# ======================================================
# GUARDAR TABLA FINAL
# ======================================================

df_result = pd.DataFrame(resultados)

archivo_out = os.path.join(
    OUTPUTS,
    "metricas_validacion_GR2M_rigurosa.csv"
)

df_result.to_csv(archivo_out, index=False)

print("\n====================================")
print("VALIDACIÓN RIGUROSA COMPLETADA")
print("Tabla guardada:", archivo_out)
print("====================================")