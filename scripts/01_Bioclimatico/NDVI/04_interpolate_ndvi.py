# =====================================================
# SCRIPT 4
# Interpolación de series temporales NDVI
# Relleno de valores faltantes mediante interpolación lineal
# =====================================================

# =====================================================
# DESCRIPCIÓN GENERAL
# =====================================================
# Este script realiza la interpolación de valores faltantes (NaN)
# en las series mensuales de NDVI generadas previamente (Script 2).
#
# Se aplica interpolación lineal para completar vacíos temporales,
# generando una serie continua necesaria para:
# - Análisis estadísticos
# - Modelamiento hidrológico
# - Integración con otras variables climáticas
#
# Salidas:
# - outputs/csv/NDVI_MATOC_interpolado.csv
# - outputs/csv/NDVI_POCCO_interpolado.csv

import pandas as pd
import os

# =====================================================
# CONFIGURACIÓN
# =====================================================
# Definición de rutas relativas y archivos de entrada

INPUT_DIR = "outputs/csv"
OUTPUT_DIR = "outputs/csv"

ARCHIVOS = {
    "MATOC": "NDVI_MATOC.csv",
    "POCCO": "NDVI_POCCO.csv"
}

# =====================================================
# FUNCIÓN: interpolar_ndvi
# =====================================================
# Realiza interpolación lineal sobre la serie NDVI.
#
# Parámetros:
# - nombre: identificador de la cuenca
# - archivo: nombre del archivo CSV de entrada
#
# Proceso:
# 1. Lee la serie original
# 2. Construye variable temporal (Fecha)
# 3. Ordena cronológicamente
# 4. Cuenta valores faltantes
# 5. Aplica interpolación lineal
# 6. Genera nueva serie sin vacíos (en lo posible)
# 7. Exporta CSV interpolado
#
# Salida:
# - Archivo CSV con NDVI interpolado

def interpolar_ndvi(nombre, archivo):

    # Lectura de datos
    ruta = os.path.join(INPUT_DIR, archivo)
    df = pd.read_csv(ruta)

    # Construcción de variable fecha (primer día del mes)
    df["Fecha"] = pd.to_datetime(
        df[['Year','Month']].assign(DAY=1)
    )

    # Orden temporal
    df = df.sort_values("Fecha")

    # Conteo de valores faltantes antes de interpolar
    n_nan_antes = df["NDVI"].isna().sum()

    # Interpolación lineal
    # Método:
    # - Conecta puntos válidos con una recta
    # - Estima valores intermedios faltantes
    df["NDVI_interp"] = df["NDVI"].interpolate(
        method="linear"
    )

    # Conteo posterior
    n_nan_despues = df["NDVI_interp"].isna().sum()

    # Preparación del archivo de salida
    salida = f"NDVI_{nombre}_interpolado.csv"

    df_salida = df[["Year","Month","NDVI_interp"]].rename(
        columns={"NDVI_interp":"NDVI"}
    )

    # Exportación
    df_salida.to_csv(
        os.path.join(OUTPUT_DIR, salida),
        index=False
    )

    # Reporte en consola
    print(f"Serie {nombre}")
    print(f"  Valores interpolados: {n_nan_antes - n_nan_despues}")
    print(f"  Archivo generado: {salida}\n")


# =====================================================
# EJECUCIÓN PRINCIPAL
# =====================================================
# Se aplica la interpolación a cada cuenca definida

for nombre, archivo in ARCHIVOS.items():
    interpolar_ndvi(nombre, archivo)

print("Interpolación completada correctamente")

# =====================================================
# SALIDAS DEL SCRIPT
# =====================================================
# Archivos generados:
#
# - outputs/csv/NDVI_MATOC_interpolado.csv
# - outputs/csv/NDVI_POCCO_interpolado.csv
#
# Estructura:
# Year | Month | NDVI
#
# Donde NDVI corresponde a la serie interpolada.

# =====================================================
# CONSIDERACIONES TÉCNICAS
# =====================================================
# - La interpolación es lineal en el tiempo
# - No extrapola valores fuera del rango de datos existentes
# - Valores iniciales o finales pueden permanecer como NaN
#   si no hay datos vecinos
#
# Limitaciones:
# - No captura variabilidad no lineal
# - Puede suavizar extremos reales
#
# Este script es clave para preparar las series NDVI
# para análisis estadísticos y modelamiento posterior.
# =====================================================
