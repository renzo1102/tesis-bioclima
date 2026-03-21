"""
Script: temperature_merra_extraction.py

Descripción general
-------------------
Este script extrae valores de temperatura del aire a 2 m (T2MMEAN)
provenientes del reanálisis atmosférico MERRA-2 en ubicaciones
correspondientes a estaciones meteorológicas o unidades hidrográficas.

El procedimiento consiste en:
- Leer coordenadas de estaciones
- Recorrer archivos diarios NetCDF del producto MERRA-2
- Extraer temperatura en la celda más cercana
- Construir una serie temporal continua por estación

Entradas
--------
- Archivos NetCDF diarios MERRA-2
- Coordenadas de estaciones (Excel)

Salidas
-------
- Serie temporal de temperatura por estación en formato Excel

Autor: Renzo Mendoza  
Año: 2026
"""

import xarray as xr
import pandas as pd
import glob
import os

print("Iniciando extracción de temperatura MERRA-2 en estaciones")

# =====================================================
# 1. LECTURA DE ESTACIONES
# =====================================================

est_path = "data/estaciones/01_Estaciones.xlsx"

est = pd.read_excel(est_path)

# Seleccionar variables relevantes
est = est[["ID_EST", "Lon", "Lat", "Alt_m"]]

"""
Este bloque:
- Carga la ubicación de estaciones meteorológicas
- Filtra solo las variables necesarias para la extracción espacial
"""

# =====================================================
# 2. LISTADO DE ARCHIVOS MERRA-2
# =====================================================

merra_path = "data/MERRA2/*/*.nc4"
files = sorted(glob.glob(merra_path))

print(f"Archivos encontrados: {len(files)}")

"""
Este bloque:
- Identifica todos los archivos diarios NetCDF disponibles
- Ordena cronológicamente la lista
"""

# =====================================================
# 3. CONTENEDOR DE RESULTADOS
# =====================================================

registros = []

"""
Lista que almacenará los valores extraídos para cada estación y fecha.
"""

# =====================================================
# 4. LOOP PRINCIPAL DE EXTRACCIÓN
# =====================================================

for f in files:

    # Extraer fecha del nombre del archivo
    fecha = os.path.basename(f).split(".")[-2]
    print(f"Procesando {fecha}")

    # Abrir dataset NetCDF
    ds = xr.open_dataset(f)

    """
    xarray permite manipular datos multidimensionales climáticos.
    """

    # Temperatura en Kelvin → Celsius
    t2m = ds["T2MMEAN"] - 273.15

    """
    Conversión necesaria para análisis hidroclimáticos.
    """

    # Extracción por estación
    for _, row in est.iterrows():

        valor = t2m.sel(
            lon=row["Lon"],
            lat=row["Lat"],
            method="nearest"
        ).values.item()

        """
        .sel(method="nearest"):
        Selecciona la celda del grid más cercana a la estación.
        """

        registros.append({
            "Fecha": fecha,
            "ID_EST": row["ID_EST"],
            "T_MERRA": round(float(valor), 2)
        })

    ds.close()

"""
Este loop:
- Recorre cada día
- Extrae temperatura para todas las estaciones
- Construye base de datos tipo panel (fecha–estación)
"""

# =====================================================
# 5. EXPORTACIÓN
# =====================================================

df = pd.DataFrame(registros)

df["Fecha"] = pd.to_datetime(
    df["Fecha"],
    format="%Y%m%d"
)

out_path = "outputs/04_Base_MERRA_Estaciones_2012_2022.xlsx"

df.to_excel(out_path, index=False)

print("Proceso terminado correctamente")
