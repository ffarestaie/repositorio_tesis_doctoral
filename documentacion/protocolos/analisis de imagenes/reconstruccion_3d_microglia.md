# Reconstrucción 3D de microglía

## Objetivo

Reconstruir microglías individuales en tres dimensiones a partir de stacks Iba1+ y extraer métricas morfológicas del soma y de la arborización celular.

## Material de entrada / insumos

- imágenes de microglía Iba1+ adquiridas con objetivo 40X en stacks Z de 20 µm de espesor total y paso Z de 0.5 µm, exportadas en formato crudo;
- software Neurolucida 360 para reconstrucción;
- software Neurolucida Explorer para extracción de métricas.

## Procedimiento

1. Cargar las imágenes crudas en Neurolucida 360 utilizando visualización en modo volumen.
2. No aplicar preprocesamientos adicionales dentro del software antes de iniciar la reconstrucción.
3. Seleccionar únicamente células con soma completamente contenido en el stack, ramificaciones visibles en X, Y y Z, y sin truncamiento por bordes.
4. Reconstruir el soma con la herramienta `Cell Body Detection`, ajustando tamaño de detección y tolerancia según la célula analizada.
5. Verificar visualmente la correspondencia entre la máscara 3D del soma y la señal original.
6. Reconstruir los procesos con la herramienta `Branch Tracing` en modalidad semiautomática, iniciando desde el soma y siguiendo cada ramificación a lo largo de toda su extensión.
7. Durante el trazado, controlar visualmente continuidad morfológica, ausencia de saltos de señal y correspondencia del eje reconstruido con la señal original.
8. Guardar la reconstrucción en formato `DATA`.
9. Abrir el archivo `DATA` en Neurolucida Explorer y exportar las métricas morfológicas de la célula completa.

## Procesamiento de reconstrucción

La reconstrucción se realiza directamente sobre la señal cruda en 3D. El soma se segmenta mediante `Cell Body Detection` y los procesos se trazan en forma semiautomática con control visual continuo. El archivo `DATA` resultante contiene la máscara tridimensional del soma y la reconstrucción de los procesos celulares.

## Métricas generadas

1. **Volumen del soma**: volumen tridimensional de la máscara del soma reconstruido, calculado por el software a partir de la segmentación 3D.
2. **Longitud de proyecciones acumuladas**: suma de la longitud de todos los segmentos reconstruidos de los procesos microgliales en la célula analizada.
3. **Intersecciones acumuladas**: suma total de las intersecciones registradas en todos los radios del análisis de Sholl aplicado a la reconstrucción celular.
4. **Valor crítico**: número máximo de intersecciones observado en un radio dado del análisis de Sholl.
5. **Radio pico**: distancia radial al soma en la que se observa el valor máximo de intersecciones del análisis de Sholl.

## Parámetros críticos

- La célula debe estar completamente contenida dentro del stack.
- No deben analizarse microglías truncadas por bordes del volumen.
- Los parámetros de `Cell Body Detection` deben ajustarse para representar fielmente la morfología observada.
- El trazado de procesos debe mantener continuidad con la señal original en los tres ejes.

## Control de calidad

Verificar visualmente la correspondencia entre la máscara somática y la señal original, así como la continuidad y fidelidad del trazado de procesos. Excluir células con soma incompleto, arborización truncada o reconstrucciones ambiguas.

## Salida

- archivo `DATA` con la reconstrucción tridimensional;
- archivo Excel por dataset con métricas volumétricas, métricas de arborización e intersecciones de Sholl.
