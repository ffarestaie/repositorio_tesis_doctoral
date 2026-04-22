# Parámetros de adquisición microscópica

## Alcance

Este documento resume los parámetros de adquisición microscópica utilizados para generar las imágenes que sirvieron de entrada a los análisis incluidos en este repositorio.

## Sistema de adquisición

- microscopio de epifluorescencia `Zeiss AxioImager.M2`;
- sistema de iluminación estructurada `ApoTome`;
- cámara monocromática;
- software de adquisición `Neurolucida StereoInvestigator`.

## Criterio general de adquisición

Las imágenes se adquirieron sobre cortes coronales de estriado, orientando el muestreo hacia el estriado dorsolateral. Dentro de cada tipo de análisis, los parámetros de adquisición se mantuvieron constantes entre grupos experimentales.

## C1. Imágenes de intensidad de TH

**Uso principal**
- cuantificación de denervación dopaminérgica estriatal mediante inmunomarcación de TH.

**Parámetros**
- objetivo: `2.5×`;
- formato: mosaico;
- número de secciones: `1` sección por animal;
- tipo de adquisición: plano único;
- canal: rojo;
- intensidad de lámpara: `100 %`;
- tiempo de exposición: `100 ms`.

## C2. Imágenes poblacionales de microglía

**Uso principal**
- densidad microglial;
- distancia al vecino más cercano;
- cobertura microglial de campo.

**Parámetros**
- objetivo: `20×`;
- espesor de stack: aproximadamente `20 µm`;
- `z-step`: `1 µm`;
- canal: `Far Red` para señal Iba1;
- intensidad de lámpara: `100 %`;
- tiempo de exposición: `400 ms`.

## C3. Imágenes de morfología microglial

**Uso principal**
- volumen del soma;
- longitud acumulada de proyecciones;
- métricas derivadas del análisis de Sholl.

**Parámetros**
- objetivo: `40×`;
- espesor de stack: aproximadamente `20–25 µm`;
- `z-step`: `1 µm`;
- canal: `Far Red` para señal Iba1;
- intensidad de lámpara: `100 %`;
- tiempo de exposición: `1500 ms`.

## C4. Imágenes de interacción microglía-neurona

**Uso principal**
- contenido intracelular de GFP;
- contacto microglía-neurona.

**Parámetros**
- objetivo: `40×`;
- espesor de stack: aproximadamente `20–25 µm`;
- `z-step`: `1 µm`;
- canal Iba1: `Far Red`, tiempo de exposición `1500 ms`;
- canal GFP: tiempo de exposición `200 ms`;
- intensidad de lámpara: `100 %`.

## C5. Imágenes de espinas dendríticas

**Uso principal**
- cuantificación tridimensional de espinas dendríticas.

**Parámetros**
- objetivo: `63×`;
- espesor de stack: aproximadamente `10 µm`;
- `z-step`: `0.1 µm`;
- señal: segmentos dendríticos GFP+;
- intensidad de lámpara: `100 %`;
- tiempo de exposición: `100 ms`.

## Nota de uso

Los parámetros aquí resumidos deben leerse en conjunto con los protocolos específicos incluidos en `documentacion/protocolos/`, ya que cada análisis utiliza distintos subconjuntos de estas adquisiciones como entrada.
