# Cálculo de distancia al vecino más cercano a partir de centroides de somas microgliales

## Objetivo

Calcular, para cada soma microglial, la distancia euclídea al vecino más cercano dentro de la misma imagen a partir de las coordenadas X,Y obtenidas en el análisis de densidad microglial.

## Material de entrada / insumos

- un archivo CSV por imagen con coordenadas X,Y de los centroides microgliales provenientes del análisis de densidad microglial;
- script en R para lectura batch, limpieza de datos, cálculo de distancias y consolidación de resultados.

## Procedimiento

Ejecutar el script en R sobre la carpeta que contiene los archivos CSV con las coordenadas X,Y.

## Análisis computacional

El script opera sobre cada CSV en forma independiente. Para cada centroide calcula el conjunto de distancias euclídeas a todos los demás centroides de la imagen y selecciona el menor valor. Posteriormente convierte el resultado a micras mediante el factor 0.16 µm/px.

## Métricas generadas

1. **Distancia al vecino más cercano**: distancia euclídea al vecino más cercano dentro de la misma imagen. Se utiliza para la construcción de histogramas de frecuencia.
2. **Clasificación por umbral**: categorización de cada microglía en `<16 µm` o `≥16 µm` para análisis posteriores de proporciones.

## Parámetros críticos

- Todas las imágenes deben compartir la misma escala espacial.
- El factor de conversión indicado en el protocolo es `1 px = 0.16 µm`.

## Control de calidad

Verificar que todos los CSV contengan columnas X,Y válidas, que no haya archivos derivados incluidos en la carpeta de entrada y que estén representados los grupos esperados en la tabla consolidada. Revisar además el número de microglías por grupo y el rango de valores de distancia antes del análisis estadístico.

## Salida

Archivo CSV consolidado con una fila por microglía y su correspondiente valor de distancia en µm.
