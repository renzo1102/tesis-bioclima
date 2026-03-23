# ==========================================================
# SCRIPT – 02_post_qc_fase1.py
# FASE 1 - Post-QC Diario con coherencia interna por UH
# ==========================================================

# ==========================================================
# DESCRIPCIÓN GENERAL
# ==========================================================
# Este script implementa la FASE 1 del post-procesamiento
# del control de calidad (Post-QC) para series de precipitación diaria.
#
# Objetivo principal:
# - Refinar la calidad de los datos luego del QC individual
# - Evaluar coherencia espacial dentro de cada Unidad Hidrológica (UH)
#
# Lógica general:
# 1. Se consolidan todos los resultados de QC individual
# 2. Se genera una nueva variable: Precip_postQC
# 3. Se eliminan valores marcados como "Completar"
# 4. Se evalúan valores "Revisar" mediante coherencia espacial
# 5. Se identifican outliers espaciales mediante Z-score
#
# Salida:
# - Dataset consolidado y depurado listo para FASE 2

import pandas as pd
import numpy as np
import os
import glob

# ----------------------------------------------------------
# 1. RUTAS
# ----------------------------------------------------------
# Definición de rutas relativas para entrada y salida.

input_dir = "outputs/qc_individual/tablas/"
metadata_path = "data/metadata_estaciones.csv"
output_dir = "outputs/post_qc"
output_path = os.path.join(output_dir, "diario_post_qc_fase1.csv")

# Crear carpeta de salida si no existe
os.makedirs(output_dir, exist_ok=True)

# ----------------------------------------------------------
# 2. CARGAR METADATA
# ----------------------------------------------------------
# Se carga información auxiliar de estaciones (no usada directamente
# en esta fase, pero útil para futuras etapas).

metadata = pd.read_csv(metadata_path)

# ----------------------------------------------------------
# 3. CARGAR Y UNIFICAR QC INDIVIDUALES
# ----------------------------------------------------------
# Se leen todos los archivos generados en el QC individual
# y se consolidan en un solo DataFrame.

files = glob.glob(os.path.join(input_dir, "QC_individual_*.csv"))

lista_df = []

for file in files:
    df = pd.read_csv(file, parse_dates=["fecha"])
    lista_df.append(df)

# Concatenación total
df_total = pd.concat(lista_df, ignore_index=True)

print(f"Registros totales: {len(df_total)}")

# ----------------------------------------------------------
# 4. CREACIÓN VARIABLE FINAL (Precip_postQC)
# ----------------------------------------------------------
# Se crea una columna que contendrá la versión final depurada.

df_total["Precip_postQC"] = df_total["precipitacion_mm"]

# Regla 1:
# Valores marcados como "Completar" se eliminan directamente
# (se convierten en NA)

df_total.loc[df_total["Decision"] == "Completar", "Precip_postQC"] = np.nan

# ----------------------------------------------------------
# 5. ANÁLISIS DE VALORES "REVISAR"
# ----------------------------------------------------------
# Se evalúan los datos clasificados como "Revisar"
# utilizando coherencia espacial dentro de la misma UH.

df_revisar = df_total[df_total["Decision"] == "Revisar"]

# Iteración sobre cada registro "Revisar"
for idx, row in df_revisar.iterrows():

    fecha = row["fecha"]
    estacion = row["Estacion"]
    uh = row["UH"]
    valor = row["precipitacion_mm"]

    # ------------------------------------------------------
    # SELECCIÓN DE REFERENCIA ESPACIAL
    # ------------------------------------------------------
    # Se buscan otras estaciones:
    # - mismo día
    # - misma UH
    # - distinta estación
    # - valores válidos (no NA)

    df_mismo_dia = df_total[
        (df_total["fecha"] == fecha) &
        (df_total["UH"] == uh) &
        (df_total["Estacion"] != estacion) &
        (df_total["Precip_postQC"].notna())
    ]

    # ------------------------------------------------------
    # CONDICIÓN MÍNIMA
    # ------------------------------------------------------
    # Se requiere al menos 2 estaciones para evaluar coherencia.

    if len(df_mismo_dia) >= 2:

        # --------------------------------------------------
        # ESTADÍSTICAS ESPACIALES
        # --------------------------------------------------
        # Se calcula media y desviación estándar espacial.

        media = df_mismo_dia["precipitacion_mm"].mean()
        std = df_mismo_dia["precipitacion_mm"].std()

        # --------------------------------------------------
        # Z-SCORE ESPACIAL
        # --------------------------------------------------
        # Se evalúa qué tan extremo es el valor respecto al grupo.

        if std > 0:
            z = (valor - media) / std

            # --------------------------------------------------
            # CRITERIO DE OUTLIER
            # --------------------------------------------------
            # Si el valor se aleja más de 2 desviaciones estándar,
            # se considera inconsistente espacialmente.

            if abs(z) > 2:
                df_total.loc[idx, "Precip_postQC"] = np.nan

# ----------------------------------------------------------
# 6. RESUMEN FINAL
# ----------------------------------------------------------
# Se calcula la cantidad y proporción de datos eliminados.

total_na = df_total["Precip_postQC"].isna().sum()
porcentaje_na = df_total["Precip_postQC"].isna().mean() * 100

print("Resumen FASE 1:")
print(f"Valores NA finales: {total_na}")
print(f"Porcentaje NA final: {porcentaje_na:.2f}%")

# ----------------------------------------------------------
# 7. EXPORTACIÓN
# ----------------------------------------------------------
# Se guarda el dataset final de esta fase.

df_total.to_csv(output_path, index=False)

print("Archivo guardado en:")
print(output_path)
print("FASE 1 completada.")


# ==========================================================
# INTERPRETACIÓN METODOLÓGICA
# ==========================================================
# Esta fase introduce un control espacial que complementa
# el QC individual.
#
# Aportes clave:
# - Reduce falsos positivos del QC inicial
# - Detecta inconsistencias locales entre estaciones
# - Mejora la coherencia hidrológica del dataset
#
# Resultado:
# - Serie más robusta para análisis hidrológico y modelamiento
#
# Este paso es fundamental antes de:
# - Relleno de datos faltantes
# - Agregación temporal
# - Modelamiento hidrológico
# ==========================================================
