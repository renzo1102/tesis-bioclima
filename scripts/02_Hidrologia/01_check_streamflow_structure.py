import os
import pandas as pd
import numpy as np

# ===============================
# CONFIGURACIÓN GENERAL
# ===============================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data_raw")
OUTPUT_DIR = os.path.join(BASE_DIR, "data_precheck")

os.makedirs(OUTPUT_DIR, exist_ok=True)

START_DATE = pd.to_datetime("2012-01-01")
END_DATE = pd.to_datetime("2022-12-31")

# ===============================
# FUNCIÓN PRINCIPAL DE ANÁLISIS
# ===============================

def analizar_archivo(filepath):

    print(f"\nAnalizando: {os.path.basename(filepath)}")

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
        return None

    reporte = {}
    reporte["archivo"] = os.path.basename(filepath)
    reporte["registros_totales"] = len(df)

    # ---------------------------
    # Verificación columna fecha
    # ---------------------------

    if "fecha" not in df.columns:
        reporte["error"] = "No existe columna fecha"
        return reporte

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    reporte["fechas_invalidas"] = df["fecha"].isna().sum()
    reporte["duplicados"] = df.duplicated(subset=["fecha"]).sum()

    fecha_min = df["fecha"].min()
    fecha_max = df["fecha"].max()

    reporte["fecha_min"] = fecha_min
    reporte["fecha_max"] = fecha_max

    # ---------------------------
    # Cobertura esperada 2012–2022
    # ---------------------------

    rango_esperado = pd.date_range(start=START_DATE, end=END_DATE, freq="D")

    fechas_validas = df["fecha"].dropna().dt.normalize().unique()
    fechas_validas = pd.to_datetime(fechas_validas)

    dias_faltantes = len(set(rango_esperado) - set(fechas_validas))

    reporte["dias_faltantes_2012_2022"] = dias_faltantes

    # ---------------------------
    # Columnas numéricas
    # ---------------------------

    columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()

    rangos = {}
    for col in columnas_numericas:
        rangos[col] = {
            "min": float(df[col].min()) if not df[col].isna().all() else None,
            "max": float(df[col].max()) if not df[col].isna().all() else None,
            "nulos": int(df[col].isna().sum())
        }

    reporte["rangos"] = rangos

    return reporte


# ===============================
# EJECUCIÓN
# ===============================

def main():

    reportes = []

    archivos = [f for f in os.listdir(RAW_DIR) if f.endswith(".csv")]

    if len(archivos) == 0:
        print("⚠ No hay archivos en data_raw/")
        return

    for archivo in archivos:
        filepath = os.path.join(RAW_DIR, archivo)
        reporte = analizar_archivo(filepath)
        if reporte:
            reportes.append(reporte)

    # ---------------------------
    # Guardar resumen CSV
    # ---------------------------

    resumen_simple = []

    for r in reportes:
        resumen_simple.append({
            "archivo": r.get("archivo"),
            "registros_totales": r.get("registros_totales"),
            "fechas_invalidas": r.get("fechas_invalidas"),
            "duplicados": r.get("duplicados"),
            "fecha_min": r.get("fecha_min"),
            "fecha_max": r.get("fecha_max"),
            "dias_faltantes_2012_2022": r.get("dias_faltantes_2012_2022")
        })

    resumen_df = pd.DataFrame(resumen_simple)
    resumen_df.to_csv(os.path.join(OUTPUT_DIR, "resumen_precheck.csv"), index=False)

    # ---------------------------
    # Guardar reporte detallado
    # ---------------------------

    with open(os.path.join(OUTPUT_DIR, "reporte_precheck.txt"), "w", encoding="utf-8") as f:

        for r in reportes:

            f.write(f"Archivo: {r.get('archivo')}\n")
            f.write(f"Registros totales: {r.get('registros_totales')}\n")
            f.write(f"Fechas inválidas: {r.get('fechas_invalidas')}\n")
            f.write(f"Duplicados: {r.get('duplicados')}\n")
            f.write(f"Fecha mínima: {r.get('fecha_min')}\n")
            f.write(f"Fecha máxima: {r.get('fecha_max')}\n")
            f.write(f"Días faltantes (2012–2022): {r.get('dias_faltantes_2012_2022')}\n")

            f.write("Rangos por columna:\n")

            if "rangos" in r:
                for col, valores in r["rangos"].items():
                    f.write(f"  {col}: min={valores['min']}, max={valores['max']}, nulos={valores['nulos']}\n")

            f.write("-" * 60 + "\n")

    print("\n✅ PRECHECK FINALIZADO")
    print("Resultados en carpeta: data_precheck/")


if __name__ == "__main__":
    main()