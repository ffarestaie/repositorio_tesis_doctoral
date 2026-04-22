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
