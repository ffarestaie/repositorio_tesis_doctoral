# Cuantificación de cobertura microglial

## Objetivo

Cuantificar la fracción del área del campo ocupada por señal microglial en imágenes del cuerpo estriado a partir de stacks binarizados de Iba1. La métrica final corresponde al porcentaje de cobertura microglial por stack.

## Material de entrada / insumos

- imágenes originales multicanal en formato `.tif` o `.tiff`, con canal microglial de interés;
- software Fiji/ImageJ para binarización;
- script en Python para cuantificación de resultados;
- las imágenes deben estar previamente recortadas al área de interés, de modo que el área total corresponda al frame completo.

## Procedimiento

1. Abrir las imágenes originales en Fiji/ImageJ.
2. Guardar como .tiff
3. AQUI COMIENZA EL MACRO: toma carpeta input con las imagenes .tiff y corre en batch los siguientes pasos
4. Separar canales y conservar el canal microglial.
5. Convertir el stack a 8 bits.
6. Aplicar substracción de background con radio 50 px, opción `sliding` y procesamiento del stack completo.
7. Umbralizar cada plano Z con método `Li` en modo `dark`.
8. Convertir el stack a máscara binaria calculando el umbral por `slice`.
9. Guardar el stack binario resultante como TIFF.
10. AQUI TERMINA EL MACRO
11. Realizar control visual de las máscaras binarizadas.
12. Ejecutar el script en Python utilizando como entrada la carpeta de TIFF binarios.

## Procesamiento de imagen

La etapa de Fiji genera un stack binario por imagen, en el que los píxeles positivos representan señal microglial y el resto corresponde a fondo. La binarización se realiza por plano Z para reducir sesgos asociados a variaciones de intensidad a lo largo del stack. El análisis posterior se realiza exclusivamente sobre esos TIFF binarios.

## Análisis computacional

El script en Python carga cada TIFF binario y calcula la cobertura microglial total del stack como la fracción de píxeles positivos respecto del número total de píxeles del volumen analizado.

## Métricas generadas

1. **Fracción de cobertura microglial**: fracción del área total ocupada por señal microglial en el stack completo.

## Parámetros críticos

- Las imágenes deben tener la misma escala y corresponder a campos previamente recortados de manera comparable.
- El área total se define como el frame completo; no se aplica máscara adicional de tejido.
- La substracción de background debe realizarse con radio 50 px.
- La umbralización debe aplicarse por `slice` con método `Li` en modo `dark`.

## Control de calidad

Revisar manualmente las máscaras binarias para detectar planos con binarización aberrante, en particular `slices` completamente negros o completamente blancos.

## Salida

Tabla resumen con una fila por archivo, incluyendo cobertura microglial total.
