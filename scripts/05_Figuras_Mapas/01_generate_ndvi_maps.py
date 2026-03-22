# ============================================================
# FIGURA NDVI 2012–2022
# MATOC – POCCO
# Versión limpia para publicación
# ============================================================

import rasterio
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.colors import TwoSlopeNorm
import geopandas as gpd

# ============================================================
# RUTAS
# ============================================================

ruta_raster = "data/rasters"
shp_matoc = "data/matoc/MATOC.shp"
shp_pocco = "data/pocco/POCCO.shp"

# ============================================================
# FUNCIÓN CARGAR
# ============================================================

def cargar(nombre):
    with rasterio.open(os.path.join(ruta_raster, nombre)) as src:
        data = src.read(1)
        transform = src.transform
        width = src.width
        height = src.height

        xmin = transform[2]
        xmax = xmin + transform[0] * width
        ymax = transform[5]
        ymin = ymax + transform[4] * height

        extent = [xmin, xmax, ymin, ymax]
        return data, extent, src.crs

# ============================================================
# CARGA RASTERS
# ============================================================

matoc_media, ext1, crs_matoc = cargar("MATOC_NDVI_mean_2012_2022.tif")
matoc_2012, ext2, _ = cargar("MATOC_NDVI_2012.tif")
matoc_2022, ext3, _ = cargar("MATOC_NDVI_2022.tif")
matoc_tend, ext4, _ = cargar("MATOC_NDVI_trend_2012_2022.tif")

pocco_media, ext5, crs_pocco = cargar("POCCO_NDVI_mean_2012_2022.tif")
pocco_2012, ext6, _ = cargar("POCCO_NDVI_2012.tif")
pocco_2022, ext7, _ = cargar("POCCO_NDVI_2022.tif")
pocco_tend, ext8, _ = cargar("POCCO_NDVI_trend_2012_2022.tif")

extents = [ext1, ext2, ext3, ext4,
           ext5, ext6, ext7, ext8]

datos = [
    matoc_media, matoc_2012, matoc_2022, matoc_tend,
    pocco_media, pocco_2012, pocco_2022, pocco_tend
]

# ============================================================
# ESCALAS GLOBALES
# ============================================================

ndvi_total = np.concatenate([matoc_media.flatten(),
                             pocco_media.flatten()])

ndvi_min = np.nanpercentile(ndvi_total, 2)
ndvi_max = np.nanpercentile(ndvi_total, 98)

trend_total = np.concatenate([matoc_tend.flatten(),
                              pocco_tend.flatten()])

trend_max = np.nanpercentile(np.abs(trend_total), 98)
norm_trend = TwoSlopeNorm(vmin=-trend_max,
                          vcenter=0,
                          vmax=trend_max)

# ============================================================
# SHAPEFILES
# ============================================================

gdf_matoc = gpd.read_file(shp_matoc).to_crs(crs_matoc)
gdf_pocco = gpd.read_file(shp_pocco).to_crs(crs_pocco)

# ============================================================
# FUNCIÓN AGREGAR NORTE
# ============================================================

def agregar_norte(ax, extent):

    xmin, xmax, ymin, ymax = extent
    ancho = xmax - xmin
    alto = ymax - ymin

    x = xmin + ancho * 0.08
    y = ymax - alto * 0.08

    ax.annotate("N",
                xy=(x, y - alto*0.07),
                xytext=(x, y),
                arrowprops=dict(facecolor="black",
                                width=1,
                                headwidth=6),
                ha="center",
                fontsize=7,
                bbox=dict(facecolor="white",
                          alpha=0.7,
                          edgecolor="none",
                          pad=1))

# ============================================================
# FIGURA
# ============================================================

fig = plt.figure(figsize=(18, 10))
axes = []

for fila in range(2):
    for col in range(4):
        ax = fig.add_axes([
            0.05 + col * 0.22,
            0.55 - fila * 0.35,
            0.16,
            0.25
        ])
        axes.append(ax)

titulos = [
    "MATOC – NDVI medio (2012–2022)",
    "MATOC – 2012",
    "MATOC – 2022",
    "MATOC – Tendencia",
    "POCCO – NDVI medio (2012–2022)",
    "POCCO – 2012",
    "POCCO – 2022",
    "POCCO – Tendencia"
]

for i, ax in enumerate(axes):

    if i in [3, 7]:
        im = ax.imshow(datos[i],
                       cmap="RdBu_r",
                       norm=norm_trend,
                       extent=extents[i])
    else:
        im = ax.imshow(datos[i],
                       cmap="YlGn",
                       vmin=ndvi_min,
                       vmax=ndvi_max,
                       extent=extents[i])

    ax.set_title(titulos[i], fontsize=9)
    ax.axis("off")

    if i < 4:
        gdf_matoc.boundary.plot(ax=ax,
                                edgecolor="0.6",
                                linewidth=0.7)
    else:
        gdf_pocco.boundary.plot(ax=ax,
                                edgecolor="0.6",
                                linewidth=0.7)

    agregar_norte(ax, extents[i])

    # barra vertical individual
    cax = fig.add_axes([
        ax.get_position().x1 + 0.004,
        ax.get_position().y0,
        0.01,
        ax.get_position().height
    ])
    plt.colorbar(im, cax=cax)

# ============================================================
# EXPORTAR
# ============================================================

os.makedirs("outputs/mapas", exist_ok=True)

plt.savefig("outputs/mapas/Figura_NDVI_Publicacion_Limpia.png",
            dpi=600,
            bbox_inches="tight")

plt.show()

print("Figura final limpia exportada.")