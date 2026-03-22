# ======================================================
# FASE 12B
# VALIDACIÓN REGIONAL – RÉGIMEN HIDROLÓGICO
# ======================================================

import pandas as pd
import matplotlib.pyplot as plt
import os

print("\nGenerando validación regional del régimen hidrológico...")

# ======================================================
# RUTAS
# ======================================================

ruta_base = r"C:\BRIGHIT_LILA\Rk\Tesis\3_Caudal\3_Proyecto_visual\Caudal_modelo"

outputs = os.path.join(ruta_base, "outputs")

archivo_matoc = os.path.join(outputs, "serie_final_Q_Matoc.csv")
archivo_pocco = os.path.join(outputs, "serie_final_Q_Pocco.csv")
archivo_ana = os.path.join(outputs, "ANA_mensual_normalizado.csv")

# ======================================================
# LEER DATOS
# ======================================================

df_matoc = pd.read_csv(archivo_matoc)
df_pocco = pd.read_csv(archivo_pocco)
df_ana = pd.read_csv(archivo_ana)

# convertir fecha
df_matoc["fecha"] = pd.to_datetime(df_matoc["fecha"])
df_pocco["fecha"] = pd.to_datetime(df_pocco["fecha"])
df_ana["fecha"] = pd.to_datetime(df_ana["fecha"])

# ======================================================
# EXTRAER MES
# ======================================================

df_matoc["mes"] = df_matoc["fecha"].dt.month
df_pocco["mes"] = df_pocco["fecha"].dt.month
df_ana["mes"] = df_ana["fecha"].dt.month

# ======================================================
# PROMEDIO MENSUAL
# ======================================================

matoc_reg = df_matoc.groupby("mes")["Q_sim"].mean()
pocco_reg = df_pocco.groupby("mes")["Q_sim"].mean()
ana_reg = df_ana.groupby("mes")["Q_norm"].mean()

# ======================================================
# NORMALIZACIÓN
# ======================================================

matoc_norm = matoc_reg / matoc_reg.mean()
pocco_norm = pocco_reg / pocco_reg.mean()
ana_norm = ana_reg / ana_reg.mean()

# ======================================================
# CORRELACIÓN DE RÉGIMEN
# ======================================================

corr_matoc = matoc_norm.corr(ana_norm)
corr_pocco = pocco_norm.corr(ana_norm)

print("\nCorrelación régimen Matoc vs ANA:", round(corr_matoc,3))
print("Correlación régimen Pocco vs ANA:", round(corr_pocco,3))

# ======================================================
# ESTILO GRÁFICO
# ======================================================

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11
})

MESES = ["E","F","M","A","M","J","J","A","S","O","N","D"]

color_matoc = "#6BAED6"
color_pocco = "#74C476"
color_ana = "#6E6E6E"

# ======================================================
# GRÁFICO
# ======================================================

plt.figure(figsize=(9,5))

plt.plot(
    matoc_norm.index,
    matoc_norm.values,
    marker="o",
    linewidth=2,
    color=color_matoc,
    label="Matoc (modelo)"
)

plt.plot(
    pocco_norm.index,
    pocco_norm.values,
    marker="s",
    linewidth=2,
    color=color_pocco,
    label="Pocco (modelo)"
)

plt.plot(
    ana_norm.index,
    ana_norm.values,
    marker="^",
    linewidth=2,
    color=color_ana,
    label="ANA (observado)"
)

plt.xticks(range(1,13), MESES)

plt.xlabel("Mes")
plt.ylabel("Índice de caudal normalizado")

plt.title("Comparación del régimen hidrológico mensual")

plt.legend(frameon=False)

plt.grid(alpha=0.3)

plt.tight_layout()

# ======================================================
# GUARDAR FIGURA
# ======================================================

archivo_fig = os.path.join(outputs, "validacion_regional_regimen.png")

plt.savefig(archivo_fig, dpi=300)

plt.show()

print("\n✔ Figura guardada en:")
print(archivo_fig)

print("\nFASE 12B COMPLETADA")