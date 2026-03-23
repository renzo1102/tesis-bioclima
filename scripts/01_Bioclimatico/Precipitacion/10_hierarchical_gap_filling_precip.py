# ============================================================
# FASE 7 — COMPLETACIÓN JERÁRQUICA 2012–2022 (VERSIÓN FINAL)
# ============================================================
"""
DESCRIPCIÓN GENERAL
------------------------------------------------------------
Este script implementa la fase final de reconstrucción de las
series mensuales de precipitación a nivel de unidad hidrológica (UH),
integrando múltiples fuentes de información bajo un enfoque jerárquico.

El objetivo es obtener una serie continua (sin vacíos) para el periodo
2012–2022, combinando:

1. Datos observados (máxima confiabilidad)
2. Estación de referencia regional (ANA 1) mediante regresión
3. Datos satelitales corregidos (CHIRPS)

El proceso sigue una lógica jerárquica:
    OBSERVADO > REGRESIÓN ANA 1 > CHIRPS CORREGIDO

Esto permite maximizar la calidad de los datos y minimizar la
incertidumbre en la reconstrucción temporal.

------------------------------------------------------------
FLUJO METODOLÓGICO
------------------------------------------------------------
1. Cargar series observadas por UH (FASE 3)
2. Cargar estación de referencia (ANA 1)
3. Cargar CHIRPS corregido (FASE 6)
4. Ajustar modelos de regresión UH vs ANA 1
5. Generar serie temporal completa (2012–2022)
6. Completar valores faltantes jerárquicamente
7. Exportar series finales y resumen de fuentes

------------------------------------------------------------
SUPUESTOS CLAVE
------------------------------------------------------------
- ANA 1 es representativa a escala regional
- La relación UH–ANA 1 es aproximadamente lineal
- CHIRPS corregido es consistente en ausencia de datos observados
- No se permiten valores negativos de precipitación

------------------------------------------------------------
SALIDAS
------------------------------------------------------------
- Series completas por UH
- Ecuaciones de regresión
- Resumen de fuentes de datos utilizadas
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

# ============================================================
# RUTAS RELATIVAS (PORTABLES)
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_MENSUALES = BASE_DIR / "outputs/mensuales"
INPUT_CHIRPS_CORR = BASE_DIR / "outputs/chirps_corregido"
OUTPUT_DIR = BASE_DIR / "outputs/serie_final"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CARGA DE DATOS
# ============================================================

"""
Se cargan tres tipos de datos:

1. Series observadas por UH (sin relleno)
2. Serie de estación regional ANA 1
3. Series CHIRPS previamente corregidas

Todas las series están en resolución mensual.
"""

matoc_obs = pd.read_csv(
    INPUT_MENSUALES / "4_Matoc_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

pocco_obs = pd.read_csv(
    INPUT_MENSUALES / "4_Pocco_UH_mensual_OBS.csv",
    parse_dates=["fecha_mensual"]
)

estaciones = pd.read_csv(
    INPUT_MENSUALES / "mensual_estaciones_2012_2022.csv",
    parse_dates=["fecha_mensual"]
)

# Extraer ANA 1 como predictor regional
ana1 = estaciones[
    estaciones["Estacion"] == "ANA 1"
][["fecha_mensual", "Prec_mensual"]].rename(
    columns={"Prec_mensual": "ANA1"}
)

# Cargar CHIRPS corregido
matoc_ch = pd.read_csv(
    INPUT_CHIRPS_CORR / "CHIRPS_MATOC_corregido.csv",
    parse_dates=["fecha_mensual"]
)

pocco_ch = pd.read_csv(
    INPUT_CHIRPS_CORR / "CHIRPS_POCCO_corregido.csv",
    parse_dates=["fecha_mensual"]
)

# ============================================================
# FUNCIÓN: AJUSTE DE REGRESIÓN LINEAL
# ============================================================

def ajustar_regresion(df_uh, ana1_df, nombre_uh):
    """
    Ajusta un modelo de regresión lineal simple entre la precipitación
    observada de la UH y la estación ANA 1.

    Modelo:
        UH = a + b * ANA1

    Parámetros:
        df_uh   : DataFrame con datos observados de la UH
        ana1_df : DataFrame con datos de ANA 1
        nombre_uh : Nombre de la unidad hidrológica

    Retorna:
        modelo, coeficientes y métricas de ajuste

    Métricas:
        - R²   : capacidad explicativa
        - RMSE : error medio
    """

    df = df_uh.merge(ana1_df, on="fecha_mensual", how="inner")
    df = df.dropna()

    X = df[["ANA1"]].values
    y = df["Prec_UH_OBS"].values

    modelo = LinearRegression()
    modelo.fit(X, y)

    pred = modelo.predict(X)

    r2 = r2_score(y, pred)
    rmse = np.sqrt(mean_squared_error(y, pred))

    a = modelo.intercept_
    b = modelo.coef_[0]

    print(f"\nModelo {nombre_uh}:")
    print(f"UH = {round(a,2)} + {round(b,2)} * ANA1")
    print(f"R2 = {round(r2,3)} | RMSE = {round(rmse,2)}")

    return modelo, a, b, r2, rmse

# ============================================================
# AJUSTE DE MODELOS
# ============================================================

modelo_matoc, a_matoc, b_matoc, r2_matoc, rmse_matoc = ajustar_regresion(
    matoc_obs, ana1, "Matoc"
)

modelo_pocco, a_pocco, b_pocco, r2_pocco, rmse_pocco = ajustar_regresion(
    pocco_obs, ana1, "Pocco"
)

# ============================================================
# GUARDAR ECUACIONES
# ============================================================

"""
Se almacenan los parámetros de regresión para trazabilidad
y reproducibilidad del modelo.
"""

ecuaciones_df = pd.DataFrame([
    {
        "UH": "Matoc",
        "Intercepto_a": a_matoc,
        "Pendiente_b": b_matoc,
        "R2_modelo": r2_matoc,
        "RMSE_modelo": rmse_matoc
    },
    {
        "UH": "Pocco",
        "Intercepto_a": a_pocco,
        "Pendiente_b": b_pocco,
        "R2_modelo": r2_pocco,
        "RMSE_modelo": rmse_pocco
    }
])

ecuaciones_df.to_csv(
    OUTPUT_DIR / "ecuaciones_regresion_ANA1.csv",
    index=False
)

# ============================================================
# BASE TEMPORAL COMPLETA
# ============================================================

"""
Se genera una serie continua mensual para todo el periodo,
independientemente de la disponibilidad de datos.
"""

fechas = pd.date_range("2012-01-01", "2022-12-01", freq="MS")
base = pd.DataFrame({"fecha_mensual": fechas})

# ============================================================
# FUNCIÓN: COMPLETACIÓN JERÁRQUICA
# ============================================================

def completar_serie(base, uh_obs, ana1_df, chirps_df, modelo, nombre_col):
    """
    Completa la serie mensual utilizando un esquema jerárquico:

    Prioridad:
        1. Observado (OBS)
        2. Regresión con ANA 1 (REG_ANA1)
        3. CHIRPS corregido (CHIRPS_CORR)

    Parámetros:
        base        : calendario completo
        uh_obs      : datos observados UH
        ana1_df     : estación regional
        chirps_df   : datos satelitales corregidos
        modelo      : modelo de regresión
        nombre_col  : nombre de columna CHIRPS

    Retorna:
        DataFrame con serie completa y fuente de datos
    """

    df = base.merge(uh_obs, on="fecha_mensual", how="left")
    df = df.merge(ana1_df, on="fecha_mensual", how="left")
    df = df.merge(
        chirps_df[["fecha_mensual", f"{nombre_col}_CORR"]],
        on="fecha_mensual",
        how="left"
    )

    valores = []
    fuentes = []

    for _, row in df.iterrows():

        # 1. Observado
        if not pd.isna(row["Prec_UH_OBS"]):
            valores.append(row["Prec_UH_OBS"])
            fuentes.append("OBS")

        # 2. Regresión
        elif not pd.isna(row["ANA1"]):
            pred = modelo.predict([[row["ANA1"]]])[0]
            valores.append(max(pred, 0))  # evitar negativos
            fuentes.append("REG_ANA1")

        # 3. CHIRPS corregido
        else:
            valores.append(row[f"{nombre_col}_CORR"])
            fuentes.append("CHIRPS_CORR")

    df["Precip_final"] = valores
    df["Fuente"] = fuentes

    return df

# ============================================================
# COMPLETAR SERIES
# ============================================================

matoc_final = completar_serie(
    base, matoc_obs, ana1, matoc_ch, modelo_matoc, "CHIRPS_MATOC"
)

pocco_final = completar_serie(
    base, pocco_obs, ana1, pocco_ch, modelo_pocco, "CHIRPS_POCCO"
)

# ============================================================
# GUARDAR RESULTADOS
# ============================================================

matoc_final.to_csv(
    OUTPUT_DIR / "Matoc_serie_mensual_2012_2022_completa.csv",
    index=False
)

pocco_final.to_csv(
    OUTPUT_DIR / "Pocco_serie_mensual_2012_2022_completa.csv",
    index=False
)

# ============================================================
# RESUMEN DE FUENTES
# ============================================================

def guardar_resumen_fuentes(df, nombre):
    """
    Calcula la proporción de datos provenientes de cada fuente.

    Permite evaluar:
    - Dependencia de datos observados
    - Uso de regresión
    - Uso de CHIRPS
    """

    resumen = df["Fuente"].value_counts()
    total = len(df)

    resumen_df = pd.DataFrame({
        "UH": nombre,
        "Fuente": resumen.index,
        "Meses": resumen.values,
        "Porcentaje_%": (resumen.values / total) * 100
    })

    return resumen_df

res_matoc = guardar_resumen_fuentes(matoc_final, "Matoc")
res_pocco = guardar_resumen_fuentes(pocco_final, "Pocco")

resumen_total = pd.concat([res_matoc, res_pocco])

resumen_total.to_csv(
    OUTPUT_DIR / "resumen_fuentes_completacion.csv",
    index=False
)

# ============================================================
# MENSAJES FINALES
# ============================================================

print("\nFASE 7 COMPLETADA.")
print("Series mensuales completas generadas.")
print("Resumen de fuentes disponible.")
print("Archivos en: outputs/serie_final/")
