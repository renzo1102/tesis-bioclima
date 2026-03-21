"""
Script: post_qc_precipitation.py
Descripción:
Limpieza posterior al QC

Entradas:
Datos filtrados

Salidas:
Datos depurados

Autor: Renzo Mendoza
Año: 2026
"""
# ==========================================================
# SCRIPT 2
# 02_post_qc_fase1.py
# FASE 1 - Post-QC Diario con coherencia interna por UH
# ==========================================================

import pandas as pd
import numpy as np
import os
import glob

# ----------------------------------------------------------
# 1. RUTAS
# ----------------------------------------------------------
input_dir = "outputs/qc_individual/tablas/"
metadata_path = "data/metadata_estaciones.csv"
output_dir = "outputs/post_qc"
output_path = os.path.join(output_dir, "diario_post_qc_fase1.csv")

os.makedirs(output_dir, exist_ok=True)

# ----------------------------------------------------------
# 2. CARGAR METADATA
# ----------------------------------------------------------
metadata = pd.read_csv(metadata_path)

# ----------------------------------------------------------
# 3. CARGAR Y UNIFICAR QC INDIVIDUALES
# ----------------------------------------------------------
files = glob.glob(os.path.join(input_dir, "QC_individual_*.csv"))

lista_df = []
for file in files:
    df = pd.read_csv(file, parse_dates=["fecha"])
    lista_df.append(df)

df_total = pd.concat(lista_df, ignore_index=True)

print(f"Registros totales: {len(df_total)}")

# ----------------------------------------------------------
# 4. PREPARAR COLUMNA FINAL
# ----------------------------------------------------------
df_total["Precip_postQC"] = df_total["precipitacion_mm"]

# Completar → NA definitivo
df_total.loc[df_total["Decision"] == "Completar", "Precip_postQC"] = np.nan

# ----------------------------------------------------------
# 5. ANALISIS DE "REVISAR" POR UH
# ----------------------------------------------------------
df_revisar = df_total[df_total["Decision"] == "Revisar"]

for idx, row in df_revisar.iterrows():

    fecha = row["fecha"]
    estacion = row["Estacion"]
    uh = row["UH"]
    valor = row["precipitacion_mm"]

    # Obtener otras estaciones de la misma UH ese día
    df_mismo_dia = df_total[
        (df_total["fecha"] == fecha) &
        (df_total["UH"] == uh) &
        (df_total["Estacion"] != estacion) &
        (df_total["Precip_postQC"].notna())
    ]

    # Necesitamos al menos 2 estaciones para evaluar coherencia
    if len(df_mismo_dia) >= 2:

        media = df_mismo_dia["precipitacion_mm"].mean()
        std = df_mismo_dia["precipitacion_mm"].std()

        if std > 0:
            z = (valor - media) / std

            # Si es muy extremo → NA
            if abs(z) > 2:
                df_total.loc[idx, "Precip_postQC"] = np.nan

# ----------------------------------------------------------
# 6. RESUMEN FINAL
# ----------------------------------------------------------
total_na = df_total["Precip_postQC"].isna().sum()
porcentaje_na = df_total["Precip_postQC"].isna().mean() * 100

print("Resumen FASE 1:")
print(f"Valores NA finales: {total_na}")
print(f"Porcentaje NA final: {porcentaje_na:.2f}%")

# ----------------------------------------------------------
# 7. GUARDAR RESULTADO
# ----------------------------------------------------------
df_total.to_csv(output_path, index=False)

print("Archivo guardado en:")
print(output_path)
print("FASE 1 completada.")
