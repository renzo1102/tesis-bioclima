# ============================================================
# SCRIPT — DESCARGA DE PRECIPITACIÓN CHIRPS DESDE GEE
# Generación de series mensuales (2012–2022)
# para unidades hidrográficas y estaciones ANA
# ============================================================

"""
DESCRIPCIÓN GENERAL
------------------------------------------------------------
Este script descarga series de precipitación mensual a partir
del producto satelital CHIRPS (Climate Hazards Group InfraRed
Precipitation with Station data) usando Google Earth Engine.

Se generan series mensuales para:

- Unidades hidrográficas (Matoc y Pocco) → promedio espacial
- Estaciones ANA (ANA 1 y ANA 2) → valores puntuales

El flujo consiste en:

1. Cargar datos diarios CHIRPS
2. Agregar a escala mensual (suma acumulada)
3. Extraer valores promedio por región o punto
4. Exportar resultados como tablas CSV a Google Drive

Este script forma parte de la validación y comparación entre:
- Precipitación observada (ANA)
- Precipitación satelital (CHIRPS)

------------------------------------------------------------
OUTPUTS GENERADOS (en Google Drive):

- CHIRPS_MATOC_2012_2022.csv
- CHIRPS_POCCO_2012_2022.csv
- CHIRPS_ANA1_2012_2022.csv
- CHIRPS_ANA2_2012_2022.csv

Cada archivo contiene:
- Fecha (YYYY-MM)
- Precipitación mensual (mm)

------------------------------------------------------------
REQUISITOS:

- Cuenta activa en Google Earth Engine
- Assets cargados en GEE:
    MATOC_GEE
    POCCO_GEE

------------------------------------------------------------
NOTA METODOLÓGICA:

CHIRPS tiene resolución espacial de ~5 km, por lo que:
- Es adecuado para análisis regional
- Puede presentar sesgos en zonas montañosas (Andes)

"""

import ee

# ===============================
# 1. INICIALIZAR GEE
# ===============================
# Se establece conexión con Google Earth Engine
ee.Initialize(project='ee-cloudatlas96')


# ===============================
# 2. CARGAR UH (ASSETS)
# ===============================
# Se cargan las unidades hidrográficas previamente
# subidas como assets en GEE (FeatureCollection)

matoc = ee.FeatureCollection("projects/ee-cloudatlas96/assets/MATOC_GEE")
pocco = ee.FeatureCollection("projects/ee-cloudatlas96/assets/POCCO_GEE")


# ===============================
# 3. CREAR ESTACIONES ANA (PUNTOS)
# ===============================
# Definición manual de coordenadas de estaciones
# Estas representan observaciones puntuales

ana1 = ee.Geometry.Point([-77.32, -9.60])
ana2 = ee.Geometry.Point([-77.27, -9.66])


# ===============================
# 4. CARGAR CHIRPS DIARIO
# ===============================
# Se carga la colección diaria de CHIRPS
# y se filtra al periodo de estudio (2012–2022)

chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
    .filterDate("2012-01-01", "2022-12-31")


# ===============================
# 5. GENERAR CHIRPS MENSUAL
# ===============================
"""
Se transforma la colección diaria en mensual mediante:

- Iteración por años (2012–2022)
- Iteración por meses (1–12)
- Suma de precipitación diaria → acumulado mensual

Cada imagen mensual contiene:
- Banda: precipitation (mm)
- Propiedades:
    year
    month
    system:time_start
"""

def monthly_sum(year):

    months = ee.List.sequence(1, 12)

    def by_month(m):

        start = ee.Date.fromYMD(year, m, 1)
        end = start.advance(1, 'month')

        # Suma de precipitación diaria
        monthly = chirps.filterDate(start, end).sum()

        # Se añaden metadatos temporales
        return monthly.set({
            'year': year,
            'month': m,
            'system:time_start': start.millis()
        })

    return months.map(by_month)


# Lista de años
years = ee.List.sequence(2012, 2022)

# Construcción de colección mensual completa
monthly_images = ee.ImageCollection(
    years.map(monthly_sum).flatten()
)


# ===============================
# 6. FUNCIÓN EXTRACCIÓN
# ===============================
"""
Esta función extrae la precipitación mensual desde cada imagen
para una región específica.

Parámetros:
- region: geometría (polígono o punto)
- region_type: "polygon" o "point"
- name: nombre de la variable en salida

Proceso:
- Aplica reduceRegion sobre cada imagen
- Calcula promedio espacial (para polígonos)
- Devuelve FeatureCollection con:
    fecha (YYYY-MM)
    valor de precipitación
"""

def extract_series(region, region_type, name):

    def extract(image):

        if region_type == "polygon":
            value = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region.geometry(),
                scale=5000,        # resolución CHIRPS (~5 km)
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


# ===============================
# 7. EXTRAER SERIES
# ===============================
# Se generan series para:
# - UH (promedio espacial)
# - Estaciones ANA (valor puntual)

matoc_series = extract_series(matoc, "polygon", "CHIRPS")
pocco_series = extract_series(pocco, "polygon", "CHIRPS")
ana1_series = extract_series(ana1, "point", "CHIRPS")
ana2_series = extract_series(ana2, "point", "CHIRPS")


# ===============================
# 8. EXPORTAR A DRIVE
# ===============================
"""
Se exportan las series como tablas CSV a Google Drive.

Cada exportación crea una tarea en GEE (Tasks),
que debe ser monitoreada o ejecutada automáticamente.

Formato de salida:
- CSV
- Columnas:
    date
    CHIRPS
"""

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


# ===============================
# MENSAJE FINAL
# ===============================

print("Exportaciones iniciadas.")
print("Revisa Tasks en GEE Code Editor.")
