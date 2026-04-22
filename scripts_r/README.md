# Scripts en R

Esta carpeta contiene scripts en R utilizados para análisis específicos complementarios.

## Contenido

- `contar_subtipos_espinas.R`: conteo de subtipos de espinas a partir de archivos exportados desde NeuronStudio.
- `calcular_vecino_mas_cercano.R`: cálculo de distancia al vecino más cercano a partir de coordenadas X,Y de centroides obtenidos en el calculo de densidad microglial.

## Uso general

Estos scripts reciben como entrada tablas generadas en etapas previas del flujo de trabajo y producen métricas derivadas o tablas consolidadas para análisis posteriores.

## Nota

Los protocolos resumidos asociados a estos análisis se encuentran en `documentacion/protocolos/`.

---
# Distancia al vecino mas cercano

## Descripción

Este script calcula la distancia al vecino más cercano a partir de coordenadas X,Y de centroides microgliales exportados desde Fiji/ImageJ. Procesa múltiples archivos, convierte las distancias de píxeles a micras y consolida los resultados en una única tabla.

## Input

- uno o más archivos `.csv` o `.xlsx` con columnas `x` e `y`;
- los nombres de archivo pueden aportar metadata como `animal`, `tratamiento` y `semana`, que el script intenta extraer de forma flexible.

## Output

- archivo `.csv` consolidado con una fila por microglía y sus distancias al vecino más cercano en píxeles y en micras.
