# ============================================================
# SCRIPT – FASE 4: ANÁLISIS REGIONAL MENSUAL
# Evaluación de coherencia UH vs estaciones ANA (ANA 1 y ANA 2)
# ============================================================

# ============================================================
# DESCRIPCIÓN GENERAL
# ============================================================
# Este script evalúa la coherencia hidrológica entre las series
# mensuales construidas a nivel de Unidad Hidrológica (UH)
# y las estaciones de referencia regional (ANA 1 y ANA 2).
#
# Objetivo:
# - Validar la consistencia espacial de las series UH
# - Comparar comportamiento regional de precipitación
# - Cuantificar similitud estadística entre series
#
# Enfoque:
# - Se comparan las series UH (Matoc y Pocco) con:
#     - ANA 1
#     - ANA 2
# - Se calculan métricas de desempeño tipo modelamiento
#
# Métricas calculadas:
# - R   : correlación de Pearson
# - R²  : coeficiente de determinación
# - RMSE: error cuadrático medio
# - Bias: sesgo medio
# - NSE : eficiencia de Nash-Sutcliffe
#
# Entradas:
# - Series UH mensuales (FASE 3)
# - Series mensuales por estación (FASE 2)
#
# Salidas:
# - Tabla de métricas regionales por UH
#
# Importancia:
# - Permite validar calidad de las series UH
# - Detecta sesgos sistemáticos
# - Base para validación de productos satelitales (CHIRPS)

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# RUTAS ROBUSTAS
# ============================================================
# Uso de rutas relativas dinámicas basadas en la ubicación del script.
# Esto garantiza portabilidad en cualquier sistema.

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "outputs/mensuales"
OUTPUT_DIR = BASE_DIR / "outputs/analisis_regional"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CARGAR DATOS
# ============================================================

print("\nCargando datos...")

# Series UH construidas (FASE 3)
matoc = pd.read_csv(
    INPUT_DIR / "4_Matoc_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

pocco = pd.read_csv(
    INPUT_DIR / "4_Pocco_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

# Series mensuales por estación (FASE 2)
estaciones = pd.read_csv(
    INPUT_DIR / "mensual_estaciones_2012_2022.csv",
    parse_dates=["fecha_mensual"]
)

# ============================================================
# EXTRACCIÓN DE ESTACIONES DE REFERENCIA (ANA)
# ============================================================
# Se seleccionan estaciones clave de referencia regional.

ana1 = estaciones[estaciones["Estacion"] == "ANA 1"][
    ["fecha_mensual", "Prec_mensual"]
].rename(columns={"Prec_mensual": "ANA1"})

ana2 = estaciones[estaciones["Estacion"] == "ANA 2"][
    ["fecha_mensual", "Prec_mensual"]
].rename(columns={"Prec_mensual": "ANA2"})

# ============================================================
# FUNCIÓN DE CÁLCULO DE MÉTRICAS
# ============================================================

def calcular_metricas(obs, pred):
    """
    Calcula métricas estadísticas entre dos series.

    Parámetros:
    - obs : serie observada (UH)
    - pred: serie de referencia (ANA)

    Retorna:
    - Diccionario con métricas o None si no hay suficientes datos
    """

    # Filtrar pares válidos simultáneamente
    mask = (~obs.isna()) & (~pred.isna())
    obs = obs[mask]
    pred = pred[mask]

    # Se requiere mínimo de datos para análisis robusto
    if len(obs) < 10:
        return None

    # --------------------------------------------------------
    # MÉTRICAS
    # --------------------------------------------------------

    # Correlación de Pearson
    r = np.corrcoef(obs, pred)[0, 1]
    r2 = r ** 2

    # Error cuadrático medio
    rmse = np.sqrt(np.mean((obs - pred) ** 2))

    # Sesgo (diferencia de medias)
    bias = pred.mean() - obs.mean()

    # Eficiencia de Nash-Sutcliffe (NSE)
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
# FUNCIÓN DE ANÁLISIS POR UH
# ============================================================

def analizar_uh(df_uh, nombre_uh):
    """
    Compara una serie UH contra estaciones ANA.

    Parámetros:
    - df_uh: DataFrame de la UH
    - nombre_uh: nombre de la unidad hidrológica

    Retorna:
    - Lista de resultados con métricas
    """

    # Unión temporal con estaciones ANA
    df = df_uh.merge(ana1, on="fecha_mensual", how="left")
    df = df.merge(ana2, on="fecha_mensual", how="left")

    resultados = []

    # Comparación con ANA 1
    met_ana1 = calcular_metricas(df["Prec_UH_OBS"], df["ANA1"])
    if met_ana1:
        resultados.append({
            "UH": nombre_uh,
            "Predictor": "ANA 1",
            **met_ana1
        })

    # Comparación con ANA 2
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

# Consolidación de resultados
resumen = pd.DataFrame(res_matoc + res_pocco)

# ============================================================
# EXPORTACIÓN
# ============================================================

output_file = OUTPUT_DIR / "5_metricas_regionales.csv"
resumen.to_csv(output_file, index=False)

print("\nResultados:")
print(resumen)

print("\nArchivo generado:")
print(output_file)

print("\nFASE 4 COMPLETADA.")

# ============================================================
# INTERPRETACIÓN METODOLÓGICA
# ============================================================
# Esta fase evalúa la consistencia regional de las series UH.
#
# Interpretación de métricas:
#
# - R / R²:
#   Indican similitud temporal entre UH y ANA.
#
# - RMSE:
#   Mide el error absoluto en mm.
#
# - Bias:
#   Detecta sobreestimación (>0) o subestimación (<0).
#
# - NSE:
#   > 0.5 → buen desempeño
#   ~ 1   → excelente ajuste
#   < 0   → mal desempeño
#
# Uso en el estudio:
# - Validar representatividad espacial de las UH
# - Identificar estaciones más consistentes
# - Base para comparación con CHIRPS y modelamiento
#
# Resultado:
# - Validación cuantitativa de coherencia regional
# - Soporte para decisiones metodológicas posteriores
# ============================================================
