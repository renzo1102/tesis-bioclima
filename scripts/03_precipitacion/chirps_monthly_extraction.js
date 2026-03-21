"""
Script: chirps_monthly_extraction_gee.py

Descripción general
-------------------
Este script genera series mensuales de precipitación del producto satelital
CHIRPS mediante procesamiento en Google Earth Engine.

El procedimiento incluye:
- Agregación temporal de precipitación diaria a mensual
- Extracción espacial sobre unidades hidrográficas (polígonos)
- Extracción puntual sobre estaciones ANA
- Exportación de series temporales a Google Drive

Entradas
--------
- ImageCollection CHIRPS diaria
- Geometrías de unidades hidrográficas
- Coordenadas de estaciones

Salidas
-------
- Series mensuales CHIRPS en formato CSV

Autor: Renzo Mendoza  
Año: 2026
"""

import ee

# ============================================================
# 1. INICIALIZAR GOOGLE EARTH ENGINE
# ============================================================

ee.Initialize(project='rmendozab')

"""
Inicializa la sesión GEE permitiendo acceso a datasets remotos
y assets propios del usuario.
"""


# ============================================================
# 2. CARGAR UNIDADES HIDROGRÁFICAS
# ============================================================

matoc = ee.FeatureCollection(
    "projects/rmendozab/assets/MATOC_GEE"
)

pocco = ee.FeatureCollection(
    "projects/rmendozab/assets/POCCO_GEE"
)

"""
Estas colecciones representan las áreas de análisis espacial.
"""


# ============================================================
# 3. DEFINIR ESTACIONES ANA
# ============================================================

ana1 = ee.Geometry.Point([-77.32, -9.60])
ana2 = ee.Geometry.Point([-77.27, -9.66])

"""
Geometrías puntuales para comparación satélite vs observación.
"""


# ============================================================
# 4. CARGAR CHIRPS DIARIO
# ============================================================

chirps = (
    ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
    .filterDate("2012-01-01", "2022-12-31")
)

"""
Se filtra el periodo de estudio hidroclimático.
"""


# ============================================================
# FUNCIÓN: GENERAR PRECIPITACIÓN MENSUAL
# ============================================================

def monthly_sum(year):
    """
    Agrega precipitación diaria en totales mensuales.

    Retorna lista de imágenes mensuales.
    """

    months = ee.List.sequence(1, 12)

    def by_month(m):

        start = ee.Date.fromYMD(year, m, 1)
        end = start.advance(1, 'month')

        monthly = chirps.filterDate(start, end).sum()

        return monthly.set({
            'year': year,
            'month': m,
            'system:time_start': start.millis()
        })

    return months.map(by_month)


years = ee.List.sequence(2012, 2022)

monthly_images = ee.ImageCollection(
    years.map(monthly_sum).flatten()
)

"""
Este bloque construye una ImageCollection mensual completa.
"""


# ============================================================
# FUNCIÓN: EXTRAER SERIE TEMPORAL
# ============================================================

def extract_series(region, region_type, name):
    """
    Extrae precipitación media mensual desde CHIRPS.

    region_type:
    - polygon → promedio espacial UH
    - point → valor puntual estación
    """

    def extract(image):

        if region_type == "polygon":

            value = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region.geometry(),
                scale=5000,
                maxPixels=1e13
            )

        else:

            value = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=5000
            )

        return ee.Feature(None, {
            'date': image.date().format("YYYY-MM"),
            name: value.get('precipitation')
        })

    return monthly_images.map(extract)


# ============================================================
# 7. GENERAR SERIES
# ============================================================

matoc_series = extract_series(matoc, "polygon", "CHIRPS")
pocco_series = extract_series(pocco, "polygon", "CHIRPS")

ana1_series = extract_series(ana1, "point", "CHIRPS")
ana2_series = extract_series(ana2, "point", "CHIRPS")


# ============================================================
# 8. EXPORTACIÓN A GOOGLE DRIVE
# ============================================================

exports = [
    ("CHIRPS_MATOC_2012_2022", matoc_series),
    ("CHIRPS_POCCO_2012_2022", pocco_series),
    ("CHIRPS_ANA1_2012_2022", ana1_series),
    ("CHIRPS_ANA2_2012_2022", ana2_series),
]

for name, collection in exports:

    task = ee.batch.Export.table.toDrive(
        collection=collection,
        description=name,
        fileFormat="CSV"
    )

    task.start()

print("Exportaciones iniciadas correctamente.")
