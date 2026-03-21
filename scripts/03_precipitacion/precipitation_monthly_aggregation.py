"""
Script: precipitation_monthly_aggregation.py

Descripción:
Agrega precipitación diaria a mensual

Entradas:
Datos diarios

Salidas:
Serie mensual

Autor: Renzo Mendoza
Año: 2026
"""
# ============================================================
# SCRIPT 4
# FASE 2 — AGREGACIÓN MENSUAL OBSERVADA
# Basado en diario_post_qc_fase1.csv
# ============================================================

import pandas as pd
import numpy as np
import os

# ============================================================
# RUTAS
# ============================================================

INPUT_FILE = "outputs/post_qc/diario_post_qc_fase1.csv"
OUTPUT_DIR = "outputs/mensuales"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# CARGAR DATOS
# ============================================================

print("\nCargando datos post-QC...")
df = pd.read_csv(INPUT_FILE, parse_dates=["fecha"])

df["anio"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month

df = df[(df["anio"] >= 2012) & (df["anio"] <= 2022)]

print(f"Registros en periodo 2012–2022: {len(df)}")

# ============================================================
# FUNCIÓN AGREGACIÓN MENSUAL
# ============================================================

def calcular_mensual(grupo):
    total_dias = grupo["fecha"].nunique()
    dias_validos = grupo["Precip_postQC"].notna().sum()

    porcentaje_validos = dias_validos / total_dias if total_dias > 0 else 0

    if porcentaje_validos >= 0.80:
        suma_mensual = grupo["Precip_postQC"].sum()
    else:
        suma_mensual = np.nan

    return pd.Series({
        "Prec_mensual": suma_mensual,
        "Dias_totales": total_dias,
        "Dias_validos": dias_validos,
        "Porcentaje_validos": round(porcentaje_validos * 100, 2)
    })

# ============================================================
# AGREGACIÓN POR ESTACIÓN
# ============================================================

mensual = (
    df.groupby(["UH", "Estacion", "anio", "mes"])
      .apply(calcular_mensual)
      .reset_index()
)

# Crear fecha mensual tipo datetime (opcional, pero útil para fases siguientes)
mensual["fecha_mensual"] = pd.to_datetime(
    mensual["anio"].astype(str) + "-" +
    mensual["mes"].astype(str) + "-01"
)

# Guardar archivo general
mensual.to_csv(
    os.path.join(OUTPUT_DIR, "mensual_estaciones_2012_2022.csv"),
    index=False
)

print("Archivo mensual generado.")

# ============================================================
# TABLA RESUMEN DISPONIBILIDAD MENSUAL
# ============================================================

resumen_mensual = (
    mensual.groupby(["UH", "Estacion"])["Prec_mensual"]
    .agg(
        meses_totales="size",
        meses_validos=lambda x: x.notna().sum(),
        meses_na=lambda x: x.isna().sum()
    )
)

resumen_mensual["porcentaje_meses_validos"] = (
    resumen_mensual["meses_validos"] /
    resumen_mensual["meses_totales"] * 100
).round(2)

resumen_mensual.to_csv(
    os.path.join(OUTPUT_DIR, "resumen_disponibilidad_mensual.csv")
)

print("Tabla resumen mensual generada.")

print("\nFASE 2 COMPLETADA CORRECTAMENTE.")
