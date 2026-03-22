# ==========================================================
# CONTROL DE CALIDAD DE PRECIPITACIÓN DIARIA
# FIGURAS FINAL – ESTILO PUBLICACIÓN CIENTÍFICA (APA)
# ==========================================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_RAW = BASE_DIR / "data" / "raw"
OUTPUTS = BASE_DIR / "outputs" / "qc_individual"
TABLAS = OUTPUTS / "tablas"
FIGURAS = OUTPUTS / "figuras"

TABLAS.mkdir(parents=True, exist_ok=True)
FIGURAS.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------
# CONFIGURACIÓN GRÁFICA
# ----------------------------------------------------------
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11
})

COLOR_SERIE_ANA = "#238b45"
COLOR_SERIE_UH  = "#1f78b4"

COLOR_OK   = "#fdae61"
COLOR_REV  = "#d73027"
COLOR_COMP = "#bdbdbd"

# ----------------------------------------------------------
# ENSO
# ----------------------------------------------------------
ENSO = {
    2011: "Neutro", 2012: "Niño", 2013: "Niña",
    2014: "Niño", 2015: "Niño", 2016: "Niño",
    2017: "Niño", 2018: "Niña", 2019: "Neutro",
    2020: "Niña", 2021: "Niña", 2022: "Niña",
    2023: "Niño", 2024: "Niño"
}

# ----------------------------------------------------------
# FUNCIONES QC
# ----------------------------------------------------------
def clasificar_epoca(fecha):
    return "Lluviosa" if fecha.month in [10,11,12,1,2,3,4] else "Seca"

def qc_fisico(p):
    return (p >= 0) & (p <= 300)

def qc_iqr_por_epoca(df):
    df = df.copy()
    df["Epoca"] = df["fecha"].apply(clasificar_epoca)
    flag = pd.Series(True, index=df.index)

    for epoca in ["Lluviosa", "Seca"]:
        sub = df.loc[df["Epoca"] == epoca, "precipitacion_mm"]
        if sub.count() < 10:
            continue
        q1, q3 = sub.quantile([0.25, 0.75])
        iqr = q3 - q1
        li, ls = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        idx = df[df["Epoca"] == epoca].index
        flag.loc[idx] = df.loc[idx, "precipitacion_mm"].between(li, ls)

    return flag

def qc_ceros(series):
    flag = []
    for i in range(len(series)):
        if series.iloc[i] == 0 and 0 < i < len(series)-1:
            flag.append(not (series.iloc[i-1] > 1 and series.iloc[i+1] > 1))
        else:
            flag.append(True)
    return pd.Series(flag, index=series.index)

def qc_temporal(series):
    return series.diff().abs() <= series.diff().abs().quantile(0.99)

def qc_enso(df):
    df = df.copy()
    df["ENSO"] = df["fecha"].dt.year.map(ENSO)
    p95 = df["precipitacion_mm"].quantile(0.95)
    return ~((df["ENSO"] == "Neutro") & (df["precipitacion_mm"] > p95))

# ----------------------------------------------------------
# QC COMPLETO
# ----------------------------------------------------------
def ejecutar_qc(df, uh, estacion):

    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha")

    p = df["precipitacion_mm"]

    df["QC_Fisico"] = qc_fisico(p)
    df["QC_IQR"] = qc_iqr_por_epoca(df)
    df["QC_Ceros"] = qc_ceros(p)
    df["QC_Temporal"] = qc_temporal(p)
    df["QC_ENSO"] = qc_enso(df)

    def decision(r):
        if not r["QC_Fisico"]:
            return "Completar"
        elif not (r["QC_IQR"] and r["QC_Ceros"] and r["QC_Temporal"] and r["QC_ENSO"]):
            return "Revisar"
        else:
            return "Aceptado"

    df["Decision"] = df.apply(decision, axis=1)
    df["UH"] = uh

    if "ANA" in estacion:
        if "1" in estacion:
            estacion = "ANA 1"
        elif "2" in estacion:
            estacion = "ANA 2"

    df["Estacion"] = estacion
    return df

# ----------------------------------------------------------
# LECTURA Y QC
# ----------------------------------------------------------
qc_total = []

for archivo in DATA_RAW.glob("*.xlsx"):
    uh = archivo.stem.split("_")[0]
    estacion = archivo.stem
    df = pd.read_excel(archivo)[["fecha", "precipitacion_mm"]]
    qc = ejecutar_qc(df, uh, estacion)
    qc_total.append(qc)

qc_total = pd.concat(qc_total, ignore_index=True)

# ----------------------------------------------------------
# FUNCIÓN DE PANEL
# ----------------------------------------------------------
def panel_series(df, estaciones, titulo, color_linea, nombre):

    n = len(estaciones)
    fig, axes = plt.subplots(n, 1, figsize=(18, 4*n), sharex=True)

    if n == 1:
        axes = [axes]

    letras = ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)"]

    for i, (ax, est) in enumerate(zip(axes, estaciones)):

        d = df[df["Estacion"] == est].sort_values("fecha")

        # Línea base
        ax.plot(d["fecha"], d["precipitacion_mm"],
                color=color_linea, lw=0.9,
                alpha=0.6, zorder=1,
                label="Serie observada")

        # Aceptado
        a = d[d["Decision"] == "Aceptado"]
        ax.scatter(a["fecha"], a["precipitacion_mm"],
                   s=14, color=COLOR_OK,
                   zorder=4, label="Aceptado")

        # Revisar
        r = d[d["Decision"] == "Revisar"]
        ax.scatter(r["fecha"], r["precipitacion_mm"],
                   s=18, facecolors="none",
                   edgecolors=COLOR_REV,
                   linewidth=0.8,
                   zorder=5, label="Revisar")

        # Completar
        c = d[d["Decision"] == "Completar"].copy()
        if not c.empty:
            c["grupo"] = (c["fecha"].diff().dt.days != 1).cumsum()
            bloques = c.groupby("grupo").agg(
                inicio=("fecha", "min"),
                fin=("fecha", "max")
            )
            for _, row in bloques.iterrows():
                ax.axvspan(row["inicio"], row["fin"],
                           color=COLOR_COMP,
                           alpha=0.08,
                           zorder=0,
                           label="Completar")

        ax.set_title(f"{letras[i]} {est}", loc="left", fontsize=11)
        ax.set_ylabel("Precipitación (mm)")
        ax.grid(True, linestyle="--", alpha=0.25)

        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(),
                  by_label.keys(),
                  loc="upper right",
                  frameon=False,
                  fontsize=10)

    axes[-1].set_xlabel("Año")

    fig.suptitle(titulo, fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(FIGURAS / nombre, dpi=600, bbox_inches="tight")
    plt.close()

# ----------------------------------------------------------
# GENERAR FIGURAS
# ----------------------------------------------------------

# ANA
panel_series(
    qc_total,
    ["ANA 1", "ANA 2"],
    "Series de precipitación diaria y control de calidad – Estaciones ANA",
    COLOR_SERIE_ANA,
    "Panel_ANA_QC.png"
)

# MATOC
est_matoc = sorted([e for e in qc_total["Estacion"].unique() if "Matoc" in e])
if est_matoc:
    panel_series(
        qc_total,
        est_matoc,
        "Series de precipitación diaria y control de calidad – UH Matoc",
        COLOR_SERIE_UH,
        "Panel_UH_Matoc_QC.png"
    )

# POCCO
est_pocco = sorted([e for e in qc_total["Estacion"].unique() if "Pocco" in e])
if est_pocco:
    panel_series(
        qc_total,
        est_pocco,
        "Series de precipitación diaria y control de calidad – UH Pocco",
        COLOR_SERIE_UH,
        "Panel_UH_Pocco_QC.png"
    )

print("Figuras generadas correctamente.")
