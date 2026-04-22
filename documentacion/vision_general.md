# Visión general del repositorio

Este repositorio organiza los scripts, macros y documentos metodológicos utilizados en los análisis de mi tesis doctoral. Su objetivo es reunir en una única estructura los procedimientos computacionales asociados al procesamiento de imágenes, la extracción de métricas, el análisis conductual y los análisis estadísticos complementarios.

## Propósito

Este repositorio fue construido con tres objetivos principales:

1. organizar de forma clara los archivos utilizados durante la tesis;
2. facilitar la trazabilidad entre código, protocolos y análisis reportados;
3. mejorar la transparencia metodológica y la reproducibilidad de los procedimientos analíticos.

No fue concebido como un paquete de software formal, sino como un repositorio de trabajo ordenado y documentado.

## Organización general

El contenido del repositorio se distribuye en cuatro bloques principales:

### 1. `macros_imagej/`
Contiene macros de ImageJ/Fiji utilizadas para procesamiento batch y preprocesamiento de imágenes. Estas macros generan archivos de entrada para análisis posteriores o automatizan tareas repetitivas del flujo de trabajo.

### 2. `scripts_python/`
Contiene scripts en Python utilizados para cálculo de métricas, análisis conductuales multivariados y análisis estadísticos complementarios.

### 3. `scripts_r/`
Contiene scripts en R utilizados para análisis específicos complementarios.

### 4. `documentacion/`
Contiene documentación general del repositorio, protocolos resumidos asociados a cada análisis y materiales fuente utilizados para construir esa documentación.

## Lógica general de uso

En la mayoría de los análisis, el flujo de trabajo sigue una de estas secuencias:

- preprocesamiento de imágenes con macros de ImageJ/Fiji;
- generación de archivos intermedios;
- cálculo de métricas con scripts en Python o R;
- análisis estadístico y organización de resultados.

No todos los análisis incluyen todas estas etapas, pero esa es la lógica general del repositorio.

## Documentación disponible

La carpeta `documentacion/` incluye dos tipos de materiales:

### Protocolos
En `documentacion/protocolos/` se encuentran descripciones resumidas de los análisis incluidos en la tesis. Estos protocolos explican el objetivo de cada procedimiento, los inputs requeridos, los pasos principales, las métricas generadas y los outputs esperados.

### Correspondencia con la tesis
En `documentacion/correspondencia_con_tesis.md` se detalla la relación entre los archivos del repositorio y los análisis reportados en el manuscrito de la tesis.

## Alcance del repositorio

Este repositorio incluye:

- macros y scripts utilizados en los análisis;
- documentación metodológica asociada;
- estructura organizada para facilitar navegación y reutilización.

Este repositorio no incluye, en principio:

- datasets crudos completos;
- imágenes originales de gran tamaño;
- archivos intermedios pesados;
- resultados finales completos de cada análisis.

## Reutilización

Los scripts y macros incluidos pueden requerir adaptaciones menores para su uso en otros conjuntos de datos, especialmente en relación con:

- rutas de archivos;
- nombres de columnas;
- formatos de metadata;
- estructura de carpetas de entrada y salida.

Por ese motivo, se recomienda leer siempre la documentación asociada antes de ejecutar cada archivo.

## Observación final

Este repositorio debe leerse como un complemento metodológico de la tesis doctoral. Su función principal es documentar y organizar los procedimientos analíticos utilizados, más que ofrecer una herramienta genérica cerrada para uso universal.
