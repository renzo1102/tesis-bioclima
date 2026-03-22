import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================
# RUTAS
# =========================

base = Path(__file__).resolve().parents[1]

matoc_file = base / "outputs" / "simulacion_GR2M_Matoc.csv"
pocco_file = base / "outputs" / "simulacion_GR2M_Pocco.csv"

out = base / "figuras"
out.mkdir(exist_ok=True)

# =========================
# ESTILO GENERAL
# =========================

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10
})

meses = ["E","F","M","A","M","J","J","A","S","O","N","D"]

gris_obs = "#6e6e6e"
azul_matoc = "#6fa8dc"
verde_pocco = "#93c47d"


# =========================
# FUNCION FIGURA
# =========================

def hacer_figura(file, nombre, color_sim):

    df = pd.read_csv(file, parse_dates=["fecha"])

    df["mes"] = df["fecha"].dt.month

    obs_m = df.groupby("mes")["Q_mm"].mean()
    sim_m = df.groupby("mes")["Q_sim"].mean()

    x = range(1,13)

    fig, ax = plt.subplots(1,2, figsize=(10,4))

    # ---------------------
    # SERIE TEMPORAL
    # ---------------------

    ax[0].plot(df["fecha"], df["Q_mm"], color=gris_obs, label="observado")
    ax[0].plot(df["fecha"], df["Q_sim"], color=color_sim, label="simulado")

    ax[0].set_ylabel("Q (mm/mes)")
    ax[0].set_xlabel("Año")  # ← agregado
    ax[0].set_title(f"{nombre} 2012–2022")

    ax[0].text(
        0.02,
        0.95,
        "(a)",
        transform=ax[0].transAxes
    )

    ax[0].legend(frameon=False)

    # ---------------------
    # REGIMEN MENSUAL
    # ---------------------

    ax[1].bar(x, obs_m, width=0.4, color=gris_obs, label="observado")

    ax[1].bar(
        [i+0.4 for i in x],
        sim_m,
        width=0.4,
        color=color_sim,
        label="simulado"
    )

    ax[1].set_xticks([i+0.2 for i in x])
    ax[1].set_xticklabels(meses)

    ax[1].set_xlabel("Mes")  # ← agregado
    ax[1].set_ylabel("Q (mm/mes)")
    ax[1].set_title("Régimen mensual")

    ax[1].text(
        0.02,
        0.95,
        "(b)",
        transform=ax[1].transAxes
    )

    ax[1].legend(frameon=False)

    plt.tight_layout()

    plt.savefig(
        out / f"fig_GR2M_{nombre}.png",
        dpi=300
    )

    plt.close()


# =========================
# CREAR FIGURAS
# =========================

hacer_figura(matoc_file, "Matoc", azul_matoc)
hacer_figura(pocco_file, "Pocco", verde_pocco)
