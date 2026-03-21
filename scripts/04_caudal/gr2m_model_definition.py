"""
Script: gr2m_model_definition.py

Descripción:
Define estructura del modelo GR2M

Entradas:
Parámetros hidrológicos implícitos en series P y Q

Salidas:
Diagnóstico de coherencia hidrológica mediante análisis
de correlación estadística y visual.

Autor: Renzo Mendoza
Año: 2026
"""

# ==========================================================
# SCRIPT 8
# FASE 5B
# ANALISIS DE CORRELACION HIDROLOGICA
# ==========================================================

# ----------------------------------------------------------
# LIBRERÍAS
# ----------------------------------------------------------
# pandas → manejo de series temporales hidrológicas
# matplotlib → generación de figuras científicas
# seaborn → visualización estadística avanzada
# pathlib → manejo robusto de rutas

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# estilo gráfico tipo paper hidrológico
plt.style.use("seaborn-v0_8-whitegrid")

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------
# Se define el directorio base del proyecto.
# Esto permite que el script sea reproducible en cualquier equipo
# sin depender de rutas absolutas.

BASE_DIR = Path(__file__).resolve().parents[1]

# Series ya procesadas mensuales (caudal)
DATA_MENSUAL = BASE_DIR / "data_mensual"

# Series mensuales originales (precipitación)
DATA_RAW = BASE_DIR / "data_raw"

# Carpeta donde se guardarán resultados del análisis
OUTPUT_DIR = BASE_DIR / "data_analisis"
OUTPUT_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------
# ARCHIVOS
# ----------------------------------------------------------
# Diccionario que define:
# nombre interno → (ruta archivo, columna hidrológica)

archivos = {

    "Q_matoc": (DATA_MENSUAL / "Q_Matoc_mensual.csv", "Q_mm_mes"),
    "Q_pocco": (DATA_MENSUAL / "Q_Pocco_mensual.csv", "Q_mm_mes"),

    # precipitación se mantiene en data_raw porque
    # representa datos observados sin transformación adicional
    "P_matoc": (DATA_RAW / "P_Matoc_mensual.csv", "P_mm"),
    "P_pocco": (DATA_RAW / "P_Pocco_mensual.csv", "P_mm")

}

# diccionario donde se almacenarán las series temporales
series = {}

# ----------------------------------------------------------
# LECTURA
# ----------------------------------------------------------
# Este bloque realiza:
# 1) detección automática del separador CSV
# 2) conversión de fecha
# 3) conversión a variable numérica
# 4) ordenamiento temporal
# 5) construcción de serie indexada

for variable, info in archivos.items():

    ruta, columna = info

    # detección del separador
    with open(ruta,"r",encoding="utf-8") as f:
        linea = f.readline()

    sep = ";" if ";" in linea else ","

    df = pd.read_csv(ruta, sep=sep)

    # limpieza de nombres de columnas
    df.columns = df.columns.str.strip()

    # conversión de fecha
    df["fecha"] = pd.to_datetime(df["fecha"])

    # conversión hidrológica segura
    df[columna] = pd.to_numeric(df[columna], errors="coerce")

    # orden cronológico
    df = df.sort_values("fecha")

    # almacenamiento como serie temporal indexada
    series[variable] = df.set_index("fecha")[columna]

# ----------------------------------------------------------
# DATAFRAME COMBINADO
# ----------------------------------------------------------
# Se construye un dataframe multivariable.
# Esto permite calcular correlaciones entre:
# - lluvia y caudal
# - caudal entre microcuencas

df = pd.DataFrame(series)

# selección de periodo con mejor disponibilidad de datos
df = df.loc["2012":"2018"]

# eliminación de meses sin información
df = df.dropna(how="all")

# ----------------------------------------------------------
# MATRIZ DE CORRELACION
# ----------------------------------------------------------
# Se calcula correlación de Pearson.
#
# Interpretación hidrológica:
# r cercano a 1 → respuesta hidrológica sincronizada
# r cercano a 0 → independencia hidrológica
# r negativo → comportamiento inverso

corr = df.corr(method="pearson", min_periods=5)

# guardar resultados numéricos
corr.to_csv(
    OUTPUT_DIR / "matriz_correlacion.csv"
)

# visualización
plt.figure(figsize=(6,5))

sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm",
    vmin=-1,
    vmax=1
)

plt.title("Matriz de correlación hidrológica")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "matriz_correlacion.png",
    dpi=300
)

plt.close()

# ----------------------------------------------------------
# SCATTER Q_matoc vs Q_pocco
# ----------------------------------------------------------
# Permite evaluar coherencia espacial del régimen hidrológico.

plt.figure(figsize=(6,5))

sns.regplot(
    x=df["Q_pocco"],
    y=df["Q_matoc"],
    scatter_kws={"alpha":0.7}
)

plt.xlabel("Q Pocco")
plt.ylabel("Q Matoc")

plt.title("Relación entre estaciones de caudal")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "Qmatoc_vs_Qpocco.png",
    dpi=300
)

plt.close()

# ----------------------------------------------------------
# LLUVIA VS CAUDAL MATOC
# ----------------------------------------------------------
# Evalúa sensibilidad lluvia–escorrentía.

plt.figure(figsize=(6,5))

sns.regplot(
    x=df["P_matoc"],
    y=df["Q_matoc"],
    scatter_kws={"alpha":0.7}
)

plt.xlabel("Precipitación Matoc (mm)")
plt.ylabel("Caudal Matoc")

plt.title("Relación lluvia-caudal Matoc")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "P_vs_Q_matoc.png",
    dpi=300
)

plt.close()

# ----------------------------------------------------------
# LLUVIA VS CAUDAL POCCO
# ----------------------------------------------------------

plt.figure(figsize=(6,5))

sns.regplot(
    x=df["P_pocco"],
    y=df["Q_pocco"],
    scatter_kws={"alpha":0.7}
)

plt.xlabel("Precipitación Pocco (mm)")
plt.ylabel("Caudal Pocco")

plt.title("Relación lluvia-caudal Pocco")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "P_vs_Q_pocco.png",
    dpi=300
)

plt.close()

print("\n====================================")
print("Analisis hidrologico completado")
print("Resultados en carpeta data_analisis")
print("====================================")
