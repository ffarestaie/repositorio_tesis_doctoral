# Repositorio de tesis doctoral

Este repositorio reúne los scripts, macros de ImageJ/Fiji y documentación asociados a los análisis realizados en mi tesis doctoral. Su objetivo es organizar de manera clara los procedimientos computacionales utilizados para el procesamiento de imágenes, la extracción de métricas cuantitativas, el análisis conductual y los análisis estadísticos complementarios.

## Contenido del repositorio

El repositorio incluye:

- macros de ImageJ/Fiji para preprocesamiento y procesamiento batch de imágenes;
- scripts en Python para análisis de métricas derivadas de imágenes, análisis multivariado conductual y análisis estadísticos;
- scripts en R para análisis específicos complementarios;
- protocolos resumidos de los análisis incluidos en la tesis;
- una ficha técnica con los parámetros de adquisición microscópica utilizados para generar las imágenes de entrada de los análisis incluidos en el repositorio;
- documentación que vincula cada archivo con los análisis y métricas reportados en el manuscrito.

## Estructura general

```text
repositorio_tesis_doctoral/
├── README.md
├── LICENSE
├── .gitignore
├── requisitos_python.txt
│
├── documentacion/
│   ├── vision_general.md
│   ├── correspondencia_con_tesis.md
│   ├── parametros_adquisicion_microscopica.md
│   ├── protocolos/
│   └── fuentes/
│
├── macros_imagej/
│   ├── README.md
│   ├── procesamiento_cobertura_microglial.ijm
│   ├── procesamiento_contactos_microglia_dendrita.ijm
│   ├── procesamiento_colocalizacion_gfp_iba1.ijm
│   └── procesamiento_espinas_dendriticas.ijm
│
├── scripts_python/
│   ├── README.md
│   ├── analisis_multivariado_longitudinal.py
│   ├── calcular_cobertura_microglial.py
│   ├── calcular_contactos_exp_001.py
│   ├── calcular_contactos_exp_002.py
│   ├── analisis_subtipos_espinas_exp_001.py
│   ├── analisis_subtipos_espinas_exp_002.py
│   └── analisis_estadistico_general.py
│
├── scripts_r/
│   ├── README.md
│   ├── contar_subtipos_espinas.R
│   └── calcular_vecino_mas_cercano.R
│
└── ejemplos/
    ├── entradas_ejemplo/
    └── salidas_ejemplo/
```
## Tipos de análisis incluidos
### Análisis de imágenes

- cuantificación de denervación dopaminérgica mediante TH;
- cuantificación de cobertura microglial;
- cuantificación de contactos microglia-dendrita;
- cuantificación de colocalización GFP-Iba1 en somas microgliales;
- reconstrucción 3D de microglía y extracción de métricas morfológicas;
- cuantificación de densidad microglial;
- cálculo de distancia al vecino más cercano;
- cuantificación de espinas dendríticas y análisis de subtipos.

### Análisis conductuales

- índice de rotaciones en open field;
- índice de uso de miembros anteriores en el test del cilindro;
- análisis multivariado longitudinal de conducta.

### Análisis estadísticos

- análisis estadísticos generales;
- análisis específicos de distribución de subtipos de espinas.

## Organización del flujo de trabajo

En términos generales, los análisis siguen una de estas lógicas:

1. preprocesamiento de imágenes con macros de ImageJ/Fiji
2. extracción o cálculo de métricas con scripts en Python o R
3. análisis estadístico y generación de resultados

Cada carpeta incluye documentación específica sobre:

- qué hace cada archivo;
- qué tipo de input espera;
- qué output produce;
- a qué análisis de la tesis corresponde.

## Relación con la tesis

Este repositorio fue organizado para complementar la descripción metodológica de la tesis doctoral. La correspondencia entre los archivos aquí incluidos y los análisis reportados en el manuscrito se detalla en:

`documentacion/correspondencia_con_tesis.md`

Los protocolos resumidos asociados a cada análisis se encuentran en:

`documentacion/protocolos/`

La ficha técnica de adquisición microscópica se encuentra en:

`documentacion/parametros_adquisicion_microscopica.md`

## Requisitos y dependencias

Los scripts incluidos fueron desarrollados principalmente en Python, R y Fiji/ImageJ.

## Software utilizado

- Python [COMPLETAR: versión]
- R [COMPLETAR: versión]
- Fiji/ImageJ
- NeuronStudio [cuando corresponda]
- Neurolucida 360 / Neurolucida Explorer [cuando corresponda]

## Paquetes de Python

Las dependencias principales pueden listarse en:
```text
requisitos_python.txt
```
[COMPLETAR: agregar librerías efectivamente utilizadas, por ejemplo pandas, numpy, matplotlib, scikit-image, scipy, statsmodels, openpyxl, etc.]

## Datos

Este repositorio no incluye los datos crudos completos utilizados en la tesis. Los scripts y macros se comparten con fines de transparencia metodológica, organización del flujo analítico y apoyo a la reproducibilidad.

Cuando corresponde, pueden incluirse ejemplos mínimos de entrada y salida en la carpeta:
```text
ejemplos/
```
## Estado del repositorio

Este repositorio contiene versiones organizadas de los scripts y macros utilizados durante el doctorado. Algunos archivos fueron adaptados para mejorar su legibilidad, documentación y reutilización.

## Autor

Félix Fares Taie

IFIBIO Houssay, Universidad de Buenos Aires - CONICET

## Observaciones

Este repositorio fue concebido como complemento metodológico de la tesis y no como un paquete de software formal. Por ese motivo, algunos scripts pueden requerir adaptación menor de rutas, nombres de archivos o tablas de metadata para su reutilización en otros conjuntos de datos.
