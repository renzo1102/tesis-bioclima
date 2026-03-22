import pandas as pd
import matplotlib.pyplot as plt
import os

print("\nGenerando figuras estilo artículo...")

# ------------------------------------------------
# RUTAS
# ------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

OUTPUTS = os.path.join(BASE_DIR, "outputs")
FIGURES = os.path.join(BASE_DIR, "figures")

os.makedirs(FIGURES, exist_ok=True)

# ------------------------------------------------
# ESTILO TIPOGRÁFICO
# ------------------------------------------------

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11
})

plt.style.use("seaborn-v0_8-whitegrid")

# ------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------

ESTACIONES = {
    "Matoc": "#6BAED6",
    "Pocco": "#74C476"
}

MESES = ["Ene","Feb","Mar","Abr","May","Jun",
         "Jul","Ago","Sep","Oct","Nov","Dic"]

# ------------------------------------------------
# PROCESO
# ------------------------------------------------

for estacion, color in ESTACIONES.items():

    archivo = os.path.join(
        OUTPUTS,
        f"simulacion_GR2M_{estacion}.csv"
    )

    df = pd.read_csv(archivo)

    df["fecha"] = pd.to_datetime(df["fecha"])

    df["mes"] = df["fecha"].dt.month
    regimen = df.groupby("mes")["Q_sim"].mean()

    # ------------------------------------------------
    # FIGURA
    # ------------------------------------------------

    fig, axes = plt.subplots(
        2,1,
        figsize=(10,6),
        gridspec_kw={'height_ratios':[2,1]}
    )

    # Serie temporal
    axes[0].plot(
        df["fecha"],
        df["Q_sim"],
        color=color,
        linewidth=2
    )

    axes[0].set_title(
        f"(a) Serie de caudal simulado (2012–2022) – {estacion}",
        loc="left"
    )

    axes[0].set_ylabel("Q (mm/mes)")

    # Régimen mensual
    axes[1].bar(
        regimen.index,
        regimen.values,
        color=color,
        edgecolor="gray"
    )

    axes[1].set_title(
        "(b) Régimen mensual",
        loc="left"
    )

    axes[1].set_ylabel("Q medio (mm)")
    axes[1].set_xlabel("Mes")

    axes[1].set_xticks(range(1,13))
    axes[1].set_xticklabels(MESES)

    plt.tight_layout()

    fig_path = os.path.join(
        FIGURES,
        f"figura_{estacion}_GR2M.png"
    )

    plt.savefig(fig_path, dpi=300)

    plt.show()

    print("Figura guardada:", fig_path)

print("\nFiguras generadas correctamente.")