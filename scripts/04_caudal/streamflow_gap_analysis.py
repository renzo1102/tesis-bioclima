"""
Script: streamflow_gap_analysis.py

Descripción:
Análisis de datos faltantes

Entradas:
Serie caudal

Salidas:
Reporte

Autor: Renzo Mendoza
Año: 2026
"""
# ==========================================================
# SCRIPT 6
# FASE 5
# DIAGNÓSTICO DE COMPLETITUD
# mensual + anual
# gráficos solo de caudal
# ==========================================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ----------------------------------------------------------
# ESTILO DE GRÁFICOS
# ----------------------------------------------------------

plt.style.use("seaborn-v0_8-whitegrid")

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_MENSUAL = BASE_DIR / "data_mensual"
DATA_RAW = BASE_DIR / "data_raw"

OUTPUT_DIR = BASE_DIR / "data_diagnostico"
OUTPUT_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------
# ARCHIVOS
# ----------------------------------------------------------

archivos = {

    "Q_matoc": (DATA_MENSUAL / "Q_Matoc_mensual.csv", "Q_mm_mes"),
    "Q_pocco": (DATA_MENSUAL / "Q_Pocco_mensual.csv", "Q_mm_mes"),

    "T_matoc": (DATA_MENSUAL / "T_Matoc_mensual.csv", "Tmed"),
    "T_pocco": (DATA_MENSUAL / "T_Pocco_mensual.csv", "Tmed"),

    # precipitación se mantiene en data_raw
    "P_matoc": (DATA_RAW / "P_Matoc_mensual.csv", "P_mm"),
    "P_pocco": (DATA_RAW / "P_Pocco_mensual.csv", "P_mm")
}

# ----------------------------------------------------------
# CLASIFICACIÓN DE CALIDAD
# ----------------------------------------------------------

def clasificar(p):

    if p >= 90:
        return "Excelente"
    elif p >= 75:
        return "Buena"
    elif p >= 50:
        return "Regular"
    else:
        return "Deficiente"

# ----------------------------------------------------------
# TABLAS RESULTADO
# ----------------------------------------------------------

tabla_cobertura = []
tabla_vacios = []
tabla_anual = []

series = {}

# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------

for variable, info in archivos.items():

    ruta, columna = info

    print("\nProcesando:", variable)

    # detectar separador
    with open(ruta, "r", encoding="utf-8") as f:
        linea = f.readline()

    sep = ";" if ";" in linea else ","

    df = pd.read_csv(ruta, sep=sep)

    df.columns = df.columns.str.strip()

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    df[columna] = pd.to_numeric(df[columna], errors="coerce")

    df = df.sort_values("fecha")

    series[variable] = df.set_index("fecha")[columna]

    # ------------------------------------------------------
    # DIAGNÓSTICO MENSUAL
    # ------------------------------------------------------

    meses_totales = len(df)
    meses_validos = df[columna].notna().sum()
    meses_vacios = df[columna].isna().sum()

    porcentaje = round((meses_validos / meses_totales) * 100, 2) if meses_totales > 0 else 0

    calidad = clasificar(porcentaje)

    tabla_cobertura.append({

        "variable": variable,
        "meses_validos": meses_validos,
        "meses_totales": meses_totales,
        "meses_vacios": meses_vacios,
        "porcentaje": porcentaje,
        "calidad": calidad
    })

    # ------------------------------------------------------
    # VACÍOS CONSECUTIVOS
    # ------------------------------------------------------

    serie_nan = df[columna].isna()

    max_vacio = 0
    actual = 0

    for v in serie_nan:

        if v:
            actual += 1
            max_vacio = max(max_vacio, actual)
        else:
            actual = 0

    tabla_vacios.append({

        "variable": variable,
        "max_vacio_consecutivo": max_vacio
    })

    # ------------------------------------------------------
    # DIAGNÓSTICO ANUAL
    # ------------------------------------------------------

    df["anio"] = df["fecha"].dt.year

    anual = df.groupby("anio")[columna].agg(

        meses_validos=lambda x: x.notna().sum(),
        meses_totales="count"

    ).reset_index()

    anual["meses_vacios"] = anual["meses_totales"] - anual["meses_validos"]

    anual["porcentaje"] = (
        anual["meses_validos"] /
        anual["meses_totales"] * 100
    ).round(2)

    anual["porcentaje"] = anual["porcentaje"].fillna(0)

    anual["calidad"] = anual["porcentaje"].apply(clasificar)

    anual["variable"] = variable

    tabla_anual.append(anual)

# ----------------------------------------------------------
# CREAR DATAFRAMES
# ----------------------------------------------------------

cobertura_df = pd.DataFrame(tabla_cobertura)

vacios_df = pd.DataFrame(tabla_vacios)

anual_df = pd.concat(tabla_anual, ignore_index=True)

# ----------------------------------------------------------
# GUARDAR TABLAS
# ----------------------------------------------------------

cobertura_df.to_csv(
    OUTPUT_DIR / "tabla_cobertura_series.csv",
    index=False
)

vacios_df.to_csv(
    OUTPUT_DIR / "tabla_vacios_series.csv",
    index=False
)

anual_df.to_csv(
    OUTPUT_DIR / "diagnostico_anual_series.csv",
    index=False
)

# ==========================================================
# GRÁFICOS SOLO DE CAUDAL
# ==========================================================

caudal_series = {

    k: v for k, v in series.items() if "Q_" in k

}

# ----------------------------------------------------------
# DISPONIBILIDAD TEMPORAL DE CAUDAL
# ----------------------------------------------------------

plt.figure(figsize=(12,4))

colores = {

    "Q_matoc": "#1f77b4",
    "Q_pocco": "#d62728"

}

for nombre, s in caudal_series.items():

    plt.plot(

        s.index,
        s.notna().astype(int),

        label=nombre,
        linewidth=2,
        color=colores[nombre]

    )

plt.yticks(
    [0,1],
    ["Sin dato","Disponible"]
)

plt.title(
    "Disponibilidad temporal de datos de caudal",
    fontsize=14,
    weight="bold"
)

plt.xlabel("Año")
plt.ylabel("Disponibilidad")

plt.legend(frameon=False)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "disponibilidad_caudal.png",
    dpi=300
)

plt.close()

# ----------------------------------------------------------
# HEATMAP DE DATOS FALTANTES DE CAUDAL (MES vs AÑO)
# Panel: Matoc y Pocco
# ----------------------------------------------------------

from matplotlib.patches import Patch

fig, axes = plt.subplots(1, 2, figsize=(14,5), sharey=True)

titulos = {
    "Q_matoc": "(a) Disponibilidad mensual de datos – Matoc",
    "Q_pocco": "(b) Disponibilidad mensual de datos – Pocco"
}

for ax, (nombre, serie) in zip(axes, caudal_series.items()):

    df_tmp = serie.to_frame(name="Q")
    df_tmp["anio"] = df_tmp.index.year
    df_tmp["mes"] = df_tmp.index.month

    matriz = df_tmp.pivot(
        index="anio",
        columns="mes",
        values="Q"
    )

    sns.heatmap(
        matriz.isna(),
        ax=ax,
        cmap=["#2fb0b9","#e3e0e0"],
        cbar=False,
        linewidths=0.3,
        linecolor="lightgray"
    )

    # Título panel
    ax.set_title(
        titulos[nombre],
        fontsize=11
    )

    # Ejes
    ax.set_xlabel("Mes", fontsize=10)
    ax.set_ylabel("Año", fontsize=10)

    # Meses
    ax.set_xticklabels(
        ["Ene","Feb","Mar","Abr","May","Jun",
         "Jul","Ago","Sep","Oct","Nov","Dic"],
        rotation=0
    )

    # Años horizontales como en tu imagen
    ax.set_yticklabels(
        [str(int(y)) for y in matriz.index],
        rotation=0
    )

# ----------------------------------------------------------
# LEYENDA
# ----------------------------------------------------------

leyenda = [
    Patch(facecolor="#2fb0b9", label="Disponible"),
    Patch(facecolor="#e3e0e0", label="Faltante")
]

fig.legend(
    handles=leyenda,
    loc="lower center",
    ncol=2,
    frameon=False
)

plt.tight_layout(rect=[0,0.08,1,1])

plt.savefig(
    OUTPUT_DIR / "heatmap_caudal_mes_anio.png",
    dpi=300
)

plt.close()

# ----------------------------------------------------------
# MENSAJE FINAL
# ----------------------------------------------------------

print("\n================================")
print("Diagnóstico mensual y anual listo")
print("Resultados en: data_diagnostico")
print("================================")
