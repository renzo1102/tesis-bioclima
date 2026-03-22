# ==========================================================
# FASE 5B
# ANALISIS DE CORRELACION HIDROLOGICA
# ==========================================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.style.use("seaborn-v0_8-whitegrid")

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_MENSUAL = BASE_DIR / "data_mensual"
DATA_RAW = BASE_DIR / "data_raw"

OUTPUT_DIR = BASE_DIR / "data_analisis"
OUTPUT_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------
# ARCHIVOS
# ----------------------------------------------------------

archivos = {

    "Q_matoc": (DATA_MENSUAL / "Q_Matoc_mensual.csv", "Q_mm_mes"),
    "Q_pocco": (DATA_MENSUAL / "Q_Pocco_mensual.csv", "Q_mm_mes"),

    # precipitación se mantiene en data_raw
    "P_matoc": (DATA_RAW / "P_Matoc_mensual.csv", "P_mm"),
    "P_pocco": (DATA_RAW / "P_Pocco_mensual.csv", "P_mm")

}

series = {}

# ----------------------------------------------------------
# LECTURA
# ----------------------------------------------------------

for variable, info in archivos.items():

    ruta, columna = info

    with open(ruta,"r",encoding="utf-8") as f:
        linea = f.readline()

    sep = ";" if ";" in linea else ","

    df = pd.read_csv(ruta, sep=sep)

    df.columns = df.columns.str.strip()

    df["fecha"] = pd.to_datetime(df["fecha"])

    df[columna] = pd.to_numeric(df[columna], errors="coerce")

    df = df.sort_values("fecha")

    series[variable] = df.set_index("fecha")[columna]

# ----------------------------------------------------------
# DATAFRAME COMBINADO
# ----------------------------------------------------------

df = pd.DataFrame(series)

df = df.loc["2012":"2018"]  # periodo útil

df = df.dropna(how="all")

# ----------------------------------------------------------
# MATRIZ DE CORRELACION
# ----------------------------------------------------------

corr = df.corr(method="pearson", min_periods=5)

corr.to_csv(
    OUTPUT_DIR / "matriz_correlacion.csv"
)

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