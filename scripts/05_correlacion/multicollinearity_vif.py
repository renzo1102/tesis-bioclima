"""
Script: multicollinearity_vif.py

Descripción:
VIF

Entradas:
Dataset

Salidas:
Indicadores

Autor: Renzo Mendoza
Año: 2026
"""
# ======================================================
# SCRIPT 5
# Modelos de regresion multivariable
# + figura del modelo multivariado
# ======================================================

import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ======================================================
# CREAR CARPETAS
# ======================================================

os.makedirs("resultados/tablas/modelos", exist_ok=True)
os.makedirs("resultados/figuras/modelos", exist_ok=True)

# ======================================================
# CARGAR DATOS
# ======================================================

matoc = pd.read_csv("resultados/tablas/matoc_datos.csv")
pocco = pd.read_csv("resultados/tablas/pocco_datos.csv")

# ======================================================
# FUNCION PARA AJUSTAR MODELOS
# ======================================================

def ajustar_modelo(data, y, x_vars):

    X = data[x_vars]
    X = sm.add_constant(X)

    Y = data[y]

    modelo = sm.OLS(Y, X).fit()

    tabla = pd.DataFrame({
        "Variable":modelo.params.index,
        "Coeficiente":modelo.params.values,
        "p_value":modelo.pvalues.values
    })

    r2 = modelo.rsquared

    return tabla, r2, modelo

# ======================================================
# MODELOS MATOC
# ======================================================

# 1 NDVI ~ P + T
tabla1, r2_1, modelo1_matoc = ajustar_modelo(matoc, "ndvi", ["P_mm","Tmed_c"])
tabla1["R2"] = r2_1
tabla1.to_csv("resultados/tablas/modelos/modelo1_matoc.csv", index=False)

# 2 Q ~ P + T
tabla2, r2_2, modelo2_matoc = ajustar_modelo(matoc, "Q_mm", ["P_mm","Tmed_c"])
tabla2["R2"] = r2_2
tabla2.to_csv("resultados/tablas/modelos/modelo2_matoc.csv", index=False)

# 3 Q ~ NDVI + P + T
tabla3, r2_3, modelo3_matoc = ajustar_modelo(matoc, "Q_mm", ["ndvi","P_mm","Tmed_c"])
tabla3["R2"] = r2_3
tabla3.to_csv("resultados/tablas/modelos/modelo3_matoc.csv", index=False)

# prediccion
X_matoc = sm.add_constant(matoc[["ndvi","P_mm","Tmed_c"]])
matoc["Q_pred"] = modelo3_matoc.predict(X_matoc)

# ======================================================
# MODELOS POCCO
# ======================================================

# 1 NDVI ~ P + T
tabla4, r2_4, modelo1_pocco = ajustar_modelo(pocco, "ndvi", ["P_mm","Tmed_c"])
tabla4["R2"] = r2_4
tabla4.to_csv("resultados/tablas/modelos/modelo1_pocco.csv", index=False)

# 2 Q ~ P + T
tabla5, r2_5, modelo2_pocco = ajustar_modelo(pocco, "Q_mm", ["P_mm","Tmed_c"])
tabla5["R2"] = r2_5
tabla5.to_csv("resultados/tablas/modelos/modelo2_pocco.csv", index=False)

# 3 Q ~ NDVI + P + T
tabla6, r2_6, modelo3_pocco = ajustar_modelo(pocco, "Q_mm", ["ndvi","P_mm","Tmed_c"])
tabla6["R2"] = r2_6
tabla6.to_csv("resultados/tablas/modelos/modelo3_pocco.csv", index=False)

# prediccion
X_pocco = sm.add_constant(pocco[["ndvi","P_mm","Tmed_c"]])
pocco["Q_pred"] = modelo3_pocco.predict(X_pocco)

# ======================================================
# FIGURA MODELO MULTIVARIADO
# ======================================================

fig, ax = plt.subplots(1,2, figsize=(12,5))

# Matoc
sns.scatterplot(
    data=matoc,
    x="Q_mm",
    y="Q_pred",
    ax=ax[0]
)

ax[0].plot(
    [matoc["Q_mm"].min(), matoc["Q_mm"].max()],
    [matoc["Q_mm"].min(), matoc["Q_mm"].max()],
    color="red",
    linestyle="--"
)

ax[0].set_title(f"Modelo multivariado Matoc (R² = {r2_3:.2f})")
ax[0].set_xlabel("Caudal observado")
ax[0].set_ylabel("Caudal predicho")

# Pocco
sns.scatterplot(
    data=pocco,
    x="Q_mm",
    y="Q_pred",
    ax=ax[1]
)

ax[1].plot(
    [pocco["Q_mm"].min(), pocco["Q_mm"].max()],
    [pocco["Q_mm"].min(), pocco["Q_mm"].max()],
    color="red",
    linestyle="--"
)

ax[1].set_title(f"Modelo multivariado Pocco (R² = {r2_6:.2f})")
ax[1].set_xlabel("Caudal observado")
ax[1].set_ylabel("Caudal predicho")

plt.tight_layout()

plt.savefig(
    "resultados/figuras/modelos/modelo_multivariado_panel.png",
    dpi=300
)

plt.close()

# ======================================================
# RESULTADOS EN PANTALLA
# ======================================================

print("✔ Modelos calculados")

print("\nR2 Matoc")
print("NDVI ~ P + T =", r2_1)
print("Q ~ P + T =", r2_2)
print("Q ~ NDVI + P + T =", r2_3)

print("\nR2 Pocco")
print("NDVI ~ P + T =", r2_4)
print("Q ~ P + T =", r2_5)
print("Q ~ NDVI + P + T =", r2_6)

print("\n✔ Figura del modelo guardada en:")
print("resultados/figuras/modelos/modelo_multivariado_panel.png")
