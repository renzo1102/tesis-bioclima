# ==========================================================
# SCRIPT – DIAGNÓSTICO FASE 1 POST-QC
# Evaluación de calidad de datos después del Post-QC Fase 1
# ==========================================================

# ==========================================================
# DESCRIPCIÓN GENERAL
# ==========================================================
# Este script realiza un diagnóstico estadístico del dataset
# generado en la FASE 1 del post-procesamiento de control de calidad.
#
# Objetivos:
# - Evaluar la disponibilidad de datos por estación
# - Identificar pérdida de información (valores NA)
# - Detectar estaciones problemáticas
# - Evaluar cobertura temporal anual
#
# Este análisis es clave antes de:
# - Aplicar relleno de datos faltantes
# - Agregación temporal (mensual/anual)
# - Modelamiento hidrológico
#
# Entradas:
# - outputs/post_qc/diario_post_qc_fase1.csv
#
# Salidas:
# - Resumen por estación
# - Resumen anual
# - Diagnóstico de calidad del dataset

import pandas as pd
import os

# ==============================
# CONFIGURACIÓN DE RUTAS
# ==============================
# Uso de rutas relativas para garantizar reproducibilidad.

INPUT_FILE = "outputs/post_qc/diario_post_qc_fase1.csv"
OUTPUT_DIR = "outputs/diagnosticos"

# Crear carpeta de salida
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==============================
# CARGAR DATOS
# ==============================
# Se carga el dataset generado en la FASE 1.

print("\nCargando archivo FASE 1...")
df = pd.read_csv(INPUT_FILE, parse_dates=["fecha"])

print(f"Total registros cargados: {len(df)}")

# ==============================
# RESUMEN POR ESTACIÓN
# ==============================
# Se calcula la calidad de datos por estación:
# - total_registros: total de observaciones
# - validos: valores no nulos
# - na: valores faltantes
#
# Esto permite identificar estaciones con problemas de datos.

resumen = (
    df.groupby("Estacion")["Precip_postQC"]
    .agg(
        total_registros="size",  # incluye NA
        validos=lambda x: x.notna().sum(),
        na=lambda x: x.isna().sum()
    )
)

# Porcentajes
resumen["%_NA"] = (resumen["na"] / resumen["total_registros"]) * 100
resumen["%_validos"] = (resumen["validos"] / resumen["total_registros"]) * 100

print("\nResumen por estación:")
print(resumen)

# Exportación
resumen.to_csv(
    os.path.join(OUTPUT_DIR, "resumen_estaciones_fase1.csv")
)

# ==============================
# RESUMEN ANUAL
# ==============================
# Se evalúa la disponibilidad de datos por año y estación.
# Métrica: porcentaje de datos válidos.

df["anio"] = df["fecha"].dt.year

resumen_anual = (
    df.groupby(["Estacion", "anio"])["Precip_postQC"]
    .apply(lambda x: x.notna().mean() * 100)
    .reset_index(name="%_datos_validos")
)

print("\nResumen anual (% datos válidos por año):")
print(resumen_anual)

# Exportación
resumen_anual.to_csv(
    os.path.join(OUTPUT_DIR, "resumen_anual_fase1.csv"),
    index=False
)

# ==============================
# DETECCIÓN DE AÑOS VACÍOS
# ==============================
# Se identifican años con 0% de datos válidos,
# lo cual indica ausencia total de información.

anios_vacios = resumen_anual[
    resumen_anual["%_datos_validos"] == 0
]

if len(anios_vacios) > 0:
    print("\nAños completamente vacíos detectados:")
    print(anios_vacios)
else:
    print("\nNo hay años completamente vacíos.")

# ==============================
# DETECCIÓN DE ESTACIONES CRÍTICAS
# ==============================
# Se identifican estaciones con más de 70% de datos faltantes,
# consideradas de baja confiabilidad.

estaciones_criticas = resumen[
    resumen["%_NA"] > 70
]

if len(estaciones_criticas) > 0:
    print("\nEstaciones con más de 70% de NA:")
    print(estaciones_criticas)
else:
    print("\nNo hay estaciones con más de 70% de NA.")

# ==============================
# RESUMEN GLOBAL
# ==============================
# Evaluación general del dataset.

total_na = df["Precip_postQC"].isna().sum()
total_global = len(df)

print("\nResumen global:")
print(f"Total NA: {total_na}")
print(f"Porcentaje NA global: {(total_na/total_global)*100:.2f}%")

# ==============================
# MENSAJE FINAL
# ==============================

print("\nDiagnóstico FASE 1 completado.")
print(f"Archivos guardados en: {OUTPUT_DIR}")


# ==========================================================
# INTERPRETACIÓN METODOLÓGICA
# ==========================================================
# Este script permite evaluar la calidad del dataset tras
# aplicar filtros físicos y coherencia espacial (FASE 1).
#
# Indicadores clave:
# - % NA por estación → confiabilidad espacial
# - % datos válidos por año → continuidad temporal
# - Años vacíos → vacíos estructurales
# - Estaciones críticas → candidatas a exclusión
#
# Importancia:
# - Permite decidir si continuar con imputación
# - Identifica debilidades en la red de estaciones
# - Garantiza calidad antes del análisis hidrológico
#
# Este paso es fundamental antes de:
# - FASE 2 (relleno de datos)
# - Agregación mensual
# - Modelamiento hidrológico
# ==========================================================
