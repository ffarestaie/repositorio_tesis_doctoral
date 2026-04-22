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
