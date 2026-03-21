"""
Script: precipitation_monthly_aggregation.py

Descripción general
-------------------
Este script realiza la agregación de precipitación diaria
post-control de calidad a escala mensual para el periodo
2012–2022.

Se aplica un criterio de completitud temporal, donde solo
se calcula el acumulado mensual si al menos el 80 % de los
días del mes presentan datos válidos.

Entradas
--------
- Serie diaria depurada de precipitación post-QC

Salidas
-------
- Serie mensual por estación
- Resumen de disponibilidad mensual

Autor: Renzo Mendoza
Año: 2026
"""

import pandas as pd
import numpy as np
import os


# ============================================================
# 1. CONFIGURACIÓN DE RUTAS
# ============================================================

INPUT_FILE = "outputs/post_qc/diario_post_qc_fase1.csv"
OUTPUT_DIR = "outputs/mensuales"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 2. CARGA Y FILTRO TEMPORAL
# ============================================================

print("\nCargando datos diarios post-QC...")

df = pd.read_csv(
    INPUT_FILE,
    parse_dates=["fecha"]
)

df["anio"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month

"""
Se restringe el análisis al periodo de estudio.
"""

df = df[
    (df["anio"] >= 2012) &
    (df["anio"] <= 2022)
]

print(f"Registros en periodo: {len(df)}")


# ============================================================
# 3. FUNCIÓN DE AGREGACIÓN MENSUAL
# ============================================================

def calcular_mensual(grupo):

    """
    Calcula precipitación mensual acumulada
    considerando criterio de disponibilidad.

    Si menos del 80 % de los días tienen datos válidos,
    el mes se considera no confiable.
    """

    total_dias = grupo["fecha"].nunique()

    dias_validos = grupo[
        "Precip_postQC"
    ].notna().sum()

    porcentaje_validos = (
        dias_validos / total_dias
        if total_dias > 0 else 0
    )

    if porcentaje_validos >= 0.80:

        suma_mensual = grupo[
            "Precip_postQC"
        ].sum()

    else:

        suma_mensual = np.nan

    return pd.Series({
        "Prec_mensual": suma_mensual,
        "Dias_totales": total_dias,
        "Dias_validos": dias_validos,
        "Porcentaje_validos":
            round(porcentaje_validos * 100, 2)
    })


# ============================================================
# 4. AGREGACIÓN POR ESTACIÓN
# ============================================================

mensual = (
    df.groupby(
        ["UH", "Estacion", "anio", "mes"]
    )
    .apply(calcular_mensual)
    .reset_index()
)

"""
Se construye fecha mensual para facilitar
integración con fases posteriores.
"""

mensual["fecha_mensual"] = pd.to_datetime(
    mensual["anio"].astype(str) + "-" +
    mensual["mes"].astype(str) + "-01"
)


# ============================================================
# 5. EXPORTACIÓN SERIE MENSUAL
# ============================================================

mensual.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "mensual_estaciones_2012_2022.csv"
    ),
    index=False
)

print("Serie mensual exportada.")


# ============================================================
# 6. RESUMEN DISPONIBILIDAD MENSUAL
# ============================================================

resumen_mensual = (
    mensual.groupby(
        ["UH", "Estacion"]
    )["Prec_mensual"]
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
    os.path.join(
        OUTPUT_DIR,
        "resumen_disponibilidad_mensual.csv"
    )
)

print("Resumen mensual generado.")
print("\nFASE 2 completada.")
