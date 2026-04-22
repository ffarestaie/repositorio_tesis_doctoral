# Cuantificación de contactos microglia-dendrita

## Objetivo

Cuantificar la fracción de área dendrítica ubicada dentro de un radio de vecindad de señal microglial y extraer métricas complementarias de cobertura microglial y eficiencia de contacto.

## Material de entrada / insumos

- archivos RAW multicanal en formato `.jpx`;
- canal 1: GFP (dendrita);
- canal 2: Iba1 (microglía);
- resolución XY: 0.16 µm/píxel;
- paso Z: 1.0 µm;
- salida intermedia requerida: stack TIFF binario multicanal.

## Procedimiento

1. Abrir el archivo `.jpx` en Fiji/ImageJ.
2. Seleccionar la dendrita de interés en el canal GFP.
3. Rotar la imagen hasta horizontalizar el eje principal de la dendrita.
4. Trazar una línea sobre la dendrita y generar una ROI rectangular centrada con altura fija de 200 px.
5. Recortar la ROI.
6. AQUI COMIENZA EL MACRO: pide carpeta input con las imagenes .tiff generadas en los pasos previos y corre en batch.
7. Separar canales.
8. Convertir ambos canales a 8 bits.
9. Aplicar substracción de background en ambos canales con radio 50 px, opción `sliding paraboloid` y procesamiento del stack completo.
10. Umbralizar GFP con método `Triangle` e Iba1 con método `Otsu`.
11. En la máscara GFP, aplicar en el plugin **MorphoLibJ**: `Connected Components` y `Keep Largest Region`.
12. Recomponer ambas máscaras en un TIFF binario multicanal.
13. AQUI TERMINA EL MACRO: devuelve una carpeta output con las nuevas imagenes procesadas. Esta carpeta es el input del script.
14. Verificar visualmente el resultado binario.
15. Analizar el TIFF binario en Python con el script correspondiente.

## Análisis computacional

El script recibe como entrada el TIFF binario multicanal y separa las máscaras de dendrita y microglía. Luego calcula, para cada plano Z, un mapa de distancias bidimensional en XY desde cada píxel dendrítico hasta el píxel microglial más cercano. A partir de ese mapa define como contacto los píxeles de dendrita ubicados a una distancia menor o igual a 0.32 µm de microglía dentro del mismo plano. Con esa máscara de contacto calcula las métricas de área y cobertura sobre el stack completo.

## Métricas generadas

1. **Área dendrítica total**: suma de los píxeles dendríticos en todos los planos del stack, convertida a µm².
2. **Área dendrítica en contacto**: suma de los píxeles dendríticos ubicados a una distancia menor o igual a 0.32 µm de microglía, convertida a µm².
3. **Fracción de área de contacto**: cociente entre el área dendrítica en contacto y el área dendrítica total.
4. **Cobertura microglial global**: fracción del área total del stack ocupada por señal microglial.
5. **Índice de eficiencia de contacto**: cociente entre la fracción de área de contacto y la cobertura microglial global.

## Parámetros críticos

- La ROI debe recortarse de forma comparable entre imágenes.
- La resolución XY debe mantenerse en 0.16 µm/píxel.
- El umbral de cercanía para definir contacto es 0.32 µm, equivalente aproximadamente a 2 píxeles en XY.
- La vecindad se calcula por plano en XY y no entre planos Z.
- Los métodos de umbralización deben mantenerse fijos: `Triangle` para GFP y `Otsu` para Iba1.

## Control de calidad

Verificar continuidad del segmento dendrítico, ausencia de ruido desconectado relevante en GFP, adecuación de la binarización de Iba1, alineación entre canales y correcta horizontalización de la dendrita. Si el binario no es satisfactorio, repetir el recorte o la binarización según corresponda.

## Salida

Tabla por ROI con las siguientes variables:

- área dendrítica total;
- área dendrítica en contacto;
- fracción de área de contacto;
- cobertura microglial global;
- índice de eficiencia de contacto.
