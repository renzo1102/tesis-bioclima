# ============================================================
# FASE 8 — VALIDACIÓN CRUZADA
# Líneas + suavizado + tendencia + estadísticos internos
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 11

COLOR_MATOC = "#1b9e77"
COLOR_POCCO = "#d95f02"

# ------------------------------------------------------------
# RUTAS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "outputs" / "validacion_cruzada"
OUTPUT_DIR = BASE_DIR / "outputs" / "figuras"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_DIR / "resultados_iteraciones_validacion_cruzada.csv")

# ------------------------------------------------------------
# FUNCIÓN CIENTÍFICA
# ------------------------------------------------------------

def plot_metrica(ax, metrica, titulo, y_label, linea_ref=None):

    for uh, color in [("Matoc", COLOR_MATOC), ("Pocco", COLOR_POCCO)]:

        sub = df[df["UH"] == uh].copy()
        sub = sub.sort_values("Iteracion")

        x = sub["Iteracion"]
        y = sub[metrica]

        # Línea original tenue
        ax.plot(x, y, color=color, linewidth=1, alpha=0.4)

        # Suavizado (media móvil ventana 3)
        y_smooth = y.rolling(window=3, center=True).mean()
        ax.plot(x, y_smooth, color=color, linewidth=2, label=f"{uh}")

        # Tendencia lineal
        coef = np.polyfit(x, y, 1)
        tendencia = np.poly1d(coef)
        ax.plot(x, tendencia(x),
                color=color, linestyle="--", linewidth=1)

        # Estadísticos
        media = y.mean()
        std = y.std()
        pendiente = coef[0]

        texto = (f"{uh}\n"
                 f"μ={media:.2f}\n"
                 f"σ={std:.2f}\n"
                 f"β={pendiente:.4f}")

        # Posición del texto
        ypos = 0.95 if uh == "Matoc" else 0.55

        ax.text(0.02, ypos, texto,
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment="top",
                color=color)

    if linea_ref is not None:
        ax.axhline(linea_ref, color="gray", linestyle=":", linewidth=1)

    ax.set_title(titulo)
    ax.set_ylabel(y_label)
    ax.set_xlabel("Iteración")
    ax.legend(frameon=False)

# ------------------------------------------------------------
# CREAR FIGURA
# ------------------------------------------------------------

fig, axes = plt.subplots(2, 2, figsize=(10, 8))

plot_metrica(axes[0,0], "R2", "(a) R² por iteración", "R²")
plot_metrica(axes[0,1], "RMSE", "(b) RMSE", "RMSE (mm)")
plot_metrica(axes[1,0], "Bias_%", "(c) Bias (%)", "Bias (%)", linea_ref=0)
plot_metrica(axes[1,1], "NSE", "(d) NSE", "NSE", linea_ref=0.5)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "Figura_Fase8_Validacion_Cruzada_Cientifica.png",
    dpi=600,
    bbox_inches="tight"
)

plt.close()

print("Figura Fase 8 científica generada correctamente.")