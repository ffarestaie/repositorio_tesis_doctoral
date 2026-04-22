// === Macro: Cuantificación de colocalización GFP-Iba1 ===

inputDir = getDirectory("Seleccionar carpeta con imágenes TIFF (input)");
if (inputDir=="") exit("Macro cancelada.");

outputDir = getDirectory("Seleccionar carpeta donde guardar resultados (output)");
if (outputDir=="") exit("Macro cancelada.");

list = getFileList(inputDir);

// Crear archivo CSV de salida
resultsFile = outputDir + "colocalizacion_gfp_iba1.csv";
File.saveString("imagen,area_colocalizada\n", resultsFile);

for (i = 0; i < list.length; i++) {
    if (endsWith(list[i], ".tif") || endsWith(list[i], ".tiff")) {

        print("Procesando: " + list[i]);
        open(inputDir + list[i]);
        title = getTitle();

        // ---- Separar canales ----
        run("Split Channels");
        gfpTitle = "C1-" + title;
        ibaTitle = "C2-" + title;

        // ---- Proyección máxima Z ----
        selectWindow(gfpTitle);
		run("8-bit");
        run("Z Project...", "projection=[Max Intensity]");
        rename("GFP_proj");
        close(gfpTitle);

        selectWindow(ibaTitle);
		run("8-bit");
        run("Z Project...", "projection=[Max Intensity]");
        rename("Iba1_proj");
        close(ibaTitle);

        // ---- Subtract Background ----
        selectWindow("GFP_proj");
        run("Subtract Background...", "rolling=50");
        selectWindow("Iba1_proj");
        run("Subtract Background...", "rolling=50");

        // ---- Umbralización automática ----
        selectWindow("GFP_proj");
        run("Auto Threshold", "method=Triangle white");
        rename("GFP_bin_" + title);

        selectWindow("Iba1_proj");
        run("Auto Threshold", "method=Otsu white");
        rename("Iba1_bin_" + title);

        // ---- Rellenar huecos en Iba1 ----
        selectWindow("Iba1_bin_" + title);
        run("Fill Holes");

        // ---- Calcular colocalización ----
        imageCalculator("AND create", "Iba1_bin_" + title, "GFP_bin_" + title);
        rename(title + "_colocalization");

        // --- Medición área colocalizada ---
        selectWindow(title + "_colocalization");
        getStatistics(area, mean, min, max, std);

        if (max > 0) {
            setThreshold(1, 255);
            run("Set Measurements...", "area redirect=None decimal=3");
            // 🔹 descartar píxeles únicos
            run("Analyze Particles...", "size=4-Infinity show=Nothing clear summarize");
            selectWindow("Summary");
            areaColoc = getResult("Total Area", 0);

        } else {
            areaColoc = 0;
        }

        // ---- Guardar resultados ----
        File.append(list[i] + "," + areaColoc + "\n", resultsFile);

        // ---- Generar imagen de control ----
        selectWindow("GFP_bin_" + title);
        rename("GFP_bin_tmp");
        selectWindow("Iba1_bin_" + title);
        rename("Iba1_bin_tmp");

        run("Merge Channels...", "c1=GFP_bin_tmp c2=Iba1_bin_tmp create");
        rename( title + "_OVERLAY");
		name = list[i];
		base = name;
		if (endsWith(name, ".tif"))  base = substring(name, 0, lengthOf(name)-4);
		if (endsWith(name, ".tiff")) base = substring(name, 0, lengthOf(name)-5);
		
		saveAs("Tiff", outputDir + base + "_OVERLAY.tif");

        // ---- Cerrar todo ----
        close(list[i] + "_OVERLAY");
        close(title + "_colocalization");
        close("GFP_bin_" + title);
        close("Iba1_bin_" + title);
        close("GFP_proj");
        close("Iba1_proj");
        close(title);

        print("✅ Completado: " + list[i]);
    }
}

print("=== Análisis completado ===");
print("Resultados guardados en: " + resultsFile);
