# ==========================================================
# FASE 4
# MENSUALIZACIÓN DE TEMPERATURA
# ==========================================================

import pandas as pd
from pathlib import Path
import numpy as np

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_DIR = BASE_DIR / "data_raw"
OUTPUT_DIR = BASE_DIR / "data_mensual"

OUTPUT_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------
# ARCHIVOS
# ----------------------------------------------------------

archivos_T = [
    "T_Matoc_diario.csv",
    "T_Pocco_diario.csv"
]

resumen = []

# ----------------------------------------------------------
# CALENDARIO FIJO
# ----------------------------------------------------------

rango = pd.date_range("2012-01-01","2022-12-31",freq="D")

# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------

for archivo_nombre in archivos_T:

    archivo = INPUT_DIR / archivo_nombre

    print("\n-----------------------------------")
    print("Procesando:", archivo.name)

    # detectar separador
    with open(archivo, "r", encoding="utf-8") as f:
        primera_linea = f.readline()

    sep = ";" if ";" in primera_linea else ","

    df = pd.read_csv(archivo, sep=sep)

    df.columns = df.columns.str.strip()

    # ------------------------------------------------------
    # FECHA
    # ------------------------------------------------------

    df["fecha"] = pd.to_datetime(
        df["fecha"],
        dayfirst=True,
        errors="coerce"
    )

    df = df.dropna(subset=["fecha"])

    df["Tmed"] = pd.to_numeric(df["Tmed"], errors="coerce")

    # ------------------------------------------------------
    # CALENDARIO COMPLETO
    # ------------------------------------------------------

    calendario = pd.DataFrame({"fecha": rango})

    df = calendario.merge(df, on="fecha", how="left")

    # ------------------------------------------------------
    # AÑO Y MES
    # ------------------------------------------------------

    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month

    df["dias_mes"] = df["fecha"].dt.days_in_month

    # ------------------------------------------------------
    # PROMEDIO MENSUAL
    # ------------------------------------------------------

    mensual = (
        df.groupby(["anio","mes"])
        .agg(
            Tmed=("Tmed","mean"),
            dias_validos=("Tmed","count"),
            dias_mes=("dias_mes","first")
        )
        .reset_index()
    )

    # ------------------------------------------------------
    # COBERTURA
    # ------------------------------------------------------

    mensual["cobertura"] = mensual["dias_validos"] / mensual["dias_mes"]

    # regla 70%
    mensual.loc[mensual["cobertura"] < 0.7, "Tmed"] = np.nan

    # ------------------------------------------------------
    # FECHA
    # ------------------------------------------------------

    mensual["fecha"] = pd.to_datetime(dict(
        year=mensual.anio,
        month=mensual.mes,
        day=1
    ))

    mensual = mensual[[
        "fecha",
        "Tmed",
        "dias_validos",
        "dias_mes",
        "cobertura"
    ]]

    # ------------------------------------------------------
    # GUARDAR
    # ------------------------------------------------------

    nombre_salida = archivo_nombre.replace("_diario","_mensual")

    salida = OUTPUT_DIR / nombre_salida

    mensual.to_csv(salida,index=False)

    print("Archivo guardado:", salida)

    resumen.append({
        "archivo": archivo_nombre,
        "meses_generados": len(mensual),
        "T_media_global": round(mensual["Tmed"].mean(),2)
    })

# ----------------------------------------------------------
# RESUMEN
# ----------------------------------------------------------

resumen_df = pd.DataFrame(resumen)

resumen_path = OUTPUT_DIR / "resumen_temperatura_mensual.csv"

resumen_df.to_csv(resumen_path,index=False)

print("\n===================================")
print("MENSUALIZACIÓN DE TEMPERATURA FINALIZADA")
print("Resumen guardado en:")
print(resumen_path)
print("===================================")