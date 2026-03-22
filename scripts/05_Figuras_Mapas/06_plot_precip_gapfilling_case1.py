# ============================================================
# FIGURA 2 — DIFERENCIA FINAL - OBSERVADA
# ============================================================

fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

for ax, df, titulo in zip(
    axes,
    [matoc, pocco],
    ["(a) Matoc — Diferencia (Final − OBS)",
     "(b) Pocco — Diferencia (Final − OBS)"]
):

    diff = df["Precip_final"] - df["Prec_UH_OBS"]

    ax.axhline(0, color="black", linewidth=1)
    ax.plot(df["fecha_mensual"], diff,
            color="#e41a1c",
            linewidth=1.5)

    ax.set_title(titulo)
    ax.set_ylabel("Diferencia (mm)")
    ax.grid(alpha=0.25)

axes[1].set_xlabel("Fecha")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "Figura2_Diferencias_Final_OBS.png",
            dpi=600, bbox_inches="tight")
plt.close()

print("Figura 2 generada.")