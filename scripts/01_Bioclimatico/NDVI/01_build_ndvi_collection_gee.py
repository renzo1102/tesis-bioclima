# =====================================================
# SCRIPT 1
# Construir colección NDVI combinada
# Landsat 7–8–9 + Sentinel-2 Harmonized
# Periodo: 2012–2022
# =====================================================

# =====================================================
# DESCRIPCIÓN GENERAL
# =====================================================
# Este script construye una colección unificada de imágenes NDVI
# utilizando múltiples sensores satelitales:
#
# - Landsat 7 (2012)
# - Landsat 8 (2013–2020)
# - Landsat 9 (2021–2022)
# - Sentinel-2 Harmonized (2019–2022)
#
# El objetivo es generar una serie temporal consistente de NDVI
# para análisis ecohidrológico, permitiendo:
# - Evaluar la dinámica de la vegetación
# - Integrar NDVI en modelos hidrológicos
# - Construir series temporales por cuenca
#
# Salida principal:
# - Colección ee.ImageCollection llamada `ndvi_all`
#   con banda adicional "NDVI"

import ee

# =====================================================
# INICIALIZAR GOOGLE EARTH ENGINE
# =====================================================
# Se establece la conexión con GEE utilizando el proyecto definido.
# Requiere autenticación previa mediante:
# earthengine authenticate

ee.Initialize(project="ee-cloudatlas96")
print("Conectado a Google Earth Engine")


# =====================================================
# BLOQUE LANDSAT
# =====================================================

# -----------------------------------------------------
# FUNCIÓN: mask_landsat
# -----------------------------------------------------
# Aplica un filtro de calidad basado en la banda QA_PIXEL
# para eliminar píxeles contaminados por:
# - Nubes (bit 3)
# - Sombras de nube (bit 4)
#
# Entrada:
# - image (ee.Image)
#
# Salida:
# - Imagen enmascarada

def mask_landsat(image):
    qa = image.select("QA_PIXEL")

    mask = (
        qa.bitwiseAnd(1 << 3).eq(0)  # nubes
        .And(qa.bitwiseAnd(1 << 4).eq(0))  # sombra de nube
    )

    return image.updateMask(mask)


# -----------------------------------------------------
# FUNCIÓN: add_ndvi_l89
# -----------------------------------------------------
# Calcula NDVI para Landsat 8 y 9
#
# Fórmula:
# NDVI = (NIR - RED) / (NIR + RED)
#
# Bandas:
# - SR_B5 → NIR
# - SR_B4 → RED
#
# Proceso:
# 1. Aplica máscara de calidad
# 2. Calcula NDVI
# 3. Añade NDVI como nueva banda

def add_ndvi_l89(img):
    img = mask_landsat(img)
    ndvi = img.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")
    return img.addBands(ndvi)


# -----------------------------------------------------
# FUNCIÓN: add_ndvi_l7
# -----------------------------------------------------
# Calcula NDVI para Landsat 7
#
# Diferencia clave:
# - Cambian las bandas respecto a Landsat 8/9
#
# Bandas:
# - SR_B4 → NIR
# - SR_B3 → RED

def add_ndvi_l7(img):
    img = mask_landsat(img)
    ndvi = img.normalizedDifference(["SR_B4", "SR_B3"]).rename("NDVI")
    return img.addBands(ndvi)


# =====================================================
# BLOQUE SENTINEL-2
# =====================================================

# -----------------------------------------------------
# FUNCIÓN: mask_sentinel_scl
# -----------------------------------------------------
# Aplica enmascaramiento basado en la capa SCL
# (Scene Classification Layer)
#
# Se conservan solo píxeles:
# - 4 → Vegetación
# - 5 → Suelo desnudo
# - 6 → Agua
#
# Se eliminan:
# - Nubes
# - Sombras
# - Nieve
# - Píxeles no confiables

def mask_sentinel_scl(img):

    scl = img.select("SCL")

    mask = (
        scl.eq(4)   # vegetación
        .Or(scl.eq(5))  # suelo desnudo
        .Or(scl.eq(6))  # agua
    )

    return img.updateMask(mask)


# -----------------------------------------------------
# FUNCIÓN: add_ndvi_s2
# -----------------------------------------------------
# Calcula NDVI para Sentinel-2
#
# Bandas:
# - B8 → NIR
# - B4 → RED
#
# Proceso:
# 1. Aplica máscara SCL
# 2. Calcula NDVI
# 3. Añade banda NDVI

def add_ndvi_s2(img):

    img = mask_sentinel_scl(img)

    ndvi = img.normalizedDifference(["B8", "B4"]).rename("NDVI")

    return img.addBands(ndvi)


# =====================================================
# CONSTRUCCIÓN DE COLECCIONES (2012–2022)
# =====================================================

# -----------------------------------------------------
# LANDSAT 7 (2012)
# -----------------------------------------------------
# Primer año de la serie temporal
# Solo disponible Landsat 7

L7 = (
    ee.ImageCollection("LANDSAT/LE07/C02/T1_L2")
    .filterDate("2012-01-01", "2012-12-31")
    .map(add_ndvi_l7)
)


# -----------------------------------------------------
# LANDSAT 8 (2013–2020)
# -----------------------------------------------------

L8 = (
    ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
    .filterDate("2013-01-01", "2020-12-31")
    .map(add_ndvi_l89)
)


# -----------------------------------------------------
# LANDSAT 9 (2021–2022)
# -----------------------------------------------------

L9 = (
    ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
    .filterDate("2021-01-01", "2022-12-31")
    .map(add_ndvi_l89)
)


# -----------------------------------------------------
# SENTINEL-2 (2019–2022)
# -----------------------------------------------------
# Se añade un filtro adicional:
# - CLOUDY_PIXEL_PERCENTAGE < 40
#
# Ventaja:
# - Mayor resolución espacial
# - Mayor densidad temporal

S2 = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterDate("2019-01-01", "2022-12-31")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40))
    .map(add_ndvi_s2)
)


# =====================================================
# INTEGRACIÓN MULTISENSOR
# =====================================================
# Se combinan todas las colecciones en una sola
# serie temporal continua
#
# Resultado:
# - Colección NDVI unificada
# - Periodo completo 2012–2022
# - Integración Landsat + Sentinel

ndvi_all = L7.merge(L8).merge(L9).merge(S2)

print("Colección Landsat + Sentinel-2 final lista")


# =====================================================
# SALIDA DEL SCRIPT
# =====================================================
# Variable final:
#
# ndvi_all → ee.ImageCollection
#
# Contiene:
# - Imágenes filtradas por calidad
# - Banda adicional "NDVI"
#
# Uso posterior:
# - Extracción de series temporales (Script 02)
# - Análisis estadístico
# - Integración en modelos hidrológicos


# =====================================================
# CONSIDERACIONES TÉCNICAS
# =====================================================
# - Diferencias entre sensores pueden introducir variabilidad
# - Sentinel-2 solo disponible desde 2017
# - No se aplica armonización radiométrica explícita
# - El NDVI depende de la calidad del enmascaramiento
#
# Este script constituye la base del procesamiento NDVI
# dentro del flujo metodológico del estudio.
# =====================================================
