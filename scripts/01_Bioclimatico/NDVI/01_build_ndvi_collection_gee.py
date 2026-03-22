# =====================================================
# SCRIPT 1
# Construir colección NDVI combinada
# Landsat 7–8–9 + Sentinel-2 Harmonized
# Periodo: 2012–2022
# =====================================================
import ee

# =====================================================
# INICIALIZAR EARTH ENGINE
# =====================================================
ee.Initialize(project="ee-cloudatlas96")
print("Conectado a Google Earth Engine")


# =====================================================
# ---------------- LANDSAT ----------------------------
# =====================================================

def mask_landsat(image):
    qa = image.select("QA_PIXEL")

    mask = (
        qa.bitwiseAnd(1 << 3).eq(0)  # nubes
        .And(qa.bitwiseAnd(1 << 4).eq(0))  # sombra de nube
    )

    return image.updateMask(mask)


def add_ndvi_l89(img):
    img = mask_landsat(img)
    ndvi = img.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")
    return img.addBands(ndvi)


def add_ndvi_l7(img):
    img = mask_landsat(img)
    ndvi = img.normalizedDifference(["SR_B4", "SR_B3"]).rename("NDVI")
    return img.addBands(ndvi)


# =====================================================
# ---------------- SENTINEL-2 --------------------------
# =====================================================

def mask_sentinel_scl(img):

    scl = img.select("SCL")

    mask = (
        scl.eq(4)   # vegetación
        .Or(scl.eq(5))  # suelo desnudo
        .Or(scl.eq(6))  # agua
    )

    return img.updateMask(mask)


def add_ndvi_s2(img):

    img = mask_sentinel_scl(img)

    ndvi = img.normalizedDifference(["B8", "B4"]).rename("NDVI")

    return img.addBands(ndvi)


# =====================================================
# COLECCIONES (2012–2022)
# =====================================================

L7 = (
    ee.ImageCollection("LANDSAT/LE07/C02/T1_L2")
    .filterDate("2012-01-01", "2012-12-31")
    .map(add_ndvi_l7)
)

L8 = (
    ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
    .filterDate("2013-01-01", "2020-12-31")
    .map(add_ndvi_l89)
)

L9 = (
    ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
    .filterDate("2021-01-01", "2022-12-31")
    .map(add_ndvi_l89)
)

S2 = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterDate("2017-01-01", "2022-12-31")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40))
    .map(add_ndvi_s2)
)

# =====================================================
# COLECCIÓN FINAL
# =====================================================

ndvi_all = L7.merge(L8).merge(L9).merge(S2)

print("Colección Landsat + Sentinel-2 final lista")