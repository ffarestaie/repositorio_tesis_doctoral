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

---
# Contactos microglía-dendrita

## Descripción

Este macro de ImageJ/Fiji realiza el preprocesamiento batch de imágenes para el análisis de contactos microglia-dendrita. Separa los canales GFP e Iba1, convierte ambos a 8 bits, aplica substracción de background, binariza cada canal, limpia la máscara de GFP conservando la región principal y genera un TIFF multicanal binario por archivo.

## Input

- carpeta con imágenes multicanal en formato `.tif` o `.tiff`;
- convención de canales:
  - `C1`: GFP;
  - `C2`: Iba1.

## Output

- carpeta con archivos TIFF multicanal binarios listos para cuantificación de contactos microglia-dendrita.

## Requisitos

- Fiji/ImageJ;
- plugin MorphoLibJ para los pasos de componentes conectados y conservación de la región principal.

---
# Colocalización GFP-Iba1

## Descripción

Este macro de ImageJ/Fiji realiza el procesamiento batch de imágenes para cuantificación de colocalización GFP-Iba1 en somas microgliales. Separa canales, genera proyecciones máximas, corrige background, binariza cada canal, calcula la intersección lógica entre ambas máscaras y guarda un archivo de resultados junto con una imagen de control por campo.

## Input

- carpeta con imágenes multicanal en formato `.tif` o `.tiff`;
- convención de canales:
  - `C1`: GFP;
  - `C2`: Iba1.

## Output

- archivo `.csv` con el área colocalizada por imagen;
- imágenes de control tipo overlay para inspección visual.
