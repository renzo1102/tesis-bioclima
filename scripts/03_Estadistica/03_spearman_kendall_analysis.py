# ======================================================
# SCRIPT 04
# Correlaciones y matrices de correlacion
# Spearman + Kendall
# ======================================================

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, kendalltau
import os

# ======================================================
# CREAR CARPETAS
# ======================================================

os.makedirs("resultados/tablas", exist_ok=True)
os.makedirs("resultados/figuras/matriz", exist_ok=True)

# ======================================================
# CARGAR DATOS
# ======================================================

matoc = pd.read_csv("resultados/tablas/matoc_datos.csv")
pocco = pd.read_csv("resultados/tablas/pocco_datos.csv")

# ======================================================
# VARIABLES ANALISIS
# ======================================================

variables = ["ndvi","P_mm","Tmed_c","Q_mm"]

# ======================================================
# FUNCION CORRELACIONES
# ======================================================

def calcular_correlaciones(data):

    resultados = []

    pares = [
        ("ndvi","Tmed_c","NDVI - Temperatura"),
        ("ndvi","P_mm","NDVI - Precipitacion"),
        ("Tmed_c","P_mm","Temperatura - Precipitacion"),
        ("ndvi","Q_mm","NDVI - Caudal"),
        ("P_mm","Q_mm","Precipitacion - Caudal"),
        ("Tmed_c","Q_mm","Temperatura - Caudal")
    ]

    for x,y,nombre in pares:

        # Spearman
        r_s, p_s = spearmanr(data[x], data[y])

        # Kendall
        r_k, p_k = kendalltau(data[x], data[y])

        resultados.append({
            "Relacion": nombre,
            "Spearman_r": r_s,
            "Spearman_p": p_s,
            "Kendall_tau": r_k,
            "Kendall_p": p_k
        })

    return pd.DataFrame(resultados)

# ======================================================
# MATRIZ DE CORRELACION
# ======================================================

def matriz_correlacion(data, nombre):

    matriz = data[variables].corr(method="spearman")

    plt.figure(figsize=(6,5))

    sns.heatmap(
        matriz,
        annot=True,
        cmap="RdBu_r",
        vmin=-1,
        vmax=1,
        fmt=".2f"
    )

    plt.title(f"Matriz de correlacion - {nombre}")

    plt.tight_layout()

    plt.savefig(
        f"resultados/figuras/matriz/matriz_correlacion_{nombre.lower()}.png",
        dpi=300
    )

    plt.close()

# ======================================================
# ANALISIS MATOC
# ======================================================

corr_matoc = calcular_correlaciones(matoc)

corr_matoc.to_csv(
    "resultados/tablas/correlaciones1_matoc.csv",
    index=False
)

matriz_correlacion(matoc,"Matoc")

# ======================================================
# ANALISIS POCCO
# ======================================================

corr_pocco = calcular_correlaciones(pocco)

corr_pocco.to_csv(
    "resultados/tablas/correlaciones1_pocco.csv",
    index=False
)

matriz_correlacion(pocco,"Pocco")

# ======================================================
# MENSAJE FINAL
# ======================================================

print("✔ Correlaciones Spearman y Kendall calculadas")
print("✔ Tablas guardadas en resultados/tablas")
print("✔ Matrices de correlacion generadas")