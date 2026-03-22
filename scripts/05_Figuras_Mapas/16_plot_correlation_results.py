import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# =========================
# Datos reales de coeficientes
# =========================
data = {
    'Variable': ['NDVI', 'P_mm', 'Tmed_c'],
    'Matoc_OLS': [51.2795, 0.4255, 0.4272],
    'Matoc_TheilSen': [57.1274, 0.3530, -0.4036],
    'Pocco_OLS': [69.2509, 0.4911, 0.4255],
    'Pocco_TheilSen': [80.7694, 0.4001, -0.7041]
}

df = pd.DataFrame(data)
x = np.arange(len(df['Variable']))  # posiciones en X

# =========================
# Parámetros de ancho de barra
# =========================
width = 0.2

# =========================
# Crear la figura
# =========================
fig, ax = plt.subplots(figsize=(10,6))

# Barras Matoc
ax.bar(x - 1.5*width, df['Matoc_OLS'], width, label='Matoc OLS', color='skyblue')
ax.bar(x - 0.5*width, df['Matoc_TheilSen'], width, label='Matoc Theil-Sen', color='dodgerblue')

# Barras Pocco
ax.bar(x + 0.5*width, df['Pocco_OLS'], width, label='Pocco OLS', color='lightcoral')
ax.bar(x + 1.5*width, df['Pocco_TheilSen'], width, label='Pocco Theil-Sen', color='red')

# =========================
# Personalización del gráfico
# =========================
ax.set_xticks(x)
ax.set_xticklabels(df['Variable'])
ax.set_ylabel('Coeficiente')
ax.set_title('Comparación de coeficientes OLS vs Theil-Sen (Matoc y Pocco)')
ax.legend()
ax.axhline(0, color='black', linewidth=0.8)  # línea base en 0

# Añadir valores sobre las barras
for i in range(len(x)):
    ax.text(x[i]-1.5*width, df['Matoc_OLS'][i]+0.5, f"{df['Matoc_OLS'][i]:.2f}", ha='center', fontsize=9)
    ax.text(x[i]-0.5*width, df['Matoc_TheilSen'][i]+0.5, f"{df['Matoc_TheilSen'][i]:.2f}", ha='center', fontsize=9)
    ax.text(x[i]+0.5*width, df['Pocco_OLS'][i]+0.5, f"{df['Pocco_OLS'][i]:.2f}", ha='center', fontsize=9)
    ax.text(x[i]+1.5*width, df['Pocco_TheilSen'][i]+0.5, f"{df['Pocco_TheilSen'][i]:.2f}", ha='center', fontsize=9)

plt.tight_layout()
plt.show()