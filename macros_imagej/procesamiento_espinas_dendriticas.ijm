// ============================================================
// procesamiento_espinas_dendriticas.ijm
// ------------------------------------------------------------
// Procesa en batch imágenes TIFF/TIFF para análisis de espinas
// dendríticas en Fiji/ImageJ.
//
// Flujo:
// 1. Conversión a 8 bits
// 2. Enhance Contrast (0.35 % de saturación, stack completo)
// 3. Subtract Background (rolling ball = 50 px, stack completo)
// 4. Guardado de la imagen procesada en formato TIFF
//
// Input:
// - Carpeta con archivos .tif o .tiff
//
// Output:
// - Un archivo TIFF procesado por imagen, con sufijo "_PROCESADA"
//
// Nota:
// - Este macro no rota ni recorta la dendrita. Solo realiza el
//   preprocesamiento general de intensidad.
// ============================================================

macro "procesamiento_espinas_dendriticas" {

    inputDir = getDirectory("Seleccionar carpeta INPUT (TIF/TIFF)");
    if (inputDir == "") exit("Macro cancelada: no se seleccionó carpeta de entrada.");

    outputDir = getDirectory("Seleccionar carpeta OUTPUT");
    if (outputDir == "") exit("Macro cancelada: no se seleccionó carpeta de salida.");

    File.makeDirectory(outputDir);

    list = getFileList(inputDir);
    setBatchMode(true);

    for (i = 0; i < list.length; i++) {
        name = list[i];

        if (File.isDirectory(inputDir + name)) continue;

        lower = toLowerCase(name);
        if (!endsWith(lower, ".tif") && !endsWith(lower, ".tiff")) continue;

        open(inputDir + name);

        // Nombre base sin extensión
        base = name;
        if (endsWith(lower, ".tiff")) {
            base = substring(name, 0, lengthOf(name) - 5);
        } else if (endsWith(lower, ".tif")) {
            base = substring(name, 0, lengthOf(name) - 4);
        }

        // 1) Conversión a 8 bits
        run("8-bit");

        // 2) Enhance Contrast 0.35 %, stack completo
        run("Enhance Contrast...", "saturated=0.35 process_all use");

        // 3) Subtract Background, rolling ball 50 px, stack completo
        run("Subtract Background...", "rolling=50 stack");

        // 4) Guardado
        saveAs("Tiff", outputDir + base + "_PROCESADA.tif");

        close();
    }

    setBatchMode(false);
    print("Procesamiento finalizado. Archivos guardados en: " + outputDir);
}