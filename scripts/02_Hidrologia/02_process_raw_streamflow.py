# ==========================================================
# 00B_procesamiento_caudal_5min_QC_robusto.py
# QC completo para datos de vertedero (5 min → diario)
# ==========================================================

import pandas as pd
import numpy as np
import os

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------

BASE_PATH = r"C:\BRIGHIT_LILA\Rk\Tesis\3_Caudal\3_Proyecto_visual\Caudal_modelo"

DATA_BRUTA = os.path.join(BASE_PATH, "data_bruta")
DATA_PROCESADA = os.path.join(BASE_PATH, "data_procesada")

os.makedirs(DATA_PROCESADA, exist_ok=True)

ESTACIONES = ["Matoc", "Pocco"]

PERIODO_INICIO = "2012-01-01"
PERIODO_FIN = "2022-12-31"

# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------

for estacion in ESTACIONES:

    print("\n======================================")
    print(f"Procesando estación: {estacion}")
    print("======================================")

    path = os.path.join(DATA_BRUTA, f"{estacion}.csv")

    # ------------------------------------------------------
    # LECTURA ROBUSTA
    # ------------------------------------------------------

    df = pd.read_csv(path, sep=";", low_memory=False)

    df = df.dropna(axis=1, how="all")

    df = df.iloc[:, :3]

    df.columns = ["fecha", "Nivel_m", "Q_ls"]

    # ------------------------------------------------------
    # CONVERSIONES
    # ------------------------------------------------------

    df["fecha"] = pd.to_datetime(df["fecha"], dayfirst=True, errors="coerce")

    df["Nivel_m"] = pd.to_numeric(df["Nivel_m"], errors="coerce")
    df["Q_ls"] = pd.to_numeric(df["Q_ls"], errors="coerce")

    df = df.dropna(subset=["fecha"])

    print("Primer dato:", df["fecha"].min())
    print("Último dato:", df["fecha"].max())

    # ------------------------------------------------------
    # QC FISICO BASICO
    # ------------------------------------------------------

    df.loc[df["Q_ls"] < 0, "Q_ls"] = np.nan
    df.loc[df["Nivel_m"] < 0, "Nivel_m"] = np.nan

    # valores físicamente absurdos
    df.loc[df["Q_ls"] > 10000, "Q_ls"] = np.nan
    df.loc[df["Nivel_m"] > 5, "Nivel_m"] = np.nan

    # ------------------------------------------------------
    # DETECCION DE PICOS EXTREMOS
    # ------------------------------------------------------

    p999 = df["Q_ls"].quantile(0.999)

    df.loc[df["Q_ls"] > p999, "Q_ls"] = np.nan

    # ------------------------------------------------------
    # DETECTAR SALTOS IRREALES
    # ------------------------------------------------------

    df["diff_q"] = df["Q_ls"].diff().abs()

    umbral = df["diff_q"].mean() + 6 * df["diff_q"].std()

    df.loc[df["diff_q"] > umbral, "Q_ls"] = np.nan

    df.drop(columns="diff_q", inplace=True)

    # ------------------------------------------------------
    # DETECTAR SENSOR TRABADO
    # (valores repetidos largos)
    # ------------------------------------------------------

    df["rep"] = df["Q_ls"].diff() == 0

    rep_count = df["rep"].rolling(20).sum()

    df.loc[rep_count == 20, "Q_ls"] = np.nan

    df.drop(columns="rep", inplace=True)

    # ------------------------------------------------------
    # CONVERSION A m3/s
    # ------------------------------------------------------

    df["Q_m3s"] = df["Q_ls"] / 1000.0

    # ------------------------------------------------------
    # GUARDAR SERIE QC 5 MIN
    # ------------------------------------------------------

    path_5min = os.path.join(DATA_PROCESADA, f"Q_{estacion}_5min_qc.csv")

    df.to_csv(path_5min, index=False)

    # ------------------------------------------------------
    # AGREGAR A DIARIO
    # ------------------------------------------------------

    df["fecha_dia"] = df["fecha"].dt.date

    df_diario = df.groupby("fecha_dia")["Q_m3s"].mean()

    df_diario.index = pd.to_datetime(df_diario.index)

    # ------------------------------------------------------
    # COMPLETAR CALENDARIO
    # ------------------------------------------------------

    rango = pd.date_range(
        start=PERIODO_INICIO,
        end=PERIODO_FIN,
        freq="D"
    )

    df_diario = df_diario.reindex(rango)

    df_out = pd.DataFrame({
        "fecha": df_diario.index,
        "Q_m3s": df_diario.values
    })

    # ------------------------------------------------------
    # GUARDAR SERIE DIARIA
    # ------------------------------------------------------

    path_diario = os.path.join(
        DATA_PROCESADA,
        f"Q_{estacion}_diario_m3s.csv"
    )

    df_out.to_csv(path_diario, index=False)

    # ------------------------------------------------------
    # REPORTE
    # ------------------------------------------------------

    print("\nResumen QC")

    total = len(df)
    validos = df["Q_m3s"].notna().sum()

    print("Registros 5 min:", total)
    print("Registros válidos:", validos)

    print("\nSerie diaria")

    print("Días totales:", len(df_out))
    print("Días con datos:", df_out["Q_m3s"].notna().sum())

    print("Q promedio (m3/s):", round(df_out["Q_m3s"].mean(), 4))
    print("Q máximo (m3/s):", round(df_out["Q_m3s"].max(), 4))

print("\nPROCESAMIENTO COMPLETADO")