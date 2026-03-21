"""
Script: gee_build_ndvi_collection.py

Descripción general
-------------------
Este script construye una colección temporal de NDVI en Google Earth Engine
integrando imágenes Landsat 7, Landsat 8, Landsat 9 y Sentinel-2 Harmonized.

Se aplican máscaras de calidad para eliminar nubes y sombras de nubes, y
posteriormente se calcula el índice NDVI para cada sensor.

Periodo de análisis: 2012–2022.

Entradas
--------
- Colecciones satelitales Landsat Collection 2 Level-2
- Colección Sentinel-2 Surface Reflectance Harmonized

Salidas
-------
- Colección integrada de imágenes con banda NDVI

Autor: Renzo Mendoza  
Año: 2026
"""
import ee

# =====================================================
# INICIALIZACIÓN DE GOOGLE EARTH ENGINE
# =====================================================
ee.Initialize(project="rmendozab")
print("Conectado a Google Earth Engine")


# =====================================================
# FUNCIONES PARA LANDSAT
# =====================================================

def mask_landsat(image):
    """
    Aplica una máscara de calidad a imágenes Landsat utilizando la banda QA_PIXEL.

    Se eliminan píxeles afectados por:
    - Nubes
    - Sombras de nube

    Parámetros
    ----------
    image : ee.Image
        Imagen Landsat Collection 2 Level-2.

    Retorna
    -------
    ee.Image
        Imagen con píxeles válidos únicamente.
    """
    qa = image.select("QA_PIXEL")

    mask = (
        qa.bitwiseAnd(1 << 3).eq(0)  # nube
        .And(qa.bitwiseAnd(1 << 4).eq(0))  # sombra de nube
    )

    return image.updateMask(mask)


def add_ndvi_l89(img):
    """
    Calcula NDVI para imágenes Landsat 8 y Landsat 9.

    Bandas utilizadas:
    - NIR: SR_B5
    - Red: SR_B4

    Parámetros
    ----------
    img : ee.Image

    Retorna
    -------
    ee.Image
        Imagen con banda adicional NDVI.
    """
    img = mask_landsat(img)

    ndvi = img.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")

    return img.addBands(ndvi)


def add_ndvi_l7(img):
    """
    Calcula NDVI para imágenes Landsat 7.

    Bandas utilizadas:
    - NIR: SR_B4
    - Red: SR_B3
    """
    img = mask_landsat(img)

    ndvi = img.normalizedDifference(["SR_B4", "SR_B3"]).rename("NDVI")

    return img.addBands(ndvi)


# =====================================================
# FUNCIONES PARA SENTINEL-2
# =====================================================

def mask_sentinel_scl(img):
    """
    Aplica máscara de calidad usando la banda Scene Classification Layer (SCL).

    Se conservan únicamente píxeles:
    - Vegetación
    - Suelo desnudo
    - Agua

    Parámetros
    ----------
    img : ee.Image

    Retorna
    -------
    ee.Image
        Imagen filtrada por calidad.
    """
    scl = img.select("SCL")

    mask = (
        scl.eq(4)
        .Or(scl.eq(5))
        .Or(scl.eq(6))
    )

    return img.updateMask(mask)


def add_ndvi_s2(img):
    """
    Calcula NDVI para imágenes Sentinel-2.

    Bandas utilizadas:
    - NIR: B8
    - Red: B4
    """
    img = mask_sentinel_scl(img)

    ndvi = img.normalizedDifference(["B8", "B4"]).rename("NDVI")

    return img.addBands(ndvi)


# =====================================================
# CONSTRUCCIÓN DE COLECCIONES TEMPORALES
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
# COLECCIÓN INTEGRADA FINAL
# =====================================================

ndvi_all = L7.merge(L8).merge(L9).merge(S2)

print("Colección Landsat + Sentinel-2 final lista")
