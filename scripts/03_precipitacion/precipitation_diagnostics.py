"""
Script: precipitation_diagnostics.py

Descripción general
-------------------
Este script realiza el diagnóstico de disponibilidad y calidad
de la serie diaria de precipitación posterior al control de calidad.

Se evalúa la completitud temporal de registros por estación y por año,
identificando estaciones críticas, años vacíos y porcentaje global
de datos faltantes.

Entradas
--------
- Serie diaria depurada de precipitación post-QC

Salidas
-------
- Resumen de disponibilidad por estación
- Resumen anual de completitud
- Reporte global de calidad de datos

Autor: Renzo Mendoza
Año: 2026
"""

import pandas as pd
import os


# ==========================================================
# 1. CONFIGURACIÓN DE RUTAS
# ==========================================================

INPUT_FILE = "outputs/post_qc/diario_post_qc_fase1.csv"
OUTPUT_DIR = "outputs/diagnosticos"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================================================
# 2. CARGA DE DATOS
# ==========================================================

print("\nCargando serie diaria post-QC...")

df = pd.read_csv(
    INPUT_FILE,
    parse_dates=["fecha"]
)

print(f"Total registros cargados: {len(df)}")


# ==========================================================
# 3. FUNCIÓN DE DIAGNÓSTICO POR ESTACIÓN
# ==========================================================

"""
Se calcula disponibilidad total de datos válidos y faltantes
para cada estación.
"""

resumen = (
    df.groupby("Estacion")["Precip_postQC"]
    .agg(
        total_registros="size",
        validos=lambda x: x.notna().sum(),
        na=lambda x: x.isna().sum()
    )
)

resumen["%_NA"] = (
    resumen["na"] /
    resumen["total_registros"]
) * 100

resumen["%_validos"] = (
    resumen["validos"] /
    resumen["total_registros"]
) * 100

print("\nResumen de disponibilidad por estación:")
print(resumen)

resumen.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "resumen_estaciones_fase1.csv"
    )
)


# ==========================================================
# 4. FUNCIÓN DE DIAGNÓSTICO ANUAL
# ==========================================================

df["anio"] = df["fecha"].dt.year

"""
Se calcula porcentaje anual de datos válidos,
permitiendo identificar vacíos temporales.
"""

resumen_anual = (
    df.groupby(["Estacion", "anio"])["Precip_postQC"]
    .apply(lambda x: x.notna().mean() * 100)
    .reset_index(name="%_datos_validos")
)

print("\nDisponibilidad anual (% datos válidos):")
print(resumen_anual)

resumen_anual.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "resumen_anual_fase1.csv"
    ),
    index=False
)


# ==========================================================
# 5. IDENTIFICACIÓN DE AÑOS VACÍOS
# ==========================================================

anios_vacios = resumen_anual[
    resumen_anual["%_datos_validos"] == 0
]

if len(anios_vacios) > 0:
    print("\n⚠ Años completamente sin datos detectados:")
    print(anios_vacios)
else:
    print("\nNo se detectaron años completamente vacíos.")


# ==========================================================
# 6. IDENTIFICACIÓN DE ESTACIONES CRÍTICAS
# ==========================================================

"""
Se consideran críticas estaciones con más de 70% de datos faltantes.
"""

estaciones_criticas = resumen[
    resumen["%_NA"] > 70
]

if len(estaciones_criticas) > 0:
    print("\n⚠ Estaciones con alta falta de datos:")
    print(estaciones_criticas)
else:
    print("\nNo se detectaron estaciones críticas.")


# ==========================================================
# 7. DIAGNÓSTICO GLOBAL
# ==========================================================

total_na = df["Precip_postQC"].isna().sum()
total_global = len(df)

print("\nDiagnóstico global:")
print(f"Total NA: {total_na}")
print(
    f"Porcentaje NA global: "
    f"{(total_na/total_global)*100:.2f}%"
)

print("\nDiagnóstico de disponibilidad completado.")
print(f"Resultados guardados en: {OUTPUT_DIR}")
