"""
Script: ndvi_interpolation.py

Descripción general
-------------------
Este script realiza la interpolación temporal de valores faltantes en las
series mensuales de NDVI para unidades hidrográficas.

Se aplica interpolación lineal en el dominio temporal con el objetivo de
obtener series continuas que permitan análisis posteriores como modelación
hidrológica o evaluación ecohidrológica.

Entradas
--------
- Series mensuales NDVI con datos faltantes

Salidas
-------
- Series NDVI continuas interpoladas en formato CSV

Autor: Renzo Mendoza  
Año: 2026
"""

import pandas as pd
import os

# =====================================================
# CONFIGURACIÓN DE RUTAS
# =====================================================

INPUT_DIR = "outputs/csv"
OUTPUT_DIR = "outputs/csv"

ARCHIVOS = {
    "MATOC": "NDVI_MATOC.csv",
    "POCCO": "NDVI_POCCO.csv"
}

# =====================================================
# FUNCIÓN DE INTERPOLACIÓN TEMPORAL
# =====================================================

def interpolar_ndvi(nombre, archivo):
    """
    Interpola valores faltantes de NDVI mediante interpolación lineal temporal.

    El procedimiento:
    - Construye una variable temporal tipo fecha
    - Ordena cronológicamente la serie
    - Aplica interpolación lineal sobre los valores NDVI
    - Exporta una nueva serie continua

    Parámetros
    ----------
    nombre : str
        Identificador de la microcuenca.

    archivo : str
        Nombre del archivo CSV de entrada.

    Retorna
    -------
    None
        Exporta directamente el archivo interpolado.
    """

    ruta = os.path.join(INPUT_DIR, archivo)
    df = pd.read_csv(ruta)

    # Construcción de variable temporal
    df["Fecha"] = pd.to_datetime(
        df[['Year','Month']].assign(DAY=1)
    )

    df = df.sort_values("Fecha")

    # Conteo de datos faltantes previo
    n_nan_antes = df["NDVI"].isna().sum()

    # Interpolación lineal
    df["NDVI_interp"] = df["NDVI"].interpolate(
        method="linear"
    )

    # Conteo posterior
    n_nan_despues = df["NDVI_interp"].isna().sum()

    # Construcción dataset final
    salida = f"NDVI_{nombre}_interp.csv"

    df_salida = df[["Year", "Month", "NDVI_interp"]].rename(
        columns={"NDVI_interp": "NDVI"}
    )

    df_salida.to_csv(
        os.path.join(OUTPUT_DIR, salida),
        index=False
    )

    print(f"Serie procesada: {nombre}")
    print(f"Valores interpolados: {n_nan_antes - n_nan_despues}")
    print(f"Archivo generado: {salida}\n")


# =====================================================
# EJECUCIÓN DEL PROCESAMIENTO
# =====================================================

for nombre, archivo in ARCHIVOS.items():
    interpolar_ndvi(nombre, archivo)

print("Interpolación temporal NDVI completada correctamente")
