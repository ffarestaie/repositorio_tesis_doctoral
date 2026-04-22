# analisis_estadistico_general.py

## Descripción

Este script implementa un workflow estadístico general para métricas derivadas de los análisis de la tesis. Incluye validación estructural del dataset, tablas descriptivas, ANOVA factorial, modelos lineales mixtos, chequeo de supuestos sobre residuos, comparaciones post hoc con Tukey cuando hay interacción y exportación de resultados.

## Input

- archivo `.csv` o `.xlsx` con el dataset curado;
- una columna de identificación de animal;
- una columna numérica con la métrica a analizar;
- columnas categóricas correspondientes a los factores experimentales del diseño.

## Output

- archivo `.json` con metadata de la corrida;
- archivo `.txt` con resumen de resultados;
- archivo `.xlsx` con tablas descriptivas, tablas de diseño, ANOVA, efectos fijos del LMM, chequeo de supuestos, intentos de ajuste del LMM y tablas post hoc cuando correspondan.
