# ==========================================================
# FASE 3B
# VERIFICACIÓN DE MENSUALIZACIÓN DE CAUDAL
# Comprueba consistencia entre serie diaria y mensual
# ==========================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DIR_DIARIO = BASE_DIR / "data_postqc"
DIR_MENSUAL = BASE_DIR / "data_mensual"
DIR_FIG = BASE_DIR / "figuras_hidrologicas"

DIR_FIG.mkdir(exist_ok=True)

# ----------------------------------------------------------
# ARCHIVOS
# ----------------------------------------------------------

archivos = [
    ("Q_Matoc_diario_m3s_postqc.csv", "Q_Matoc_mensual.csv"),
    ("Q_Pocco_diario_m3s_postqc.csv", "Q_Pocco_mensual.csv")
]

resumen = []

# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------

for diario, mensual in archivos:

    estacion = diario.split("_")[1]

    print("\n-----------------------------------")
    print("Estación:", estacion)

    path_d = DIR_DIARIO / diario
    path_m = DIR_MENSUAL / mensual

    df_d = pd.read_csv(path_d)
    df_m = pd.read_csv(path_m)

    # ------------------------------------------------------
    # LIMPIEZA
    # ------------------------------------------------------

    df_d["fecha"] = pd.to_datetime(df_d["fecha"], errors="coerce")
    df_d["Q_m3s"] = pd.to_numeric(df_d["Q_m3s"], errors="coerce")

    df_m["fecha"] = pd.to_datetime(df_m["fecha"], errors="coerce")
    df_m["Q_m3s"] = pd.to_numeric(df_m["Q_m3s"], errors="coerce")

    # ------------------------------------------------------
    # VOLUMEN DIARIO
    # ------------------------------------------------------

    df_d["vol_m3"] = df_d["Q_m3s"] * 86400

    volumen_diario = df_d["vol_m3"].sum(skipna=True)

    # ------------------------------------------------------
    # VOLUMEN MENSUAL
    # ------------------------------------------------------

    df_m_valid = df_m.dropna(subset=["Q_m3s"]).copy()

    df_m_valid["vol_m3"] = (
        df_m_valid["Q_m3s"] *
        86400 *
        df_m_valid["dias_mes"]
    )

    volumen_mensual = df_m_valid["vol_m3"].sum()

    # ------------------------------------------------------
    # ERROR DE CONSERVACIÓN
    # ------------------------------------------------------

    if volumen_diario > 0:
        error_pct = (volumen_mensual - volumen_diario) / volumen_diario * 100
    else:
        error_pct = None

    print("Volumen diario (m3):", round(volumen_diario, 2))
    print("Volumen mensual (m3):", round(volumen_mensual, 2))
    print("Error (%):", round(error_pct, 4) if error_pct is not None else "NA")

    # ------------------------------------------------------
    # EVALUACIÓN
    # ------------------------------------------------------

    if error_pct is None:
        evaluacion = "SIN DATOS"
    elif abs(error_pct) < 1:
        evaluacion = "EXCELENTE"
    elif abs(error_pct) < 3:
        evaluacion = "BUENO"
    else:
        evaluacion = "REVISAR"

    print("Evaluación:", evaluacion)

    # ------------------------------------------------------
    # MESES FALTANTES
    # ------------------------------------------------------

    meses_esperados = pd.period_range(
        start=df_m["fecha"].min(),
        end=df_m["fecha"].max(),
        freq="M"
    )

    meses_presentes = df_m["fecha"].dt.to_period("M")

    faltantes = set(meses_esperados) - set(meses_presentes)

    print("Meses faltantes:", len(faltantes))

    # ------------------------------------------------------
    # CLIMATOLOGÍA PARA VERIFICACIÓN
    # ------------------------------------------------------

    df_d["mes"] = df_d["fecha"].dt.month
    df_m["mes"] = df_m["fecha"].dt.month

    clim_d = df_d.groupby("mes")["Q_m3s"].mean()
    clim_m = df_m.groupby("mes")["Q_m3s"].mean()

    # ------------------------------------------------------
    # GRÁFICO
    # ------------------------------------------------------

    plt.figure(figsize=(8,4))

    plt.plot(clim_d.index, clim_d.values, marker="o", label="Diario")
    plt.plot(clim_m.index, clim_m.values, marker="s", label="Mensual")

    plt.title(f"Climatología comparada - {estacion}")
    plt.xlabel("Mes")
    plt.ylabel("Caudal (m³/s)")
    plt.legend()
    plt.grid(True)

    fig_path = DIR_FIG / f"verificacion_climatologia_{estacion}.png"

    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()

    print("Figura guardada:", fig_path)

    # ------------------------------------------------------
    # RESUMEN
    # ------------------------------------------------------

    resumen.append({
        "estacion": estacion,
        "volumen_diario_m3": volumen_diario,
        "volumen_mensual_m3": volumen_mensual,
        "error_pct": error_pct,
        "meses_faltantes": len(faltantes),
        "evaluacion": evaluacion
    })

# ----------------------------------------------------------
# GUARDAR RESUMEN FINAL
# ----------------------------------------------------------

resumen_df = pd.DataFrame(resumen)

resumen_path = BASE_DIR / "resumen_verificacion_mensualizacion.csv"

resumen_df.to_csv(resumen_path, index=False)

print("\n===================================")
print("VERIFICACIÓN FINALIZADA")
print("Resumen guardado en:")
print(resumen_path)
print("===================================")