"""
Script: precipitation_regional_metrics.py

Descripción general
-------------------
Este script evalúa la coherencia espacial de la precipitación
mensual observada en las unidades hidrográficas Matoc y Pocco
respecto a estaciones regionales de referencia (ANA 1 y ANA 2).

Se calculan métricas estadísticas de desempeño para determinar
la representatividad espacial de las estaciones como predictores
de precipitación en las UH.

Entradas
--------
- Series mensuales observadas UH
- Series mensuales estaciones

Salidas
-------
- Métricas estadísticas regionales de coherencia espacial

Autor: Renzo Mendoza
Año: 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# 1. CONFIGURACIÓN DE RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "outputs/mensuales"
OUTPUT_DIR = BASE_DIR / "outputs/analisis_regional"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. FUNCIÓN CÁLCULO DE MÉTRICAS
# ============================================================

def calcular_metricas(obs, pred):

    """
    Calcula métricas de coherencia espacial entre
    precipitación observada en UH y estación regional.

    Métricas:
    - Correlación
    - R²
    - RMSE
    - Bias
    - NSE
    """

    mask = (~obs.isna()) & (~pred.isna())

    obs = obs[mask]
    pred = pred[mask]

    if len(obs) < 10:
        return None

    r = np.corrcoef(obs, pred)[0, 1]
    r2 = r ** 2

    rmse = np.sqrt(
        np.mean((obs - pred) ** 2)
    )

    bias = pred.mean() - obs.mean()

    nse = 1 - (
        np.sum((obs - pred) ** 2) /
        np.sum((obs - obs.mean()) ** 2)
    )

    return {
        "R": round(r, 3),
        "R2": round(r2, 3),
        "RMSE": round(rmse, 2),
        "Bias": round(bias, 2),
        "NSE": round(nse, 3),
        "n_meses": len(obs)
    }


# ============================================================
# 3. FUNCIÓN ANÁLISIS POR UH
# ============================================================

def analizar_uh(df_uh, nombre_uh):

    """
    Evalúa coherencia espacial de una UH
    frente a estaciones ANA.
    """

    df = df_uh.merge(
        ana1,
        on="fecha_mensual",
        how="left"
    )

    df = df.merge(
        ana2,
        on="fecha_mensual",
        how="left"
    )

    resultados = []

    met_ana1 = calcular_metricas(
        df["Prec_UH_OBS"],
        df["ANA1"]
    )

    if met_ana1:
        resultados.append({
            "UH": nombre_uh,
            "Predictor": "ANA 1",
            **met_ana1
        })

    met_ana2 = calcular_metricas(
        df["Prec_UH_OBS"],
        df["ANA2"]
    )

    if met_ana2:
        resultados.append({
            "UH": nombre_uh,
            "Predictor": "ANA 2",
            **met_ana2
        })

    return resultados
