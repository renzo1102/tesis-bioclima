"""
Script: gr2m_simulation.py

Descripción:
Realiza diagnóstico hidrológico del dataset previo a la simulación
del modelo GR2M, evaluando coherencia climática e hidrológica.

Entradas:
Series mensuales de precipitación, evapotranspiración potencial
y caudal observado.

Salidas:
Indicadores hidrológicos resumen y tabla diagnóstica.

Autor: Renzo Mendoza
Año: 2026
"""

# ==========================================================
# SCRIPT 12
# FASE 7B
# DIAGNÓSTICO HIDROLÓGICO DEL DATASET
# ==========================================================

import pandas as pd
from pathlib import Path
import numpy as np

print("\n====================================")
print("FASE 7B - DIAGNÓSTICO HIDROLÓGICO")
print("====================================")

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------
# Se define el directorio base del proyecto para permitir
# ejecución reproducible del análisis.

BASE_DIR = Path(__file__).resolve().parents[1]

# Carpeta con datasets finales preparados para modelación
DATA_MODEL = BASE_DIR / "data_model"

# Carpeta donde se almacenarán tablas diagnósticas
OUTPUT_TABLAS = BASE_DIR / "outputs" / "tablas"

OUTPUT_TABLAS.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------
# UNIDADES HIDROLÓGICAS
# ----------------------------------------------------------
# Lista de microcuencas analizadas.

UH_LIST = ["Matoc", "Pocco"]

# ----------------------------------------------------------
# RESUMEN
# ----------------------------------------------------------
# Lista donde se almacenarán indicadores hidrológicos.

resumen = []

# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------
# Se realiza diagnóstico independiente para cada cuenca.

for uh in UH_LIST:

    print("\n------------------------------------")
    print("Procesando UH:", uh)
    print("------------------------------------")

    archivo = DATA_MODEL / f"modelo_{uh}.csv"

    if not archivo.exists():
        print("⚠ Archivo no encontrado:", archivo)
        continue

    df = pd.read_csv(
        archivo,
        parse_dates=["fecha"]
    )

    # asegurar variables numéricas
    df["P_mm"] = pd.to_numeric(df["P_mm"], errors="coerce")
    df["PET_mm"] = pd.to_numeric(df["PET_mm"], errors="coerce")
    df["Q_mm"] = pd.to_numeric(df["Q_mm"], errors="coerce")

    # ------------------------------------------------------
    # DISPONIBILIDAD DE DATOS
    # ------------------------------------------------------
    # Se evalúa cantidad de meses con información válida.

    total = len(df)

    nP = df["P_mm"].notna().sum()
    nPET = df["PET_mm"].notna().sum()
    nQ = df["Q_mm"].notna().sum()

    print("Meses totales:", total)
    print("Meses con P:", nP)
    print("Meses con PET:", nPET)
    print("Meses con Q:", nQ)

    # ------------------------------------------------------
    # PROMEDIOS HIDROCLIMÁTICOS
    # ------------------------------------------------------
    # Representan condiciones medias de la cuenca.

    P_prom = df["P_mm"].mean(skipna=True)
    PET_prom = df["PET_mm"].mean(skipna=True)
    Q_prom = df["Q_mm"].mean(skipna=True)

    print("\nPromedios mensuales")

    print("P:", round(P_prom, 2), "mm")
    print("PET:", round(PET_prom, 2), "mm")
    print("Q:", round(Q_prom, 2), "mm")

    # ------------------------------------------------------
    # COEFICIENTE DE ESCORRENTÍA
    # ------------------------------------------------------
    # Indica proporción de precipitación que se transforma
    # en caudal superficial.

    coef = np.nan
    if P_prom > 0:
        coef = Q_prom / P_prom

    print("\nCoeficiente escorrentía:",
          round(coef,3) if not np.isnan(coef) else None)

    # ------------------------------------------------------
    # ÍNDICE DE ARIDEZ
    # ------------------------------------------------------
    # PET/P permite evaluar grado de demanda evaporativa.

    aridez = np.nan
    if P_prom > 0:
        aridez = PET_prom / P_prom

    print("Indice aridez PET/P:",
          round(aridez,3) if not np.isnan(aridez) else None)

    # ------------------------------------------------------
    # CORRELACIÓN LLUVIA–CAUDAL
    # ------------------------------------------------------
    # Permite evaluar respuesta hidrológica directa.

    df_valid = df.dropna(
        subset=["P_mm", "Q_mm"]
    )

    corr = np.nan
    if len(df_valid) > 3:
        corr = df_valid["P_mm"].corr(
            df_valid["Q_mm"]
        )

    print("Correlación P-Q:",
          round(corr,3) if not np.isnan(corr) else None)

    # ------------------------------------------------------
    # BALANCE HÍDRICO APROXIMADO
    # ------------------------------------------------------
    # Representa coherencia física de los datos climáticos.

    balance = P_prom - (Q_prom + PET_prom)

    print("Balance aproximado P-(Q+PET):",
          round(balance,2),"mm")

    # ------------------------------------------------------
    # GUARDAR RESUMEN
    # ------------------------------------------------------

    resumen.append({
        "UH": uh,
        "meses_totales": total,
        "meses_con_Q": nQ,
        "P_prom_mm": round(P_prom,2),
        "PET_prom_mm": round(PET_prom,2),
        "Q_prom_mm": round(Q_prom,2),
        "coef_escorrentia": round(coef,3)
            if not np.isnan(coef) else None,
        "indice_aridez_PET_P": round(aridez,3)
            if not np.isnan(aridez) else None,
        "correlacion_P_Q": round(corr,3)
            if not np.isnan(corr) else None,
        "balance_P_Q_PET_mm": round(balance,2)
    })

# ----------------------------------------------------------
# TABLA RESUMEN FINAL
# ----------------------------------------------------------

tabla = pd.DataFrame(resumen)

salida = OUTPUT_TABLAS / "tabla_diagnostico_hidrologico.csv"

tabla.to_csv(
    salida,
    index=False
)

print("\n====================================")
print("TABLA RESUMEN GUARDADA")
print(salida)
print("====================================")
