# ============================================================
# calcular_vecino_mas_cercano.R
# ------------------------------------------------------------
# Calcula la distancia al vecino más cercano a partir de
# coordenadas X,Y exportadas desde Fiji/ImageJ.
#
# - Selección interactiva de archivos .csv o .xlsx
# - Cálculo de NND por archivo
# - Conversión a micras
# - Extracción flexible de metadata desde el nombre del archivo
# - Consolidación en un único CSV
# ============================================================

library(dplyr)
library(readr)
library(readxl)
library(stringr)
library(spatstat.geom)
library(tcltk)

# ------------------------------------------------------------
# Parámetros
# ------------------------------------------------------------
factor_conversion_um <- 0.16

# ------------------------------------------------------------
# Selección interactiva de archivos
# ------------------------------------------------------------
archivos <- tk_choose.files(
  caption = "Seleccionar archivos CSV o XLSX con coordenadas X,Y",
  multi = TRUE,
  filters = matrix(
    c("Archivos de datos", ".csv .xlsx"),
    ncol = 2,
    byrow = TRUE
  )
)

if (length(archivos) == 0) {
  stop("No se seleccionaron archivos.")
}

# ------------------------------------------------------------
# Función: lectura de archivo
# ------------------------------------------------------------
leer_archivo_coordenadas <- function(path) {
  ext <- tolower(tools::file_ext(path))
  
  if (ext == "csv") {
    datos <- read_csv(path, col_types = cols(), show_col_types = FALSE)
  } else if (ext == "xlsx") {
    datos <- read_excel(path)
  } else {
    stop(paste("Formato no soportado:", ext))
  }
  
  colnames(datos) <- tolower(colnames(datos))
  
  if (!all(c("x", "y") %in% colnames(datos))) {
    stop(
      paste0(
        "El archivo no contiene columnas 'x' e 'y'. Columnas encontradas: ",
        paste(colnames(datos), collapse = ", ")
      )
    )
  }
  
  datos <- datos %>%
    mutate(
      x = as.numeric(x),
      y = as.numeric(y)
    ) %>%
    filter(!is.na(x), !is.na(y))
  
  return(datos)
}

# ------------------------------------------------------------
# Función: cálculo NND
# ------------------------------------------------------------
distancia_vecino_mas_cercano <- function(x, y) {
  ventana <- owin(
    xrange = range(x, na.rm = TRUE),
    yrange = range(y, na.rm = TRUE)
  )
  puntos <- ppp(x, y, window = ventana)
  nndist(puntos)
}

# ------------------------------------------------------------
# Función: extracción flexible de metadata desde nombre archivo
# ------------------------------------------------------------
extraer_metadata_archivo <- function(path) {
  nombre <- basename(path)
  nombre_sin_ext <- tools::file_path_sans_ext(nombre)
  
  # Separar por guión bajo, guión medio o espacio
  tokens <- unlist(str_split(nombre_sin_ext, "[_\\-\\s]+"))
  tokens <- tokens[tokens != ""]
  
  tokens_lower <- tolower(tokens)
  
  # -------------------------
  # Animal
  # -------------------------
  animal <- NA_character_
  
  # Buscar un token de 2 a 4 dígitos
  idx_animal <- which(str_detect(tokens_lower, "^\\d{2,4}$"))
  if (length(idx_animal) > 0) {
    animal <- tokens[idx_animal[1]]
  } else {
    # Buscar patrones tipo FFT001, mouse001, m001, etc.
    idx_animal2 <- which(str_detect(tokens_lower, "([a-z]*\\d{2,4})"))
    if (length(idx_animal2) > 0) {
      animal <- tokens[idx_animal2[1]]
    }
  }
  
  # -------------------------
  # Semana
  # -------------------------
  semana <- NA_character_
  
  idx_semana <- which(
    str_detect(tokens_lower, "^s\\d+$") |
      str_detect(tokens_lower, "^semana\\d+$") |
      str_detect(tokens_lower, "^week\\d+$")
  )
  
  if (length(idx_semana) > 0) {
    semana <- tokens[idx_semana[1]]
  }
  
  # -------------------------
  # Tratamiento / condición
  # -------------------------
  tratamiento <- NA_character_
  
  # Sacar tokens que ya fueron asignados a animal o semana
  usados <- unique(c(
    if (!is.na(animal)) which(tokens == animal) else integer(0),
    if (!is.na(semana)) which(tokens == semana) else integer(0)
  ))
  
  candidatos <- tokens
  if (length(usados) > 0) {
    candidatos <- tokens[-usados]
  }
  
  if (length(candidatos) > 0) {
    tratamiento <- paste(candidatos, collapse = "_")
  }
  
  return(list(
    archivo = nombre,
    animal = animal,
    tratamiento = tratamiento,
    semana = semana
  ))
}

# ------------------------------------------------------------
# Procesamiento batch
# ------------------------------------------------------------
resultados <- list()

for (archivo in archivos) {
  cat("\nProcesando archivo:", archivo, "\n")
  
  datos <- tryCatch(
    leer_archivo_coordenadas(archivo),
    error = function(e) {
      cat("Error al leer el archivo:", e$message, "\n")
      return(NULL)
    }
  )
  
  if (is.null(datos)) next
  
  if (nrow(datos) < 2) {
    cat("No hay suficientes puntos para calcular distancias en:", basename(archivo), "\n")
    next
  }
  
  distancias_px <- distancia_vecino_mas_cercano(datos$x, datos$y)
  distancias_um <- distancias_px * factor_conversion_um
  
  info <- extraer_metadata_archivo(archivo)
  
  if (is.na(info$animal)) {
    cat("Advertencia: no se pudo inferir 'animal' desde el nombre:", info$archivo, "\n")
  }
  if (is.na(info$tratamiento)) {
    cat("Advertencia: no se pudo inferir 'tratamiento' desde el nombre:", info$archivo, "\n")
  }
  if (is.na(info$semana)) {
    cat("Advertencia: no se pudo inferir 'semana' desde el nombre:", info$archivo, "\n")
  }
  
  resultados[[length(resultados) + 1]] <- data.frame(
    archivo = info$archivo,
    animal = info$animal,
    tratamiento = info$tratamiento,
    semana = info$semana,
    distancia_px = distancias_px,
    distancia_um = distancias_um,
    stringsAsFactors = FALSE
  )
}

# ------------------------------------------------------------
# Consolidación final
# ------------------------------------------------------------
df_resultados <- bind_rows(resultados)

if (nrow(df_resultados) == 0) {
  stop("No se generaron resultados. Revisar archivos de entrada.")
}

# ------------------------------------------------------------
# Guardado
# ------------------------------------------------------------
salida <- file.path(getwd(), "distancias_vecino_mas_cercano.csv")
write_csv(df_resultados, salida)

cat("\nArchivo consolidado guardado en:\n", salida, "\n")