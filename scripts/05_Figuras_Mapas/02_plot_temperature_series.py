# ======================================================
# SCRIPT FINAL FIGURAS TIPO ARTÍCULO - TEMPERATURA Y VALIDACIÓN
# ======================================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.ticker import MaxNLocator

# ===============================
# Configuración de estilo
# ===============================
sns.set_style("whitegrid")
plt.rcParams.update({
    "figure.figsize": (10,6),
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "font.family": "serif"
})

# Paleta tipo artículo, colores suaves pero visibles
colores = sns.color_palette("Set2") 
linea_tendencia = "#999999"  # gris suave para líneas de tendencia

# ===============================
# Crear carpeta de resultados
# ===============================
os.makedirs("resultados/figuras", exist_ok=True)

# ===============================
# Leer archivos Excel
# ===============================
ruta_excel = "excel"
pre_bias = pd.read_excel(os.path.join(ruta_excel, "1_Merra_PreBIAS.xlsx"), sheet_name="MERRA")
post_bias = pd.read_excel(os.path.join(ruta_excel, "1_Merra_PostBIAS.xlsx"), sheet_name="Bias-TCORR")
urua = pd.read_excel(os.path.join(ruta_excel, "2_Urua_Serie.xlsx"), sheet_name="URUA-SerieTemp")
yana = pd.read_excel(os.path.join(ruta_excel, "2_Yana_Serie.xlsx"), sheet_name="YANA-SerieTemp")
uh_final = pd.read_excel(os.path.join(ruta_excel, "4_Seriefinal_diario_UH-Matoc-Pococ.xlsx"), sheet_name="UNIDO")
val_uru_yana = pd.read_excel(os.path.join(ruta_excel, "5_Validacion_Urua-Yana.xlsx"), sheet_name="URU-VALIDA-YANA")
val_yana_uru = pd.read_excel(os.path.join(ruta_excel, "5_Validacion_Yana-Urua.xlsx"), sheet_name="YANA-VALIDA-URUA")

# ===============================
# Convertir fecha a datetime
# ===============================
for df in [pre_bias, post_bias, urua, yana, uh_final, val_uru_yana, val_yana_uru]:
    df['Fecha'] = pd.to_datetime(df['Fecha'])

# ===============================
# FIGURA 1: Scatter Pre vs Post Bias
# ===============================
fig, axs = plt.subplots(1,2, figsize=(14,6), sharey=True)

# a) Pre-bias
sns.scatterplot(data=pre_bias, x="T_OBS", y="T_MERRA", ax=axs[0], color=colores[0], s=30)
sns.regplot(data=pre_bias, x="T_OBS", y="T_MERRA", ax=axs[0], scatter=False, color=linea_tendencia, line_kws={"linewidth":2})
axs[0].set_xlabel("Temperatura observada (°C)")
axs[0].set_ylabel("Temperatura MERRA (°C)")
axs[0].text(0.01,1.02,'a) Pre-bias', transform=axs[0].transAxes, fontsize=12)

# b) Post-bias
sns.scatterplot(data=post_bias, x="T_OBS", y="T_CORR", ax=axs[1], color=colores[1], s=30)
sns.regplot(data=post_bias, x="T_OBS", y="T_CORR", ax=axs[1], scatter=False, color=linea_tendencia, line_kws={"linewidth":2})
axs[1].set_xlabel("Temperatura observada (°C)")
axs[1].set_ylabel("Temperatura corregida (°C)")
axs[1].text(0.01,1.02,'b) Post-bias', transform=axs[1].transAxes, fontsize=12)

plt.tight_layout()
plt.savefig("resultados/figuras/fig1_pre_post_bias.png", dpi=300)

# ===============================
# FIGURA 2: Series temporales URUA y YANA
# ===============================
urua = urua[(urua['Fecha'].dt.year >= 2012) & (urua['Fecha'].dt.year <= 2022)]
yana = yana[(yana['Fecha'].dt.year >= 2012) & (yana['Fecha'].dt.year <= 2022)]

fig, axs = plt.subplots(2,1, figsize=(16,8), sharex=True, gridspec_kw={'height_ratios':[1,1]})

# a) URUA
axs[0].scatter(urua['Fecha'], urua['T_OBS'], color=colores[0], s=15, label='Observada')
axs[0].plot(urua['Fecha'], urua['T_MERRA'], color=colores[1], linewidth=2, label='MERRA')
axs[0].plot(urua['Fecha'], urua['T_CORR'], color=colores[2], linewidth=2, label='Corregida')
axs[0].set_ylabel("Temperatura (°C)")
axs[0].text(0.01,1.02,'a) Urua', transform=axs[0].transAxes, fontsize=12)
axs[0].legend()

# b) YANA
axs[1].scatter(yana['Fecha'], yana['T_OBS'], color=colores[0], s=15, label='Observada')
axs[1].plot(yana['Fecha'], yana['T_MERRA'], color=colores[1], linewidth=2, label='MERRA')
axs[1].plot(yana['Fecha'], yana['T_CORR'], color=colores[2], linewidth=2, label='Corregida')
axs[1].set_ylabel("Temperatura (°C)")
axs[1].set_xlabel("Fecha")
axs[1].text(0.01,1.02,'b) Yana', transform=axs[1].transAxes, fontsize=12)
axs[1].legend()

plt.tight_layout()
plt.savefig("resultados/figuras/fig2_serie_estaciones.png", dpi=300)

# ===============================
# FIGURA 3: UH diario y mensual
# ===============================
uh_final['Pocco'] = pd.to_numeric(uh_final['Pocco'])
uh_final['Matoc'] = pd.to_numeric(uh_final['Matoc'])
uh_final.set_index('Fecha', inplace=True)
uh_monthly = uh_final.resample("ME").mean()

fig, axs = plt.subplots(2,2, figsize=(14,10))

# a) Pocco diario
axs[0,0].plot(uh_final.index, uh_final['Pocco'], color=colores[0])
axs[0,0].set_ylabel("Temperatura UH (°C)")
axs[0,0].text(0.01,1.02,'a) Pocco diario', transform=axs[0,0].transAxes, fontsize=12)

# b) Matoc diario
axs[0,1].plot(uh_final.index, uh_final['Matoc'], color=colores[1])
axs[0,1].set_ylabel("Temperatura UH (°C)")
axs[0,1].text(0.01,1.02,'b) Matoc diario', transform=axs[0,1].transAxes, fontsize=12)

# c) Pocco mensual
axs[1,0].plot(uh_monthly.index, uh_monthly['Pocco'], color=colores[0])
axs[1,0].set_ylabel("Temperatura UH (°C)")
axs[1,0].text(0.01,1.02,'c) Pocco mensual', transform=axs[1,0].transAxes, fontsize=12)

# d) Matoc mensual
axs[1,1].plot(uh_monthly.index, uh_monthly['Matoc'], color=colores[1])
axs[1,1].set_ylabel("Temperatura UH (°C)")
axs[1,1].text(0.01,1.02,'d) Matoc mensual', transform=axs[1,1].transAxes, fontsize=12)

for ax in axs.flat:
    ax.set_xlabel("Fecha")
    ax.xaxis.set_major_locator(MaxNLocator(6))

plt.tight_layout()
plt.savefig("resultados/figuras/fig3_uh_final.png", dpi=300)

# ===============================
# FIGURA 4: Validación URUA-YANA con scatter y distribución
# ===============================
fig, axs = plt.subplots(2,2, figsize=(14,10))

valid_uru = val_uru_yana.dropna(subset=['T_CORR','T_OBS_YANA','Error'])
axs[0,0].scatter(valid_uru['T_CORR'], valid_uru['T_OBS_YANA'], s=20, color=colores[0])
sns.regplot(x=valid_uru['T_CORR'], y=valid_uru['T_OBS_YANA'], scatter=False, ax=axs[0,0], color=linea_tendencia, line_kws={"linewidth":2})
axs[0,0].set_xlabel("Temperatura corregida (°C)")
axs[0,0].set_ylabel("Temperatura observada (°C)")
rmse = valid_uru['Error'].dropna().pow(2).mean()**0.5
bias = (valid_uru['T_CORR'] - valid_uru['T_OBS_YANA']).mean()
axs[0,0].text(0.05,0.95,f"RMSE={rmse:.2f}, Bias={bias:.2f}", transform=axs[0,0].transAxes, verticalalignment='top')
axs[0,0].text(0.01,1.05,'a) Urua → Yana', transform=axs[0,0].transAxes, fontsize=12)

valid_yana = val_yana_uru.dropna(subset=['T_CORR','T_OBS_URUA','Error'])
axs[0,1].scatter(valid_yana['T_CORR'], valid_yana['T_OBS_URUA'], s=20, color=colores[1])
sns.regplot(x=valid_yana['T_CORR'], y=valid_yana['T_OBS_URUA'], scatter=False, ax=axs[0,1], color=linea_tendencia, line_kws={"linewidth":2})
axs[0,1].set_xlabel("Temperatura corregida (°C)")
axs[0,1].set_ylabel("Temperatura observada (°C)")
rmse = valid_yana['Error'].dropna().pow(2).mean()**0.5
bias = (valid_yana['T_CORR'] - valid_yana['T_OBS_URUA']).mean()
axs[0,1].text(0.05,0.95,f"RMSE={rmse:.2f}, Bias={bias:.2f}", transform=axs[0,1].transAxes, verticalalignment='top')
axs[0,1].text(0.01,1.05,'b) Yana → Urua', transform=axs[0,1].transAxes, fontsize=12)

# c) Histograma Urua → Yana
axs[1,0].hist(valid_uru['Error'], bins=30, color=colores[0], alpha=0.7)
axs[1,0].set_xlabel("Error (°C)")
axs[1,0].set_ylabel("Frecuencia")
axs[1,0].text(0.01,1.05,'c) Distribución Urua → Yana', transform=axs[1,0].transAxes, fontsize=12)

# d) Histograma Yana → Urua
axs[1,1].hist(valid_yana['Error'], bins=30, color=colores[1], alpha=0.7)
axs[1,1].set_xlabel("Error (°C)")
axs[1,1].set_ylabel("Frecuencia")
axs[1,1].text(0.01,1.05,'d) Distribución Yana → Urua', transform=axs[1,1].transAxes, fontsize=12)

plt.tight_layout()
plt.savefig("resultados/figuras/fig4_validacion_final.png", dpi=300)

print("✔ Todas las figuras generadas correctamente en resultados/figuras")