# ============================================================
# SCRIPT 4 – EXPORTAR RASTERS A GOOGLE DRIVE
# Método robusto oficial
# ============================================================

import ee
import geemap

ee.Initialize(project="ee-cloudatlas96")
print("Conectado a Google Earth Engine")

from Script1_BuildCollection_Landsat_Sentinel_FINAL import ndvi_all
print("Colección NDVI cargada")

roi_matoc = geemap.shp_to_ee("data/matoc/MATOC.shp")
roi_pocco = geemap.shp_to_ee("data/pocco/POCCO.shp")

# ============================================================
# FUNCIÓN CREAR IMÁGENES
# ============================================================

def crear_imagenes(roi):

    ndvi_mean = ndvi_all.select("NDVI").mean()

    ndvi_2012 = (
        ndvi_all
        .filterDate("2012-01-01", "2012-12-31")
        .select("NDVI")
        .mean()
    )

    ndvi_2022 = (
        ndvi_all
        .filterDate("2022-01-01", "2022-12-31")
        .select("NDVI")
        .mean()
    )

    years = ee.List.sequence(2012, 2022)

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

    yearly = ee.ImageCollection(years.map(yearly_mean))

    def add_time(img):
        year = ee.Number(img.get("year"))
        return img.addBands(
            ee.Image.constant(year).rename("t").toFloat()
        )

    yearly = yearly.map(add_time)

    trend = (
        yearly.select(["t", "NDVI"])
        .reduce(ee.Reducer.linearFit())
        .select("scale")
        .rename("NDVI_trend")
    )

    return ndvi_mean, ndvi_2012, ndvi_2022, trend


# ============================================================
# EXPORTAR A DRIVE
# ============================================================

def exportar_drive(nombre, roi):

    mean, y2012, y2022, trend = crear_imagenes(roi)

    region = roi.geometry()

    ee.batch.Export.image.toDrive(
        image=mean.clip(region),
        description=f"{nombre}_NDVI_mean",
        folder="NDVI_RASTERS",
        fileNamePrefix=f"{nombre}_NDVI_mean_2012_2022",
        region=region,
        scale=30,
        maxPixels=1e13
    ).start()

    ee.batch.Export.image.toDrive(
        image=y2012.clip(region),
        description=f"{nombre}_NDVI_2012",
        folder="NDVI_RASTERS",
        fileNamePrefix=f"{nombre}_NDVI_2012",
        region=region,
        scale=30,
        maxPixels=1e13
    ).start()

    ee.batch.Export.image.toDrive(
        image=y2022.clip(region),
        description=f"{nombre}_NDVI_2022",
        folder="NDVI_RASTERS",
        fileNamePrefix=f"{nombre}_NDVI_2022",
        region=region,
        scale=30,
        maxPixels=1e13
    ).start()

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
# EJECUCIÓN
# ============================================================

exportar_drive("MATOC", roi_matoc)
exportar_drive("POCCO", roi_pocco)

print("Revisa Google Drive > carpeta NDVI_RASTERS")