# ======================================================
# FASE 12A
# PROCESAR CAUDAL ANA
# diario -> mensual
# ======================================================

import pandas as pd
import os

ruta_base = r"C:\BRIGHIT_LILA\Rk\Tesis\3_Caudal\3_Proyecto_visual\Caudal_modelo"

data_postqc = os.path.join(ruta_base,"data_postqc")
outputs = os.path.join(ruta_base,"outputs")

archivo = os.path.join(data_postqc,"ANA_diario_postqc.csv")

df = pd.read_csv(archivo)

df["fecha"] = pd.to_datetime(df["fecha"])

# -----------------------------
# mensualizar
# -----------------------------

df["anio"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month

df_mensual = df.groupby(["anio","mes"]).agg({

    "Q_m3s":"mean"

}).reset_index()

df_mensual["fecha"] = pd.to_datetime(dict(year=df_mensual.anio,month=df_mensual.mes,day=1))

# -----------------------------
# caudal normalizado
# -----------------------------

Qmedio = df_mensual["Q_m3s"].mean()

df_mensual["Q_norm"] = df_mensual["Q_m3s"] / Qmedio

# -----------------------------
# guardar
# -----------------------------

archivo_out = os.path.join(outputs,"ANA_mensual_normalizado.csv")

df_mensual.to_csv(archivo_out,index=False)

print("Serie ANA procesada")
print("Guardado en:",archivo_out)