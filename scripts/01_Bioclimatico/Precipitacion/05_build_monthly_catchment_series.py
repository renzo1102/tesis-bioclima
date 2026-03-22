# ============================================================
# FASE 3 — CONSTRUCCIÓN SERIE MENSUAL REPRESENTATIVA POR UH
# Solo con datos observados (sin relleno)
# Incluye tabla resumen estructural
# ============================================================

import pandas as pd
import numpy as np
import os

# ============================================================
# RUTAS
# ============================================================

INPUT_FILE = "outputs/mensuales/mensual_estaciones_2012_2022.csv"
OUTPUT_DIR = "outputs/mensuales"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# CARGAR DATOS
# ============================================================

print("\nCargando datos mensuales por estación...")
df = pd.read_csv(INPUT_FILE, parse_dates=["fecha_mensual"])

# ============================================================
# FUNCIÓN CONSTRUCCIÓN UH
# ============================================================

def construir_uh(df_uh, nombre_uh):

    resultados = []

    for fecha, grupo in df_uh.groupby("fecha_mensual"):

        valores_validos = grupo["Prec_mensual"].dropna()
        n_validos = len(valores_validos)

        if n_validos >= 2:
            prec_uh = valores_validos.mean()
            fuente = "Promedio >=2 estaciones"
        elif n_validos == 1:
            prec_uh = valores_validos.iloc[0]
            fuente = "1 estación"
        else:
            prec_uh = np.nan
            fuente = "Sin datos"

        resultados.append({
            "fecha_mensual": fecha,
            "Prec_UH_OBS": prec_uh,
            "n_estaciones_validas": n_validos,
            "Fuente": fuente
        })

    df_resultado = pd.DataFrame(resultados)
    df_resultado["UH"] = nombre_uh

    return df_resultado.sort_values("fecha_mensual")

# ============================================================
# SEPARAR UHs
# ============================================================

matoc_df = df[df["UH"] == "Matoc"]
pocco_df = df[df["UH"] == "Pocco"]

# ============================================================
# CONSTRUIR SERIES
# ============================================================

matoc_uh = construir_uh(matoc_df, "Matoc")
pocco_uh = construir_uh(pocco_df, "Pocco")

# ============================================================
# GUARDAR SERIES
# ============================================================

matoc_uh.to_csv(
    os.path.join(OUTPUT_DIR, "4_Matoc_UH_mensual_OBS.csv"),
    index=False
)

pocco_uh.to_csv(
    os.path.join(OUTPUT_DIR, "4_Pocco_UH_mensual_OBS.csv"),
    index=False
)

print("\nSeries UH generadas.")

# ============================================================
# TABLA RESUMEN FASE 3
# ============================================================

def resumen_uh(df_uh):

    meses_totales = len(df_uh)
    meses_validos = df_uh["Prec_UH_OBS"].notna().sum()
    meses_na = df_uh["Prec_UH_OBS"].isna().sum()
    porcentaje_cobertura = round((meses_validos / meses_totales) * 100, 2)

    dist_fuente = df_uh["Fuente"].value_counts()

    return {
        "meses_totales": meses_totales,
        "meses_validos": meses_validos,
        "meses_na": meses_na,
        "porcentaje_cobertura": porcentaje_cobertura,
        "meses_promedio_>=2_est": dist_fuente.get("Promedio >=2 estaciones", 0),
        "meses_1_estacion": dist_fuente.get("1 estación", 0),
        "meses_sin_datos": dist_fuente.get("Sin datos", 0)
    }

resumen_matoc = resumen_uh(matoc_uh)
resumen_pocco = resumen_uh(pocco_uh)

resumen_df = pd.DataFrame([
    {"UH": "Matoc", **resumen_matoc},
    {"UH": "Pocco", **resumen_pocco}
])

resumen_df.to_csv(
    os.path.join(OUTPUT_DIR, "4_resumen_UH_mensual_OBS.csv"),
    index=False
)

print("Tabla resumen FASE 3 generada:")
print(resumen_df)

print("\nFASE 3 COMPLETADA.")