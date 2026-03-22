import pandas as pd
import os

# ==============================
# CONFIGURACIÓN DE RUTAS
# ==============================

INPUT_FILE = "outputs/post_qc/diario_post_qc_fase1.csv"
OUTPUT_DIR = "outputs/diagnosticos"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==============================
# CARGAR DATOS
# ==============================

print("\nCargando archivo FASE 1...")
df = pd.read_csv(INPUT_FILE, parse_dates=["fecha"])

print(f"Total registros cargados: {len(df)}")

# ==============================
# RESUMEN POR ESTACIÓN (CORREGIDO)
# ==============================

resumen = (
    df.groupby("Estacion")["Precip_postQC"]
    .agg(
        total_registros="size",  # cuenta todo (incluye NA)
        validos=lambda x: x.notna().sum(),
        na=lambda x: x.isna().sum()
    )
)

resumen["%_NA"] = (resumen["na"] / resumen["total_registros"]) * 100
resumen["%_validos"] = (resumen["validos"] / resumen["total_registros"]) * 100

print("\nResumen por estación:")
print(resumen)

resumen.to_csv(
    os.path.join(OUTPUT_DIR, "resumen_estaciones_fase1.csv")
)

# ==============================
# RESUMEN ANUAL
# ==============================

df["anio"] = df["fecha"].dt.year

resumen_anual = (
    df.groupby(["Estacion", "anio"])["Precip_postQC"]
    .apply(lambda x: x.notna().mean() * 100)
    .reset_index(name="%_datos_validos")
)

print("\nResumen anual (% datos válidos por año):")
print(resumen_anual)

resumen_anual.to_csv(
    os.path.join(OUTPUT_DIR, "resumen_anual_fase1.csv"),
    index=False
)

# ==============================
# AÑOS COMPLETAMENTE VACÍOS
# ==============================

anios_vacios = resumen_anual[
    resumen_anual["%_datos_validos"] == 0
]

if len(anios_vacios) > 0:
    print("\n⚠ Años completamente vacíos detectados:")
    print(anios_vacios)
else:
    print("\nNo hay años completamente vacíos.")

# ==============================
# ESTACIONES CRÍTICAS (>70% NA)
# ==============================

estaciones_criticas = resumen[
    resumen["%_NA"] > 70
]

if len(estaciones_criticas) > 0:
    print("\n⚠ Estaciones con más de 70% de NA:")
    print(estaciones_criticas)
else:
    print("\nNo hay estaciones con más de 70% de NA.")

# ==============================
# RESUMEN GLOBAL
# ==============================

total_na = df["Precip_postQC"].isna().sum()
total_global = len(df)

print("\nResumen global:")
print(f"Total NA: {total_na}")
print(f"Porcentaje NA global: {(total_na/total_global)*100:.2f}%")

print("\nDiagnóstico FASE 1 completado.")
print(f"Archivos guardados en: {OUTPUT_DIR}")