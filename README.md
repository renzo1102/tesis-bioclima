## Influencia de los parámetros bioclimáticos en el caudal de las unidades hidrográficas Matoc y Pocco, Recuay, 2012–2022

---

**Autor:** Renzo Mendoza  

**Tesis de pregrado – Facultad de Ciencias del Ambiente**  
**Centro de Investigación en Ciencias de la Tierra, Ambiente y Tecnología (ESAT-FCAM)** 
Universidad Nacional Santiago Antúnez de Mayolo (UNASAM), Huaraz, Perú  

---

## Descripción

Este repositorio contiene el flujo completo de procesamiento ecohidrológico desarrollado para analizar la influencia de variables bioclimáticas sobre el comportamiento del caudal mensual en las unidades hidrográficas Matoc y Pocco.

El estudio integra información satelital, observacional y modelamiento hidrológico mediante scripts reproducibles en Python y Google Earth Engine. La metodología permite construir series hidroclimáticas consistentes, evaluar relaciones estadísticas multivariables y simular el régimen hidrológico mensual.

Variables analizadas:

- Índice de Vegetación de Diferencia Normalizada (NDVI)  
- Temperatura del aire (MERRA-2)  
- Precipitación observada (ANA) y satelital (CHIRPS)  
- Caudal observado  
- Caudal modelado mediante GR2M y Lutz-Scholz  

---

## Objetivo

Evaluar la influencia de los parámetros bioclimáticos sobre la variabilidad hidrológica mensual en las microcuencas Matoc y Pocco mediante la integración de datos climáticos, satelitales y modelamiento hidrológico conceptual.

---

## Área de estudio

Unidades hidrográficas Matoc y Pocco, provincia de Recuay, región Áncash, Perú.  
Periodo de análisis: 2012 – 2022.

---

## Estructura del repositorio

```
tesis-bioclimatica/
│
├── README.md
├── requirements.txt
│
├── data/
│   ├── raw/
│   └── processed/
│
├── scripts/
│   ├── 01_Bioclimatic/
│   │   ├── NDVI/
│   │   ├── Precipitation/
│   │   └── Temperature/
│   │
│   ├── 02_Hydrology/
│   ├── 03_Statistics/
│   ├── 04_Diagnostics/
│   └── 05_Figuras_Mapas/
│
├── outputs/
│   ├── series/
│   ├── figures/
│   └── tables/
│
└── LICENSE
```

---

## Requisitos

- Python ≥ 3.9  
- Cuenta activa en Google Earth Engine  
- Librerías listadas en `requirements.txt`

Instalación:

```bash
pip install -r requirements.txt
```

---

## Flujo de trabajo

### Procesamiento bioclimático

**Temperatura**

- `01_extract_merra_temperature.py`  
- `02_temperature_monthly_aggregation.py`  

**Precipitación**

- `01_qc_precipitation_daily.py`  
- `02_post_qc_processing_precip.py`  
- `03_post_qc_diagnosis_precip.py`  
- `04_precipitation_monthly_aggregation.py`  
- `05_build_monthly_catchment_series.py`  
- `06_regional_precip_analysis.py`  
- `07_download_chirps_monthly_gee.py`  
- `08_validate_chirps_monthly.py`  
- `09_bias_correct_chirps_monthly.py`  
- `10_hierarchical_gap_filling_precip.py`  
- `11_cross_validation_precip.py`  

**NDVI**

- `01_build_ndvi_collection_gee.py`  
- `02_extract_ndvi_timeseries.py`  
- `03_ndvi_timeseries_diagnosis.py`  
- `04_interpolate_ndvi.py`  
- `05_ndvi_statistical_analysis.py`  
- `06_ndvi_qualitative_classification.py`  
- `07_export_ndvi_rasters.py`  

---

### Procesamiento hidrológico

- `01_check_streamflow_structure.py`  
- `02_process_raw_streamflow.py`  
- `03_qc_streamflow_level.py`  
- `04_post_qc_streamflow_processing.py`  
- `05_streamflow_monthly_aggregation.py`  
- `06_verify_monthly_streamflow.py`  
- `07_process_ana_streamflow.py`  

- `08_compute_pet_thornthwaite.py`  

- `09_prepare_hydrological_dataset.py`  

- `10_calibrate_gr2m.py`  
- `11_validate_gr2m.py`  
- `12_calibrate_lutz_scholz.py`  
- `13_compare_hydrological_models.py`  

- `14_run_final_hydrological_simulation.py`  
- `15_build_final_streamflow_series.py`  

- `16_regional_hydrological_validation.py`  
- `17_streamflow_data_completeness.py`  
- `18_hydrological_correlation_analysis.py`  
- `19_hydrological_regime_diagnosis.py`  
- `20_precip_streamflow_lag_analysis.py`  

---

### Análisis estadístico

- `01_load_dataset.py`  
- `02_descriptive_statistics.py`  
- `03_compute_correlations.py`  
- `04_spearman_kendall_analysis.py`  
- `05_multivariate_ols_models.py`  
- `06_theilsen_models.py`  

---

### Diagnósticos estadísticos

- `01_vif_analysis.py`  
- `02_residual_analysis.py`  
- `03_normality_tests.py`  

---

### Generación de figuras

Los scripts en `05_Figuras_Mapas/` generan paneles científicos, mapas ecohidrológicos y visualizaciones finales del análisis.

---

## Datos de entrada

- Landsat 7, 8 y 9  
- Sentinel-2  
- CHIRPS  
- MERRA-2  
- Estaciones meteorológicas ANA  
- Registros de caudal  
- Shapefiles de unidades hidrográficas  

---

## Resultados generados

- Series hidroclimáticas mensuales consolidadas  
- Dataset ecohidrológico integrado  
- Evaluación del desempeño hidrológico  
- Correlaciones bioclimáticas multivariables  
- Validación regional del régimen hidrológico  
- Figuras científicas reproducibles  

---

## Reproducibilidad

El análisis es completamente reproducible ejecutando los scripts siguiendo el orden lógico indicado por la numeración dentro de cada carpeta.

El flujo metodológico general comprende:

1. Procesamiento bioclimático  
2. Construcción del dataset hidrológico  
3. Calibración y validación de modelos hidrológicos  
4. Integración estadística multivariable  
5. Diagnósticos de supuestos  
6. Generación de resultados y figuras finales  

Todos los outputs intermedios se almacenan en la carpeta `outputs/`, permitiendo verificar y reutilizar cada etapa del procesamiento.

---

## Citación

Mendoza, R. (2026).  
*Influencia de los parámetros bioclimáticos en el caudal de las unidades hidrográficas Matoc y Pocco, Recuay, 2012-2022.*  
Tesis de pregrado. Facultad de Ciencias del Ambiente.  
Universidad Nacional Santiago Antúnez de Mayolo (UNASAM), Huaraz, Perú.

---

## Licencia

MIT License  

---

## Contacto

Renzo Mendoza  
Facultad de Ciencias del Ambiente  
Centro de Investigación en Ciencias de la Tierra, Ambiente y Tecnología (ESAT-FCAM)  
Universidad Nacional Santiago Antúnez de Mayolo (UNASAM)  
