# ==========================================================
# 01_diagnostico_hidrologico_panel.py
# Panel de diagnóstico hidrológico por estación
# ==========================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------

BASE_PATH = r"C:\BRIGHIT_LILA\Rk\Tesis\3_Caudal\3_Proyecto_visual\Caudal_modelo"

DATA_PROCESADA = os.path.join(BASE_PATH, "data_procesada")
OUTPUT_FIG = os.path.join(BASE_PATH, "figuras_hidrologicas")

os.makedirs(OUTPUT_FIG, exist_ok=True)

ESTACIONES = ["Matoc", "Pocco"]

# ----------------------------------------------------------
# COLORES SUAVES PARA CADA FIGURA
# ----------------------------------------------------------

color_serie = "#6BAED6"   # azul suave
color_hist = "#74C476"    # verde suave
color_fdc = "#FDAE6B"     # naranja suave
color_hidro = "#9E9AC8"   # morado suave

# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------

for estacion in ESTACIONES:

    print("\n================================")
    print("Analizando:", estacion)
    print("================================")

    path = os.path.join(DATA_PROCESADA, f"Q_{estacion}_diario_m3s.csv")

    df = pd.read_csv(path)

    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.set_index("fecha")

    q = df["Q_m3s"].dropna()

    # ------------------------------------------------------
    # PANEL DE FIGURAS
    # ------------------------------------------------------

    fig, axs = plt.subplots(2,2, figsize=(12,8))

    fig.suptitle(f"Diagnóstico hidrológico – {estacion}", fontsize=14)

    # ------------------------------------------------------
    # 1 SERIE TEMPORAL
    # ------------------------------------------------------

    axs[0,0].plot(q.index, q.values, color=color_serie, linewidth=1.5)

    axs[0,0].set_title("Serie temporal")
    axs[0,0].set_ylabel("Q (m³/s)")
    axs[0,0].grid(True, alpha=0.3)

    # ------------------------------------------------------
    # 2 HISTOGRAMA
    # ------------------------------------------------------

    axs[0,1].hist(q, bins=30, color=color_hist, edgecolor="white")

    axs[0,1].set_title("Histograma")
    axs[0,1].set_xlabel("Q (m³/s)")
    axs[0,1].set_ylabel("Frecuencia")

    # ------------------------------------------------------
    # 3 CURVA DE PERMANENCIA
    # ------------------------------------------------------

    q_sorted = np.sort(q)[::-1]
    prob = np.arange(1, len(q_sorted)+1) / (len(q_sorted)+1)

    axs[1,0].plot(prob*100, q_sorted, color=color_fdc, linewidth=2)

    axs[1,0].set_title("Curva de permanencia")
    axs[1,0].set_xlabel("Probabilidad de excedencia (%)")
    axs[1,0].set_ylabel("Q (m³/s)")
    axs[1,0].grid(True, alpha=0.3)

    # ------------------------------------------------------
    # 4 HIDROGRAMA MEDIO ANUAL
    # ------------------------------------------------------

    df["dia_del_año"] = df.index.dayofyear
    q_anual = df.groupby("dia_del_año")["Q_m3s"].mean()

    axs[1,1].plot(q_anual.index, q_anual.values, color=color_hidro, linewidth=2)

    axs[1,1].set_title("Hidrograma medio anual")
    axs[1,1].set_xlabel("Día del año")
    axs[1,1].set_ylabel("Q medio (m³/s)")
    axs[1,1].grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(os.path.join(
        OUTPUT_FIG,
        f"panel_diagnostico_{estacion}.png"
    ), dpi=300)

    plt.close()

print("\nDIAGNÓSTICO COMPLETADO")
print("Figuras guardadas en:", OUTPUT_FIG)