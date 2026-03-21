# tesis-bioclima

Análisis bioclimático de NDVI, temperatura, precipitación y caudal

---

# INFLUENCIA DE LOS PARÁMETROS BIOCLIMÁTICOS EN EL CAUDAL DE LAS UNIDADES HIDROGRÁFICAS MATOC Y POCCO, RECUAY, 2012 – 2022

## Descripción

Este repositorio contiene el conjunto completo de scripts desarrollados para el procesamiento y análisis de variables bioclimáticas en las UU.HH. Matoc y Pocco, incluyendo:

- Índice de Vegetación de Diferencia Normalizada (NDVI)
- Temperatura (MERRA-2)
- Precipitación (estaciones ANA y CHIRPS)
- Caudal (datos observados y GR2M)
- Análisis estadístico (correlaciones y tendencias)

El objetivo es evaluar la influencia de los parámetros bioclimáticos en el comportamiento del caudal mediante un enfoque reproducible basado en datos satelitales, observacionales y modelamiento hidrometeorológico.

---

## Estructura del repositorio


```
tesis-bioclima/
│
├── README.md
├── requirements.txt
│
├── data/
│   ├── raw/
│   └── processed/
│
├── scripts/
│   ├── 01_ndvi/
│   ├── 02_temperatura/
│   ├── 03_precipitacion/
│   ├── 04_caudal/
│   └── 05_analisis_integrado/
│
├── outputs/
│   ├── csv/
│   ├── figuras/
│   └── estadisticas/
│
└── LICENSE
```

---

## Requisitos

### Software

- Python 3.9 o superior  
- Cuenta en Google Earth Engine (GEE)  

---

## Instalación

```bash
pip install -r requirements.txt
```

## Flujo de trabajo

### 1. NDVI
- gee_build_ndvi_collection.js  
- gee_extract_ndvi_series.py  
- ndvi_descriptive_analysis.py  
- ndvi_interpolation.py  
- ndvi_trend_analysis.py  
- ndvi_classification.py  

### 2. Temperatura
- merra_temperature_extraction.py  

### 3. Precipitación
- qc_precipitation_daily.py  
- post_qc_precipitation.py  
- precipitation_diagnostics.py  
- precipitation_monthly_aggregation.py  
- precipitation_uh_series.py  
- precipitation_regional_metrics.py  
- chirps_monthly_extraction.js  
- chirps_validation.py  
- chirps_bias_correction.py  
- precipitation_final_dataset.py  
- precipitation_final_validation.py  

### 4. Caudal
- streamflow_raw_processing.py  
- streamflow_quality_control.py  
- streamflow_diagnostics.py  
- streamflow_monthly_aggregation.py  
- streamflow_uh_series.py  
- streamflow_gap_analysis.py  
- streamflow_data_completion.py  
- gr2m_model_definition.py  
- gr2m_parameter_initialization.py  
- gr2m_calibration.py  
- gr2m_validation.py  
- gr2m_simulation.py  
- gr2m_performance_metrics.py  

### 6. Análisis de caudal
- streamflow_trend_analysis.py  
- streamflow_variability_analysis.py  
- streamflow_extreme_events.py  
- streamflow_comparison_observed_vs_simulated.py  
- streamflow_model_validation_summary.py  
- streamflow_regional_analysis.py  
- ana_streamflow_processing.py  
- streamflow_final_dataset.py  

### 7. Análisis integrado
- data_integration_dataset.py  
- correlation_pearson.py  
- correlation_spearman.py  
- correlation_kendall.py  
- multicollinearity_vif.py  
- regression_analysis.py  
- statistical_diagnostics.py  
- final_results_generation.py

## Datos de entrada

- Landsat 7, 8, 9  
- Sentinel-2  
- CHIRPS  
- MERRA-2  
- Estaciones meteorológicas  
- Datos de caudal  
- Shapefiles de microcuencas  

## Resultados

- Series mensuales de NDVI, temperatura, precipitación y caudal  
- Figuras científicas  
- Tablas estadísticas  
- Tendencias climáticas  
- Correlaciones entre variables  
- Resultados del modelo hidrológico  

## Reproducibilidad

El flujo completo puede reproducirse ejecutando los scripts en el orden indicado.

## Citación

Mendoza, R. (2026).
Influencia de los parámetros bioclimáticos en el caudal de las microcuencas Matoc y Pocco.
[Tesis de pregrado].

## Licencia

Licencia MIT

## Contacto

Renzo Mendoza  
Ingeniería Ambiental
