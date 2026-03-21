"""
Script: streamflow_raw_processing.py

Descripción:
Procesa datos crudos de caudal

Entradas:
Datos ANA

Salidas:
Datos limpios

Autor: Renzo Mendoza
Año: 2026
"""
# ==========================================================
# SCRIPT 2
# FASE 1
# CONTROL DE CALIDAD DE CAUDAL DIARIO
# Cuencas Matoc y Pocco – Olleros
# Periodo: 2012–2022
# ==========================================================

import pandas as pd
from pathlib import Path
import numpy as np

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_DIR = BASE_DIR / "data_procesada"
OUTPUT_DIR = BASE_DIR / "data_qc"

OUTPUT_DIR.mkdir(exist_ok=True)

archivos_qc = [
    "Q_Matoc_diario_m3s.csv",
    "Q_Pocco_diario_m3s.csv"
]

resumen = []

# ----------------------------------------------------------
# PERIODO DE ESTUDIO
# ----------------------------------------------------------

rango_completo = pd.date_range("2012-01-01", "2022-12-31", freq="D")

# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------

for nombre_archivo in archivos_qc:

    archivo = INPUT_DIR / nombre_archivo

    print("\n-----------------------------------")
    print("Procesando:", archivo.name)

    df = pd.read_csv(archivo)

    df.columns = df.columns.str.strip()

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["Q_m3s"] = pd.to_numeric(df["Q_m3s"], errors="coerce")

    df = df.dropna(subset=["fecha"])
    df = df.drop_duplicates(subset="fecha")

    df = df.sort_values("fecha")

    print("Periodo observado:", df["fecha"].min(), "→", df["fecha"].max())

    # ------------------------------------------------------
    # CREAR SERIE COMPLETA
    # ------------------------------------------------------

    df = df.set_index("fecha").reindex(rango_completo)

    df.index.name = "fecha"

    df = df.reset_index()

    # ------------------------------------------------------
    # FLAGS QC
    # ------------------------------------------------------

    df["flag_negativo"] = df["Q_m3s"] < 0
    df["flag_iqr"] = False
    df["flag_percentil"] = False
    df["flag_salto"] = False

    serie = df["Q_m3s"].dropna()

    # ------------------------------------------------------
    # OUTLIERS IQR (bidireccional)
    # ------------------------------------------------------

    Q1 = serie.quantile(0.25)
    Q3 = serie.quantile(0.75)

    IQR = Q3 - Q1

    limite_sup = Q3 + 1.5 * IQR
    limite_inf = Q1 - 1.5 * IQR

    df.loc[df["Q_m3s"] > limite_sup, "flag_iqr"] = True
    df.loc[df["Q_m3s"] < limite_inf, "flag_iqr"] = True

    # ------------------------------------------------------
    # PERCENTILES EXTREMOS
    # ------------------------------------------------------

    p005 = serie.quantile(0.005)
    p995 = serie.quantile(0.995)

    df.loc[df["Q_m3s"] > p995, "flag_percentil"] = True
    df.loc[df["Q_m3s"] < p005, "flag_percentil"] = True

    # ------------------------------------------------------
    # SALTOS HIDROLÓGICOS
    # ------------------------------------------------------

    df["diff_q"] = df["Q_m3s"].diff().abs()

    umbral = df["diff_q"].quantile(0.99)

    df.loc[df["diff_q"] > umbral, "flag_salto"] = True

    df.drop(columns="diff_q", inplace=True)

    # ------------------------------------------------------
    # ESTADO QC
    # ------------------------------------------------------

    df["estado_qc"] = "ACEPTADO"

    df.loc[df["Q_m3s"].isna(), "estado_qc"] = "FALTANTE"

    df.loc[
        (df["flag_negativo"]) |
        (df["flag_iqr"]) |
        (df["flag_percentil"]) |
        (df["flag_salto"]),
        "estado_qc"
    ] = "REVISAR"

    # ------------------------------------------------------
    # ESTADISTICAS
    # ------------------------------------------------------

    total = len(df)

    aceptados = (df["estado_qc"] == "ACEPTADO").sum()
    revisar = (df["estado_qc"] == "REVISAR").sum()
    faltantes = (df["estado_qc"] == "FALTANTE").sum()

    pct_faltantes = round(faltantes / total * 100, 2)

    print("Registros totales:", total)
    print("Aceptados:", aceptados)
    print("Revisar:", revisar)
    print("Faltantes:", faltantes, f"({pct_faltantes}%)")

    # ------------------------------------------------------
    # GUARDAR
    # ------------------------------------------------------

    salida = OUTPUT_DIR / f"{archivo.stem}_qc.csv"

    df.to_csv(salida, index=False)

    resumen.append({
        "archivo": archivo.name,
        "total": total,
        "aceptados": aceptados,
        "revisar": revisar,
        "faltantes": faltantes,
        "pct_faltantes": pct_faltantes
    })

# ----------------------------------------------------------
# RESUMEN FINAL
# ----------------------------------------------------------

resumen_df = pd.DataFrame(resumen)

resumen_path = OUTPUT_DIR / "resumen_qc_caudal.csv"

resumen_df.to_csv(resumen_path, index=False)

print("\n===================================")
print("QC DIARIO FINALIZADO")
print("Resumen guardado en:")
print(resumen_path)
print("===================================")
