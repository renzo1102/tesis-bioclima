"""
Script: gee_extract_ndvi_series.py

Descripción general
-------------------
Este script extrae series temporales mensuales de NDVI para unidades
hidrográficas (microcuencas) a partir de una colección integrada de
imágenes Landsat y Sentinel-2 previamente generada.

Para cada mes del periodo 2012–2022 se calcula el NDVI promedio espacial
dentro de cada microcuenca y se exporta la serie temporal en formato CSV.

Entradas
--------
- Colección NDVI integrada (Script 1)
- Shapefiles de microcuencas

Salidas
-------
- Archivos CSV con series mensuales de NDVI sin interpolación

Autor: Renzo Mendoza  
Año: 2026
"""

import ee
import geemap
import pandas as pd
import os

# =====================================================
# INICIALIZACIÓN DE GOOGLE EARTH ENGINE
# =====================================================
ee.Initialize(project="rmendozab")
print("Conectado a Google Earth Engine")

# =====================================================
# IMPORTAR COLECCIÓN NDVI (GENERADA EN SCRIPT 1)
# =====================================================
from Script1_BuildCollection_Landsat_Sentinel_FINAL import ndvi_all
print("Colección NDVI cargada correctamente")

# =====================================================
# CREACIÓN DE CARPETA DE SALIDA
# =====================================================
os.makedirs("outputs/csv", exist_ok=True)

# =====================================================
# CARGA DE UNIDADES HIDROGRÁFICAS
# =====================================================
roi_matoc = geemap.shp_to_ee("data/matoc/MATOC.shp")
roi_pocco = geemap.shp_to_ee("data/pocco/POCCO.shp")


# =====================================================
# FUNCIÓN DE EXTRACCIÓN DE SERIE TEMPORAL
# =====================================================
def extraer_serie(roi, nombre):
    """
    Extrae la serie temporal mensual de NDVI promedio para una región dada.

    Para cada mes del periodo 2012–2022:
    - Se filtra la colección NDVI
    - Se calcula el NDVI medio mensual
    - Se obtiene el promedio espacial dentro del ROI
    - Se almacena el resultado en una tabla

    Parámetros
    ----------
    roi : ee.Geometry o ee.FeatureCollection
        Región de interés (microcuenca).

    nombre : str
        Nombre identificador usado en el archivo de salida.

    Retorna
    -------
    None
        Exporta directamente un archivo CSV.
    """

    years = range(2012, 2023)
    registros = []

    for y in years:
        for m in range(1, 13):

            # Definir ventana temporal mensual
            inicio = ee.Date.fromYMD(y, m, 1)
            fin = inicio.advance(1, "month")

            # Calcular NDVI medio mensual
            imagen = (
                ndvi_all
                .filterDate(inicio, fin)
                .select("NDVI")
                .mean()
            )

            # Reducir espacialmente sobre la microcuenca
            stats = imagen.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=30,
                maxPixels=1e13
            )

            valor = stats.getInfo()

            if valor:
                ndvi = valor.get("NDVI")
            else:
                ndvi = None

            registros.append([y, m, ndvi])

    # Construcción de DataFrame
    df = pd.DataFrame(
        registros,
        columns=["Year", "Month", "NDVI"]
    )

    # Exportación a CSV
    ruta = f"outputs/csv/NDVI_{nombre}.csv"
    df.to_csv(ruta, index=False)

    print(f"Serie NDVI exportada: {nombre}")
    print(f"Número de meses sin datos: {df['NDVI'].isna().sum()}")


# =====================================================
# EJECUCIÓN DEL PROCESAMIENTO
# =====================================================
extraer_serie(roi_matoc, "MATOC")
extraer_serie(roi_pocco, "POCCO")

print("Extracción de series NDVI finalizada correctamente")
