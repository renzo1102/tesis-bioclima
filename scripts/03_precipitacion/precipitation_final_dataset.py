"""
Script: precipitation_final_dataset.py

Descripción general
-------------------
Este script construye la serie mensual final de precipitación
para las unidades hidrográficas Matoc y Pocco en el periodo
2012–2022 mediante una estrategia jerárquica de completación.

La completación sigue el siguiente orden de prioridad:

1. Observaciones directas de precipitación en la UH
2. Estimación mediante regresión lineal con estación ANA 1
3. Datos satelitales CHIRPS previamente corregidos por sesgo

Entradas
--------
- Series mensuales observadas UH
- Series mensuales estaciones ANA
- Series CHIRPS corregidas

Salidas
-------
- Series mensuales completas por UH
- Ecuaciones de regresión utilizadas
- Resumen de fuentes de completación

Autor: Renzo Mendoza  
Año: 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error


# ============================================================
# 1. CONFIGURACIÓN DE RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_MENSUALES = BASE_DIR / "outputs/mensuales"
INPUT_CHIRPS_CORR = BASE_DIR / "outputs/chirps_corregido"

OUTPUT_DIR = BASE_DIR / "outputs/serie_final"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. CARGA DE SERIES
# ============================================================

"""
Se cargan las series observadas de precipitación mensual
para las unidades hidrográficas y estaciones.
"""

matoc_obs = pd.read_csv(
    INPUT_MENSUALES / "4_Matoc_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

pocco_obs = pd.read_csv(
    INPUT_MENSUALES / "4_Pocco_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

estaciones = pd.read_csv(
    INPUT_MENSUALES / "mensual_estaciones_2012_2022.csv",
    parse_dates=["fecha_mensual"]
)

ana1 = estaciones[
    estaciones["Estacion"] == "ANA 1"
][["fecha_mensual", "Prec_mensual"]].rename(
    columns={"Prec_mensual": "ANA1"}
)


# ============================================================
# 3. FUNCIÓN DE AJUSTE DE REGRESIÓN
# ============================================================

def ajustar_regresion(df_uh, ana1_df, nombre_uh):

    """
    Ajusta un modelo de regresión lineal simple entre
    precipitación mensual de la UH y estación ANA 1.

    Permite estimar valores faltantes mediante relación espacial.
    """

    df = df_uh.merge(
        ana1_df,
        on="fecha_mensual",
        how="inner"
    ).dropna()

    X = df[["ANA1"]].values
    y = df["Prec_UH_OBS"].values

    modelo = LinearRegression()
    modelo.fit(X, y)

    pred = modelo.predict(X)

    r2 = r2_score(y, pred)
    rmse = np.sqrt(mean_squared_error(y, pred))

    a = modelo.intercept_
    b = modelo.coef_[0]

    print(f"\nModelo {nombre_uh}")
    print(f"UH = {round(a,2)} + {round(b,2)} * ANA1")
    print(f"R2={round(r2,3)} | RMSE={round(rmse,2)}")

    return modelo, a, b, r2, rmse


# ============================================================
# 4. FUNCIÓN DE COMPLETACIÓN JERÁRQUICA
# ============================================================

def completar_serie(base, uh_obs, ana1_df,
                   chirps_df, modelo, nombre_col):

    """
    Completa la serie mensual aplicando prioridad:

    OBS → REGRESIÓN ANA → CHIRPS CORREGIDO
    """

    df = base.merge(uh_obs, on="fecha_mensual", how="left")
    df = df.merge(ana1_df, on="fecha_mensual", how="left")
    df = df.merge(
        chirps_df[["fecha_mensual",
                   f"{nombre_col}_CORR"]],
        on="fecha_mensual",
        how="left"
    )

    valores = []
    fuentes = []

    for _, row in df.iterrows():

        if not pd.isna(row["Prec_UH_OBS"]):

            valores.append(row["Prec_UH_OBS"])
            fuentes.append("OBS")

        elif not pd.isna(row["ANA1"]):

            pred = modelo.predict([[row["ANA1"]]])[0]

            valores.append(max(pred, 0))
            fuentes.append("REG_ANA1")

        else:

            valores.append(row[f"{nombre_col}_CORR"])
            fuentes.append("CHIRPS_CORR")

    df["Precip_final"] = valores
    df["Fuente"] = fuentes

    return df
