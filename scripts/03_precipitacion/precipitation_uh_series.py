"""
Script: precipitation_uh_series.py

Descripción general
-------------------
Este script construye la serie mensual representativa de
precipitación observada para cada unidad hidrográfica (UH)
a partir de la integración espacial de estaciones.

La precipitación mensual de la UH se define como:

- Promedio de estaciones cuando existen ≥2 registros válidos
- Valor único cuando solo una estación presenta datos
- NA cuando no existen registros

Entradas
--------
- Serie mensual de precipitación por estación

Salidas
-------
- Serie mensual observada representativa por UH
- Tabla resumen estructural de cobertura

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
# 2. FUNCIÓN CONSTRUCCIÓN SERIE UH
# ============================================================

def construir_uh(df_uh, nombre_uh):

    """
    Construye serie mensual representativa
    mediante agregación espacial de estaciones.
    """

    resultados = []

    for fecha, grupo in df_uh.groupby("fecha_mensual"):

        valores_validos = grupo[
            "Prec_mensual"
        ].dropna()

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

    return df_resultado.sort_values(
        "fecha_mensual"
    )


# ============================================================
# 3. FUNCIÓN RESUMEN DE COBERTURA UH
# ============================================================

def resumen_uh(df_uh):

    """
    Calcula indicadores de disponibilidad
    estructural de la serie UH.
    """

    meses_totales = len(df_uh)

    meses_validos = df_uh[
        "Prec_UH_OBS"
    ].notna().sum()

    meses_na = df_uh[
        "Prec_UH_OBS"
    ].isna().sum()

    porcentaje_cobertura = round(
        (meses_validos / meses_totales) * 100,
        2
    )

    dist_fuente = df_uh["Fuente"].value_counts()

    return {
        "meses_totales": meses_totales,
        "meses_validos": meses_validos,
        "meses_na": meses_na,
        "porcentaje_cobertura": porcentaje_cobertura,
        "meses_promedio_>=2_est":
            dist_fuente.get(
                "Promedio >=2 estaciones", 0
            ),
        "meses_1_estacion":
            dist_fuente.get(
                "1 estación", 0
            ),
        "meses_sin_datos":
            dist_fuente.get(
                "Sin datos", 0
            )
    }
