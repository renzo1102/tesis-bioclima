# ============================================================
# FASE 5 — VALIDACIÓN INTEGRAL CHIRPS (AJUSTADA A RESULTADOS)
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
OUTPUT_DIR = BASE_DIR / "outputs/validacion_chirps"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CARGAR OBSERVADOS
# ============================================================

matoc_obs = pd.read_csv(
    INPUT_OBS / "4_Matoc_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

pocco_obs = pd.read_csv(
    INPUT_OBS / "4_Pocco_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

estaciones = pd.read_csv(
    INPUT_OBS / "mensual_estaciones_2012_2022.csv",
    parse_dates=["fecha_mensual"]
)

ana1_obs = estaciones[estaciones["Estacion"] == "ANA 1"][
    ["fecha_mensual", "Prec_mensual"]
].rename(columns={"Prec_mensual": "ANA1_OBS"})

ana2_obs = estaciones[estaciones["Estacion"] == "ANA 2"][
    ["fecha_mensual", "Prec_mensual"]
].rename(columns={"Prec_mensual": "ANA2_OBS"})

# ============================================================
# CARGAR CHIRPS
# ============================================================

def cargar_chirps(nombre_archivo, nueva_col):
    df = pd.read_csv(INPUT_CHIRPS / nombre_archivo)
    df["fecha_mensual"] = pd.to_datetime(df["date"] + "-01")
    df = df.rename(columns={"CHIRPS": nueva_col})
    return df[["fecha_mensual", nueva_col]]

matoc_ch = cargar_chirps("CHIRPS_MATOC_2012_2022.csv", "CHIRPS_MATOC")
pocco_ch = cargar_chirps("CHIRPS_POCCO_2012_2022.csv", "CHIRPS_POCCO")
ana1_ch = cargar_chirps("CHIRPS_ANA1_2012_2022.csv", "CHIRPS_ANA1")
ana2_ch = cargar_chirps("CHIRPS_ANA2_2012_2022.csv", "CHIRPS_ANA2")

# ============================================================
# FUNCIÓN MÉTRICAS
# ============================================================

def calcular_metricas(obs, pred):

    mask = (~obs.isna()) & (~pred.isna())
    obs = obs[mask]
    pred = pred[mask]

    if len(obs) < 10:
        return None

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
# VALIDACIONES
# ============================================================

resultados = []

# ANA 1
df = ana1_obs.merge(ana1_ch, on="fecha_mensual", how="inner")
met = calcular_metricas(df["ANA1_OBS"], df["CHIRPS_ANA1"])
if met:
    resultados.append({"Serie": "ANA 1", **met})

# ANA 2
df = ana2_obs.merge(ana2_ch, on="fecha_mensual", how="inner")
met = calcular_metricas(df["ANA2_OBS"], df["CHIRPS_ANA2"])
if met:
    resultados.append({"Serie": "ANA 2", **met})

# Matoc
df = matoc_obs.merge(matoc_ch, on="fecha_mensual", how="inner")
met = calcular_metricas(df["Prec_UH_OBS"], df["CHIRPS_MATOC"])
if met:
    resultados.append({"Serie": "Matoc_UH", **met})

# Pocco
df = pocco_obs.merge(pocco_ch, on="fecha_mensual", how="inner")
met = calcular_metricas(df["Prec_UH_OBS"], df["CHIRPS_POCCO"])
if met:
    resultados.append({"Serie": "Pocco_UH", **met})

resumen = pd.DataFrame(resultados)

resumen.to_csv(
    OUTPUT_DIR / "7_fase5_validacion_chirps_integral.csv",
    index=False
)

print("\nRESULTADOS FASE 5 — VALIDACIÓN INTEGRAL CHIRPS")
print(resumen)
print("\nFASE 5 COMPLETADA.")