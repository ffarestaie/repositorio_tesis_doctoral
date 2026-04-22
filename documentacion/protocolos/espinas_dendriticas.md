# Cuantificación de espinas dendríticas

## Objetivo

Cuantificar la densidad de espinas dendríticas y la proporción de subtipos morfológicos a partir de imágenes de dendritas procesadas digitalmente y analizadas en NeuronStudio.

## Material de entrada / insumos

- imágenes de microscopía en formato original, incluyendo stacks en formato `.jpx`;
- software Fiji/ImageJ para procesamiento de imagen;
- software NeuronStudio para reconstrucción del segmento dendrítico y detección de espinas;
- salida intermedia: imagen TIFF procesada del segmento dendrítico de interés.

## Etapa 1. Procesamiento de imagen

1. Abrir la imagen original en Fiji/ImageJ.
2. Guardarla en formato TIFF.
3. Rotar la imagen para alinear horizontalmente la dendrita de interés y guardar la imagen rotada.
4. Trazar una línea a lo largo del segmento dendrítico de interés.
5. Generar una ROI rectangular centrada en esa línea con altura suficiente para incluir la dendrita y todas sus espinas.
6. Recortar la ROI.
7. AQUI EMPIEZA EL MACRO: pide carpeta input con las imagenes .tiff generadas en los pasos anteriores, y corre en batch lo siguiente:
8. Convertir la imagen a 8 bits.
9. Mejorar el contraste con `Enhance Contrast` utilizando `Saturated Pixels = 0.3%`.
10. Aplicar `Subtract Background` con radio 50 px.
11. Guardar la imagen final procesada en formato TIFF.
12. AQUI TERMINA EL MACRO

## Etapa 2. Cuantificación en NeuronStudio

1. Abrir la imagen procesada en NeuronStudio.
2. Reconstruir el eje del segmento dendrítico con la herramienta de dendrita.
3. Cambiar la visualización del esqueleto dendrítico a `Point` en `Render > Neurite Vertex Shape`.
4. Ejecutar `Build Spines` para detección automática de espinas.
5. Cambiar a `XY Slice Viewer` para revisar la detección en cortes bidimensionales.
6. Editar manualmente las espinas detectadas: eliminar falsos positivos, agregar falsos negativos y corregir la clasificación morfológica cuando corresponda.

## Criterios de clasificación de subtipos

La asignación de subtipos se realizó sobre la base de características morfológicas descriptas en la literatura y operacionalizadas en NeuronStudio. En términos descriptivos:

- **mushroom**: espina con cabeza ensanchada y cuello identificable;
- **thin**: espina delgada, con cuello estrecho y cabeza pequeña;
- **stubby**: protrusión corta, sin cuello claramente distinguible;
- **filopodia**: protrusión alargada, sin ensanchamiento evidente de la cabeza.

Estas categorías corresponden a subclases morfológicas ampliamente utilizadas en estudios de espinas dendríticas. En este protocolo, la clasificación automática fue revisada y corregida manualmente cuando correspondió.

## Procesamiento de cuantificación

La cuantificación se realiza sobre un segmento dendrítico previamente procesado. NeuronStudio reconstruye el eje dendrítico y detecta automáticamente las espinas asociadas. Esa detección se corrige manualmente mediante inspección en vista XY. La clasificación final de cada espina se establece a partir de su morfología.

## Métricas generadas

1. **Longitud del segmento dendrítico analizado**: longitud del eje dendrítico reconstruido en NeuronStudio.
2. **Número total de espinas**: cantidad final de espinas detectadas y corregidas.
3. **Densidad de espinas**: número total de espinas expresado por 10 µm de longitud dendrítica.
4. **Proporción de subtipos**: proporción de espinas `mushroom`, `thin`, `stubby` y `filopodia` respecto del total de espinas del segmento o del grupo analizado.
5. **Delta de cambio por subtipo**: variación de la proporción de cada subtipo respecto del grupo de referencia.
   - En `EXP-001`, el grupo de referencia es `S1/CONTRA`.
   - En `EXP-002`, el grupo de referencia es `sham/veh`.

## Parámetros críticos

- La dendrita debe quedar alineada en forma consistente entre imágenes.
- La ROI debe incluir todo el segmento de interés y sus espinas sin incorporar regiones irrelevantes.
- La reconstrucción del eje dendrítico debe seguir fielmente el trayecto de la dendrita.
- La detección automática de espinas debe revisarse manualmente en todos los casos.
- La clasificación de subtipos debe basarse en criterios morfológicos consistentes entre muestras.

## Control de calidad

Verificar que el procesamiento no elimine espinas finas relevantes, que la reconstrucción dendrítica sea continua, que se corrijan falsos positivos y falsos negativos, y que la asignación de subtipos sea consistente.

## Salida

- imagen TIFF procesada;
- archivo de neuritas;
- archivo de espinas;
- tabla final con longitud dendrítica, número total de espinas, densidad de espinas por 10 µm, proporción de subtipos y delta de cambio por subtipo.
