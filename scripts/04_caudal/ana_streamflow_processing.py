"""
Script: ana_streamflow_processing.py

Descripción general
-------------------
Este script realiza el procesamiento hidrológico adicional de la serie de
caudal observada de la estación ANA. El objetivo principal es transformar
la serie temporal de caudal diario (posterior al control de calidad) en una
serie mensual representativa, así como calcular una serie de caudal
normalizado respecto al caudal medio del periodo de estudio.

Este procesamiento permite:
- Reducir la variabilidad diaria y obtener una señal hidrológica mensual.
- Facilitar análisis de variabilidad climática e hidrológica.
- Permitir comparaciones relativas mediante normalización del caudal.

Entradas
--------
- ANA_diario_postqc.csv
  Serie diaria de caudal (m³/s) posterior al control de calidad.

Salidas
-------
- ANA_mensual_normalizado.csv
  Serie mensual de caudal medio y caudal normalizado.

Autor: Renzo Mendoza
Año: 2026
"""

# ======================================================
# SCRIPT 20
# FASE 12A — PROCESAMIENTO DE CAUDAL ANA
# Conversión diario → mensual + normalización hidrológica
# ======================================================

import pandas as pd
import os

# ======================================================
# CONFIGURACIÓN DE RUTAS
# ======================================================

# Ruta base del proyecto hidrológico
ruta_base = r"C:\Tesis\3_Caudal\3_Proyecto_visual\Caudal_modelo"

# Directorios de entrada y salida
data_postqc = os.path.join(ruta_base, "data_postqc")
outputs = os.path.join(ruta_base, "outputs")

# Archivo de entrada (serie diaria ya controlada)
archivo = os.path.join(data_postqc, "ANA_diario_postqc.csv")

# ======================================================
# CARGA DE DATOS
# ======================================================

# Lectura de la serie diaria de caudal
df = pd.read_csv(archivo)

# Conversión explícita a formato datetime
df["fecha"] = pd.to_datetime(df["fecha"])

# ======================================================
# MENSUALIZACIÓN DEL CAUDAL
# ======================================================
# Se agregan los datos diarios a escala mensual mediante
# el cálculo del caudal medio mensual.
#
# Este procedimiento es estándar en hidrología para:
# - reducir ruido hidrológico diario
# - representar la disponibilidad hídrica promedio

df["anio"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month

df_mensual = (
    df.groupby(["anio", "mes"])
      .agg({
          "Q_m3s": "mean"   # caudal medio mensual
      })
      .reset_index()
)

# Construcción de fecha representativa mensual
df_mensual["fecha"] = pd.to_datetime(
    dict(
        year=df_mensual.anio,
        month=df_mensual.mes,
        day=1
    )
)

# ======================================================
# NORMALIZACIÓN HIDROLÓGICA DEL CAUDAL
# ======================================================
# Se calcula el caudal medio del periodo completo.
# Luego se obtiene un índice hidrológico relativo:
#
# Q_norm = Q_mensual / Q_medio_periodo
#
# Interpretación:
# Q_norm > 1 → mes húmedo (caudal superior al promedio)
# Q_norm < 1 → mes seco (caudal inferior al promedio)

Qmedio = df_mensual["Q_m3s"].mean()

df_mensual["Q_norm"] = df_mensual["Q_m3s"] / Qmedio

# ======================================================
# GUARDADO DE RESULTADOS
# ======================================================

archivo_out = os.path.join(
    outputs,
    "ANA_mensual_normalizado.csv"
)

df_mensual.to_csv(
    archivo_out,
    index=False
)

# ======================================================
# MENSAJE FINAL DE CONTROL
# ======================================================

print("Serie mensual ANA procesada correctamente.")
print("Archivo generado en:", archivo_out)
