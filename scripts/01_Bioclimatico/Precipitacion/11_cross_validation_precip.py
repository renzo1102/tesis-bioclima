# ============================================================
# FASE 8 — VALIDACIÓN CRUZADA ROBUSTA (30 ITERACIONES)
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

np.random.seed(42)

# ============================================================
# RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_MENSUALES = BASE_DIR / "outputs/mensuales"
INPUT_CHIRPS = BASE_DIR / "outputs/chirps_corregido"
OUTPUT_DIR = BASE_DIR / "outputs/validacion_cruzada"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CARGAR DATOS
# ============================================================

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

ana1 = estaciones[
    estaciones["Estacion"] == "ANA 1"
][["fecha_mensual", "Prec_mensual"]].rename(
    columns={"Prec_mensual": "ANA1"}
)

matoc_ch = pd.read_csv(
    INPUT_CHIRPS / "CHIRPS_MATOC_corregido.csv",
    parse_dates=["fecha_mensual"]
)

pocco_ch = pd.read_csv(
    INPUT_CHIRPS / "CHIRPS_POCCO_corregido.csv",
    parse_dates=["fecha_mensual"]
)

# ============================================================
# MÉTRICAS
# ============================================================

def calcular_metricas(obs, pred):

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
# FUNCIÓN VALIDACIÓN
# ============================================================

def validacion_montecarlo(uh_obs, chirps_df, nombre_uh):

    resultados = []

    df = uh_obs.merge(ana1, on="fecha_mensual", how="left")
    df = df.merge(
        chirps_df[["fecha_mensual", chirps_df.columns[-1]]],
        on="fecha_mensual",
        how="left"
    )

    df = df.dropna(subset=["Prec_UH_OBS"])

    for i in range(30):

        df_iter = df.copy()

        # Seleccionar 20% para eliminar
        n_remove = int(len(df_iter) * 0.2)
        idx_remove = np.random.choice(df_iter.index, n_remove, replace=False)

        df_iter.loc[idx_remove, "Prec_UH_OBS"] = np.nan

        # Ajustar modelo con datos restantes
        df_train = df_iter.dropna(subset=["Prec_UH_OBS", "ANA1"])

        X_train = df_train[["ANA1"]].values
        y_train = df_train["Prec_UH_OBS"].values

        modelo = LinearRegression()
        modelo.fit(X_train, y_train)

        # Reconstrucción
        predicciones = []
        reales = []

        for idx in idx_remove:

            row = df.loc[idx]

            if not pd.isna(row["ANA1"]):
                pred = modelo.predict([[row["ANA1"]]])[0]
            else:
                pred = row[chirps_df.columns[-1]]

            predicciones.append(max(pred, 0))
            reales.append(row["Prec_UH_OBS"])

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
# EJECUTAR VALIDACIÓN
# ============================================================

res_matoc = validacion_montecarlo(
    matoc_obs, matoc_ch, "Matoc"
)

res_pocco = validacion_montecarlo(
    pocco_obs, pocco_ch, "Pocco"
)

resultados_totales = pd.concat([res_matoc, res_pocco])

resultados_totales.to_csv(
    OUTPUT_DIR / "resultados_iteraciones_validacion_cruzada.csv",
    index=False
)

# Promedio final
resumen_final = resultados_totales.groupby("UH").mean(numeric_only=True)
resumen_final.to_csv(
    OUTPUT_DIR / "resumen_promedio_validacion_cruzada.csv"
)

print("\nFASE 8 COMPLETADA.")
print("\nResumen promedio:")
print(resumen_final)