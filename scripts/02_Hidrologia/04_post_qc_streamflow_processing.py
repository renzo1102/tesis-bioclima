# ==========================================================
# FASE 2
# POST-QC – SERIE LIMPIA PARA MODELACIÓN
# Periodo de estudio: 2012–2022
# ==========================================================

import pandas as pd
from pathlib import Path
import numpy as np

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_DIR = BASE_DIR / "data_qc"
OUTPUT_DIR = BASE_DIR / "data_postqc"

OUTPUT_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------
# ARCHIVOS
# ----------------------------------------------------------

archivos = [
    "Q_Matoc_diario_m3s_qc.csv",
    "Q_Pocco_diario_m3s_qc.csv"
]

resumen = []

# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------

for nombre_archivo in archivos:

    archivo = INPUT_DIR / nombre_archivo

    print("\n-----------------------------------")
    print("Procesando:", archivo.name)

    df = pd.read_csv(archivo)

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["Q_m3s"] = pd.to_numeric(df["Q_m3s"], errors="coerce")

    total_estudio = len(df)

    # ------------------------------------------------------
    # REGLAS FISICAS
    # ------------------------------------------------------

    df.loc[df["Q_m3s"] < 0, "Q_m3s"] = np.nan

    if "flag_negativo" in df.columns:
        df.loc[df["flag_negativo"], "Q_m3s"] = np.nan

    # ------------------------------------------------------
    # ESTADISTICAS PERIODO OBSERVADO
    # ------------------------------------------------------

    datos_observados = df["Q_m3s"].notna().sum()

    revisar = 0
    if "estado_qc" in df.columns:
        revisar = (df["estado_qc"] == "REVISAR").sum()

    periodo_observado = datos_observados + revisar

    faltantes_estudio = total_estudio - datos_observados

    pct_completitud_obs = round(datos_observados / periodo_observado * 100, 2) if periodo_observado > 0 else 0

    pct_faltantes_estudio = round(faltantes_estudio / total_estudio * 100, 2)

    # ------------------------------------------------------
    # CALIDAD REAL DE LA ESTACION
    # ------------------------------------------------------

    if pct_completitud_obs > 95:
        calidad = "EXCELENTE"
    elif pct_completitud_obs > 90:
        calidad = "BUENA"
    elif pct_completitud_obs > 80:
        calidad = "ACEPTABLE"
    else:
        calidad = "BAJA"

    print("Periodo estudio (días):", total_estudio)
    print("Periodo observado:", periodo_observado)
    print("Datos válidos:", datos_observados)

    print("Completitud observada:", pct_completitud_obs, "%")

    print("Faltantes periodo estudio:", faltantes_estudio,
          f"({pct_faltantes_estudio}%)")

    print("Calidad estación:", calidad)

    # ------------------------------------------------------
    # DATASET FINAL LIMPIO
    # ------------------------------------------------------

    df_final = df[["fecha", "Q_m3s"]]

    salida = OUTPUT_DIR / f"{archivo.stem.replace('_qc','')}_postqc.csv"

    df_final.to_csv(salida, index=False)

    print("Serie guardada en:", salida)

    resumen.append({
        "archivo": archivo.name,
        "periodo_estudio_dias": total_estudio,
        "periodo_observado_dias": periodo_observado,
        "datos_validos": datos_observados,
        "faltantes_periodo_estudio": faltantes_estudio,
        "pct_completitud_observada": pct_completitud_obs,
        "pct_faltantes_periodo_estudio": pct_faltantes_estudio,
        "calidad_estacion": calidad
    })

# ----------------------------------------------------------
# RESUMEN FINAL
# ----------------------------------------------------------

resumen_df = pd.DataFrame(resumen)

resumen_path = OUTPUT_DIR / "resumen_postqc.csv"

resumen_df.to_csv(resumen_path, index=False)

print("\n===================================")
print("POST-QC FINALIZADO")
print("Resumen guardado en:")
print(resumen_path)
print("===================================")