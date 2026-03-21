"""
Script: gr2m_performance_metrics.py

Descripción:
Evalúa desempeño del modelo

Entradas:
Q simulado

Salidas:
NSE, RMSE, etc.

Autor: Renzo Mendoza
Año: 2026
"""
# ==========================================================
# SCRIPT 13
# FASE 7C
# DIAGNÓSTICO DE REZAGO HIDROLÓGICO
# ==========================================================

import pandas as pd
from pathlib import Path

print("\n====================================")
print("FASE 7C - REZAGO HIDROLÓGICO")
print("====================================")

# ----------------------------------------------------------
# RUTAS
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_MODEL = BASE_DIR / "data_model"
OUTPUT_TABLAS = BASE_DIR / "outputs" / "tablas"

OUTPUT_TABLAS.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------
# UNIDADES HIDROLÓGICAS
# ----------------------------------------------------------

UH_LIST = ["Matoc", "Pocco"]

# ----------------------------------------------------------
# RESULTADOS
# ----------------------------------------------------------

resultados = []

# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------

for uh in UH_LIST:

    print("\n------------------------------------")
    print("Procesando UH:", uh)
    print("------------------------------------")

    archivo = DATA_MODEL / f"modelo_{uh}.csv"

    if not archivo.exists():
        print("⚠ Archivo no encontrado:", archivo)
        continue

    df = pd.read_csv(archivo, parse_dates=["fecha"])

    # asegurar numéricos
    df["P_mm"] = pd.to_numeric(df["P_mm"], errors="coerce")
    df["Q_mm"] = pd.to_numeric(df["Q_mm"], errors="coerce")

    # ------------------------------------------------------
    # CREAR REZAGOS
    # ------------------------------------------------------

    df["P_t"]  = df["P_mm"]
    df["P_t1"] = df["P_mm"].shift(1)
    df["P_t2"] = df["P_mm"].shift(2)
    df["P_t3"] = df["P_mm"].shift(3)

    # eliminar filas sin Q
    df_valid = df.dropna(subset=["Q_mm"])

    # ------------------------------------------------------
    # CORRELACIONES
    # ------------------------------------------------------

    corr_t  = df_valid[["P_t","Q_mm"]].dropna().corr().iloc[0,1]
    corr_t1 = df_valid[["P_t1","Q_mm"]].dropna().corr().iloc[0,1]
    corr_t2 = df_valid[["P_t2","Q_mm"]].dropna().corr().iloc[0,1]
    corr_t3 = df_valid[["P_t3","Q_mm"]].dropna().corr().iloc[0,1]

    print("P(t)   vs Q:", round(corr_t,3))
    print("P(t-1) vs Q:", round(corr_t1,3))
    print("P(t-2) vs Q:", round(corr_t2,3))
    print("P(t-3) vs Q:", round(corr_t3,3))

    # ------------------------------------------------------
    # MEJOR REZAGO
    # ------------------------------------------------------

    correlaciones = {
        "P_t": corr_t,
        "P_t1": corr_t1,
        "P_t2": corr_t2,
        "P_t3": corr_t3
    }

    mejor = max(correlaciones, key=correlaciones.get)

    print("Mejor rezago:", mejor)

    # ------------------------------------------------------
    # GUARDAR RESULTADOS
    # ------------------------------------------------------

    resultados.append({
        "UH": uh,
        "corr_P_t": round(corr_t,3),
        "corr_P_t1": round(corr_t1,3),
        "corr_P_t2": round(corr_t2,3),
        "corr_P_t3": round(corr_t3,3),
        "mejor_rezago": mejor
    })

# ----------------------------------------------------------
# TABLA RESULTADOS
# ----------------------------------------------------------

tabla = pd.DataFrame(resultados)

salida = OUTPUT_TABLAS / "tabla_rezago_hidrologico.csv"

tabla.to_csv(salida, index=False)

print("\n====================================")
print("TABLA DE REZAGO GUARDADA")
print(salida)
print("====================================")
