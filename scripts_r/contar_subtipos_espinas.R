
library(dplyr)
library(tidyr)

# Seleccionar carpeta donde están los .txt
carpeta <- choose.dir(caption = "Selecciona la carpeta con los archivos .txt")
if (is.na(carpeta) || carpeta == "") {
  stop("No se seleccionó ninguna carpeta.")
}

# Listar todos los .txt
archivos <- list.files(carpeta, pattern = "\\.txt$", full.names = TRUE)
if (length(archivos) == 0) {
  stop("No se encontraron archivos .txt en la carpeta seleccionada.")
}

# Función para procesar un archivo
procesar_archivo <- function(archivo) {
  df <- data.table::fread(archivo, check.names = FALSE, data.table = FALSE)
  
  # Buscar columna que contenga "TYPE"
  clean_names <- gsub("[.\\s]+", "", colnames(df))
  idx <- which(grepl("TYPE", clean_names, ignore.case = TRUE))
  if (length(idx) == 0) {
    warning(paste("No se encontró columna TYPE en", basename(archivo)))
    return(NULL)
  }
  
  colname_type <- colnames(df)[idx[1]]
  
  # Limpiar valores
  df$subtipo_clean <- tolower(trimws(as.character(df[[colname_type]])))
  df$subtipo_clean <- dplyr::recode(df$subtipo_clean,
                                    "mushrrom" = "mushroom",
                                    .default = df$subtipo_clean)
  
  # Contar y pivotear
  conteo <- df %>%
    count(subtipo_clean) %>%
    tidyr::pivot_wider(names_from = subtipo_clean,
                       values_from = n,
                       values_fill = 0)
  
  # Agregar nombre del archivo
  conteo$archivo <- basename(archivo)
  
  return(conteo)
}

# Procesar todos los archivos y combinarlos
resultados <- lapply(archivos, procesar_archivo)
resultados <- bind_rows(resultados)

# Reordenar para que "archivo" quede primera columna
resultados <- resultados %>%
  relocate(archivo)

# Mostrar tabla final
print(resultados)

# Guardar en CSV si querés
write.csv(resultados, file.path(carpeta, "conteo_subtipos_batch.csv"), row.names = FALSE)
cat("Resultado guardado en: ", file.path(carpeta, "conteo_subtipos_batch.csv"), "\n")
