# ============================================================
# FASE 8 — VALIDACIÓN CRUZADA ROBUSTA (MONTE CARLO)
# ============================================================
"""
OBJETIVO GENERAL
---------------
Evaluar la robustez del modelo de completación mensual (FASE 7)
mediante simulaciones de pérdida de datos y reconstrucción.

ENFOQUE METODOLÓGICO
--------------------
Se implementa validación cruzada tipo Monte Carlo:
- 30 iteraciones independientes
- En cada iteración:
    1. Se elimina aleatoriamente el 20% de los datos observados
    2. Se entrena un modelo de regresión (UH vs ANA1)
    3. Se reconstruyen los datos eliminados
    4. Se comparan contra valores reales

JERARQUÍA DE RECONSTRUCCIÓN
---------------------------
1. Regresión lineal con estación ANA1
2. Datos CHIRPS corregidos (fallback)

ENTRADAS
--------
- 4_Matoc_UH_mensual_OBS.csv
- 4_Pocco_UH_mensual_OBS.csv
- mensual_estaciones_2012_2022.csv
- CHIRPS_*_corregido.csv

SALIDAS
-------
1. resultados_iteraciones_validacion_cruzada.csv
   → métricas por iteración

2. resumen_promedio_validacion_cruzada.csv
   → promedio de métricas por UH
"""

# ============================================================
# 1. LIBRERÍAS
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error

# ============================================================
# 2. REPRODUCIBILIDAD
# ============================================================
# Fija semilla para obtener siempre los mismos resultados

np.random.seed(42)

# ============================================================
# 3. RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_MENSUALES = BASE_DIR / "outputs/mensuales"
INPUT_CHIRPS = BASE_DIR / "outputs/chirps_corregido"
OUTPUT_DIR = BASE_DIR / "outputs/validacion_cruzada"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 4. CARGA DE DATOS
# ============================================================

print("\nCargando datos de entrada...")

# -------------------------
# 4.1 Series UH observadas
# -------------------------
matoc_obs = pd.read_csv(
    INPUT_MENSUALES / "4_Matoc_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

pocco_obs = pd.read_csv(
    INPUT_MENSUALES / "4_Pocco_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

# -------------------------
# 4.2 Estaciones (incluye ANA1)
# -------------------------
estaciones = pd.read_csv(
    INPUT_MENSUALES / "mensual_estaciones_2012_2022.csv",
    parse_dates=["fecha_mensual"]
)

# Selección de estación de referencia
ana1 = estaciones[
    estaciones["Estacion"] == "ANA 1"
][["fecha_mensual", "Prec_mensual"]].rename(
    columns={"Prec_mensual": "ANA1"}
)

# -------------------------
# 4.3 CHIRPS corregido
# -------------------------
matoc_ch = pd.read_csv(
    INPUT_CHIRPS / "CHIRPS_MATOC_corregido.csv",
    parse_dates=["fecha_mensual"]
)

pocco_ch = pd.read_csv(
    INPUT_CHIRPS / "CHIRPS_POCCO_corregido.csv",
    parse_dates=["fecha_mensual"]
)

# ============================================================
# 5. FUNCIÓN: calcular_metricas
# ============================================================
def calcular_metricas(obs, pred):
    """
    Calcula métricas de desempeño hidrológico.

    PARÁMETROS
    ----------
    obs : array-like
        Serie de valores observados (verdaderos)

    pred : array-like
        Serie de valores estimados (modelo)

    RETORNA
    -------
    r : float
        Correlación de Pearson

    r2 : float
        Coeficiente de determinación

    rmse : float
        Raíz del error cuadrático medio

    mae : float
        Error absoluto medio

    bias_pct : float
        Sesgo relativo (%)

    nse : float
        Eficiencia de Nash-Sutcliffe

    INTERPRETACIÓN
    --------------
    - R² alto → buena capacidad explicativa
    - RMSE bajo → bajo error
    - Bias cercano a 0 → sin sesgo
    - NSE > 0.6 → modelo aceptable
    """

    # Correlación
    r = np.corrcoef(obs, pred)[0, 1]

    # Coeficiente de determinación
    r2 = r ** 2

    # Error cuadrático medio
    rmse = np.sqrt(mean_squared_error(obs, pred))

    # Error absoluto medio
    mae = mean_absolute_error(obs, pred)

    # Sesgo porcentual
    bias = pred.mean() - obs.mean()
    bias_pct = (bias / obs.mean()) * 100

    # Nash-Sutcliffe Efficiency
    nse = 1 - (
        np.sum((obs - pred) ** 2) /
        np.sum((obs - obs.mean()) ** 2)
    )

    return r, r2, rmse, mae, bias_pct, nse

# ============================================================
# 6. FUNCIÓN: validacion_montecarlo
# ============================================================
def validacion_montecarlo(uh_obs, chirps_df, nombre_uh):
    """
    Ejecuta validación cruzada Monte Carlo.

    PARÁMETROS
    ----------
    uh_obs : DataFrame
        Serie mensual observada de la UH
        Columnas:
            - fecha_mensual
            - Prec_UH_OBS

    chirps_df : DataFrame
        Serie CHIRPS corregida
        Última columna = precipitación corregida

    nombre_uh : str
        Nombre de la unidad hidrológica

    RETORNA
    -------
    DataFrame con métricas por iteración

    PROCESO
    --------
    1. Integración de datos (UH + ANA1 + CHIRPS)
    2. Loop Monte Carlo:
        a. Eliminar 20% de datos
        b. Entrenar modelo
        c. Reconstruir datos eliminados
        d. Evaluar desempeño
    """

    resultados = []

    # -------------------------
    # 6.1 Integración de datos
    # -------------------------
    df = uh_obs.merge(ana1, on="fecha_mensual", how="left")

    df = df.merge(
        chirps_df[["fecha_mensual", chirps_df.columns[-1]]],
        on="fecha_mensual",
        how="left"
    )

    # Solo registros con dato observado real
    df = df.dropna(subset=["Prec_UH_OBS"])

    # ========================================================
    # 6.2 LOOP MONTE CARLO
    # ========================================================
    for i in range(30):

        df_iter = df.copy()

        # -------------------------
        # (a) Eliminación aleatoria
        # -------------------------
        n_remove = int(len(df_iter) * 0.2)

        idx_remove = np.random.choice(
            df_iter.index,
            n_remove,
            replace=False
        )

        df_iter.loc[idx_remove, "Prec_UH_OBS"] = np.nan

        # -------------------------
        # (b) Entrenamiento modelo
        # -------------------------
        df_train = df_iter.dropna(subset=["Prec_UH_OBS", "ANA1"])

        X_train = df_train[["ANA1"]].values
        y_train = df_train["Prec_UH_OBS"].values

        modelo = LinearRegression()
        modelo.fit(X_train, y_train)

        # -------------------------
        # (c) Reconstrucción
        # -------------------------
        predicciones = []
        reales = []

        for idx in idx_remove:

            row = df.loc[idx]

            # Prioridad 1: regresión
            if not pd.isna(row["ANA1"]):
                pred = modelo.predict([[row["ANA1"]]])[0]

            # Prioridad 2: CHIRPS
            else:
                pred = row[chirps_df.columns[-1]]

            predicciones.append(max(pred, 0))
            reales.append(row["Prec_UH_OBS"])

        # -------------------------
        # (d) Evaluación
        # -------------------------
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

# ============================================================
# 7. EJECUCIÓN DEL MODELO
# ============================================================

print("\nEjecutando validación Monte Carlo...")

res_matoc = validacion_montecarlo(
    matoc_obs, matoc_ch, "Matoc"
)

res_pocco = validacion_montecarlo(
    pocco_obs, pocco_ch, "Pocco"
)

# Unificación
resultados_totales = pd.concat([res_matoc, res_pocco])

# ============================================================
# 8. EXPORTACIÓN
# ============================================================

# Resultados por iteración
resultados_totales.to_csv(
    OUTPUT_DIR / "resultados_iteraciones_validacion_cruzada.csv",
    index=False
)

# Promedio final
resumen_final = resultados_totales.groupby("UH").mean(numeric_only=True)

resumen_final.to_csv(
    OUTPUT_DIR / "resumen_promedio_validacion_cruzada.csv"
)

# ============================================================
# 9. SALIDA FINAL
# ============================================================

print("\nFASE 8 COMPLETADA.")
print("\nResumen promedio por UH:")
print(resumen_final)
