# Correspondencia entre el repositorio y la tesis

Este documento resume la relación entre los archivos incluidos en este repositorio y los análisis reportados en la tesis doctoral. Su objetivo es facilitar la trazabilidad entre protocolos, código y resultados.

## Criterio de organización

La correspondencia se presenta por tipo de análisis:

- procedimientos generales;
- análisis conductuales;
- análisis de imágenes;
- análisis estadísticos.

En cada caso se indica:

- el análisis o procedimiento;
- el protocolo asociado;
- los archivos del repositorio vinculados;
- el tipo de output generado;
- su relación general con la tesis.

---

## 1. Procedimientos generales

### Cirugía estereotáxica para inducción de lesión con 6-OHDA
- **Protocolo asociado:** `documentacion/protocolos/cirugia_6_ohda.md` **[COMPLETAR si el archivo final llevará otro nombre]**
- **Código asociado:** no aplica
- **Output principal:** lesión dopaminérgica unilateral para evaluación histológica y conductual
- **Relación con la tesis:** procedimiento general utilizado para generar el modelo experimental

### Perfusión transcardíaca y fijación tisular
- **Protocolo asociado:** `documentacion/protocolos/perfusion_y_fijacion_tisular.md` **[COMPLETAR si el archivo final llevará otro nombre]**
- **Código asociado:** no aplica
- **Output principal:** tejido fijado para procesamiento histológico posterior
- **Relación con la tesis:** procedimiento general de obtención y preservación de muestras

### Inmunohistoquímica / inmunofluorescencia
- **Protocolo asociado:** `documentacion/protocolos/inmunohistoquimica.md` **[COMPLETAR cuando esté disponible]**
- **Código asociado:** no aplica
- **Output principal:** cortes procesados para adquisición de imágenes
- **Relación con la tesis:** preparación de muestras para cuantificaciones histológicas y morfológicas

---

## 2. Análisis conductuales

### Índice de rotaciones en open field
- **Protocolo asociado:** `documentacion/protocolos/rotaciones_open_field.md`
- **Código asociado:** no aplica
- **Output principal:** índice de rotaciones por animal
- **Relación con la tesis:** evaluación univariada de asimetría motora

### Índice de uso de miembros anteriores en el test del cilindro
- **Protocolo asociado:** `documentacion/protocolos/asimetria_miembros_anteriores.md`
- **Código asociado:** no aplica
- **Output principal:** índice de uso de miembros anteriores por animal
- **Relación con la tesis:** evaluación univariada de asimetría motora

### Análisis multivariado longitudinal de conducta
- **Protocolo asociado:** `documentacion/protocolos/analisis_multivariado_longitudinal.md`
- **Código asociado:** `scripts_python/analisis_multivariado_longitudinal.py`
- **Output principal:** reducción de dimensionalidad, clustering, métricas derivadas de pertenencia y análisis de robustez
- **Relación con la tesis:** análisis multivariado exploratorio de la conducta a lo largo del seguimiento longitudinal

---

## 3. Análisis de imágenes

### Cuantificación de denervación dopaminérgica mediante TH
- **Protocolo asociado:** `documentacion/protocolos/cuantificacion_th.md`
- **Código asociado:** no aplica
- **Output principal:** índice final de TH por animal
- **Relación con la tesis:** validación histológica de la magnitud de denervación dopaminérgica

### Cuantificación de densidad microglial
- **Protocolo asociado:** `documentacion/protocolos/densidad_microglial.md`
- **Código asociado:** no aplica
- **Output principal:** número de somas por imagen y coordenadas X,Y de centroides
- **Relación con la tesis:** cuantificación de densidad celular y generación de insumo para análisis de distancia al vecino más cercano

### Cálculo de distancia al vecino más cercano
- **Protocolo asociado:** `documentacion/protocolos/vecino_mas_cercano.md`
- **Código asociado:** `scripts_r/calcular_vecino_mas_cercano.R`
- **Output principal:** distancia al vecino más cercano por microglía y tabla consolidada
- **Relación con la tesis:** análisis espacial de distribución de somas microgliales

### Cuantificación de cobertura microglial
- **Protocolo asociado:** `documentacion/protocolos/cobertura_microglial.md`
- **Macros asociadas:** `macros_imagej/procesamiento_cobertura_microglial.ijm`
- **Código asociado:** `scripts_python/calcular_cobertura_microglial.py`
- **Output principal:** cobertura microglial y tablas resumidas
- **Relación con la tesis:** cuantificación de cobertura de señal microglial en imágenes del cuerpo estriado

### Reconstrucción 3D de microglía
- **Protocolo asociado:** `documentacion/protocolos/reconstruccion_3d_microglia.md`
- **Código asociado:** no aplica
- **Output principal:** volumen del soma, longitud total de ramificaciones y métricas derivadas del análisis de Sholl
- **Relación con la tesis:** cuantificación morfológica tridimensional de microglías individuales
  
### Cuantificación de colocalización GFP-Iba1 en somas microgliales
- **Protocolo asociado:** `documentacion/protocolos/colocalizacion_gfp_iba1.md`
- **Macros asociadas:** `macros_imagej/procesamiento_colocalizacion_gfp_iba1.ijm`
- **Código asociado:** no aplica
- **Output principal:** área colocalizada
- **Relación con la tesis:** cuantificación de señal GFP asociada a somas microgliales

### Cuantificación de contactos microglia-dendrita
- **Protocolo asociado:** `documentacion/protocolos/contactos_microglia_dendrita.md`
- **Macros asociadas:** `macros_imagej/procesamiento_contactos_microglia_dendrita.ijm`
- **Código asociado:** `scripts_python/calcular_contactos_exp_001.py`, `scripts_python/calcular_contactos_exp_002.py`
- **Output principal:** fracción areal de contacto, cobertura microglial r índice de eficiencia de contacto
- **Relación con la tesis:** cuantificación de interacción espacial entre dendritas GFP+ y señal microglial

### Cuantificación de espinas dendríticas
- **Protocolo asociado:** `documentacion/protocolos/espinas_dendriticas.md`
- **Macros asociadas:** `macros_imagej/procesamiento_espinas_dendriticas.ijm`
- **Código asociado:** `scripts_r/contar_subtipos_espinas.R`, `scripts_python/analisis_subtipos_espinas_exp_001.py`, `scripts_python/analisis_subtipos_espinas_exp_002.py`
- **Output principal:** longitud dendrítica, densidad de espinas, proporción de subtipos y métricas de cambio por subtipo
- **Relación con la tesis:** cuantificación estructural de remodelado dendrítico y composición morfológica de espinas

---

## 4. Análisis estadístico general de variables conductuales e histológicas
- **Código asociado:** `scripts_python/analisis_estadistico_general.py`
- **Output principal:** análisis estadísticos complementarios
- **Relación con la tesis:** procesamiento estadístico general de variables derivadas de los experimentos

---

## 5. Relación entre tipos de archivo

En términos generales, la lógica del repositorio puede resumirse así:

- las **macros de ImageJ/Fiji** se utilizan para preprocesamiento de imágenes o generación de archivos intermedios;
- los **scripts en Python o R** se utilizan para cálculo de métricas, análisis estadístico o consolidación de resultados;
- los **protocolos** documentan el objetivo, los inputs, el procedimiento, las métricas generadas y los outputs de cada análisis.

---

## 6. Observaciones

- Algunos análisis dependen de más de un archivo y deben interpretarse como un flujo de trabajo integrado.
- En varios casos, las macros generan archivos de entrada que luego son procesados por scripts en Python o R.
- Cuando un análisis no tiene código asociado en este repositorio, el procedimiento correspondiente se realizó manualmente o con software específico no incluido como script.
