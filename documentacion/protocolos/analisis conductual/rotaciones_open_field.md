# Cuantificación del índice de rotaciones en Open Field test

## Objetivo

Cuantificar la asimetría direccional de la locomoción espontánea en el test de open field como medida funcional de denervación dopaminérgica unilateral.

## Material de entrada / insumos

- archivo de resultados generado por el sistema de tracking AnyMaze.

## Procedimiento

1. Registrar la sesión de `Open Field test` y obtener, para cada animal, el número total de rotaciones ipsilaterales, contralaterales y totales.
2. Calcular el índice de rotaciones a partir del número de rotaciones ipsilaterales y contralaterales.

## Cálculo de la métrica

El índice de rotaciones se calculó como la proporción de rotaciones ipsilaterales respecto del número total de rotaciones registradas.

## Parámetros críticos

- El criterio de definición de rotación debe mantenerse constante entre animales.
- Debe verificarse la calidad del tracking antes del cálculo.

## Interpretación

- Un valor cercano a `0.5` indica ausencia de sesgo direccional, compatible con animales control.
- Valores desplazados hacia `1` indican predominio de rotaciones en dirección del hemicuerpo sano y son compatibles con animales lesionados.
- Se estableció un índice de `0.8` como umbral de criterio de lesión completa.

## Salida

Tabla por animal con:

- número de rotaciones ipsilaterales;
- número de rotaciones contralaterales;
- índice final de rotaciones.
