# ======================================================
# SCRIPT 07
# Evaluación de residuos OLS - Matoc y Pocco
# ======================================================

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats import shapiro
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ======================================================
# CREAR CARPETAS
# ======================================================

os.makedirs("resultados/tablas/residuos", exist_ok=True)
os.makedirs("resultados/figuras/residuos", exist_ok=True)

# ======================================================
# CARGAR DATOS
# ======================================================

matoc = pd.read_csv("resultados/tablas/matoc_datos.csv")
pocco = pd.read_csv("resultados/tablas/pocco_datos.csv")

# ======================================================
# VARIABLES
# ======================================================

x_vars = ["ndvi","P_mm","Tmed_c"]
y_var = "Q_mm"

# ======================================================
# FUNCION PARA AJUSTAR OLS Y EVALUAR RESIDUOS
# ======================================================

def evaluar_ols(data, nombre):

    # Ajuste OLS
    X = data[x_vars]
    X = sm.add_constant(X)
    Y = data[y_var]
    modelo = sm.OLS(Y, X).fit()

    # Predicciones y residuos
    Y_pred = modelo.predict(X)
    residuos = Y - Y_pred
    r2 = modelo.rsquared

    # Tabla de coeficientes
    tabla_coef = pd.DataFrame({
        "Variable": modelo.params.index,
        "Coeficiente": modelo.params.values,
        "p_value": modelo.pvalues.values
    })
    tabla_coef["R2"] = r2
    tabla_coef.to_csv(f"resultados/tablas/residuos/coeficientes_OLS_{nombre}.csv", index=False)

    # Tabla de residuos
    tabla_residuos = pd.DataFrame({
        "Observado": Y,
        "Predicho": Y_pred,
        "Residuo": residuos
    })
    tabla_residuos.to_csv(f"resultados/tablas/residuos/residuos_{nombre}.csv", index=False)

    # Shapiro-Wilk sobre residuos
    stat, p_val = shapiro(residuos)
    tabla_normalidad = pd.DataFrame({
        "Variable": ["Residuos"],
        "Shapiro_W": [stat],
        "p_value": [p_val]
    })
    tabla_normalidad.to_csv(f"resultados/tablas/residuos/normalidad_residuos_{nombre}.csv", index=False)

    # ======================================================
    # FIGURAS
    # ======================================================

    fig, ax = plt.subplots(1,2, figsize=(12,5))

    # Q-Q plot
    sm.qqplot(residuos, line="45", ax=ax[0])
    ax[0].set_title(f"Q-Q Plot Residuos - {nombre}\np={p_val:.3f}")

    # Scatter residuos vs predicho
    sns.scatterplot(x=Y_pred, y=residuos, ax=ax[1])
    ax[1].axhline(0, color='red', linestyle='--')
    ax[1].set_xlabel("Valores predichos")
    ax[1].set_ylabel("Residuos")
    ax[1].set_title(f"Residuos vs Predicho - {nombre}")

    plt.tight_layout()
    plt.savefig(f"resultados/figuras/residuos/evaluacion_residuos_{nombre}.png", dpi=300)
    plt.close()

    # Retorno de resultados
    return modelo, r2, p_val

# ======================================================
# EJECUCION PARA MATOC
# ======================================================

modelo_matoc, r2_matoc, p_resid_matoc = evaluar_ols(matoc, "Matoc")
print("✔ Matoc evaluado")
print(f"R² = {r2_matoc:.3f}, Shapiro-Wilk p = {p_resid_matoc:.3f}")

# ======================================================
# EJECUCION PARA POCCO
# ======================================================

modelo_pocco, r2_pocco, p_resid_pocco = evaluar_ols(pocco, "Pocco")
print("✔ Pocco evaluado")
print(f"R² = {r2_pocco:.3f}, Shapiro-Wilk p = {p_resid_pocco:.3f}")

# ======================================================
# FIN
# ======================================================

print("✔ Tablas y figuras de evaluación de residuos guardadas en resultados/tablas/residuos y resultados/figuras/residuos")