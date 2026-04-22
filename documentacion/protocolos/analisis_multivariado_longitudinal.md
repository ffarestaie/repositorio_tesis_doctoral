# Análisis multivariado longitudinal de conducta

## Objetivo

Cuantificar y visualizar la estructura multivariada de variables conductuales derivadas de un sistema de tracking automático en un diseño longitudinal, y evaluar si los datos se organizan en clústeres conductuales discretos o en un gradiente continuo de variación entre grupos y a lo largo del tiempo.

## Material de entrada / insumos

- archivo `.xlsx` con una única hoja que contenga el dataset completo;
- cada fila debe corresponder a una observación `animal × semana`;
- el diseño contempla 6 semanas de seguimiento por animal.

## Procedimiento

### Etapa 1. Carga y validación del dataset

1. Cargar el archivo `.xlsx`.
2. Verificar la presencia de las columnas de metadata requeridas.
3. Confirmar que `semana` contenga valores enteros entre 1 y 6.
4. Definir como variables candidatas todas las columnas no incluidas en la metadata.

### Etapa 2. Filtrado de variables

1. Calcular la varianza de cada variable en el dataset completo.
2. Eliminar las variables ubicadas por debajo del percentilo 10 de varianza.
3. Calcular la matriz de correlación entre las variables retenidas.
4. Identificar pares con correlación absoluta `|r| > 0.95`.
5. Resolver redundancia eliminando iterativamente la variable con mayor correlación absoluta media respecto del resto hasta que no queden pares por encima del umbral.

### Etapa 3. Escalado

1. Definir como subconjunto de referencia los animales `SHAM` en `semana 1`.
2. Calcular, para cada variable retenida, la media y el desvío estándar en ese subconjunto.
3. Estandarizar todas las observaciones mediante `z-score` usando esos parámetros de referencia.

### Etapa 4. Control descriptivo y detección de valores extremos

1. Generar resúmenes descriptivos por variable.
2. Inspeccionar distribuciones por semana.
3. Identificar valores extremos mediante aproximación robusta basada en `MAD`.
4. No excluir valores automáticamente; documentarlos para evaluación de sensibilidad.

### Etapa 5. PCA

1. Ajustar el análisis de componentes principales utilizando únicamente las observaciones de `semana 1`.
2. Retener el número mínimo de componentes necesario para explicar al menos 80% de la varianza acumulada.
3. Proyectar todas las observaciones de `semana 1` a `semana 6` en ese espacio PCA definido en línea de base.

### Etapa 6. Selección de K y clustering difuso

1. Evaluar valores candidatos de `K` en el rango 2–8 utilizando únicamente los datos de `semana 1`.
2. Para cada `K`, calcular `WSS` y `silhouette`.
3. Seleccionar `K` con base en ambos criterios e interpretabilidad.
4. Ajustar un modelo de `fuzzy c-means` en el espacio PCA utilizando `m = 2.0`.
5. Guardar las probabilidades de pertenencia de cada observación a cada clúster.
6. Definir una asignación dura derivada como el clúster con mayor probabilidad de pertenencia.
7. En el flujo principal, la estructura de clústeres se entrena en `semana 1` y las semanas posteriores se proyectan usando esos centroides de referencia.

### Etapa 7. Métricas derivadas

1. Identificar el clúster de referencia o `clúster sano` como aquel con mayor probabilidad agregada de pertenencia entre los animales `SHAM` de `semana 1`.
2. Calcular, para cada animal, el cambio de pertenencia al clúster de referencia entre `semana 1` y `semana 6`.

## Análisis computacional

El pipeline integra reducción de dimensionalidad, clustering difuso y métricas derivadas de pertenencia. El análisis se ancla en la línea de base, definida por `semana 1`, y utiliza ese espacio de referencia para proyectar la trayectoria longitudinal de cada observación.

## Métricas generadas

1. **Probabilidades de pertenencia**: pertenencia difusa de cada observación a cada clúster.
2. **Asignación dura de clúster**: clúster de máxima pertenencia por observación.
3. **Cambio de pertenencia al clúster de referencia (`ΔP_sano`)**.

## Parámetros críticos

- El subconjunto de referencia para escalado debe mantenerse fijo en `SHAM semana 1`.
- El PCA debe ajustarse en `semana 1` y luego proyectarse sobre el resto de las semanas.
- El umbral de varianza por defecto es percentilo 10.
- El umbral de correlación es `|r| > 0.95`.
- El rango de evaluación de `K` es 2–8.
- El parámetro de `fuzziness` es `m = 2.0`.

## Control de calidad

Verificar integridad de la estructura del dataset, cantidad esperada de observaciones por animal, ausencia de errores en `semana`, presencia de metadata completa y consistencia de datos faltantes. Inspeccionar la distribución de variables antes y después del filtrado, revisar la varianza explicada por el PCA y controlar la estabilidad de la selección de `K` mediante `WSS` y `silhouette`.

## Salida

- tablas con dataset filtrado;
- dataset escalado;
- scores y loadings de PCA;
- probabilidades de pertenencia;
- asignación dura;
- métricas de cambio longitudinal;

Figuras de apoyo:

- mapas de correlación;
- distribución de varianzas;
- scree plot;
- proyecciones PCA;
- selección de `K`;
- trayectorias de pertenencia;
- visualizaciones de clústeres.
