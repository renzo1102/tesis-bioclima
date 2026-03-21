"""
Script: precipitation_uh_series.py

Descripción general
-------------------
Este script construye la serie mensual representativa de
precipitación observada para cada unidad hidrográfica (UH)
a partir de la agregación espacial de estaciones pluviométricas.

La precipitación mensual de la UH se estima según la disponibilidad:

- Si existen dos o más estaciones con datos válidos:
  se calcula el promedio espacial.
- Si solo una estación presenta datos:
  se adopta dicho valor como representativo.
- Si no existen datos disponibles:
  el mes se clasifica como faltante.

El script también genera indicadores estructurales de cobertura
temporal y fuente de información utilizada.

Entradas
--------
Archivo CSV con precipitación mensual por estación:
outputs/mensuales/mensual_estaciones_2012_2022.csv

Salidas
-------
- Series mensuales representativas por UH
- Tabla resumen de cobertura observacional

Autor: Renzo Mendoza
Año: 2026
"""

import pandas as pd
import numpy as np
import os


# ============================================================
# 1. CONFIGURACIÓN DE RUTAS
# ============================================================

INPUT_FILE = "outputs/mensuales/mensual_estaciones_2012_2022.csv"
OUTPUT_DIR = "outputs/mensuales"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 2. CARGA DE DATOS
# ============================================================

print("\nCargando datos mensuales por estación...")
df = pd.read_csv(INPUT_FILE, parse_dates=["fecha_mensual"])


# ============================================================
# 3. FUNCIÓN PARA CONSTRUIR SERIE REPRESENTATIVA DE UH
# ============================================================

def construir_uh(df_uh, nombre_uh):
    """
    Construye la serie mensual representativa de precipitación
    para una unidad hidrográfica mediante agregación espacial
    de estaciones.

    Parámetros
    ----------
    df_uh : DataFrame
        Datos mensuales de estaciones pertenecientes a la UH.
    nombre_uh : str
        Nombre de la unidad hidrográfica.

    Retorna
    -------
    DataFrame
        Serie mensual representativa con indicadores de fuente.
    """

    resultados = []

    for fecha, grupo in df_uh.groupby("fecha_mensual"):

        valores_validos = grupo["Prec_mensual"].dropna()
        n_validos = len(valores_validos)

        if n_validos >= 2:
            prec_uh = valores_validos.mean()
            fuente = "Promedio >=2 estaciones"

        elif n_validos == 1:
            prec_uh = valores_validos.iloc[0]
            fuente = "1 estación"

        else:
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
# 4. SEPARACIÓN DE UNIDADES HIDROGRÁFICAS
# ============================================================

matoc_df = df[df["UH"] == "Matoc"]
pocco_df = df[df["UH"] == "Pocco"]


# ============================================================
# 5. CONSTRUCCIÓN DE SERIES REPRESENTATIVAS
# ============================================================

matoc_uh = construir_uh(matoc_df, "Matoc")
pocco_uh = construir_uh(pocco_df, "Pocco")


# ============================================================
# 6. GUARDADO DE RESULTADOS
# ============================================================

matoc_uh.to_csv(
    os.path.join(OUTPUT_DIR, "4_Matoc_UH_mensual_OBS.csv"),
    index=False
)

pocco_uh.to_csv(
    os.path.join(OUTPUT_DIR, "4_Pocco_UH_mensual_OBS.csv"),
    index=False
)

print("\nSeries UH generadas correctamente.")


# ============================================================
# 7. FUNCIÓN PARA RESUMEN ESTRUCTURAL DE COBERTURA
# ============================================================

def resumen_uh(df_uh):
    """
    Calcula indicadores de disponibilidad observacional
    y fuente de construcción de la serie UH.

    Parámetros
    ----------
    df_uh : DataFrame

    Retorna
    -------
    dict
        Indicadores de cobertura temporal y fuente de datos.
    """

    meses_totales = len(df_uh)
    meses_validos = df_uh["Prec_UH_OBS"].notna().sum()
    meses_na = df_uh["Prec_UH_OBS"].isna().sum()

    porcentaje_cobertura = round(
        (meses_validos / meses_totales) * 100, 2
    )

    dist_fuente = df_uh["Fuente"].value_counts()

    return {
        "meses_totales": meses_totales,
        "meses_validos": meses_validos,
        "meses_na": meses_na,
        "porcentaje_cobertura": porcentaje_cobertura,
        "meses_promedio_>=2_est":
            dist_fuente.get("Promedio >=2 estaciones", 0),
        "meses_1_estacion":
            dist_fuente.get("1 estación", 0),
        "meses_sin_datos":
            dist_fuente.get("Sin datos", 0)
    }


# ============================================================
# 8. GENERACIÓN TABLA RESUMEN
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
