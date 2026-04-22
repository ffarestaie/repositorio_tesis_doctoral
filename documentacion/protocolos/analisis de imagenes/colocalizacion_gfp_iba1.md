# Cuantificación de colocalización GFP-Iba1 en somas microgliales

## Objetivo

Cuantificar la señal GFP colocalizada con Iba1 en imágenes multicanal de microscopía de fluorescencia. La métrica final se obtiene como el área total de GFP en cada soma microglial.

## Material de entrada / insumos

- imágenes de campo adquiridas con objetivo 40X en stacks Z de 10 planos, con 2 µm por plano;
- software Fiji/ImageJ;
- canal 1: Iba1;
- canal 2: GFP;
- salida intermedia: imágenes TIFF recortadas, una por microglía seleccionada.

## Procedimiento

1. Abrir el stack completo e identificar microglías elegibles.
2. Seleccionar únicamente microglías con soma completamente contenido en X, Y y Z, ubicadas a una distancia menor o igual a 10 µm de una neurona GFP+, y sin señal GFP por encima o por debajo del soma en el eje Z.
3. Para cada microglía seleccionada, dibujar una ROI rectangular que contenga únicamente el soma, duplicarla incluyendo todos los canales y guardarla como TIFF individual. Guardar además el registro de ROIs correspondiente a cada imagen de origen.
4. Abrir las imágenes TIFF recortadas en Fiji y confirmar la asignación de canales.
5. AQUI COMIENZA EL MACRO: pide carpeta input con las imagnees .tiff generadas en los pasos amteriores, y procesa lo siguiente en batch.
6. Convertir cada imagen a 8 bits y separar los canales.
7. Realizar proyección máxima en Z para cada canal.
8. Aplicar substracción de background con radio 50.
9. Umbralizar manualmente cada canal: `Triangle` para GFP y `Otsu` para Iba1. Aplicar el umbral y guardar las imágenes binarizadas.
10. Calcular la colocalización mediante operación `AND` entre las imágenes binarizadas de Iba1 y GFP.
11. Medir el área colocalizada dentro de la ROI correspondiente.
12. Generar una imagen de control visual combinando Iba1 binarizado en rojo y GFP binarizado en verde.
13. AQUI TERMINA EL MACRO

## Procesamiento de imagen

El análisis se realiza sobre imágenes recortadas por soma. Luego de la proyección máxima, cada canal se binariza por separado. La colocalización se define como la intersección lógica entre las máscaras binarias de Iba1 y GFP. A partir de esa imagen de intersección se mide el área colocalizada.

## Métricas generadas

1. **Área colocalizada (`Iba1 ∩ GFP`)**: área de intersección entre ambas máscaras binarias, definida en resultados como contenido GFP en células Iba1+.

## Parámetros críticos

- La selección de microglías debe excluir somas truncados y células con señal GFP fuera del plano somático que pueda distorsionar la proyección máxima.
- Los métodos de umbralización deben mantenerse constantes entre imágenes: `Triangle` para GFP y `Otsu` para Iba1.
- La ROI debe contener únicamente el soma microglial.

## Control de calidad

Verificar correspondencia correcta entre canales, adecuación del recorte por soma, consistencia de la binarización y plausibilidad visual de la imagen de control de colocalización. Mantener trazabilidad entre imagen original, TIFF recortado y archivo ROI.

## Salida

Tabla en formato `.csv` con identificador de imagen y área colocalizada.
