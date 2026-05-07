# Análisis estadísticos

## Objetivo

Estandarizar el análisis estadístico de datasets curados por experimento, generando visualizaciones de validación, chequeo de supuestos, ANOVA como modelo principal, análisis complementarios mediante modelos lineales mixtos (LMM) cuando existe anidamiento de mediciones dentro de animal, análisis no paramétricos de sensibilidad cuando corresponde, y análisis de distribuciones categóricas mediante tablas de contingencia.

## Material de entrada / insumos

- dataset curado por experimento en formato tabular;
- una corrida por métrica;
- columna `animal`;
- factores experimentales definidos para cada análisis;
- columna numérica correspondiente a la métrica de interés;
- tabla de recuentos por animal o por grupo para análisis de distribuciones categóricas;
- scripts asociados:
  - `scripts_python/analisis_estadistico_general.py`;
  - `scripts_python/analisis_chi2_contribuciones.py`.

## Procedimiento

### Etapa 1. Ingesta y validación de estructura

1. Cargar el dataset.
2. Verificar la presencia de las columnas mínimas requeridas:
   - `animal`;
   - factores experimentales definidos para el análisis;
   - columna de la métrica;
   - `cell_id`, `dendrite_id` u otro identificador de unidad técnica, si está disponible.
3. Convertir tipos de datos según corresponda:
   - `animal` como categórica;
   - factores experimentales como categóricos;
   - métrica como numérica.
4. Para análisis de distribuciones, cargar tablas de conteo con categorías en filas y grupos experimentales en columnas, o en el formato requerido por el script correspondiente.

### Etapa 2. Control de calidad estructural

1. Calcular el número de mediciones por animal y por condición.
2. Identificar animales subrepresentados o sobrerrepresentados.
3. Cuantificar datos faltantes por columna y por condición.
4. Marcar posibles valores extremos sin eliminarlos automáticamente.
5. Registrar exclusiones manuales, si las hubiera.

### Etapa 3. Visualización de validación

1. Generar gráficos `bar + dots` por medición.
2. Generar gráficos tipo `raincloud`, cuando corresponda.
3. Generar gráficos `spaghetti` cuando exista pareamiento real a nivel animal.
4. Generar gráficos de medias por animal.
5. Verificar visualmente la consistencia entre el patrón a nivel de medición y el patrón a nivel de animal.

### Etapa 4. Chequeo de supuestos

1. Evaluar normalidad y homocedasticidad sobre los residuos del modelo, no únicamente sobre los datos crudos.
2. Generar:
   - gráfico QQ de residuos;
   - prueba de Shapiro-Wilk sobre residuos;
   - prueba de Levene para homogeneidad de varianzas.
3. Registrar la magnitud de las desviaciones y su posible impacto sobre la inferencia.
4. Interpretar con cautela aquellos resultados en los que exista una desviación marcada de normalidad o de homogeneidad de varianzas, especialmente cuando la significancia dependa de pocas observaciones o de distribuciones altamente asimétricas.

### Etapa 5. Modelado estadístico principal

1. Ajustar un modelo ANOVA de acuerdo con el diseño experimental y la métrica analizada.
2. Cuando existan observaciones múltiples por animal, ajustar un modelo lineal mixto complementario con la misma estructura de efectos fijos y, como mínimo, un intercepto aleatorio por animal: `(1 | animal)`.
3. Comparar ANOVA y LMM para evaluar si el patrón observado se sostiene al considerar explícitamente la dependencia intra-animal.
4. Considerar robustos los efectos que muestran patrones consistentes entre ANOVA, LMM y visualización de datos.
5. No considerar concluyentes los efectos que dependen exclusivamente de un único enfoque estadístico en presencia de anidamiento, desbalance marcado o violaciones importantes de supuestos.

### Etapa 6. Comparaciones post hoc

1. Aplicar comparaciones post hoc con corrección de Tukey cuando corresponda.
2. No realizar post hoc cuando un factor tenga dos niveles y no exista interacción relevante.
3. Si hay interacción significativa, descomponer en efectos simples y corregir las comparaciones múltiples.
4. Si un factor tiene más de dos niveles, realizar comparaciones por pares con corrección de Tukey.
5. Para comparaciones de múltiples grupos contra un único control, aplicar corrección de Dunnett cuando corresponda.

### Etapa 7. Análisis no paramétricos complementarios

1. En variables con marcada desviación de normalidad o heterogeneidad de varianzas, realizar análisis no paramétricos complementarios basados en cocientes respecto del control correspondiente.
2. Comparar cada cociente contra el valor hipotético 1, que representa ausencia de diferencia relativa respecto del control.
3. Utilizar la prueba de Wilcoxon para una muestra.
4. En EXP-001, calcular los cocientes dividiendo los valores ipsilaterales por el promedio del grupo contralateral de la semana correspondiente.
5. En EXP-002, calcular los cocientes dividiendo los valores del grupo 6-OHDA por el promedio de su grupo sham correspondiente, por separado según tratamiento y subtipo neuronal cuando corresponda.
6. Aplicar corrección por comparaciones múltiples:
   - EXP-001: umbral ajustado `p < 0.0167`;
   - EXP-002: umbral ajustado `p < 0.0125`.
7. Utilizar estos análisis como evidencia complementaria o de sensibilidad, no como reemplazo automático del modelo factorial principal.

### Etapa 8. Análisis de distribuciones categóricas

1. Analizar distribuciones de categorías mediante pruebas de χ² de independencia sobre tablas de contingencia.
2. Aplicar este enfoque a:
   - distribución de subtipos de espinas dendríticas;
   - distribución de distancias al vecino más cercano según el punto de corte definido;
   - otras variables categóricas derivadas de recuentos, si corresponde.
3. Calcular frecuencias observadas y esperadas bajo independencia.
4. Calcular la contribución absoluta de cada celda al estadístico χ²:

   ```text
   contribución de celda = (observado - esperado)^2 / esperado
   ```

5. Calcular el aporte porcentual de cada celda al χ² total:

   ```text
   aporte porcentual = 100 × contribución de celda / χ² total
   ```

6. Generar una tabla de contribución porcentual y un heatmap para identificar qué combinaciones de grupo experimental y categoría explican en mayor medida la desviación global respecto de la independencia.
7. Interpretar el heatmap como una descomposición descriptiva del χ² global, no como una prueba post hoc independiente por celda.

## Criterio general de interpretación

- Si ANOVA y LMM concuerdan, el resultado se considera robusto.
- Si solo ANOVA resulta significativo en datos anidados, se interpreta con cautela por posible inflación asociada a la dependencia intra-animal.
- Si existen desviaciones marcadas de normalidad u homocedasticidad, la interpretación debe considerar la magnitud de esas desviaciones y apoyarse en análisis complementarios cuando corresponda.
- Los análisis no paramétricos basados en cocientes se utilizan como controles de sensibilidad para evaluar la consistencia de patrones en variables problemáticas.
- En análisis de distribuciones categóricas, el χ² indica si la distribución global difiere entre condiciones, mientras que el aporte porcentual permite identificar qué categorías contribuyen más a esa diferencia global.

## Modelos utilizados

### EXP-001

Para variables con comparación entre hemisferios y semanas:

```text
ANOVA: metric ~ hemisphere * week
LMM:   metric ~ hemisphere * week + (1 | animal)
```

Factores:

- `hemisphere`: ipsilateral vs. contralateral;
- `week`: S1, S2, S4.

Para variables de validación conductual o cuantificación de TH en las que se comparó un único grupo sham con distintos puntos temporales post-lesión:

```text
ANOVA: metric ~ group
Post hoc: Dunnett contra grupo sham
```

### EXP-002

Para variables sin subtipo celular:

```text
ANOVA: metric ~ tratamiento1 * tratamiento2
LMM:   metric ~ tratamiento1 * tratamiento2 + (1 | animal)
```

Factores:

- `tratamiento1`: sham vs. 6-OHDA;
- `tratamiento2`: vehículo vs. DOX.

Para variables con subtipo celular:

```text
ANOVA: metric ~ tratamiento1 * tratamiento2 * msn_subtype
LMM:   metric ~ tratamiento1 * tratamiento2 * msn_subtype + (1 | animal)
```

Factores:

- `tratamiento1`: sham vs. 6-OHDA;
- `tratamiento2`: vehículo vs. DOX;
- `msn_subtype`: dNEM vs. iNEM.

Para análisis conductual longitudinal:

```text
ANOVA: metric ~ tratamiento1 * tratamiento2 * time
```

Factores:

- `tratamiento1`: sham vs. 6-OHDA;
- `tratamiento2`: vehículo vs. DOX;
- `time`: semanas experimentales, modelado como factor de medidas repetidas.

## Análisis de distribuciones

### Subtipos de espinas dendríticas

Categorías:

- mushroom;
- thin;
- stubby;
- filopodia.

Análisis:

```text
χ² de independencia: grupo experimental × subtipo de espina
```

Output:

- tabla de frecuencias observadas;
- tabla de frecuencias esperadas;
- estadístico χ² total;
- valor de p;
- contribución absoluta por celda;
- aporte porcentual por celda;
- heatmap de aporte porcentual.

Uso interpretativo:

- identificar qué combinaciones de grupo experimental y subtipo explican en mayor medida la desviación global respecto de la independencia;
- complementar la visualización de proporciones y Δ-proporciones.

### Distancia al vecino más cercano

Categorías:

- distancia menor o igual al punto de corte definido;
- distancia mayor al punto de corte definido.

Punto de corte:

```text
16 µm
```

Análisis:

```text
χ² de independencia: grupo experimental × categoría de distancia
```

Output:

- tabla de frecuencias observadas;
- tabla de frecuencias esperadas;
- estadístico χ² total;
- valor de p;
- contribución absoluta por celda;
- aporte porcentual por celda, cuando corresponda.

## Outputs esperados

- tablas de conteo y faltantes;
- archivo de marcas de outliers;
- gráficos de validación y QC;
- gráficos de residuos;
- tabla ANOVA;
- tabla de efectos del LMM;
- tablas de comparaciones post hoc cuando apliquen;
- tablas de análisis no paramétricos complementarios;
- tablas de frecuencias observadas y esperadas para χ²;
- tablas de contribución absoluta y porcentual al χ²;
- heatmaps de aporte porcentual al χ²;
- resumen final por métrica.

## Parámetros críticos

- La unidad biológica superior es el animal.
- Los LMM deben incluir al menos un intercepto aleatorio por animal.
- Los supuestos se evalúan preferentemente sobre residuos del modelo.
- Los valores extremos se marcan, pero no se eliminan automáticamente.
- Las comparaciones post hoc se corrigen por comparaciones múltiples.
- El análisis no paramétrico por cocientes se interpreta como complemento de sensibilidad.
- El aporte porcentual al χ² no reemplaza al test global, sino que permite descomponer descriptivamente qué celdas contribuyen más al resultado.
- En análisis de conteos de espinas, considerar que las espinas individuales no son unidades biológicas independientes; por eso, la interpretación debe integrarse con análisis por animal y con el diseño experimental.

## Control de calidad

Verificar consistencia estructural del dataset, balance de observaciones por animal, datos faltantes, plausibilidad de la distribución de la métrica, diagnóstico de residuos, coherencia entre ANOVA y LMM, consistencia de los análisis no paramétricos complementarios y correspondencia entre los resultados del χ², las proporciones observadas y los heatmaps de contribución porcentual.

## Scripts asociados

- `scripts_python/analisis_estadistico_general.py`
- `scripts_python/analisis_chi2_contribuciones.py`
