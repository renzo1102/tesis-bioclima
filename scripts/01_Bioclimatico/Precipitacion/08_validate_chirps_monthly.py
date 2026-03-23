# ============================================================
# FASE 5 — VALIDACIÓN INTEGRAL CHIRPS (AJUSTADA A RESULTADOS)
# ============================================================

"""
DESCRIPCIÓN GENERAL
------------------------------------------------------------
Este script realiza la validación integral del producto
satelital CHIRPS frente a datos observados de precipitación.

Se comparan cuatro tipos de series:

1. Estación ANA 1 (observado vs CHIRPS)
2. Estación ANA 2 (observado vs CHIRPS)
3. Unidad Hidrográfica Matoc (promedio observado vs CHIRPS)
4. Unidad Hidrográfica Pocco (promedio observado vs CHIRPS)

El objetivo es cuantificar el desempeño de CHIRPS en términos de:

- Correlación (R, R²)
- Error (RMSE)
- Sesgo (Bias absoluto y porcentual)
- Eficiencia hidrológica (NSE)

------------------------------------------------------------
IMPORTANCIA METODOLÓGICA

Esta fase permite:

- Evaluar la confiabilidad de CHIRPS en zonas altoandinas
- Justificar su uso en el relleno de datos faltantes
- Identificar sesgos sistemáticos del producto satelital

------------------------------------------------------------
INPUTS:

Desde outputs/mensuales:
- 4_Matoc_UH_mensual_OBS.csv
- 4_Pocco_UH_mensual_OBS.csv
- mensual_estaciones_2012_2022.csv

Desde outputs/chirps:
- CHIRPS_MATOC_2012_2022.csv
- CHIRPS_POCCO_2012_2022.csv
- CHIRPS_ANA1_2012_2022.csv
- CHIRPS_ANA2_2012_2022.csv

------------------------------------------------------------
OUTPUT:

outputs/validacion_chirps/
- 7_fase5_validacion_chirps_integral.csv

------------------------------------------------------------
NOTA:

La validación se realiza únicamente en meses con datos
observados disponibles (sin imputación).

"""

import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# RUTAS
# ============================================================
# Se usan rutas relativas robustas basadas en la ubicación del script

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_OBS = BASE_DIR / "outputs/mensuales"
INPUT_CHIRPS = BASE_DIR / "outputs/chirps"
OUTPUT_DIR = BASE_DIR / "outputs/validacion_chirps"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CARGAR DATOS OBSERVADOS
# ============================================================

# Series mensuales a nivel de unidad hidrográfica
matoc_obs = pd.read_csv(
    INPUT_OBS / "4_Matoc_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

pocco_obs = pd.read_csv(
    INPUT_OBS / "4_Pocco_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

# Series mensuales por estación
estaciones = pd.read_csv(
    INPUT_OBS / "mensual_estaciones_2012_2022.csv",
    parse_dates=["fecha_mensual"]
)

# Extracción de estaciones ANA
ana1_obs = estaciones[estaciones["Estacion"] == "ANA 1"][
    ["fecha_mensual", "Prec_mensual"]
].rename(columns={"Prec_mensual": "ANA1_OBS"})

ana2_obs = estaciones[estaciones["Estacion"] == "ANA 2"][
    ["fecha_mensual", "Prec_mensual"]
].rename(columns={"Prec_mensual": "ANA2_OBS"})


# ============================================================
# CARGAR DATOS CHIRPS
# ============================================================

def cargar_chirps(nombre_archivo, nueva_col):
    """
    Carga archivos CSV exportados desde Google Earth Engine
    y los adapta al formato del análisis.

    Parámetros:
    ----------
    nombre_archivo : str
        Nombre del archivo CSV CHIRPS
    nueva_col : str
        Nombre de la columna de salida

    Proceso:
    ----------
    - Convierte 'date' (YYYY-MM) a datetime
    - Renombra la variable CHIRPS
    - Devuelve solo columnas relevantes

    Retorna:
    ----------
    DataFrame con:
    - fecha_mensual
    - variable CHIRPS renombrada
    """

    df = pd.read_csv(INPUT_CHIRPS / nombre_archivo)

    # Convertir fecha a formato datetime mensual
    df["fecha_mensual"] = pd.to_datetime(df["date"] + "-01")

    # Renombrar variable
    df = df.rename(columns={"CHIRPS": nueva_col})

    return df[["fecha_mensual", nueva_col]]


# Cargar todas las series CHIRPS
matoc_ch = cargar_chirps("CHIRPS_MATOC_2012_2022.csv", "CHIRPS_MATOC")
pocco_ch = cargar_chirps("CHIRPS_POCCO_2012_2022.csv", "CHIRPS_POCCO")
ana1_ch = cargar_chirps("CHIRPS_ANA1_2012_2022.csv", "CHIRPS_ANA1")
ana2_ch = cargar_chirps("CHIRPS_ANA2_2012_2022.csv", "CHIRPS_ANA2")


# ============================================================
# FUNCIÓN DE MÉTRICAS
# ============================================================

def calcular_metricas(obs, pred):
    """
    Calcula métricas estadísticas entre datos observados y estimados.

    Parámetros:
    ----------
    obs : Serie observada
    pred : Serie estimada (CHIRPS)

    Proceso:
    ----------
    - Elimina valores NaN en ambas series
    - Calcula métricas de desempeño

    Métricas calculadas:
    ----------
    R       : correlación de Pearson
    R2      : coeficiente de determinación
    RMSE    : error cuadrático medio
    Bias_mm : sesgo absoluto (mm)
    Bias_%  : sesgo relativo (%)
    NSE     : eficiencia de Nash-Sutcliffe

    Retorna:
    ----------
    Diccionario con métricas
    """

    # Filtrar valores válidos simultáneamente
    mask = (~obs.isna()) & (~pred.isna())
    obs = obs[mask]
    pred = pred[mask]

    # Control de tamaño mínimo
    if len(obs) < 10:
        return None

    # Correlación
    r = np.corrcoef(obs, pred)[0, 1]
    r2 = r ** 2

    # Error
    rmse = np.sqrt(np.mean((obs - pred) ** 2))

    # Sesgo
    bias = pred.mean() - obs.mean()
    bias_pct = (bias / obs.mean()) * 100

    # Eficiencia hidrológica (NSE)
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

"""
Se realizan comparaciones independientes para:

- Estaciones puntuales (ANA)
- Unidades hidrográficas (promedios espaciales)
"""

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

# Matoc UH
df = matoc_obs.merge(matoc_ch, on="fecha_mensual", how="inner")
met = calcular_metricas(df["Prec_UH_OBS"], df["CHIRPS_MATOC"])
if met:
    resultados.append({"Serie": "Matoc_UH", **met})

# Pocco UH
df = pocco_obs.merge(pocco_ch, on="fecha_mensual", how="inner")
met = calcular_metricas(df["Prec_UH_OBS"], df["CHIRPS_POCCO"])
if met:
    resultados.append({"Serie": "Pocco_UH", **met})


# ============================================================
# EXPORTAR RESULTADOS
# ============================================================

resumen = pd.DataFrame(resultados)

resumen.to_csv(
    OUTPUT_DIR / "7_fase5_validacion_chirps_integral.csv",
    index=False
)


# ============================================================
# MENSAJES FINALES
# ============================================================

print("\nRESULTADOS FASE 5 — VALIDACIÓN INTEGRAL CHIRPS")
print(resumen)

print("\nFASE 5 COMPLETADA.")
