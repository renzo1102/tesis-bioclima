"""
Script: final_results_generation.py

Descripción:
Genera resultados finales

Entradas:
Todos

Salidas:
Figuras, tablas

Autor: Renzo Mendoza
Año: 2026
"""
# ======================================================
# SCRIPT 8
# Diagnostico de multicolinealidad (VIF)
# ======================================================

import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import os

# ======================================================
# CARPETA
# ======================================================

os.makedirs("resultados/tablas/diagnostico", exist_ok=True)

# ======================================================
# DATOS
# ======================================================

matoc = pd.read_csv("resultados/tablas/matoc_datos.csv")
pocco = pd.read_csv("resultados/tablas/pocco_datos.csv")

# ======================================================
# FUNCION VIF
# ======================================================

def calcular_vif(data, variables):

    X = data[variables]
    X = sm.add_constant(X)

    vif = pd.DataFrame()
    vif["Variable"] = X.columns

    vif["VIF"] = [
        variance_inflation_factor(X.values, i)
        for i in range(X.shape[1])
    ]

    return vif

# ======================================================
# VIF MODELO PRINCIPAL
# Q ~ NDVI + P + T
# ======================================================

vars_modelo = ["ndvi","P_mm","Tmed_c"]

vif_matoc = calcular_vif(matoc, vars_modelo)
vif_pocco = calcular_vif(pocco, vars_modelo)

# guardar resultados
vif_matoc.to_csv(
    "resultados/tablas/diagnostico/vif_matoc.csv",
    index=False
)

vif_pocco.to_csv(
    "resultados/tablas/diagnostico/vif_pocco.csv",
    index=False
)

print("✔ VIF calculado")
print("\nVIF Matoc")
print(vif_matoc)

print("\nVIF Pocco")
print(vif_pocco)

