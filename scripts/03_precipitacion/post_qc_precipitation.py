"""
Script: post_qc_precipitation.py

Descripción general
-------------------
Este script realiza la limpieza posterior al control de calidad
individual de datos diarios de precipitación.

Se evalúa la coherencia espacial interna entre estaciones
pertenecientes a una misma unidad hidrográfica (UH), eliminando
valores extremos inconsistentes mediante un criterio estadístico
basado en desviación estándar.

Entradas
--------
- Tablas de precipitación diaria filtradas por QC individual

Salidas
-------
- Serie diaria depurada de precipitación post-QC

Autor: Renzo Mendoza  
Año: 2026
"""

import pandas as pd
import numpy as np
import os
import glob


# ==========================================================
# 1. CONFIGURACIÓN DE RUTAS
# ==========================================================

input_dir = "outputs/qc_individual/tablas/"
metadata_path = "data/metadata_estaciones.csv"

output_dir = "outputs/post_qc"
output_path = os.path.join(
    output_dir,
    "diario_post_qc_fase1.csv"
)

os.makedirs(output_dir, exist_ok=True)


# ==========================================================
# 2. CARGA DE METADATA
# ==========================================================

metadata = pd.read_csv(metadata_path)

"""
La metadata contiene información espacial de estaciones
como unidad hidrográfica y ubicación.
"""


# ==========================================================
# 3. UNIFICACIÓN DE RESULTADOS QC INDIVIDUALES
# ==========================================================

files = glob.glob(
    os.path.join(input_dir, "QC_individual_*.csv")
)

lista_df = []

for file in files:
    df = pd.read_csv(file, parse_dates=["fecha"])
    lista_df.append(df)

df_total = pd.concat(
    lista_df,
    ignore_index=True
)

print(f"Registros totales: {len(df_total)}")


# ==========================================================
# 4. CONSTRUCCIÓN VARIABLE POST-QC
# ==========================================================

df_total["Precip_postQC"] = df_total["precipitacion_mm"]

"""
Inicialmente la serie depurada es igual a la original.
"""

# Valores que requieren completación → NA definitivo
df_total.loc[
    df_total["Decision"] == "Completar",
    "Precip_postQC"
] = np.nan


# ==========================================================
# 5. FUNCIÓN DE COHERENCIA ESPACIAL POR UH
# ==========================================================

df_revisar = df_total[
    df_total["Decision"] == "Revisar"
]

"""
Estos valores presentan sospecha de inconsistencia
y requieren evaluación adicional.
"""

for idx, row in df_revisar.iterrows():

    fecha = row["fecha"]
    estacion = row["Estacion"]
    uh = row["UH"]
    valor = row["precipitacion_mm"]

    # Estaciones de la misma UH ese día
    df_mismo_dia = df_total[
        (df_total["fecha"] == fecha) &
        (df_total["UH"] == uh) &
        (df_total["Estacion"] != estacion) &
        (df_total["Precip_postQC"].notna())
    ]

    """
    Se requiere al menos dos estaciones adicionales
    para evaluar coherencia espacial.
    """

    if len(df_mismo_dia) >= 2:

        media = df_mismo_dia["precipitacion_mm"].mean()
        std = df_mismo_dia["precipitacion_mm"].std()

        if std > 0:

            z = (valor - media) / std

            # Umbral estadístico de valor extremo
            if abs(z) > 2:

                df_total.loc[
                    idx,
                    "Precip_postQC"
                ] = np.nan


# ==========================================================
# 6. RESUMEN ESTADÍSTICO FINAL
# ==========================================================

total_na = df_total["Precip_postQC"].isna().sum()

porcentaje_na = (
    df_total["Precip_postQC"].isna().mean() * 100
)

print("Resumen Fase 1 Post-QC:")
print(f"Valores NA finales: {total_na}")
print(f"Porcentaje NA final: {porcentaje_na:.2f}%")


# ==========================================================
# 7. EXPORTACIÓN
# ==========================================================

df_total.to_csv(
    output_path,
    index=False
)

print("Archivo exportado correctamente")
print("Fase 1 Post-QC completada")
