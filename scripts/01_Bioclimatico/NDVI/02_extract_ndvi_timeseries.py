# =====================================================
# SCRIPT 2
# Extraer serie mensual NDVI desde GEE
# usando Landsat + Sentinel-2
# Exporta CSV originales (sin interpolar)
# =====================================================
import ee
import geemap
import pandas as pd
import os

# =====================================================
# INICIALIZAR EARTH ENGINE
# =====================================================
ee.Initialize(project="ee-cloudatlas96")
print("Conectado a Google Earth Engine")

# =====================================================
# IMPORTAR COLECCIÓN NDVI (SCRIPT 1)
# =====================================================
from Script1_BuildCollection_Landsat_Sentinel_FINAL import ndvi_all
print("Colección NDVI cargada")

# =====================================================
# CREAR CARPETA DE SALIDA
# =====================================================
os.makedirs("outputs/csv", exist_ok=True)

# =====================================================
# CARGAR SHAPEFILES
# =====================================================
roi_matoc = geemap.shp_to_ee("data/matoc/MATOC.shp")
roi_pocco = geemap.shp_to_ee("data/pocco/POCCO.shp")

# =====================================================
# FUNCIÓN PARA EXTRAER SERIE MENSUAL
# =====================================================
def extraer_serie(roi, nombre):

    years = range(2012, 2023)
    registros = []

    for y in years:
        for m in range(1, 13):

            inicio = ee.Date.fromYMD(y, m, 1)
            fin = inicio.advance(1, "month")

            imagen = (
                ndvi_all
                .filterDate(inicio, fin)
                .select("NDVI")
                .mean()
            )

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

    df = pd.DataFrame(
        registros,
        columns=["Year", "Month", "NDVI"]
    )

    ruta = f"outputs/csv/NDVI_{nombre}.csv"
    df.to_csv(ruta, index=False)

    print(f"Serie exportada: {nombre}")
    print(f"Meses vacíos: {df['NDVI'].isna().sum()}")

# =====================================================
# EJECUCIÓN
# =====================================================
extraer_serie(roi_matoc, "MATOC")
extraer_serie(roi_pocco, "POCCO")

print("Series mensuales NDVI extraídas correctamente")