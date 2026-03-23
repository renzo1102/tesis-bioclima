# ============================================================
# SCRIPT 4 – EXPORTAR RASTERS A GOOGLE DRIVE
# Método robusto oficial
# ============================================================

# ============================================================
# DESCRIPCIÓN GENERAL
# ============================================================
# Este script genera y exporta productos raster NDVI desde
# Google Earth Engine hacia Google Drive.
#
# Productos generados por cada cuenca:
# - NDVI promedio multianual (2012–2022)
# - NDVI promedio del año inicial (2012)
# - NDVI promedio del año final (2022)
# - Tendencia temporal (pendiente) del NDVI
#
# Los resultados son exportados como imágenes GeoTIFF,
# listas para análisis espacial en GIS (ArcGIS, QGIS, etc.).
#
# Este script constituye la fase de generación de productos
# espaciales del análisis ecohidrológico.

import ee
import geemap

# ============================================================
# INICIALIZACIÓN DE GOOGLE EARTH ENGINE
# ============================================================
# Se establece la conexión con GEE utilizando el proyecto activo.
# Requiere autenticación previa.

ee.Initialize(project="ee-cloudatlas96")
print("Conectado a Google Earth Engine")

# ============================================================
# IMPORTAR COLECCIÓN NDVI (SCRIPT 1)
# ============================================================
# Se importa la colección multisensor con banda NDVI.

from Script1_BuildCollection_Landsat_Sentinel_FINAL import ndvi_all
print("Colección NDVI cargada")

# ============================================================
# CARGA DE REGIONES DE INTERÉS (CUENCAS)
# ============================================================
# Se cargan los shapefiles y se convierten a objetos GEE.

roi_matoc = geemap.shp_to_ee("data/matoc/MATOC.shp")
roi_pocco = geemap.shp_to_ee("data/pocco/POCCO.shp")

# ============================================================
# FUNCIÓN: crear_imagenes
# ============================================================
# Genera productos raster NDVI para una región específica.
#
# Parámetro:
# - roi: geometría de la cuenca (ee.FeatureCollection)
#
# Retorna:
# - ndvi_mean: promedio NDVI 2012–2022
# - ndvi_2012: promedio NDVI año 2012
# - ndvi_2022: promedio NDVI año 2022
# - trend: tendencia temporal (pendiente NDVI)
#
# Descripción del proceso:
# 1. Calcula promedio multianual
# 2. Calcula promedios anuales extremos
# 3. Construye colección anual
# 4. Añade variable temporal (t)
# 5. Aplica regresión lineal pixel a pixel
# 6. Extrae la pendiente (trend)

def crear_imagenes(roi):

    # --------------------------------------------------------
    # NDVI promedio multianual
    # --------------------------------------------------------
    # Promedio de todas las imágenes NDVI del periodo completo

    ndvi_mean = ndvi_all.select("NDVI").mean()

    # --------------------------------------------------------
    # NDVI año inicial (2012)
    # --------------------------------------------------------

    ndvi_2012 = (
        ndvi_all
        .filterDate("2012-01-01", "2012-12-31")
        .select("NDVI")
        .mean()
    )

    # --------------------------------------------------------
    # NDVI año final (2022)
    # --------------------------------------------------------

    ndvi_2022 = (
        ndvi_all
        .filterDate("2022-01-01", "2022-12-31")
        .select("NDVI")
        .mean()
    )

    # --------------------------------------------------------
    # CREACIÓN DE SERIE ANUAL
    # --------------------------------------------------------
    # Se genera una lista de años

    years = ee.List.sequence(2012, 2022)

    # --------------------------------------------------------
    # FUNCIÓN INTERNA: yearly_mean
    # --------------------------------------------------------
    # Calcula el promedio NDVI para cada año.
    #
    # Entrada:
    # - y: año (ee.Number)
    #
    # Salida:
    # - Imagen con NDVI promedio anual y atributo "year"

    def yearly_mean(y):
        y = ee.Number(y)
        img = (
            ndvi_all
            .filter(ee.Filter.calendarRange(y, y, "year"))
            .select("NDVI")
            .mean()
            .set("year", y)
        )
        return img

    # Se aplica la función a todos los años
    yearly = ee.ImageCollection(years.map(yearly_mean))

    # --------------------------------------------------------
    # FUNCIÓN INTERNA: add_time
    # --------------------------------------------------------
    # Añade una banda temporal "t" a cada imagen.
    #
    # Esta banda representa el tiempo (año) y es necesaria
    # para realizar regresión lineal pixel a pixel.

    def add_time(img):
        year = ee.Number(img.get("year"))
        return img.addBands(
            ee.Image.constant(year).rename("t").toFloat()
        )

    # Se añade la dimensión temporal
    yearly = yearly.map(add_time)

    # --------------------------------------------------------
    # CÁLCULO DE TENDENCIA (REGRESIÓN LINEAL)
    # --------------------------------------------------------
    # Se aplica regresión lineal:
    # NDVI = a + b*t
    #
    # Donde:
    # - b (scale) = pendiente → tendencia del NDVI

    trend = (
        yearly.select(["t", "NDVI"])
        .reduce(ee.Reducer.linearFit())
        .select("scale")
        .rename("NDVI_trend")
    )

    return ndvi_mean, ndvi_2012, ndvi_2022, trend


# ============================================================
# FUNCIÓN: exportar_drive
# ============================================================
# Envía tareas de exportación a Google Drive.
#
# Parámetros:
# - nombre: identificador de la cuenca
# - roi: geometría de la cuenca
#
# Proceso:
# 1. Genera imágenes con crear_imagenes
# 2. Define región de exportación
# 3. Exporta cada raster como tarea independiente
#
# Salida:
# - Archivos GeoTIFF en Google Drive (carpeta NDVI_RASTERS)

def exportar_drive(nombre, roi):

    mean, y2012, y2022, trend = crear_imagenes(roi)

    region = roi.geometry()

    # --------------------------------------------------------
    # EXPORTACIÓN NDVI PROMEDIO
    # --------------------------------------------------------

    ee.batch.Export.image.toDrive(
        image=mean.clip(region),
        description=f"{nombre}_NDVI_mean",
        folder="NDVI_RASTERS",
        fileNamePrefix=f"{nombre}_NDVI_mean_2012_2022",
        region=region,
        scale=30,
        maxPixels=1e13
    ).start()

    # --------------------------------------------------------
    # EXPORTACIÓN NDVI 2012
    # --------------------------------------------------------

    ee.batch.Export.image.toDrive(
        image=y2012.clip(region),
        description=f"{nombre}_NDVI_2012",
        folder="NDVI_RASTERS",
        fileNamePrefix=f"{nombre}_NDVI_2012",
        region=region,
        scale=30,
        maxPixels=1e13
    ).start()

    # --------------------------------------------------------
    # EXPORTACIÓN NDVI 2022
    # --------------------------------------------------------

    ee.batch.Export.image.toDrive(
        image=y2022.clip(region),
        description=f"{nombre}_NDVI_2022",
        folder="NDVI_RASTERS",
        fileNamePrefix=f"{nombre}_NDVI_2022",
        region=region,
        scale=30,
        maxPixels=1e13
    ).start()

    # --------------------------------------------------------
    # EXPORTACIÓN TENDENCIA
    # --------------------------------------------------------

    ee.batch.Export.image.toDrive(
        image=trend.clip(region),
        description=f"{nombre}_NDVI_trend",
        folder="NDVI_RASTERS",
        fileNamePrefix=f"{nombre}_NDVI_trend_2012_2022",
        region=region,
        scale=30,
        maxPixels=1e13
    ).start()

    print(f"Tareas enviadas a Drive: {nombre}")


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================
# Se ejecuta la exportación para ambas cuencas.

exportar_drive("MATOC", roi_matoc)
exportar_drive("POCCO", roi_pocco)

print("Revisa Google Drive > carpeta NDVI_RASTERS")


# ============================================================
# SALIDAS DEL SCRIPT
# ============================================================
# En Google Drive (carpeta NDVI_RASTERS):
#
# Por cada cuenca:
# - NDVI_mean_2012_2022.tif
# - NDVI_2012.tif
# - NDVI_2022.tif
# - NDVI_trend_2012_2022.tif
#
# Estos productos permiten:
# - Análisis espacial de vegetación
# - Evaluación de cambios temporales
# - Integración con SIG
#
# ============================================================
# CONSIDERACIONES TÉCNICAS
# ============================================================
# - Resolución espacial: 30 m
# - Tendencia calculada pixel a pixel
# - Exportación asincrónica (requiere monitoreo en GEE Tasks)
# - Puede tardar dependiendo del tamaño de la cuenca
#
# Este script representa la fase de generación de outputs espaciales
# del análisis ecohidrológico.
# ============================================================
