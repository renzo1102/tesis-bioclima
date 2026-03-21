"""
Script: chirps_bias_correction.py

Descripción:
Corrige sesgo CHIRPS

Entradas:
CHIRPS, estaciones

Salidas:
CHIRPS corregido

Autor: Renzo Mendoza
Año: 2026
"""
# ============================================================
# SCRIPT 9
# FASE 6 — CORRECCIÓN MENSUAL CHIRPS (BASE ANA 1)
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_OBS = BASE_DIR / "outputs/mensuales"
INPUT_CHIRPS = BASE_DIR / "outputs/chirps"
OUTPUT_DIR = BASE_DIR / "outputs/chirps_corregido"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CARGAR ANA 1 OBSERVADO
# ============================================================

estaciones = pd.read_csv(
    INPUT_OBS / "mensual_estaciones_2012_2022.csv",
    parse_dates=["fecha_mensual"]
)

ana1_obs = estaciones[
    estaciones["Estacion"] == "ANA 1"
][["fecha_mensual", "Prec_mensual"]].rename(
    columns={"Prec_mensual": "ANA1_OBS"}
)

# ============================================================
# CARGAR CHIRPS
# ============================================================

def cargar_chirps(nombre_archivo, nueva_col):
    df = pd.read_csv(INPUT_CHIRPS / nombre_archivo)
    df["fecha_mensual"] = pd.to_datetime(df["date"] + "-01")
    df["mes"] = df["fecha_mensual"].dt.month
    df = df.rename(columns={"CHIRPS": nueva_col})
    return df

ana1_ch = cargar_chirps("CHIRPS_ANA1_2012_2022.csv", "CHIRPS_ANA1")
matoc_ch = cargar_chirps("CHIRPS_MATOC_2012_2022.csv", "CHIRPS_MATOC")
pocco_ch = cargar_chirps("CHIRPS_POCCO_2012_2022.csv", "CHIRPS_POCCO")

# ============================================================
# CALCULAR FACTORES MENSUALES (BASE ANA 1)
# ============================================================

df_factor = ana1_obs.merge(
    ana1_ch[["fecha_mensual", "CHIRPS_ANA1"]],
    on="fecha_mensual",
    how="inner"
)

df_factor["mes"] = df_factor["fecha_mensual"].dt.month

factores = (
    df_factor
    .groupby("mes")
    .apply(lambda x: x["ANA1_OBS"].mean() / x["CHIRPS_ANA1"].mean())
    .reset_index(name="Factor_correccion")
)

factores.to_csv(
    OUTPUT_DIR / "factores_mensuales_base_ANA1.csv",
    index=False
)

print("\nFACTORES MENSUALES:")
print(factores)

# ============================================================
# APLICAR CORRECCIÓN
# ============================================================

def aplicar_correccion(df, col_name):
    df = df.merge(factores, on="mes", how="left")
    df[f"{col_name}_CORR"] = df[col_name] * df["Factor_correccion"]
    return df

ana1_corr = aplicar_correccion(ana1_ch, "CHIRPS_ANA1")
matoc_corr = aplicar_correccion(matoc_ch, "CHIRPS_MATOC")
pocco_corr = aplicar_correccion(pocco_ch, "CHIRPS_POCCO")

# ============================================================
# GUARDAR SERIES CORREGIDAS
# ============================================================

ana1_corr.to_csv(
    OUTPUT_DIR / "CHIRPS_ANA1_corregido.csv",
    index=False
)

matoc_corr.to_csv(
    OUTPUT_DIR / "CHIRPS_MATOC_corregido.csv",
    index=False
)

pocco_corr.to_csv(
    OUTPUT_DIR / "CHIRPS_POCCO_corregido.csv",
    index=False
)

# ============================================================
# FUNCIÓN MÉTRICAS
# ============================================================

def calcular_metricas(obs, pred):

    mask = (~obs.isna()) & (~pred.isna())
    obs = obs[mask]
    pred = pred[mask]

    r = np.corrcoef(obs, pred)[0, 1]
    r2 = r ** 2
    rmse = np.sqrt(np.mean((obs - pred) ** 2))
    bias = pred.mean() - obs.mean()
    bias_pct = (bias / obs.mean()) * 100

    nse = 1 - (
        np.sum((obs - pred) ** 2) /
        np.sum((obs - obs.mean()) ** 2)
    )

    return {
        "R": round(r, 3),
        "R2": round(r2, 3),
        "RMSE": round(rmse, 2),
        "Bias_mm": round(bias, 2),
        "Bias_%": round(bias_pct, 2),
        "NSE": round(nse, 3),
        "n_meses": len(obs)
    }

# ============================================================
# EVALUACIÓN POST CORRECCIÓN (ANA 1)
# ============================================================

df_eval = ana1_obs.merge(
    ana1_corr[["fecha_mensual", "CHIRPS_ANA1_CORR"]],
    on="fecha_mensual",
    how="inner"
)

metricas_post = calcular_metricas(
    df_eval["ANA1_OBS"],
    df_eval["CHIRPS_ANA1_CORR"]
)

metricas_df = pd.DataFrame([metricas_post])
metricas_df.to_csv(
    OUTPUT_DIR / "metricas_post_correccion_ANA1.csv",
    index=False
)

print("\nMÉTRICAS DESPUÉS DE CORRECCIÓN (ANA 1):")
print(metricas_post)

print("\nFASE 6 COMPLETADA CORRECTAMENTE.")
