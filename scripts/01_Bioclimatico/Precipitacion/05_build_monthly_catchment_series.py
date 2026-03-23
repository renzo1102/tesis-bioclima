# ============================================================
# SCRIPT – FASE 3: CONSTRUCCIÓN DE SERIE MENSUAL REPRESENTATIVA POR UH
# Solo con datos observados (sin relleno)
# Incluye tabla resumen estructural
# ============================================================

# ============================================================
# DESCRIPCIÓN GENERAL
# ============================================================
# Este script construye una serie mensual representativa a nivel
# de Unidad Hidrológica (UH) a partir de las estaciones disponibles.
#
# Objetivo:
# - Integrar múltiples estaciones en una sola serie por UH
# - Mantener únicamente datos observados (sin interpolación)
# - Evaluar la robustez espacial de cada mes
#
# Lógica principal:
# - Si hay ≥ 2 estaciones válidas → promedio espacial
# - Si hay 1 estación → se usa ese valor (menor robustez)
# - Si no hay datos → NA
#
# Entradas:
# - outputs/mensuales/mensual_estaciones_2012_2022.csv
#
# Salidas:
# - Series mensuales por UH (Matoc y Pocco)
# - Tabla resumen de cobertura y fuentes
#
# Importancia:
# - Genera la serie base para validación y modelamiento hidrológico
# - Permite evaluar consistencia espacial de la red de estaciones

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
# Se carga la serie mensual por estación generada en FASE 2.

print("\nCargando datos mensuales por estación...")
df = pd.read_csv(INPUT_FILE, parse_dates=["fecha_mensual"])

# ============================================================
# FUNCIÓN CONSTRUCCIÓN DE SERIE UH
# ============================================================

def construir_uh(df_uh, nombre_uh):
    """
    Construye la serie mensual representativa de una UH.

    Parámetros:
    - df_uh: datos de estaciones dentro de una UH
    - nombre_uh: nombre de la unidad hidrológica

    Retorna:
    - DataFrame con serie mensual consolidada
    """

    resultados = []

    # Iteración por cada mes
    for fecha, grupo in df_uh.groupby("fecha_mensual"):

        # Valores válidos (no NA)
        valores_validos = grupo["Prec_mensual"].dropna()
        n_validos = len(valores_validos)

        # ----------------------------------------------------
        # CRITERIO DE REPRESENTATIVIDAD
        # ----------------------------------------------------
        # Se define la calidad del dato mensual según número
        # de estaciones disponibles.

        if n_validos >= 2:
            # Promedio espacial (más robusto)
            prec_uh = valores_validos.mean()
            fuente = "Promedio >=2 estaciones"

        elif n_validos == 1:
            # Uso de una sola estación (menor confiabilidad)
            prec_uh = valores_validos.iloc[0]
            fuente = "1 estación"

        else:
            # Sin información disponible
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
# SEPARACIÓN POR UNIDAD HIDROLÓGICA
# ============================================================

matoc_df = df[df["UH"] == "Matoc"]
pocco_df = df[df["UH"] == "Pocco"]

# ============================================================
# CONSTRUCCIÓN DE SERIES
# ============================================================

matoc_uh = construir_uh(matoc_df, "Matoc")
pocco_uh = construir_uh(pocco_df, "Pocco")

# ============================================================
# EXPORTACIÓN DE SERIES
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
# FUNCIÓN RESUMEN ESTRUCTURAL
# ============================================================

def resumen_uh(df_uh):
    """
    Genera métricas de calidad y cobertura para la UH.

    Indicadores:
    - Número total de meses
    - Meses válidos
    - Meses sin datos
    - Cobertura porcentual
    - Distribución por tipo de fuente
    """

    meses_totales = len(df_uh)
    meses_validos = df_uh["Prec_UH_OBS"].notna().sum()
    meses_na = df_uh["Prec_UH_OBS"].isna().sum()

    porcentaje_cobertura = round((meses_validos / meses_totales) * 100, 2)

    # Distribución de fuentes
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

# ============================================================
# GENERACIÓN DE TABLA RESUMEN
# ============================================================

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

# ============================================================
# INTERPRETACIÓN METODOLÓGICA
# ============================================================
# Esta fase integra la información espacial de estaciones
# para construir una serie hidrológica representativa.
#
# Aportes clave:
# - Reduce ruido de estaciones individuales
# - Mejora representatividad espacial
# - Permite evaluar dependencia de estaciones
#
# Indicadores clave:
# - n_estaciones_validas → robustez espacial mensual
# - Fuente → calidad del dato (promedio vs individual)
# - Cobertura (%) → completitud de la serie
#
# Resultado:
# - Serie mensual observada por UH
# - Base directa para:
#     - Validación de CHIRPS
#     - Modelamiento hidrológico
#     - Análisis clima–caudal
#
# Nota:
# Esta serie aún NO incluye relleno de datos,
# por lo que refleja estrictamente la disponibilidad observada.
# ============================================================
