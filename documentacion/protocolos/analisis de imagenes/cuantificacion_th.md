# Cuantificación de denervación dopaminérgica estriatal mediante inmunomarcación de TH

## Objetivo

Cuantificar la pérdida de inmunorreactividad para tirosina hidroxilasa (TH) en el estriado ipsilateral respecto del contralateral como medida de denervación dopaminérgica.

## Material de entrada / insumos

- imágenes de cortes coronales del estriado con inmunomarcación anti-TH en las que se distingan ambos hemisferios;
- para cada animal se definen cuatro regiones de interés por hemisferio:
  - dorsolateral (DL);
  - dorsoventral (DV);
  - ventromedial (VM);
  - ventrolateral (VL);
- se define además una región cortical de `background` por imagen.

## Procedimiento

1. Medir la intensidad media de gris en las cuatro regiones estriatales de cada hemisferio.
2. Medir la intensidad media de gris en la región cortical de `background`.
3. Corregir cada medición estriatal restando el valor de `background` cortical.
4. Calcular, para cada subregión, el cociente entre la intensidad corregida ipsilateral y la contralateral.
5. Obtener el índice final de TH por animal como el promedio de los cuatro cocientes subregionales.

## Parámetros críticos

- Las regiones de interés deben definirse de forma anatómicamente consistente entre animales y entre hemisferios.
- La corrección por `background` debe aplicarse a todas las mediciones.

## Control de calidad

Verificar que las imágenes incluyan ambos hemisferios y permitan identificar con claridad las cuatro subregiones analizadas.

## Salida

Tabla por animal con:

- intensidades crudas;
- valor de `background`;
- cocientes por subregión;
- índice final de TH.

## Interpretación esperada

- Un índice cercano a `0` indica denervación ipsilateral marcada.
- Un índice cercano a `1` indica ausencia de denervación o lesión incompleta.
- Se estableció un índice de `0.25` como umbral de criterio de lesión completa.
