# ==========================================================
# FASE 3
# MENSUALIZACIÓN DE CAUDAL
# Serie diaria → Serie mensual
# Regla hidrológica: mínimo 80% de cobertura mensual
# Periodo de estudio: 2012–2022
# ==========================================================

import pandas as pd
import numpy as np
from pathlib import Path

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_DIR = BASE_DIR / "data_postqc"
OUTPUT_DIR = BASE_DIR / "data_mensual"

OUTPUT_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------
# AREAS DE CUENCA (km2)
# ----------------------------------------------------------

areas = {
    "Matoc": 2.71,
    "Pocco": 4.22
}

# ----------------------------------------------------------
# ARCHIVOS
# ----------------------------------------------------------

archivos = [
    "Q_Matoc_diario_m3s_postqc.csv",
    "Q_Pocco_diario_m3s_postqc.csv"
]

# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------

for nombre_archivo in archivos:

    archivo = INPUT_DIR / nombre_archivo

    print("\n-----------------------------------")
    print("Procesando:", archivo.name)

    df = pd.read_csv(archivo)

    # ------------------------------------------------------
    # LIMPIEZA BASICA
    # ------------------------------------------------------

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["Q_m3s"] = pd.to_numeric(df["Q_m3s"], errors="coerce")

    df = df.dropna(subset=["fecha"])
    df = df.sort_values("fecha")
    df = df.drop_duplicates(subset="fecha")

    # ------------------------------------------------------
    # CALENDARIO COMPLETO
    # ------------------------------------------------------

    calendario = pd.date_range(
        start=df["fecha"].min(),
        end=df["fecha"].max(),
        freq="D"
    )

    df = (
        df
        .set_index("fecha")
        .reindex(calendario)
        .rename_axis("fecha")
        .reset_index()
    )

    # ------------------------------------------------------
    # VARIABLES TEMPORALES
    # ------------------------------------------------------

    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["year_month"] = df["fecha"].dt.to_period("M")

    # ------------------------------------------------------
    # AGREGACIÓN MENSUAL
    # ------------------------------------------------------

    mensual = df.groupby("year_month").agg(
        Q_m3s=("Q_m3s", "mean"),
        dias_validos=("Q_m3s", lambda x: x.notna().sum()),
        dias_mes=("Q_m3s", "size")
    ).reset_index()

    mensual["fecha"] = mensual["year_month"].dt.to_timestamp()

    # ------------------------------------------------------
    # COBERTURA DE DATOS
    # ------------------------------------------------------

    mensual["cobertura"] = (
        mensual["dias_validos"] /
        mensual["dias_mes"].replace(0, np.nan)
    )

    # ------------------------------------------------------
    # CLASIFICACIÓN DE CALIDAD
    # ------------------------------------------------------

    mensual["calidad_mes"] = np.where(
        mensual["cobertura"] >= 0.8,
        "ACEPTABLE",
        "BAJA"
    )

    # meses con baja cobertura se eliminan
    mensual.loc[mensual["cobertura"] < 0.8, "Q_m3s"] = np.nan

    # ------------------------------------------------------
    # IDENTIFICAR ESTACIÓN
    # ------------------------------------------------------

    estacion = nombre_archivo.split("_")[1]

    area = areas.get(estacion)

    # ------------------------------------------------------
    # CAUDAL ESPECÍFICO
    # ------------------------------------------------------

    mensual["Q_Ls_km2"] = (
        mensual["Q_m3s"] * 1000 / area
    )

    # ------------------------------------------------------
    # ESCORRENTÍA (mm/mes)
    # usando días del mes (corrección hidrológica)
    # ------------------------------------------------------

    mensual["Q_mm_mes"] = (
        mensual["Q_m3s"] * 86.4 * mensual["dias_mes"] / area
    )

    # ------------------------------------------------------
    # REDONDEO DE RESULTADOS
    # ------------------------------------------------------

    mensual["Q_m3s"] = mensual["Q_m3s"].round(3)
    mensual["Q_Ls_km2"] = mensual["Q_Ls_km2"].round(2)
    mensual["Q_mm_mes"] = mensual["Q_mm_mes"].round(2)

    # ------------------------------------------------------
    # GUARDAR RESULTADOS
    # ------------------------------------------------------

    salida = OUTPUT_DIR / f"Q_{estacion}_mensual.csv"

    mensual.to_csv(salida, index=False)

    print("Archivo generado:", salida)

    # ------------------------------------------------------
    # RESUMEN
    # ------------------------------------------------------

    meses_total = len(mensual)
    meses_validos = mensual["Q_m3s"].notna().sum()

    print("Meses totales:", meses_total)
    print("Meses válidos:", meses_validos)

print("\n===================================")
print("MENSUALIZACIÓN FINALIZADA")
print("===================================")