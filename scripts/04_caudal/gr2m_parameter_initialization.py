"""
Script: gr2m_parameter_initialization.py

Descripción:
Inicializa parámetros del modelo

Entradas:
Datos hidrológicos de temperatura diaria

Salidas:
Series mensuales de temperatura media y resumen estadístico

Autor: Renzo Mendoza
Año: 2026
"""

# ==========================================================
# SCRIPT 9
# FASE 4
# MENSUALIZACIÓN DE TEMPERATURA
# ==========================================================

import pandas as pd
from pathlib import Path
import numpy as np

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------
# Se define el directorio base del proyecto para permitir
# reproducibilidad del procesamiento climático.

BASE_DIR = Path(__file__).resolve().parents[1]

# Carpeta donde se encuentran las series diarias observadas
INPUT_DIR = BASE_DIR / "data_raw"

# Carpeta donde se almacenarán las series mensuales generadas
OUTPUT_DIR = BASE_DIR / "data_mensual"

OUTPUT_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------
# ARCHIVOS
# ----------------------------------------------------------
# Lista de estaciones térmicas a procesar.

archivos_T = [
    "T_Matoc_diario.csv",
    "T_Pocco_diario.csv"
]

# Lista para almacenar métricas resumen
resumen = []

# ----------------------------------------------------------
# CALENDARIO FIJO
# ----------------------------------------------------------
# Se construye un calendario continuo diario para todo el
# periodo de estudio. Esto permite:
#
# ✔ detectar vacíos de información
# ✔ garantizar consistencia temporal
# ✔ evitar sesgos en promedios mensuales

rango = pd.date_range(
    "2012-01-01",
    "2022-12-31",
    freq="D"
)

# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------
# Se procesa cada estación térmica de forma independiente.

for archivo_nombre in archivos_T:

    archivo = INPUT_DIR / archivo_nombre

    print("\n-----------------------------------")
    print("Procesando:", archivo.name)

    # detectar separador CSV automáticamente
    with open(archivo, "r", encoding="utf-8") as f:
        primera_linea = f.readline()

    sep = ";" if ";" in primera_linea else ","

    df = pd.read_csv(archivo, sep=sep)

    # limpieza de nombres de columnas
    df.columns = df.columns.str.strip()

    # ------------------------------------------------------
    # FECHA
    # ------------------------------------------------------
    # Conversión robusta a datetime.
    # Se eliminan registros con fecha inválida.

    df["fecha"] = pd.to_datetime(
        df["fecha"],
        dayfirst=True,
        errors="coerce"
    )

    df = df.dropna(subset=["fecha"])

    # conversión segura de temperatura
    df["Tmed"] = pd.to_numeric(
        df["Tmed"],
        errors="coerce"
    )

    # ------------------------------------------------------
    # CALENDARIO COMPLETO
    # ------------------------------------------------------
    # Se fusiona la serie observada con el calendario total.
    # Esto permite identificar explícitamente los días sin datos.

    calendario = pd.DataFrame({"fecha": rango})

    df = calendario.merge(df, on="fecha", how="left")

    # ------------------------------------------------------
    # AÑO Y MES
    # ------------------------------------------------------
    # Variables auxiliares necesarias para agregación temporal.

    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month

    df["dias_mes"] = df["fecha"].dt.days_in_month

    # ------------------------------------------------------
    # PROMEDIO MENSUAL
    # ------------------------------------------------------
    # Se calcula temperatura media mensual y métricas de cobertura.

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
    # Se calcula porcentaje de días con datos válidos.
    #
    # Regla hidrológica adoptada:
    # Se acepta el promedio mensual solo si existe ≥70%
    # de cobertura diaria.

    mensual["cobertura"] = (
        mensual["dias_validos"] /
        mensual["dias_mes"]
    )

    mensual.loc[
        mensual["cobertura"] < 0.7,
        "Tmed"
    ] = np.nan

    # ------------------------------------------------------
    # FECHA REPRESENTATIVA MENSUAL
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
    # GUARDAR RESULTADOS
    # ------------------------------------------------------

    nombre_salida = archivo_nombre.replace(
        "_diario",
        "_mensual"
    )

    salida = OUTPUT_DIR / nombre_salida

    mensual.to_csv(salida, index=False)

    print("Archivo guardado:", salida)

    # guardar métricas resumen
    resumen.append({
        "archivo": archivo_nombre,
        "meses_generados": len(mensual),
        "T_media_global": round(
            mensual["Tmed"].mean(),
            2
        )
    })

# ----------------------------------------------------------
# RESUMEN GLOBAL
# ----------------------------------------------------------
# Se construye tabla resumen del procesamiento térmico.

resumen_df = pd.DataFrame(resumen)

resumen_path = OUTPUT_DIR / "resumen_temperatura_mensual.csv"

resumen_df.to_csv(
    resumen_path,
    index=False
)

print("\n===================================")
print("MENSUALIZACIÓN DE TEMPERATURA FINALIZADA")
print("Resumen guardado en:")
print(resumen_path)
print("===================================")
