"""
Script: gr2m_validation.py

Descripción:
Valida el modelo

Entradas:
Q simulado, observado

Salidas:
Métricas

Autor: Renzo Mendoza
Año: 2026
"""
# ==========================================================
# Script 11
# FASE 7
# PREPARACIÓN DATASET MODELO HIDROLÓGICO
# + FIGURA CLIMÁTICA COMPARATIVA
# ==========================================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

print("\n====================================")
print("FASE 7 - PREPARACIÓN DATASET MODELO")
print("====================================")

# ----------------------------------------------------------
# ESTILO DE FIGURAS
# ----------------------------------------------------------

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11
})

# ----------------------------------------------------------
# RUTAS DEL PROYECTO
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_RAW = BASE_DIR / "data_raw"
DATA_MENSUAL = BASE_DIR / "data_mensual"
DATA_MODEL = BASE_DIR / "data_model"
FIG_DIR = BASE_DIR / "figuras_clima"

DATA_MODEL.mkdir(exist_ok=True)
FIG_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------
# UNIDADES HIDROLÓGICAS
# ----------------------------------------------------------

UH_LIST = ["Matoc", "Pocco"]

# ----------------------------------------------------------
# PERIODO DEL MODELO
# ----------------------------------------------------------

inicio = "2012-01-01"
fin = "2022-12-01"

fechas = pd.date_range(inicio, fin, freq="MS")

# ----------------------------------------------------------
# LECTURA ROBUSTA CSV
# ----------------------------------------------------------

def leer_csv_auto(ruta):

    try:
        df = pd.read_csv(ruta, sep=";")
        if len(df.columns) == 1:
            df = pd.read_csv(ruta, sep=",")
    except:
        df = pd.read_csv(ruta, sep=",")

    df["fecha"] = pd.to_datetime(df["fecha"])

    return df


# ----------------------------------------------------------
# CLASIFICACIÓN CALIBRACIÓN / VALIDACIÓN
# ----------------------------------------------------------

def clasificar_periodo(fecha):

    anio = fecha.year

    if 2013 <= anio <= 2016:
        return True, False

    elif 2017 <= anio <= 2018:
        return False, True

    else:
        return False, False


# ----------------------------------------------------------
# FIGURA CLIMÁTICA COMPARATIVA
# ----------------------------------------------------------

def figura_clima_panel(df_matoc, df_pocco):

    fig, axes = plt.subplots(
        2, 1,
        figsize=(11,7),
        sharex=True
    )

    COLOR_P_MATOC = "#0047AB"
    COLOR_P_POCCO = "#2ca02c"
    COLOR_PET = "#d62728"

    # ---------------- MATOC ----------------

    ax1 = axes[0]

    ax1.bar(
        df_matoc["fecha"],
        df_matoc["P_mm"],
        color=COLOR_P_MATOC,
        width=20
    )

    ax1.invert_yaxis()

    ax1.set_ylabel("P (mm)")
    ax1.set_title("UH Matoc")

    ax1b = ax1.twinx()

    ax1b.plot(
        df_matoc["fecha"],
        df_matoc["PET_mm"],
        color=COLOR_PET,
        linewidth=2.5
    )

    ax1b.set_ylabel("PET (mm)")

    # ---------------- POCCO ----------------

    ax2 = axes[1]

    ax2.bar(
        df_pocco["fecha"],
        df_pocco["P_mm"],
        color=COLOR_P_POCCO,
        width=20
    )

    ax2.invert_yaxis()

    ax2.set_ylabel("P (mm)")
    ax2.set_title("UH Pocco")

    ax2b = ax2.twinx()

    ax2b.plot(
        df_pocco["fecha"],
        df_pocco["PET_mm"],
        color=COLOR_PET,
        linewidth=2.5
    )

    ax2b.set_ylabel("PET (mm)")

    # ---------------- ESTÉTICA ----------------

    for ax in axes:
        ax.grid(True, alpha=0.3)

    plt.xlabel("Fecha")

    plt.tight_layout()

    plt.savefig(
        FIG_DIR / "clima_matoc_pocco.png",
        dpi=400
    )

    plt.close()


# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------

resumen = []

for uh in UH_LIST:

    print(f"\nProcesando UH: {uh}")

    archivo_P = DATA_RAW / f"P_{uh}_mensual.csv"
    archivo_Q = DATA_MENSUAL / f"Q_{uh}_mensual.csv"
    archivo_PET = DATA_MODEL / f"PET_{uh}_mensual.csv"

    if not archivo_P.exists():
        print("⚠ No existe:", archivo_P)
        continue

    if not archivo_Q.exists():
        print("⚠ No existe:", archivo_Q)
        continue

    if not archivo_PET.exists():
        print("⚠ No existe:", archivo_PET)
        continue

    # ---------------- CARGAR ----------------

    P = leer_csv_auto(archivo_P)
    Q = leer_csv_auto(archivo_Q)
    PET = leer_csv_auto(archivo_PET)

    # ---------------- CALENDARIO BASE ----------------

    df = pd.DataFrame({"fecha": fechas})

    df = df.merge(P[["fecha","P_mm"]], on="fecha", how="left")
    df = df.merge(PET[["fecha","PET_mm"]], on="fecha", how="left")

    # usar Q_mm_mes y renombrar

    df = df.merge(Q[["fecha","Q_mm_mes"]], on="fecha", how="left")

    df = df.rename(columns={
        "Q_mm_mes": "Q_mm"
    })

    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month

    # ---------------- CALIBRACIÓN / VALIDACIÓN ----------------

    cal = []
    val = []

    for f in df["fecha"]:
        c, v = clasificar_periodo(f)
        cal.append(c)
        val.append(v)

    df["usar_calibracion"] = cal
    df["usar_validacion"] = val

    # ---------------- RESUMEN ----------------

    resumen.append({

        "UH": uh,
        "P_media_mm": round(df["P_mm"].mean(),2),
        "PET_media_mm": round(df["PET_mm"].mean(),2),
        "Q_media_mm": round(df["Q_mm"].mean(),2),
        "meses_Q_disponible": df["Q_mm"].count()

    })

    # ---------------- GUARDAR DATASET ----------------

    salida = DATA_MODEL / f"modelo_{uh}.csv"

    df.to_csv(
        salida,
        index=False
    )

    print("✔ Archivo generado:", salida)


# ----------------------------------------------------------
# RESUMEN GLOBAL
# ----------------------------------------------------------

resumen_df = pd.DataFrame(resumen)

resumen_df.to_csv(
    DATA_MODEL / "resumen_dataset_modelo.csv",
    index=False
)

# ----------------------------------------------------------
# FIGURA COMPARATIVA FINAL
# ----------------------------------------------------------

df_matoc = pd.read_csv(DATA_MODEL / "modelo_Matoc.csv")
df_pocco = pd.read_csv(DATA_MODEL / "modelo_Pocco.csv")

df_matoc["fecha"] = pd.to_datetime(df_matoc["fecha"])
df_pocco["fecha"] = pd.to_datetime(df_pocco["fecha"])

figura_clima_panel(df_matoc, df_pocco)

print("✔ Figura climática comparativa generada")

print("\n====================================")
print("DATASET MODELO GENERADO")
print("====================================")
