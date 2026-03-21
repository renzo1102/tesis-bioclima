"""
Script: precipitation_final_validation.py

Descripción general
-------------------
Este script evalúa la robustez de la serie mensual final
de precipitación mediante validación cruzada tipo Monte Carlo.

Se eliminan aleatoriamente datos observados y se reconstruyen
utilizando regresión espacial con estación ANA 1 o, en ausencia
de esta, datos satelitales CHIRPS corregidos.

Entradas
--------
- Series mensuales observadas UH
- Series CHIRPS corregidas
- Serie estación ANA 1

Salidas
-------
- Métricas por iteración
- Resumen promedio de desempeño

Autor: Renzo Mendoza
Año: 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    r2_score,
    mean_squared_error,
    mean_absolute_error
)

np.random.seed(42)


# ============================================================
# 1. CONFIGURACIÓN DE RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_MENSUALES = BASE_DIR / "outputs/mensuales"
INPUT_CHIRPS = BASE_DIR / "outputs/chirps_corregido"

OUTPUT_DIR = BASE_DIR / "outputs/validacion_cruzada"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. FUNCIÓN DE CÁLCULO DE MÉTRICAS
# ============================================================

def calcular_metricas(obs, pred):

    """
    Calcula métricas de desempeño entre valores observados
    y reconstruidos.

    Métricas:
    - Correlación
    - R²
    - RMSE
    - MAE
    - Bias porcentual
    - NSE
    """

    r = np.corrcoef(obs, pred)[0, 1]
    r2 = r ** 2
    rmse = np.sqrt(mean_squared_error(obs, pred))
    mae = mean_absolute_error(obs, pred)

    bias = pred.mean() - obs.mean()
    bias_pct = (bias / obs.mean()) * 100

    nse = 1 - (
        np.sum((obs - pred) ** 2) /
        np.sum((obs - obs.mean()) ** 2)
    )

    return r, r2, rmse, mae, bias_pct, nse


# ============================================================
# 3. FUNCIÓN DE VALIDACIÓN MONTE CARLO
# ============================================================

def validacion_montecarlo(uh_obs, chirps_df, nombre_uh):

    """
    Ejecuta validación cruzada Monte Carlo eliminando
    aleatoriamente el 20% de los datos observados.

    Se reconstruyen los valores faltantes usando:

    1. Regresión con ANA 1
    2. CHIRPS corregido
    """

    resultados = []

    df = uh_obs.merge(
        ana1,
        on="fecha_mensual",
        how="left"
    )

    df = df.merge(
        chirps_df[
            ["fecha_mensual",
             chirps_df.columns[-1]]
        ],
        on="fecha_mensual",
        how="left"
    )

    df = df.dropna(subset=["Prec_UH_OBS"])

    for i in range(30):

        df_iter = df.copy()

        n_remove = int(len(df_iter) * 0.2)

        idx_remove = np.random.choice(
            df_iter.index,
            n_remove,
            replace=False
        )

        df_iter.loc[
            idx_remove,
            "Prec_UH_OBS"
        ] = np.nan

        df_train = df_iter.dropna(
            subset=["Prec_UH_OBS", "ANA1"]
        )

        X_train = df_train[["ANA1"]].values
        y_train = df_train["Prec_UH_OBS"].values

        modelo = LinearRegression()
        modelo.fit(X_train, y_train)

        predicciones = []
        reales = []

        for idx in idx_remove:

            row = df.loc[idx]

            if not pd.isna(row["ANA1"]):

                pred = modelo.predict(
                    [[row["ANA1"]]]
                )[0]

            else:

                pred = row[
                    chirps_df.columns[-1]
                ]

            predicciones.append(max(pred, 0))
            reales.append(row["Prec_UH_OBS"])

        r, r2, rmse, mae, bias_pct, nse = calcular_metricas(
            np.array(reales),
            np.array(predicciones)
        )

        resultados.append({
            "UH": nombre_uh,
            "Iteracion": i + 1,
            "R": r,
            "R2": r2,
            "RMSE": rmse,
            "MAE": mae,
            "Bias_%": bias_pct,
            "NSE": nse
        })

    return pd.DataFrame(resultados)
