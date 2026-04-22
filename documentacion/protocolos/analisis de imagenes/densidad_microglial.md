# Cuantificación de densidad microglial

## Objetivo

Contar el número de somas microgliales por imagen y registrar las coordenadas X,Y de sus centroides a partir de una proyección máxima del stack.

## Material de entrada / insumos

- stacks de imágenes de microglía adquiridos en Z, con 20 µm de espesor total y 1 imagen por µm;
- software Fiji/ImageJ;
- salida intermedia: proyección máxima en formato TIFF, archivo ROI y archivo CSV con centroides.

## Procedimiento

1. Abrir el stack en Fiji/ImageJ.
2. Convertir la imagen a 8 bits.
3. Generar una proyección máxima en Z.
4. Identificar visualmente cada soma completo y marcar su centro con la herramienta `Multi-point`. Si una célula en división presenta dos cuerpos celulares distinguibles, registrar dos puntos.
5. Medir las selecciones para obtener una tabla con coordenadas X,Y.
6. Exportar la tabla de resultados como CSV y guardar también el archivo ROI.

## Procesamiento de imagen

El análisis se realiza sobre una proyección máxima del stack original. La detección de somas es manual. Cada punto marcado corresponde al centroide de un soma microglial y queda registrado tanto como ROI como en una tabla de coordenadas exportable.

## Métricas generadas

1. **Número total de somas por imagen**: cantidad de puntos marcados.
2. **Coordenadas X,Y por soma**: centroides exportados desde Fiji/ImageJ.
3. **Archivos de trazabilidad**: TIFF de proyección máxima, archivo ROI y archivo CSV de resultados.

## Parámetros críticos

- Todas las imágenes deben tener la misma escala y aumento.
- El conteo debe incluir únicamente somas completos y evitar duplicados.
- La proyección máxima y los archivos exportados deben conservar una nomenclatura consistente para vincular imagen, ROI y CSV.

## Control de calidad

Revisar visualmente que no se hayan contado somas incompletos ni duplicados. Verificar que el número de puntos en ROI Manager coincida con el número de filas exportadas en el CSV.

## Salida

- un archivo TIFF por imagen;
- un archivo ROI con los puntos marcados;
- un archivo CSV con el número total de somas y sus coordenadas X,Y.
