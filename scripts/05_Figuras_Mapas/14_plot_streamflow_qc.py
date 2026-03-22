# ==========================================================
# 02_panel_hidrologico_revista.py
# Panel hidrológico tipo revista
# Incluye disponibilidad de datos y boxplot mensual
# Periodo: 2012–2022
# ==========================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------

BASE_PATH = r"C:\BRIGHIT_LILA\Rk\Tesis\3_Caudal\3_Proyecto_visual\Caudal_modelo"

DATA_QC = os.path.join(BASE_PATH, "data_qc")
OUTPUT_FIG = os.path.join(BASE_PATH, "figuras_hidrologicas")

os.makedirs(OUTPUT_FIG, exist_ok=True)

# ----------------------------------------------------------
# COLORES SUAVES
# ----------------------------------------------------------

ESTACIONES = {
    "Matoc": "#66C2A4",   # verde suave
    "Pocco": "#F4A261"    # naranja suave
}

# ----------------------------------------------------------
# PERIODO
# ----------------------------------------------------------

FECHA_INI = "2012-01-01"
FECHA_FIN = "2022-12-31"

estadisticos = []

# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------

for estacion, color in ESTACIONES.items():

    print("\nProcesando:", estacion)

    path = os.path.join(DATA_QC, f"Q_{estacion}_diario_m3s_qc.csv")

    df = pd.read_csv(path)

    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.set_index("fecha")

    df = df.loc[FECHA_INI:FECHA_FIN]

    q = df["Q_m3s"]

    # ------------------------------------------------------
    # ESTADISTICOS
    # ------------------------------------------------------

    q_mean = q.mean()
    q_max = q.max()
    q_min = q.min()

    q10 = q.quantile(0.10)
    q50 = q.quantile(0.50)
    q90 = q.quantile(0.90)

    cv = q.std() / q_mean

    estadisticos.append({

        "estacion": estacion,
        "Qmean": q_mean,
        "Qmax": q_max,
        "Qmin": q_min,
        "Q10": q10,
        "Q50": q50,
        "Q90": q90,
        "CV": cv,
        "n_datos": q.count()

    })

    # ------------------------------------------------------
    # PANEL
    # ------------------------------------------------------

    fig, axs = plt.subplots(2,3, figsize=(16,9))

    fig.suptitle(
        f"Diagnóstico hidrológico – {estacion} (2012–2022)",
        fontsize=16
    )

    # ------------------------------------------------------
    # 1 SERIE TEMPORAL
    # ------------------------------------------------------

    axs[0,0].plot(q.index, q.values, color=color, linewidth=1)

    axs[0,0].axhline(q_mean, linestyle="--", color="gray", alpha=0.7)

    axs[0,0].set_title("Serie temporal")
    axs[0,0].set_ylabel("Q (m³/s)")
    axs[0,0].grid(alpha=0.3)

    # ------------------------------------------------------
    # 2 HISTOGRAMA
    # ------------------------------------------------------

    axs[0,1].hist(q.dropna(), bins=30, color=color, alpha=0.85)

    axs[0,1].axvline(q_mean, linestyle="--", color="gray")

    axs[0,1].set_title("Distribución de caudales")
    axs[0,1].set_xlabel("Q (m³/s)")
    axs[0,1].set_ylabel("Frecuencia")

    # ------------------------------------------------------
    # 3 CURVA DE PERMANENCIA
    # ------------------------------------------------------

    q_sorted = np.sort(q.dropna())[::-1]

    prob = np.arange(1, len(q_sorted)+1) / (len(q_sorted)+1)

    axs[0,2].plot(prob*100, q_sorted, color=color)

    axs[0,2].set_title("Curva de permanencia")
    axs[0,2].set_xlabel("Probabilidad de excedencia (%)")
    axs[0,2].set_ylabel("Q (m³/s)")
    axs[0,2].grid(alpha=0.3)

    # ------------------------------------------------------
    # 4 HIDROGRAMA MEDIO ANUAL
    # ------------------------------------------------------

    df["dia"] = df.index.dayofyear

    hidro = df.groupby("dia")["Q_m3s"].mean()

    axs[1,0].plot(hidro.index, hidro.values, color=color)

    axs[1,0].set_title("Hidrograma medio anual")
    axs[1,0].set_xlabel("Día del año")
    axs[1,0].set_ylabel("Q medio (m³/s)")
    axs[1,0].grid(alpha=0.3)

    # ------------------------------------------------------
    # 5 DISPONIBILIDAD DE DATOS
    # ------------------------------------------------------

    df["año"] = df.index.year
    df["mes"] = df.index.month

    disp = df.copy()

    disp["dato"] = disp["Q_m3s"].notna().astype(int)

    tabla = disp.pivot_table(
        values="dato",
        index="año",
        columns="mes",
        aggfunc="mean"
    )

    cmap = sns.light_palette(color, as_cmap=True)

    sns.heatmap(
        tabla,
        cmap=cmap,
        ax=axs[1,1],
        cbar=True,
        vmin=0,
        vmax=1
    )

    axs[1,1].set_title("Disponibilidad de datos")
    axs[1,1].set_xlabel("Mes")
    axs[1,1].set_ylabel("Año")

    # ------------------------------------------------------
    # 6 BOXPLOT MENSUAL
    # ------------------------------------------------------

    df["mes"] = df.index.month

    sns.boxplot(
        x="mes",
        y="Q_m3s",
        data=df,
        ax=axs[1,2],
        color=color
    )

    axs[1,2].set_title("Variabilidad mensual del caudal")
    axs[1,2].set_xlabel("Mes")
    axs[1,2].set_ylabel("Q (m³/s)")

    # ------------------------------------------------------
    # GUARDAR FIGURA
    # ------------------------------------------------------

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_FIG,
            f"panel_hidrologico_{estacion}.png"
        ),
        dpi=300
    )

    plt.close()

# ----------------------------------------------------------
# GUARDAR ESTADISTICOS
# ----------------------------------------------------------

df_stats = pd.DataFrame(estadisticos)

df_stats.to_csv(
    os.path.join(OUTPUT_FIG, "estadisticos_hidrologicos.csv"),
    index=False
)

print("\nPaneles generados correctamente")
print("Estadísticos guardados en CSV")