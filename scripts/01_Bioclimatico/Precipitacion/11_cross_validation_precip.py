# ============================================================
# FASE 8 — VALIDACIÓN CRUZADA ROBUSTA (30 ITERACIONES)
# ============================================================
"""
DESCRIPCIÓN GENERAL
------------------------------------------------------------
Este script implementa una validación cruzada robusta basada
en simulaciones Monte Carlo para evaluar el desempeño del
modelo de completación jerárquica desarrollado en la FASE 7.

El objetivo es cuantificar la capacidad del modelo para
reconstruir datos faltantes bajo condiciones controladas,
simulando escenarios de pérdida de información.

------------------------------------------------------------
ENFOQUE METODOLÓGICO
------------------------------------------------------------
Se aplica un esquema de validación tipo "data withholding":

1. Se eliminan aleatoriamente el 20% de los datos observados
2. Se recalibra el modelo con el 80% restante
3. Se reconstruyen los valores eliminados
4. Se comparan valores reconstruidos vs reales
5. Se repite el proceso 30 veces (Monte Carlo)

Esto permite evaluar:
- Robustez del modelo
- Sensibilidad a pérdida de datos
- Estabilidad estadística

------------------------------------------------------------
JERARQUÍA DE RECONSTRUCCIÓN
------------------------------------------------------------
Se replica la lógica de FASE 7:

    1. Regresión con ANA 1
    2. CHIRPS corregido (fallback)

------------------------------------------------------------
MÉTRICAS EVALUADAS
------------------------------------------------------------
- R       : correlación
- R²      : varianza explicada
- RMSE    : error cuadrático medio
- MAE     : error absoluto medio
- Bias %  : sesgo relativo
- NSE     : eficiencia de Nash-Sutcliffe

------------------------------------------------------------
SALIDAS
------------------------------------------------------------
1. Resultados por iteración (30 simulaciones)
2. Promedio estadístico por unidad hidrológica
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# Fijar semilla para reproducibilidad
np.random.seed(42)

# ============================================================
# RUTAS RELATIVAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_MENSUALES = BASE_DIR / "outputs/mensuales"
INPUT_CHIRPS = BASE_DIR / "outputs/chirps_corregido"
OUTPUT_DIR = BASE_DIR / "outputs/validacion_cruzada"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CARGA DE DATOS
# ============================================================

"""
Se utilizan:
- Series observadas por UH (referencia real)
- Estación ANA 1 (predictor regional)
- CHIRPS corregido (respaldo)
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

# Predictor regional
ana1 = estaciones[
    estaciones["Estacion"] == "ANA 1"
][["fecha_mensual", "Prec_mensual"]].rename(
    columns={"Prec_mensual": "ANA1"}
)

# CHIRPS corregido
matoc_ch = pd.read_csv(
    INPUT_CHIRPS / "CHIRPS_MATOC_corregido.csv",
    parse_dates=["fecha_mensual"]
)

pocco_ch = pd.read_csv(
    INPUT_CHIRPS / "CHIRPS_POCCO_corregido.csv",
    parse_dates=["fecha_mensual"]
)

# ============================================================
# FUNCIÓN: CÁLCULO DE MÉTRICAS
# ============================================================

def calcular_metricas(obs, pred):
    """
    Calcula métricas de desempeño entre valores observados
    y reconstruidos.

    Parámetros:
        obs  : valores reales
        pred : valores estimados

    Retorna:
        r, r2, rmse, mae, bias_pct, nse
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
# FUNCIÓN: VALIDACIÓN MONTE CARLO
# ============================================================

def validacion_montecarlo(uh_obs, chirps_df, nombre_uh):
    """
    Ejecuta validación cruzada mediante simulaciones Monte Carlo.

    Procedimiento por iteración:
    1. Eliminar aleatoriamente 20% de datos
    2. Ajustar modelo con datos restantes
    3. Reconstruir valores eliminados
    4. Evaluar desempeño

    Parámetros:
        uh_obs     : serie observada UH
        chirps_df  : datos CHIRPS corregido
        nombre_uh  : nombre de la UH

    Retorna:
        DataFrame con métricas por iteración
    """

    resultados = []

    # Integración de datasets
    df = uh_obs.merge(ana1, on="fecha_mensual", how="left")
    df = df.merge(
        chirps_df[["fecha_mensual", chirps_df.columns[-1]]],
        on="fecha_mensual",
        how="left"
    )

    # Solo datos con observación real
    df = df.dropna(subset=["Prec_UH_OBS"])

    for i in range(30):

        df_iter = df.copy()

        # ----------------------------------------------------
        # 1. ELIMINAR 20% DE DATOS (SIMULACIÓN)
        # ----------------------------------------------------
        n_remove = int(len(df_iter) * 0.2)
        idx_remove = np.random.choice(df_iter.index, n_remove, replace=False)

        df_iter.loc[idx_remove, "Prec_UH_OBS"] = np.nan

        # ----------------------------------------------------
        # 2. ENTRENAR MODELO
        # ----------------------------------------------------
        df_train = df_iter.dropna(subset=["Prec_UH_OBS", "ANA1"])

        X_train = df_train[["ANA1"]].values
        y_train = df_train["Prec_UH_OBS"].values

        modelo = LinearRegression()
        modelo.fit(X_train, y_train)

        # ----------------------------------------------------
        # 3. RECONSTRUCCIÓN
        # ----------------------------------------------------
        predicciones = []
        reales = []

        for idx in idx_remove:

            row = df.loc[idx]

            # Regresión
            if not pd.isna(row["ANA1"]):
                pred = modelo.predict([[row["ANA1"]]])[0]

            # Fallback CHIRPS
            else:
                pred = row[chirps_df.columns[-1]]

            predicciones.append(max(pred, 0))
            reales.append(row["Prec_UH_OBS"])

        # ----------------------------------------------------
        # 4. EVALUACIÓN
        # ----------------------------------------------------
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
# EJECUCIÓN
# ============================================================

res_matoc = validacion_montecarlo(
    matoc_obs, matoc_ch, "Matoc"
)

res_pocco = validacion_montecarlo(
    pocco_obs, pocco_ch, "Pocco"
)

# Unificar resultados
resultados_totales = pd.concat([res_matoc, res_pocco])

# ============================================================
# EXPORTAR RESULTADOS
# ============================================================

resultados_totales.to_csv(
    OUTPUT_DIR / "resultados_iteraciones_validacion_cruzada.csv",
    index=False
)

# Promedio por UH
resumen_final = resultados_totales.groupby("UH").mean(numeric_only=True)

resumen_final.to_csv(
    OUTPUT_DIR / "resumen_promedio_validacion_cruzada.csv"
)

# ============================================================
# MENSAJES FINALES
# ============================================================

print("\nFASE 8 COMPLETADA.")
print("\nResumen promedio por unidad hidrológica:")
print(resumen_final)
print("\nResultados guardados en: outputs/validacion_cruzada/")
