macro "MicrogliaCoverage_Preprocess" {

// === 1. Pedir carpetas ===
inputDir  = getDirectory("Seleccioná carpeta INPUT:");
if (inputDir=="") exit("Macro cancelada.");

outputDir = getDirectory("Seleccioná carpeta OUTPUT:");
if (outputDir=="") exit("Macro cancelada.");

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

		if (isOpen(gfp)) { selectWindow(gfp); close(); }
		if (!isOpen(iba)) { close("*"); continue; }
	
		selectWindow(iba);
	
		// --- Convertir a 8-bit ---
		run("8-bit");
	        
		// Subtract background
		run("Subtract Background...", "rolling=50 sliding stack");
	        
		// Threshold automático, Otsu
		setAutoThreshold("Li dark");
		run("Convert to Mask", "method=Li background=Dark calculate");
	
		name = list[i];
		if (endsWith(name, ".tif"))  base = substring(name, 0, lengthOf(name)-4);
		if (endsWith(name, ".tiff")) base = substring(name, 0, lengthOf(name)-5);
		saveAs("Tiff", outputDir + base + "_BIN.tif");
	    run("Close All");
		
    }
}    
print("Batch finalizado.");