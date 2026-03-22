import ee

# ===============================
# 1. INICIALIZAR GEE
# ===============================
ee.Initialize(project='ee-cloudatlas96')
# ===============================
# 2. CARGAR UH (ASSETS)
# ===============================
matoc = ee.FeatureCollection("projects/ee-cloudatlas96/assets/MATOC_GEE")
pocco = ee.FeatureCollection("projects/ee-cloudatlas96/assets/POCCO_GEE")

# ===============================
# 3. CREAR ESTACIONES ANA (PUNTOS)
# ===============================
ana1 = ee.Geometry.Point([-77.32, -9.60])
ana2 = ee.Geometry.Point([-77.27, -9.66])

# ===============================
# 4. CARGAR CHIRPS DIARIO
# ===============================
chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
    .filterDate("2012-01-01", "2022-12-31")

# ===============================
# 5. GENERAR CHIRPS MENSUAL
# ===============================
def monthly_sum(year):
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

# ===============================
# 6. FUNCIÓN EXTRACCIÓN
# ===============================
def extract_series(region, region_type, name):

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

# ===============================
# 7. EXTRAER SERIES
# ===============================
matoc_series = extract_series(matoc, "polygon", "CHIRPS")
pocco_series = extract_series(pocco, "polygon", "CHIRPS")
ana1_series = extract_series(ana1, "point", "CHIRPS")
ana2_series = extract_series(ana2, "point", "CHIRPS")

# ===============================
# 8. EXPORTAR A DRIVE
# ===============================
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

print("Exportaciones iniciadas.")
print("Revisa Tasks en GEE Code Editor.")