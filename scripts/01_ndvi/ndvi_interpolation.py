"""
Script: ndvi_interpolation.py
Descripción:
Interpola valores faltantes de NDVI
Entradas:
NDVI mensual incompleto
Salidas:
NDVI continuo

Autor: Renzo Mendoza
Año: 2026
"""
# =====================================================
# SCRIPT 4
# interpolación de NDVI
# =====================================================

import pandas as pd
import os

# ===============================
# CONFIGURACIÓN
# ===============================

INPUT_DIR = "outputs/csv"
OUTPUT_DIR = "outputs/csv"

ARCHIVOS = {
    "MATOC": "NDVI_MATOC.csv",
    "POCCO": "NDVI_POCCO.csv"
}

# ===============================
# FUNCIÓN DE INTERPOLACIÓN
# ===============================

def interpolar_ndvi(nombre, archivo):

    ruta = os.path.join(INPUT_DIR, archivo)
    df = pd.read_csv(ruta)

    # Crear fecha
    df["Fecha"] = pd.to_datetime(
        df[['Year','Month']].assign(DAY=1)
    )

    df = df.sort_values("Fecha")

    # Conteo previo
    n_nan_antes = df["NDVI"].isna().sum()

    # Interpolación lineal temporal
    df["NDVI_interp"] = df["NDVI"].interpolate(
        method="linear"
    )

    n_nan_despues = df["NDVI_interp"].isna().sum()

    # Guardar nuevo archivo
    salida = f"NDVI_{nombre}_interp.csv"
    df_salida = df[["Year","Month","NDVI_interp"]].rename(
        columns={"NDVI_interp":"NDVI"}
    )

    df_salida.to_csv(
        os.path.join(OUTPUT_DIR, salida),
        index=False
    )

    print(f"Serie {nombre}")
    print(f"  Valores interpolados: {n_nan_antes - n_nan_despues}")
    print(f"  Archivo generado: {salida}\n")


# ===============================
# EJECUCIÓN
# ===============================

for nombre, archivo in ARCHIVOS.items():
    interpolar_ndvi(nombre, archivo)

print("Interpolación completada correctamente")
