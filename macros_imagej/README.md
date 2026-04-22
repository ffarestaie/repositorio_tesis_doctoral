# Macros de ImageJ/Fiji

Esta carpeta contiene macros de ImageJ/Fiji utilizadas para procesamiento batch y preprocesamiento de imágenes.

## Contenido

- `procesamiento_cobertura_microglial.ijm`: genera imágenes binarias para cuantificación de cobertura microglial.
- `procesamiento_contactos_microglia_dendrita.ijm`: procesa imágenes para el análisis de contactos microglia-dendrita.
- `procesamiento_colocalizacion_gfp_iba1.ijm`: procesa y cauntifica imágenes para cuantificación de colocalización GFP-Iba1.
- `procesamiento_espinas_dendriticas.ijm`: procesa imágenes de dendritas para análisis de espinas.

## Uso general

Estas macros se utilizan como etapa previa a la extracción de métricas cuantitativas. En la mayoría de los casos generan archivos intermedios que luego son analizados con scripts en Python o R.

## Nota

La descripción metodológica resumida de cada análisis se encuentra en `documentacion/protocolos/`.

---
# Cobertura microglial

## Descripción

Este macro de ImageJ/Fiji realiza el preprocesamiento batch de imágenes para el análisis de cobertura microglial. Separa canales, conserva el canal de Iba1, convierte las imágenes a 8 bits, aplica substracción de background, binariza el stack y guarda un TIFF binario por archivo.

## Input

- carpeta con imágenes multicanal en formato `.tif` o `.tiff`.

## Output

- carpeta con stacks TIFF binarios listos para cuantificación de cobertura microglial en Python.
