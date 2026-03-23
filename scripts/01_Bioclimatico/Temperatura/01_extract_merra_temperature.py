# ============================================================
# FASE 8 — VALIDACIÓN CRUZADA ROBUSTA (MONTE CARLO)
# ============================================================
# OBJETIVO:
# Evaluar la robustez del modelo de completación mensual (FASE 7)
# mediante simulación de pérdida de datos (20%) y reconstrucción
# usando regresión con ANA1 y respaldo CHIRPS corregido.
#
# MÉTODO:
# - 30 iteraciones Monte Carlo
# - Eliminación aleatoria de datos observados
# - Reconstrucción jerárquica:
#     1) Regresión con ANA1
#     2) CHIRPS corregido (fallback)
# - Evaluación con métricas hidrológicas estándar
#
# SALIDAS:
# - Resultados por iteración
# - Resumen promedio por unidad hidrológica
# ============================================================

# ============================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# ============================================================
# 2. REPRODUCIBILIDAD
# ============================================================
# Se fija semilla aleatoria para garantizar replicabilidad

np.random.seed(42)

# ============================================================
# 3. DEFINICIÓN DE RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_MENSUALES = BASE_DIR / "outputs/mensuales"
INPUT_CHIRPS = BASE_DIR / "outputs/chirps_corregido"
OUTPUT_DIR = BASE_DIR / "outputs/validacion_cruzada"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 4. CARGA DE DATOS
# ============================================================

print("\nCargando datos...")

# Series observadas por UH
matoc_obs = pd.read_csv(
    INPUT_MENSUALES / "4_Matoc_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

pocco_obs = pd.read_csv(
    INPUT_MENSUALES / "4_Pocco_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

# Estaciones (incluye ANA1)
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
# 5. FUNCIÓN DE MÉTRICAS
# ============================================================
def calcular_metricas(obs, pred):
    """
    Calcula métricas de desempeño entre valores observados y predichos.

    Parámetros:
    ----------
    obs : array-like
        Valores observados reales
    pred : array-like
        Valores estimados por el modelo

    Retorna:
    -------
    tuple:
        (R, R2, RMSE, MAE, Bias_pct, NSE)
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
# 6. FUNCIÓN PRINCIPAL: VALIDACIÓN MONTE CARLO
# ============================================================
def validacion_montecarlo(uh_obs, chirps_df, nombre_uh):
    """
    Ejecuta validación cruzada tipo Monte Carlo.

    Procedimiento:
    -------------
    1. Combina UH observada + ANA1 + CHIRPS
    2. Itera 30 veces:
        - Elimina 20% de datos reales
        - Ajusta modelo con datos restantes
        - Reconstruye valores eliminados
        - Evalúa desempeño

    Parámetros:
    ----------
    uh_obs : DataFrame
        Serie observada UH
    chirps_df : DataFrame
        Serie CHIRPS corregida
    nombre_uh : str
        Nombre de la unidad hidrológica

    Retorna:
    -------
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

    # Solo datos observados reales
    df = df.dropna(subset=["Prec_UH_OBS"])

    # ========================================================
    # LOOP MONTE CARLO
    # ========================================================
    for i in range(30):

        df_iter = df.copy()

        # ----------------------------
        # 1. ELIMINAR 20% DE DATOS
        # ----------------------------
        n_remove = int(len(df_iter) * 0.2)

        idx_remove = np.random.choice(
            df_iter.index,
            n_remove,
            replace=False
        )

        df_iter.loc[idx_remove, "Prec_UH_OBS"] = np.nan

        # ----------------------------
        # 2. ENTRENAR MODELO
        # ----------------------------
        df_train = df_iter.dropna(subset=["Prec_UH_OBS", "ANA1"])

        X_train = df_train[["ANA1"]].values
        y_train = df_train["Prec_UH_OBS"].values

        modelo = LinearRegression()
        modelo.fit(X_train, y_train)

        # ----------------------------
        # 3. RECONSTRUCCIÓN
        # ----------------------------
        predicciones = []
        reales = []

        for idx in idx_remove:

            row = df.loc[idx]

            # Prioridad: regresión con ANA1
            if not pd.isna(row["ANA1"]):
                pred = modelo.predict([[row["ANA1"]]])[0]

            # Fallback: CHIRPS corregido
            else:
                pred = row[chirps_df.columns[-1]]

            predicciones.append(max(pred, 0))
            reales.append(row["Prec_UH_OBS"])

        # ----------------------------
        # 4. EVALUACIÓN
        # ----------------------------
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
# 7. EJECUCIÓN
# ============================================================

print("\nEjecutando validación cruzada...")

res_matoc = validacion_montecarlo(
    matoc_obs, matoc_ch, "Matoc"
)

res_pocco = validacion_montecarlo(
    pocco_obs, pocco_ch, "Pocco"
)

# Unir resultados
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
# 9. SALIDA EN CONSOLA
# ============================================================

print("\nFASE 8 COMPLETADA.")
print("\nResumen promedio por UH:")
print(resumen_final)
