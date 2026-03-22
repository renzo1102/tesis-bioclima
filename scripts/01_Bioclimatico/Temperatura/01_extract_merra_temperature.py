
import xarray as xr
import pandas as pd
import glob
import os

print("Iniciando extracción MERRA-2 en estaciones")

# ==========================
# 1. LEER ESTACIONES
# ==========================
est_path = "data/estaciones/01_Estaciones.xlsx"
est = pd.read_excel(est_path)

est = est[["ID_EST", "Lon", "Lat", "Alt_m"]]

# ==========================
# 2. LISTAR ARCHIVOS MERRA-2
# ==========================
merra_path = "data/MERRA2/*/*.nc4"
files = sorted(glob.glob(merra_path))

print(f"Archivos encontrados: {len(files)}")

# ==========================
# 3. CONTENEDOR FINAL
# ==========================
registros = []

# ==========================
# 4. LOOP PRINCIPAL
# ==========================
for f in files:

    fecha = os.path.basename(f).split(".")[-2]  # 20120101
    print(f"Procesando {fecha}")

    ds = xr.open_dataset(f)

    t2m = ds["T2MMEAN"] - 273.15

    for _, row in est.iterrows():
        valor = t2m.sel(
            lon=row["Lon"],
            lat=row["Lat"],
            method="nearest"
        ).values.item()

        registros.append({
            "Fecha": fecha,
            "ID_EST": row["ID_EST"],
            "T_MERRA": round(float(valor), 2)
        })

    ds.close()

# ==========================
# 5. EXPORTAR RESULTADO
# ==========================
df = pd.DataFrame(registros)
df["Fecha"] = pd.to_datetime(df["Fecha"], format="%Y%m%d")

out_path = "outputs/04_Base_MERRA_Estaciones_2012_2022.xlsx"
df.to_excel(out_path, index=False)

print("-Proceso terminado con éxito")
