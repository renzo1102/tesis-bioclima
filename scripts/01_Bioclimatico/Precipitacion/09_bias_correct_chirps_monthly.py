# ============================================================
# FASE 6 — CORRECCIÓN MENSUAL CHIRPS (BASE ANA 1)
# ============================================================

"""
DESCRIPCIÓN GENERAL
------------------------------------------------------------
Este script implementa la corrección de sesgo (bias correction)
del producto satelital CHIRPS a escala mensual, utilizando como
referencia la estación observada ANA 1.

El objetivo es ajustar sistemáticamente los valores de CHIRPS
para que sean más consistentes con las observaciones reales,
reduciendo errores sistemáticos (sobreestimación o subestimación).

------------------------------------------------------------
ENFOQUE METODOLÓGICO

Se aplica un método de corrección multiplicativa mensual:

Factor_mensual = Media(Observado) / Media(CHIRPS)

Este factor se calcula para cada mes (enero–diciembre) usando
la serie histórica (2012–2022).

Luego se aplica:

CHIRPS_corregido = CHIRPS_original × Factor_mensual

------------------------------------------------------------
SERIES CORREGIDAS

- ANA 1 (para validación interna)
- UH Matoc
- UH Pocco

------------------------------------------------------------
OUTPUTS GENERADOS

outputs/chirps_corregido/

- factores_mensuales_base_ANA1.csv
- CHIRPS_ANA1_corregido.csv
- CHIRPS_MATOC_corregido.csv
- CHIRPS_POCCO_corregido.csv
- metricas_post_correccion_ANA1.csv

------------------------------------------------------------
IMPORTANCIA

Esta fase es clave porque:

- Reduce sesgos sistemáticos del producto CHIRPS
- Mejora la coherencia hidrológica
- Permite usar CHIRPS para relleno de datos faltantes
- Prepara datos para modelamiento hidrológico

------------------------------------------------------------
SUPUESTO

Se asume que:
- El sesgo es sistemático por mes (estacional)
- ANA 1 es representativa regionalmente

"""

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

# Se extrae la serie mensual observada de ANA 1,
# que será usada como referencia para la corrección

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
    """
    Carga archivos CHIRPS exportados desde GEE.

    Proceso:
    - Convierte fecha a datetime
    - Extrae el mes
    - Renombra la variable

    Retorna:
    DataFrame con:
    - fecha_mensual
    - mes
    - variable CHIRPS
    """

    df = pd.read_csv(INPUT_CHIRPS / nombre_archivo)

    df["fecha_mensual"] = pd.to_datetime(df["date"] + "-01")
    df["mes"] = df["fecha_mensual"].dt.month

    df = df.rename(columns={"CHIRPS": nueva_col})

    return df


# Cargar series CHIRPS
ana1_ch = cargar_chirps("CHIRPS_ANA1_2012_2022.csv", "CHIRPS_ANA1")
matoc_ch = cargar_chirps("CHIRPS_MATOC_2012_2022.csv", "CHIRPS_MATOC")
pocco_ch = cargar_chirps("CHIRPS_POCCO_2012_2022.csv", "CHIRPS_POCCO")


# ============================================================
# CALCULAR FACTORES MENSUALES (BASE ANA 1)
# ============================================================

"""
Se calculan factores de corrección por mes:

Para cada mes:
Factor = media(ANA1_OBS) / media(CHIRPS_ANA1)

Esto captura el sesgo sistemático mensual del producto CHIRPS.
"""

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

# Guardar factores
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
    """
    Aplica corrección multiplicativa mensual.

    Parámetros:
    ----------
    df : DataFrame con CHIRPS
    col_name : nombre de la variable CHIRPS

    Proceso:
    ----------
    - Une con factores mensuales
    - Multiplica cada valor por su factor

    Retorna:
    ----------
    DataFrame con columna corregida
    """

    df = df.merge(factores, on="mes", how="left")

    df[f"{col_name}_CORR"] = df[col_name] * df["Factor_correccion"]

    return df


# Aplicar corrección a todas las series
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
    """
    Calcula métricas de desempeño post-corrección.

    Métricas:
    - R, R2
    - RMSE
    - Bias (mm y %)
    - NSE
    """

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

"""
Se evalúa la mejora del producto corregido comparando:

ANA1_OBS vs CHIRPS_ANA1_CORR

Esto permite verificar si:
- Disminuye el RMSE
- Mejora el NSE
- Se reduce el sesgo
"""

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
