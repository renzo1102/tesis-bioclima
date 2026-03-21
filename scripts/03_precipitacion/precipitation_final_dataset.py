"""
Script: precipitation_final_dataset.py

Descripción:
Integra dataset final de precipitación

Entradas:
Datos corregidos

Salidas:
Dataset final

Autor: Renzo Mendoza
Año: 2026
"""
# ============================================================
# SCRIPT 10
# FASE 7 — COMPLETACIÓN JERÁRQUICA 2012–2022 (VERSIÓN FINAL)
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

# ============================================================
# RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_MENSUALES = BASE_DIR / "outputs/mensuales"
INPUT_CHIRPS_CORR = BASE_DIR / "outputs/chirps_corregido"
OUTPUT_DIR = BASE_DIR / "outputs/serie_final"

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
    INPUT_CHIRPS_CORR / "CHIRPS_MATOC_corregido.csv",
    parse_dates=["fecha_mensual"]
)

pocco_ch = pd.read_csv(
    INPUT_CHIRPS_CORR / "CHIRPS_POCCO_corregido.csv",
    parse_dates=["fecha_mensual"]
)

# ============================================================
# FUNCIÓN AJUSTE REGRESIÓN
# ============================================================

def ajustar_regresion(df_uh, ana1_df, nombre_uh):

    df = df_uh.merge(ana1_df, on="fecha_mensual", how="inner")
    df = df.dropna()

    X = df[["ANA1"]].values
    y = df["Prec_UH_OBS"].values

    modelo = LinearRegression()
    modelo.fit(X, y)

    pred = modelo.predict(X)

    r2 = r2_score(y, pred)
    rmse = np.sqrt(mean_squared_error(y, pred))

    a = modelo.intercept_
    b = modelo.coef_[0]

    print(f"\nModelo {nombre_uh}:")
    print(f"UH = {round(a,2)} + {round(b,2)} * ANA1")
    print(f"R2 = {round(r2,3)} | RMSE = {round(rmse,2)}")

    return modelo, a, b, r2, rmse

# ============================================================
# AJUSTAR MODELOS
# ============================================================

modelo_matoc, a_matoc, b_matoc, r2_matoc, rmse_matoc = ajustar_regresion(
    matoc_obs, ana1, "Matoc"
)

modelo_pocco, a_pocco, b_pocco, r2_pocco, rmse_pocco = ajustar_regresion(
    pocco_obs, ana1, "Pocco"
)

# ============================================================
# GUARDAR ECUACIONES
# ============================================================

ecuaciones_df = pd.DataFrame([
    {
        "UH": "Matoc",
        "Intercepto_a": a_matoc,
        "Pendiente_b": b_matoc,
        "R2_modelo": r2_matoc,
        "RMSE_modelo": rmse_matoc
    },
    {
        "UH": "Pocco",
        "Intercepto_a": a_pocco,
        "Pendiente_b": b_pocco,
        "R2_modelo": r2_pocco,
        "RMSE_modelo": rmse_pocco
    }
])

ecuaciones_df.to_csv(
    OUTPUT_DIR / "ecuaciones_regresion_ANA1.csv",
    index=False
)

# ============================================================
# BASE COMPLETA
# ============================================================

fechas = pd.date_range("2012-01-01", "2022-12-01", freq="MS")
base = pd.DataFrame({"fecha_mensual": fechas})

# ============================================================
# FUNCIÓN COMPLETACIÓN
# ============================================================

def completar_serie(base, uh_obs, ana1_df, chirps_df, modelo, nombre_col):

    df = base.merge(uh_obs, on="fecha_mensual", how="left")
    df = df.merge(ana1_df, on="fecha_mensual", how="left")
    df = df.merge(
        chirps_df[["fecha_mensual", f"{nombre_col}_CORR"]],
        on="fecha_mensual",
        how="left"
    )

    valores = []
    fuentes = []

    for _, row in df.iterrows():

        if not pd.isna(row["Prec_UH_OBS"]):
            valores.append(row["Prec_UH_OBS"])
            fuentes.append("OBS")

        elif not pd.isna(row["ANA1"]):
            pred = modelo.predict([[row["ANA1"]]])[0]
            valores.append(max(pred, 0))
            fuentes.append("REG_ANA1")

        else:
            valores.append(row[f"{nombre_col}_CORR"])
            fuentes.append("CHIRPS_CORR")

    df["Precip_final"] = valores
    df["Fuente"] = fuentes

    return df

# ============================================================
# COMPLETAR
# ============================================================

matoc_final = completar_serie(
    base, matoc_obs, ana1, matoc_ch, modelo_matoc, "CHIRPS_MATOC"
)

pocco_final = completar_serie(
    base, pocco_obs, ana1, pocco_ch, modelo_pocco, "CHIRPS_POCCO"
)

# ============================================================
# GUARDAR SERIES
# ============================================================

matoc_final.to_csv(
    OUTPUT_DIR / "Matoc_serie_mensual_2012_2022_completa.csv",
    index=False
)

pocco_final.to_csv(
    OUTPUT_DIR / "Pocco_serie_mensual_2012_2022_completa.csv",
    index=False
)

# ============================================================
# RESUMEN DE FUENTES
# ============================================================

def guardar_resumen_fuentes(df, nombre):

    resumen = df["Fuente"].value_counts()
    total = len(df)

    resumen_df = pd.DataFrame({
        "UH": nombre,
        "Fuente": resumen.index,
        "Meses": resumen.values,
        "Porcentaje_%": (resumen.values / total) * 100
    })

    return resumen_df

res_matoc = guardar_resumen_fuentes(matoc_final, "Matoc")
res_pocco = guardar_resumen_fuentes(pocco_final, "Pocco")

resumen_total = pd.concat([res_matoc, res_pocco])

resumen_total.to_csv(
    OUTPUT_DIR / "resumen_fuentes_completacion.csv",
    index=False
)

print("\nFASE 7 COMPLETADA.")
print("Archivos generados en outputs/serie_final/")
