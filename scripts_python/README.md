# Scripts en Python

Esta carpeta contiene scripts en Python utilizados para cálculo de métricas, análisis multivariado conductual y análisis estadísticos complementarios.

## Contenido

- `analisis_multivariado_longitudinal.py`: análisis multivariado longitudinal de conducta.
- `calcular_cobertura_microglial.py`: cuantificación de cobertura microglial a partir de stacks binarios.
- `calcular_contactos_exp_001.py`: cálculo de métricas de contactos microglia-dendrita para EXP-001.
- `calcular_contactos_exp_002.py`: cálculo de métricas de contactos microglia-dendrita para EXP-002.
- `analisis_estadistico_general.py`: análisis estadísticos generales.

## Uso general

Cada script está asociado a un análisis específico y puede requerir archivos de entrada previamente generados por macros, software de terceros o tablas de metadata.

## Nota

La relación entre estos scripts y los análisis reportados en la tesis se resume en `documentacion/correspondencia_con_tesis.md`.


# Análisis multivariado longitudinal de la conducta

## Descripción

Este script realiza un análisis multivariado longitudinal de variables conductuales derivadas de tracking automático. Incluye filtrado de variables, escalado, detección de valores extremos, reducción de dimensionalidad mediante PCA, clustering difuso y cálculo de métricas derivadas de pertenencia a clústeres.

## Input

- archivo `.xlsx` con una única hoja de datos;
- una fila por observación `animal × semana`;
- columnas de metadata y variables conductuales numéricas.

## Output

- tablas con dataset filtrado y escalado;
- scores y loadings de PCA;
- probabilidades de pertenencia a clústeres;
- asignación dura de clúster;
- métricas de cambio longitudinal;
- figuras de apoyo para visualización y control de calidad.


# Cobertura microglial

## Descripción

Este script cuantifica la cobertura microglial a partir de imágenes TIFF binarias. Calcula la fracción del campo ocupada por señal microglial en cada stack, genera una tabla resumen por archivo, una tabla de control de calidad por slice y un PDF con gráficos exploratorios por animal.

## Input

- carpeta con archivos TIFF binarios;
- archivo `.xlsx` con metadata por animal, incluyendo las columnas `animal` y `semana`.

## Output

- archivo `microglia_coverage_summary.csv` con una fila por imagen;
- archivo `microglia_coverage_per_slice.csv` con una fila por slice;
- archivo `microglia_coverage_plots.pdf` con gráficos exploratorios por animal.
