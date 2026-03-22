# ======================================================
# SCRIPT 06
# Regresion multivariada robusta - Theil-Sen
# ======================================================

import pandas as pd
import numpy as np
from sklearn.linear_model import TheilSenRegressor
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ======================================================
# CREAR CARPETAS
# ======================================================

os.makedirs("resultados/tablas/modelos_robustos", exist_ok=True)
os.makedirs("resultados/figuras/modelos_robustos", exist_ok=True)

# ======================================================
# CARGAR DATOS
# ======================================================

matoc = pd.read_csv("resultados/tablas/matoc_datos.csv")
pocco = pd.read_csv("resultados/tablas/pocco_datos.csv")

# ======================================================
# FUNCION PARA AJUSTAR THEIL-SEN
# ======================================================

def ajustar_theilsen(data, y_var, x_vars):
    
    X = data[x_vars].values
    Y = data[y_var].values
    
    modelo = TheilSenRegressor(random_state=42)
    modelo.fit(X, Y)
    
    # prediccion
    Y_pred = modelo.predict(X)
    
    # R2 aproximado
    r2 = r2_score(Y, Y_pred)
    
    # tabla de coeficientes
    tabla = pd.DataFrame({
        "Variable": ["Intercept"] + x_vars,
        "Coeficiente": [modelo.intercept_] + list(modelo.coef_)
    })
    
    return tabla, r2, Y_pred

# ======================================================
# VARIABLES
# ======================================================

x_vars = ["ndvi", "P_mm", "Tmed_c"]
y_var = "Q_mm"

# ======================================================
# MODELO MATOC
# ======================================================

tabla_matoc, r2_matoc, Q_pred_matoc = ajustar_theilsen(matoc, y_var, x_vars)
matoc["Q_pred"] = Q_pred_matoc

tabla_matoc["R2"] = r2_matoc
tabla_matoc.to_csv("resultados/tablas/modelos_robustos/theilsen_matoc.csv", index=False)

# ======================================================
# MODELO POCCO
# ======================================================

tabla_pocco, r2_pocco, Q_pred_pocco = ajustar_theilsen(pocco, y_var, x_vars)
pocco["Q_pred"] = Q_pred_pocco

tabla_pocco["R2"] = r2_pocco
tabla_pocco.to_csv("resultados/tablas/modelos_robustos/theilsen_pocco.csv", index=False)

# ======================================================
# FIGURA COMPARATIVA
# ======================================================

fig, ax = plt.subplots(1,2, figsize=(12,5))

# Matoc
sns.scatterplot(x=matoc["Q_mm"], y=matoc["Q_pred"], ax=ax[0])
ax[0].plot([matoc["Q_mm"].min(), matoc["Q_mm"].max()],
           [matoc["Q_mm"].min(), matoc["Q_mm"].max()],
           color="red", linestyle="--")
ax[0].set_title(f"Theil-Sen Matoc (R² = {r2_matoc:.2f})")
ax[0].set_xlabel("Caudal observado")
ax[0].set_ylabel("Caudal predicho")

# Pocco
sns.scatterplot(x=pocco["Q_mm"], y=pocco["Q_pred"], ax=ax[1])
ax[1].plot([pocco["Q_mm"].min(), pocco["Q_mm"].max()],
           [pocco["Q_mm"].min(), pocco["Q_mm"].max()],
           color="red", linestyle="--")
ax[1].set_title(f"Theil-Sen Pocco (R² = {r2_pocco:.2f})")
ax[1].set_xlabel("Caudal observado")
ax[1].set_ylabel("Caudal predicho")

plt.tight_layout()
plt.savefig("resultados/figuras/modelos_robustos/theilsen_multivariado.png", dpi=300)
plt.close()

# ======================================================
# RESULTADOS EN PANTALLA
# ======================================================

print("✔ Modelos Theil-Sen calculados y guardados")
print("\nR2 Matoc =", r2_matoc)
print("\nR2 Pocco =", r2_pocco)
print("✔ Figura comparativa guardada en resultados/figuras/modelos_robustos/theilsen_multivariado.png")