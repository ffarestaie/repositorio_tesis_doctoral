// ----------------------------------------------------------
// BATCH LIMPIEZA DENDRITA–MICROGLIA (Félix - vFinal)
// ----------------------------------------------------------

// === 1. Pedir carpetas ===
inputDir  = getDirectory("Seleccioná carpeta INPUT:");
if (inputDir=="") exit("Macro cancelada.");

outputDir = getDirectory("Seleccioná carpeta OUTPUT:");
if (outputDir=="") exit("Macro cancelada.");

// === 2. Listar archivos TIFF ===
list = getFileList(inputDir);

for (i=0; i<list.length; i++) {
    
    if (endsWith(list[i], ".tif") || endsWith(list[i], ".tiff")) {
        
        print("Procesando: " + list[i]);
        
        // --- ABRIR ---
        open(inputDir + list[i]);
        title = getTitle();
                
        // --- Split Channels ---
        run("Split Channels");
        gfp = "C1-" + title;
        iba = "C2-" + title;
        
        
        // ----------------------------------------------------------
        // === GFP ===
        // ----------------------------------------------------------
        selectWindow(gfp);
        // --- Convertir a 8-bit ---
        run("8-bit");
        
        // Subtract background
        run("Subtract Background...", "rolling=50 sliding stack");
        
		// Threshold Triangle
		setAutoThreshold("Triangle dark");
		run("Convert to Mask", "method=Triangle background=Dark calculate");

                // Connected Components Labeling
        run("Connected Components Labeling", "connectivity=6 type=[16 bits]");
        rename("GFP_labels");
        
        // Keep Largest Region
        run("Keep Largest Region", "connectivity=6");
        rename("GFP_clean");
        
        
        // ----------------------------------------------------------
        // === IBA1 ===
        // ----------------------------------------------------------
        selectWindow(iba);
        // --- Convertir a 8-bit ---
        run("8-bit");
        
        // Subtract background
        run("Subtract Background...", "rolling=50 sliding stack");
        
		// Threshold automático, Otsu
		setAutoThreshold("Otsu dark");
		run("Convert to Mask", "method=Otsu background=Dark calculate");
        
        rename("IBA1_clean");
        
        
        // ----------------------------------------------------------
        // === MERGE + LUTs ===
        // ----------------------------------------------------------
        run("Merge Channels...", "c1=GFP_clean c2=IBA1_clean create composite");
        
        // Aplicar LUTs
        Stack.setChannel(1);
        run("Green");
        
        Stack.setChannel(2);
        run("Red");
        
        // Guardar
		name = list[i];
		base = name;
		if (endsWith(name, ".tif"))  base = substring(name, 0, lengthOf(name)-4);
		if (endsWith(name, ".tiff")) base = substring(name, 0, lengthOf(name)-5);
		
		saveAs("Tiff", outputDir + base + "_CLEANED.tif");
        
        // ----------------------------------------------------------
        // === Cerrar todo antes de pasar a la siguiente imagen ===
        // ----------------------------------------------------------
        run("Close All");
    }
}

print("Batch finalizado.");
