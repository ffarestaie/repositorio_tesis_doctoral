# Análisis estadísticos

## Objetivo

Estandarizar el análisis estadístico de datasets curados por experimento, generando visualizaciones de validación, chequeo de supuestos, ANOVA como modelo principal y confirmación mediante modelos lineales mixtos (LMM) considerando el anidamiento de mediciones dentro de animal.

## Material de entrada / insumos

- dataset curado por experimento en formato tabular;
- una corrida por métrica;
- columna `animal`;
- factores experimentales definidos para cada análisis;
- columna numérica correspondiente a la métrica de interés;
- script `analisis_estadistico_general.py`.

## Procedimiento

### Etapa 1. Ingesta y validación de estructura

1. Cargar el dataset.
2. Verificar la presencia de las columnas mínimas requeridas:
   - `animal`;
   - factores experimentales definidos para el análisis;
   - columna de la métrica;
   - `cell_id`, si está disponible.
3. Convertir tipos de datos según corresponda:
   - `animal` como categórica;
   - factores como categóricas;
   - métrica como numérica.

### Etapa 2. Control de calidad estructural

1. Calcular el número de mediciones por animal y por condición.
2. Identificar animales subrepresentados o sobrerrepresentados.
3. Cuantificar datos faltantes por columna y por condición.
4. Marcar posibles valores extremos sin eliminarlos automáticamente.
5. Registrar exclusiones manuales, si las hubiera.

### Etapa 3. Visualización de validación

1. Generar gráficos `bar + dots` por medición.
2. Generar gráficos tipo `raincloud`.
3. Generar gráficos `spaghetti` cuando exista pareamiento real a nivel animal.
4. Generar gráficos de medias por animal.

### Etapa 4. Chequeo de supuestos

1. Evaluar normalidad y homocedasticidad sobre los residuos del modelo, no sobre los datos crudos.
2. Generar:
   - gráfico QQ de residuos;
   - prueba de Shapiro sobre residuos;
   - prueba de Levene;

### Etapa 5. Modelado estadístico

1. Ajustar un modelo ANOVA a nivel de medición utilizando la combinación de factores experimentales correspondiente.
2. Ajustar un modelo lineal mixto confirmatorio con la misma estructura de efectos fijos y, como mínimo, un intercepto aleatorio por animal: `(1 | animal)`.
3. Comparar ambos niveles de inferencia para evaluar la robustez del resultado.

### Etapa 6. Comparaciones post hoc

1. Aplicar comparaciones post hoc con corrección de Tukey cuando corresponda.
2. No realizar post hoc cuando un factor tenga dos niveles y no exista interacción relevante.
3. Si hay interacción significativa, descomponer en efectos simples y corregir con Tukey.
4. Si un factor tiene más de dos niveles, realizar comparaciones por pares con corrección de Tukey.

## Criterio general de interpretación

- Si ANOVA y LMM concuerdan, el resultado se considera robusto.
- Si solo ANOVA resulta significativo, se prioriza la interpretación del LMM por posible inflación asociada al anidamiento.

## Modelos utilizados

### EXP-001

- modelo ANOVA: `metric ~ hemisphere * week`
- modelo LMM: `metric ~ hemisphere * week + (1 | animal)`

### EXP-002

Sin subtipo celular:
- modelo ANOVA: `metric ~ tratamiento1 * tratamiento2`
- modelo LMM: `metric ~ tratamiento1 * tratamiento2 + (1 | animal)`

Con subtipo celular:
- modelo ANOVA: `metric ~ tratamiento1 * tratamiento2 * msn_subtype`
- modelo LMM: `metric ~ tratamiento1 * tratamiento2 * msn_subtype + (1 | animal)`

## Outputs esperados

- tablas de conteo y faltantes;
- archivo de marcas de outliers;
- gráficos de validación y QC;
- tabla ANOVA;
- tabla de efectos del LMM;
- tablas de comparaciones post hoc cuando apliquen;
- resumen final por métrica.

## Parámetros críticos

- La unidad biológica superior es el animal.
- Los LMM deben incluir al menos un intercepto aleatorio por animal.
- Los supuestos se evalúan sobre residuos.
- Los valores extremos se marcan, pero no se eliminan automáticamente.
- Las comparaciones post hoc se corrigen con Tukey.

## Control de calidad

Verificar consistencia estructural del dataset, balance de observaciones por animal, faltantes, plausibilidad de la distribución de la métrica, diagnóstico de residuos y coherencia entre ANOVA y LMM.

## Scripts asociados

- `scripts_python/analisis_estadistico_general.py`
