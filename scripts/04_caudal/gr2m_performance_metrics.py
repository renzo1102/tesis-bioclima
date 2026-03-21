"""
Script: gr2m_performance_metrics.py

Descripción:
Evalúa desempeño del modelo mediante diagnóstico de rezago hidrológico
entre precipitación y caudal observado.

Entradas:
Series mensuales simuladas y observadas del modelo hidrológico

Salidas:
Correlaciones lluvia–caudal con distintos rezagos temporales
y tabla resumen del rezago dominante.

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
# Se define el directorio base del proyecto para permitir
# ejecución reproducible del análisis hidrológico.

BASE_DIR = Path(__file__).resolve().parents[1]

# Carpeta donde se encuentran resultados del modelo hidrológico
DATA_MODEL = BASE_DIR / "data_model"

# Carpeta donde se guardarán tablas diagnósticas
OUTPUT_TABLAS = BASE_DIR / "outputs" / "tablas"

OUTPUT_TABLAS.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------
# UNIDADES HIDROLÓGICAS
# ----------------------------------------------------------
# Lista de microcuencas o unidades hidrológicas analizadas.

UH_LIST = ["Matoc", "Pocco"]

# ----------------------------------------------------------
# RESULTADOS
# ----------------------------------------------------------
# Lista donde se almacenarán resultados del análisis de rezago.

resultados = []

# ----------------------------------------------------------
# PROCESAMIENTO
# ----------------------------------------------------------
# Se realiza análisis independiente para cada unidad hidrológica.

for uh in UH_LIST:

    print("\n------------------------------------")
    print("Procesando UH:", uh)
    print("------------------------------------")

    archivo = DATA_MODEL / f"modelo_{uh}.csv"

    # control de existencia del archivo
    if not archivo.exists():
        print("⚠ Archivo no encontrado:", archivo)
        continue

    # lectura de datos mensuales del modelo
    df = pd.read_csv(
        archivo,
        parse_dates=["fecha"]
    )

    # asegurar variables numéricas hidrológicas
    df["P_mm"] = pd.to_numeric(
        df["P_mm"],
        errors="coerce"
    )

    df["Q_mm"] = pd.to_numeric(
        df["Q_mm"],
        errors="coerce"
    )

    # ------------------------------------------------------
    # CREAR REZAGOS
    # ------------------------------------------------------
    # Se generan variables de precipitación desplazadas en el
    # tiempo para evaluar respuesta retardada del caudal.
    #
    # Interpretación hidrológica:
    # P_t  → lluvia del mismo mes
    # P_t1 → lluvia 1 mes antes
    # P_t2 → lluvia 2 meses antes
    # P_t3 → lluvia 3 meses antes

    df["P_t"]  = df["P_mm"]
    df["P_t1"] = df["P_mm"].shift(1)
    df["P_t2"] = df["P_mm"].shift(2)
    df["P_t3"] = df["P_mm"].shift(3)

    # eliminar meses sin caudal válido
    df_valid = df.dropna(subset=["Q_mm"])

    # ------------------------------------------------------
    # CORRELACIONES
    # ------------------------------------------------------
    # Se calcula correlación de Pearson entre caudal mensual
    # y precipitación con distintos rezagos.

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
    # Se identifica el rezago con mayor correlación positiva.
    #
    # Esto permite inferir:
    # ✔ tiempo de respuesta de la cuenca
    # ✔ almacenamiento subsuperficial
    # ✔ persistencia hidrológica mensual

    correlaciones = {
        "P_t": corr_t,
        "P_t1": corr_t1,
        "P_t2": corr_t2,
        "P_t3": corr_t3
    }

    mejor = max(
        correlaciones,
        key=correlaciones.get
    )

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
# Se construye tabla comparativa final entre unidades hidrológicas.

tabla = pd.DataFrame(resultados)

salida = OUTPUT_TABLAS / "tabla_rezago_hidrologico.csv"

tabla.to_csv(
    salida,
    index=False
)

print("\n====================================")
print("TABLA DE REZAGO GUARDADA")
print(salida)
print("====================================")
