# =====================================================
# SCRIPT 2
# Extraer serie mensual NDVI desde GEE
# usando Landsat + Sentinel-2
# Exporta CSV originales (sin interpolar)
# =====================================================

# =====================================================
# DESCRIPCIÓN GENERAL
# =====================================================
# Este script extrae series temporales mensuales de NDVI
# a partir de la colección multisensor construida en el Script 1.
#
# Se calcula el NDVI promedio mensual dentro de cada unidad
# hidrográfica (Matoc y Pocco) usando Google Earth Engine.
#
# Características:
# - No se realiza interpolación
# - Se conservan valores faltantes (None)
# - Se genera un archivo CSV por cuenca
#
# Salidas:
# - outputs/csv/NDVI_MATOC.csv
# - outputs/csv/NDVI_POCCO.csv

import ee
import geemap
import pandas as pd
import os

# =====================================================
# INICIALIZAR EARTH ENGINE
# =====================================================
# Se establece la conexión con Google Earth Engine.
# Requiere autenticación previa.

ee.Initialize(project="ee-cloudatlas96")
print("Conectado a Google Earth Engine")

# =====================================================
# IMPORTAR COLECCIÓN NDVI (SCRIPT 1)
# =====================================================
# Se importa la colección generada previamente.
# Esta colección contiene imágenes con la banda "NDVI".

from Script1_BuildCollection_Landsat_Sentinel_FINAL import ndvi_all
print("Colección NDVI cargada")

# =====================================================
# CREAR CARPETA DE SALIDA
# =====================================================
# Se crea la carpeta donde se almacenarán los CSV.
# Uso de ruta relativa para asegurar portabilidad.

os.makedirs("outputs/csv", exist_ok=True)

# =====================================================
# CARGAR SHAPEFILES
# =====================================================
# Se cargan los límites espaciales de las cuencas.
# geemap convierte shapefiles locales a objetos de GEE.

roi_matoc = geemap.shp_to_ee("data/matoc/MATOC.shp")
roi_pocco = geemap.shp_to_ee("data/pocco/POCCO.shp")

# =====================================================
# FUNCIÓN: extraer_serie
# =====================================================
# Extrae la serie temporal mensual de NDVI para una región.
#
# Parámetros:
# - roi: geometría en GEE
# - nombre: identificador de la cuenca
#
# Proceso:
# 1. Itera por años (2012–2022) y meses (1–12)
# 2. Filtra la colección NDVI por mes
# 3. Calcula el promedio mensual (mean)
# 4. Reduce espacialmente (mean sobre la cuenca)
# 5. Guarda resultados en lista
# 6. Convierte a DataFrame
# 7. Exporta CSV
#
# Salida:
# - Archivo CSV con columnas:
#   Year, Month, NDVI

def extraer_serie(roi, nombre):

    years = range(2012, 2023)
    registros = []

    for y in years:
        for m in range(1, 13):

            # Definición del intervalo temporal mensual
            inicio = ee.Date.fromYMD(y, m, 1)
            fin = inicio.advance(1, "month")

            # Filtrado de la colección y cálculo de promedio mensual
            imagen = (
                ndvi_all
                .filterDate(inicio, fin)
                .select("NDVI")
                .mean()
            )

            # Reducción espacial sobre la cuenca
            stats = imagen.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=30,
                maxPixels=1e13
            )

            # Conversión a diccionario Python
            valor = stats.getInfo()

            # Manejo de valores nulos
            if valor:
                ndvi = valor.get("NDVI")
            else:
                ndvi = None

            # Registro mensual
            registros.append([y, m, ndvi])

    # Conversión a DataFrame
    df = pd.DataFrame(
        registros,
        columns=["Year", "Month", "NDVI"]
    )

    # Exportación a CSV
    ruta = f"outputs/csv/NDVI_{nombre}.csv"
    df.to_csv(ruta, index=False)

    print(f"Serie exportada: {nombre}")
    print(f"Meses vacíos: {df['NDVI'].isna().sum()}")

# =====================================================
# EJECUCIÓN PRINCIPAL
# =====================================================
# Se ejecuta la función para cada cuenca.

extraer_serie(roi_matoc, "MATOC")
extraer_serie(roi_pocco, "POCCO")

print("Series mensuales NDVI extraídas correctamente")

# =====================================================
# SALIDA DEL SCRIPT
# =====================================================
# Archivos generados:
#
# - outputs/csv/NDVI_MATOC.csv
# - outputs/csv/NDVI_POCCO.csv
#
# Estructura:
# Year | Month | NDVI
#
# Los valores NDVI pueden contener:
# - Valores reales (promedio mensual)
# - None (meses sin datos válidos)

# =====================================================
# CONSIDERACIONES TÉCNICAS
# =====================================================
# - La escala espacial es de 30 m (resolución Landsat)
# - Sentinel-2 se adapta a esta escala en la reducción
# - El uso de .mean() genera un compuesto mensual
# - reduceRegion calcula el promedio espacial
#
# Limitaciones:
# - Meses con alta nubosidad pueden generar valores nulos
# - No se aplica interpolación (se mantiene serie original)
#
# Este script genera la base de datos NDVI mensual
# utilizada en análisis estadísticos posteriores.
# =====================================================
