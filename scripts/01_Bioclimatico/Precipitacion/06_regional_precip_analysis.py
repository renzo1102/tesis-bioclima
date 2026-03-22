# ============================================================
# FASE 4 — ANÁLISIS REGIONAL MENSUAL
# Evaluación coherencia UH vs ANA 1 y ANA 2
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# RUTAS ROBUSTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "outputs/mensuales"
OUTPUT_DIR = BASE_DIR / "outputs/analisis_regional"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CARGAR DATOS
# ============================================================

print("\nCargando datos...")

matoc = pd.read_csv(
    INPUT_DIR / "4_Matoc_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

pocco = pd.read_csv(
    INPUT_DIR / "4_Pocco_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

estaciones = pd.read_csv(
    INPUT_DIR / "mensual_estaciones_2012_2022.csv",
    parse_dates=["fecha_mensual"]
)

# ============================================================
# EXTRAER ANA 1 Y ANA 2
# ============================================================

ana1 = estaciones[estaciones["Estacion"] == "ANA 1"][
    ["fecha_mensual", "Prec_mensual"]
].rename(columns={"Prec_mensual": "ANA1"})

ana2 = estaciones[estaciones["Estacion"] == "ANA 2"][
    ["fecha_mensual", "Prec_mensual"]
].rename(columns={"Prec_mensual": "ANA2"})

# ============================================================
# FUNCIÓN MÉTRICAS
# ============================================================

def calcular_metricas(obs, pred):

    # Quitar NaN simultáneamente
    mask = (~obs.isna()) & (~pred.isna())
    obs = obs[mask]
    pred = pred[mask]

    if len(obs) < 10:
        return None

    # Correlación
    r = np.corrcoef(obs, pred)[0, 1]
    r2 = r ** 2

    # RMSE
    rmse = np.sqrt(np.mean((obs - pred) ** 2))

    # Bias
    bias = pred.mean() - obs.mean()

    # NSE
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
# FUNCIÓN PARA ANALIZAR CADA UH
# ============================================================

def analizar_uh(df_uh, nombre_uh):

    df = df_uh.merge(ana1, on="fecha_mensual", how="left")
    df = df.merge(ana2, on="fecha_mensual", how="left")

    resultados = []

    met_ana1 = calcular_metricas(df["Prec_UH_OBS"], df["ANA1"])
    if met_ana1:
        resultados.append({
            "UH": nombre_uh,
            "Predictor": "ANA 1",
            **met_ana1
        })

    met_ana2 = calcular_metricas(df["Prec_UH_OBS"], df["ANA2"])
    if met_ana2:
        resultados.append({
            "UH": nombre_uh,
            "Predictor": "ANA 2",
            **met_ana2
        })

    return resultados

# ============================================================
# EJECUCIÓN
# ============================================================

print("Calculando métricas regionales...")

res_matoc = analizar_uh(matoc, "Matoc")
res_pocco = analizar_uh(pocco, "Pocco")

resumen = pd.DataFrame(res_matoc + res_pocco)

# ============================================================
# GUARDAR RESULTADOS
# ============================================================

output_file = OUTPUT_DIR / "5_metricas_regionales.csv"
resumen.to_csv(output_file, index=False)

print("\nResultados:")
print(resumen)

print("\nArchivo generado:")
print(output_file)

print("\nFASE 4 COMPLETADA.")