# ============================================================
# SCRIPT – FASE 2: AGREGACIÓN MENSUAL OBSERVADA
# Basado en diario_post_qc_fase1.csv
# ============================================================

# ============================================================
# DESCRIPCIÓN GENERAL
# ============================================================
# Este script transforma las series de precipitación diaria
# (ya depuradas en FASE 1) en series mensuales consolidadas.
#
# Objetivo:
# - Obtener precipitación mensual confiable por estación
# - Aplicar un criterio de calidad basado en cobertura diaria
#
# Criterio clave:
# - Un mes es válido solo si tiene ≥ 80% de datos diarios válidos
#
# Entradas:
# - outputs/post_qc/diario_post_qc_fase1.csv
#
# Salidas:
# - Serie mensual por estación
# - Tabla resumen de disponibilidad mensual
#
# Importancia:
# - Este paso es crítico para evitar sesgos por datos incompletos
# - Base para análisis hidrológico y modelamiento

import pandas as pd
import numpy as np
import os

# ============================================================
# RUTAS
# ============================================================
# Uso de rutas relativas para garantizar reproducibilidad.

INPUT_FILE = "outputs/post_qc/diario_post_qc_fase1.csv"
OUTPUT_DIR = "outputs/mensuales"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# CARGAR DATOS
# ============================================================
# Se carga la serie diaria post-QC (FASE 1)

print("\nCargando datos post-QC...")
df = pd.read_csv(INPUT_FILE, parse_dates=["fecha"])

# Extracción de componentes temporales
df["anio"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month

# Filtrado del periodo de estudio
df = df[(df["anio"] >= 2012) & (df["anio"] <= 2022)]

print(f"Registros en periodo 2012–2022: {len(df)}")

# ============================================================
# FUNCIÓN DE AGREGACIÓN MENSUAL
# ============================================================
# Esta función define cómo se construye la precipitación mensual
# a partir de datos diarios.

def calcular_mensual(grupo):
    """
    Calcula la precipitación mensual para un grupo dado
    (estación, año, mes).

    Parámetros:
    - grupo: subconjunto de datos diarios

    Retorna:
    - Serie con:
        Prec_mensual: suma mensual (si cumple criterio)
        Dias_totales: número de días en el mes
        Dias_validos: días con datos válidos
        Porcentaje_validos: % de cobertura
    """

    # Número total de días únicos en el mes
    total_dias = grupo["fecha"].nunique()

    # Número de días con datos válidos
    dias_validos = grupo["Precip_postQC"].notna().sum()

    # Porcentaje de datos disponibles
    porcentaje_validos = dias_validos / total_dias if total_dias > 0 else 0

    # --------------------------------------------------------
    # CRITERIO DE CALIDAD (80%)
    # --------------------------------------------------------
    # Si el mes tiene suficiente información → se calcula suma
    # Si no → se descarta (NA)

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
# Se aplica la función a cada combinación:
# UH – Estación – Año – Mes

mensual = (
    df.groupby(["UH", "Estacion", "anio", "mes"])
      .apply(calcular_mensual)
      .reset_index()
)

# Creación de variable temporal mensual
# (útil para análisis posteriores)
mensual["fecha_mensual"] = pd.to_datetime(
    mensual["anio"].astype(str) + "-" +
    mensual["mes"].astype(str) + "-01"
)

# Guardar dataset mensual completo
mensual.to_csv(
    os.path.join(OUTPUT_DIR, "mensual_estaciones_2012_2022.csv"),
    index=False
)

print("Archivo mensual generado.")

# ============================================================
# RESUMEN DE DISPONIBILIDAD MENSUAL
# ============================================================
# Se evalúa la calidad de la serie mensual por estación.

resumen_mensual = (
    mensual.groupby(["UH", "Estacion"])["Prec_mensual"]
    .agg(
        meses_totales="size",
        meses_validos=lambda x: x.notna().sum(),
        meses_na=lambda x: x.isna().sum()
    )
)

# Porcentaje de meses válidos
resumen_mensual["porcentaje_meses_validos"] = (
    resumen_mensual["meses_validos"] /
    resumen_mensual["meses_totales"] * 100
).round(2)

# Exportación
resumen_mensual.to_csv(
    os.path.join(OUTPUT_DIR, "resumen_disponibilidad_mensual.csv")
)

print("Tabla resumen mensual generada.")

print("\nFASE 2 COMPLETADA CORRECTAMENTE.")


# ============================================================
# INTERPRETACIÓN METODOLÓGICA
# ============================================================
# Esta fase convierte datos diarios en información mensual
# confiable, aplicando un criterio de cobertura temporal.
#
# Aspectos clave:
# - Evita subestimación de precipitación mensual
# - Filtra meses incompletos o poco representativos
# - Genera una base robusta para análisis hidrológico
#
# Indicador crítico:
# - 80% de datos diarios válidos por mes
#
# Resultado:
# - Serie mensual depurada por estación
# - Diagnóstico de disponibilidad mensual
#
# Este dataset es utilizado en:
# - Validación de datos satelitales (CHIRPS)
# - Modelamiento hidrológico
# - Análisis de correlaciones clima–caudal
# ============================================================
