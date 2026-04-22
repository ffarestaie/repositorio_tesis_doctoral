#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
SCRIPT: microglia_field_coverage – Cobertura global microglial por campo

OBJETIVO
Este notebook cuantifica la cobertura global de microglía en campos
de imagen binarizados, independientemente de estructuras dendríticas.

El análisis calcula:

    - fracción del campo ocupada por microglía,
    - área total microglial,

y genera un dataset consolidado listo para análisis estadístico posterior
(LMM / ANOVA en graphs&stats).

---------------------------------------------------------------------
ENTRADA (INPUT)
---------------------------------------------------------------------

• Carpeta de imágenes TIFF binarizadas (2D).

Requisitos:

- Imágenes monocanal binarias (microglía ya segmentada).
- Formato esperado:
      array 2D (Y,X) o 3D con un único canal.
- Cada imagen representa un campo independiente.

Metadata:
- Se extrae desde el nombre del archivo:
      - ID animal
      - hemisferio (si está codificado)
      - semana o tratamiento (según convención del experimento)

- Se puede cargar un CSV externo para mapear:
      animal → grupo experimental (semana / tratamiento).

---------------------------------------------------------------------
PROCEDIMIENTO COMPUTACIONAL
---------------------------------------------------------------------

1) CARGA DE IMÁGENES
   - Itera sobre todos los TIFF en carpeta seleccionada.
   - Verifica dimensiones válidas.

2) CÁLCULO DE MÉTRICAS

Definiciones:

Sea:
    total_pixels = Y * X
    micro_pixels = suma de píxeles True

Entonces:

A) microglia_coverage_fraction
   = micro_pixels / total_pixels

   Interpretación:
   fracción del campo ocupada por microglía.

B) microglia_area_um2 (si VOXEL_SIZE está definido)
   = micro_pixels * pixel_area_um2
   donde pixel_area_um2 = dy * dx

3) CONSOLIDACIÓN
   - Una fila por imagen.
   - Se agregan columnas de metadata.
   - Se exporta CSV final consolidado.

---------------------------------------------------------------------
SALIDAS
---------------------------------------------------------------------

• CSV consolidado con:

    - file
    - ID_animal
    - grupo
    - microglia_coverage_fraction
    - microglia_area_um2 (si aplica)

---------------------------------------------------------------------
SUPUESTOS Y LIMITACIONES
---------------------------------------------------------------------

• La segmentación binaria es correcta.
• No se corrige por artefactos de borde.
• No se normaliza por profundidad Z (es análisis 2D).
• No se modela organización espacial (solo fracción ocupada).

Interpretación:

    Cambios en microglia_coverage_fraction reflejan
    cambios globales de ocupación del campo,
    no necesariamente cambios en morfología fina.



# In[1]:


import os
import re
from glob import glob

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from tqdm import tqdm

import tkinter as tk
from tkinter import filedialog

try:
    import tifffile as tiff
    _HAS_TIFFFILE = True
except Exception:
    _HAS_TIFFFILE = False
    from skimage import io


# -----------------------------
# Metadata (idéntico a contactos)
# -----------------------------
def extraer_animal(path):
    m = re.search(r"FFT\d{6}-(\d{3})-", path)
    return m.group(1) if m else np.nan

def extraer_hemi(path):
    m = re.search(r"(?:^|-) (?:[1-4])? ([IC]) (?=-)", path, flags=re.VERBOSE)
    if not m:
        return np.nan
    return "Ipsi" if m.group(1) == "I" else "Contra"


# -----------------------------
# Load TIFF binario (1 canal)
# -----------------------------
def load_tiff_binary(path):
    """
    Carga TIFF binario.
    Esperado: (Z,Y,X) o (Y,X). Devuelve bool (Z,Y,X).
    """
    if _HAS_TIFFFILE:
        img = tiff.imread(path)
    else:
        img = io.imread(path)

    if img.ndim == 2:
        img = img[None, :, :]  # (1,Y,X)
    elif img.ndim != 3:
        raise ValueError(f"Formato no reconocido para {os.path.basename(path)}: shape={img.shape}")

    return img.astype(bool)


# -----------------------------
# Coverage (idéntico concepto a contactos)
# -----------------------------
def microglia_coverage_stack(micro_bool):
    """
    micro_bool: (Z,Y,X) bool
    coverage global del stack = micro.sum()/micro.size
    """
    tot = micro_bool.size
    pos = int(micro_bool.sum())
    return (pos / tot) if tot > 0 else np.nan

def microglia_coverage_per_slice(micro_bool):
    """
    Devuelve vector (Z,) con coverage por slice (QC).
    """
    Z, Y, X = micro_bool.shape
    tot = Y * X
    pos = micro_bool.reshape(Z, -1).sum(axis=1)
    return pos / float(tot)


def main():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    input_dir = filedialog.askdirectory(title="Carpeta INPUT (TIFF binarizados)")
    if not input_dir:
        raise SystemExit("Cancelado (INPUT).")

    output_dir = filedialog.askdirectory(title="Carpeta OUTPUT")
    if not output_dir:
        raise SystemExit("Cancelado (OUTPUT).")

    xlsx_path = filedialog.askopenfilename(
        title="XLSX con semana por animal (columnas: animal, semana)",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not xlsx_path:
        raise SystemExit("Cancelado (XLSX).")

    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Leer XLSX (asumo sheet 1)
    group_df = pd.read_excel(xlsx_path)
    if not {"animal", "semana"}.issubset(group_df.columns):
        raise ValueError(f"El XLSX debe tener columnas 'animal' y 'semana'. Tiene: {group_df.columns.tolist()}")

    group_df["animal"] = group_df["animal"].astype(str).str.zfill(3)
    group_df["semana"] = group_df["semana"].astype(str)

    # Listar TIFFs
    paths = sorted(
        glob(os.path.join(input_dir, "*.tif")) +
        glob(os.path.join(input_dir, "*.tiff")) +
        glob(os.path.join(input_dir, "*.TIF")) +
        glob(os.path.join(input_dir, "*.TIFF"))
    )
    if not paths:
        raise ValueError("No encontré TIFFs en la carpeta INPUT.")

    summary_rows = []
    per_slice_rows = []

    print(f"Procesando {len(paths)} archivos…")

    for p in tqdm(paths):
        fname = os.path.basename(p)

        micro = load_tiff_binary(p)

        animal = extraer_animal(fname)
        hemi = extraer_hemi(fname)

        cov_stack = microglia_coverage_stack(micro)
        cov_z = microglia_coverage_per_slice(micro)

        summary_rows.append({
            "file": fname,
            "animal": str(animal).zfill(3) if pd.notna(animal) else np.nan,
            "hemisferio": hemi,
            "microglia_coverage": float(cov_stack),
            "n_slices": int(micro.shape[0]),
        })

        for z, cov in enumerate(cov_z, start=1):
            per_slice_rows.append({
                "file": fname,
                "animal": str(animal).zfill(3) if pd.notna(animal) else np.nan,
                "hemisferio": hemi,
                "slice": z,
                "microglia_coverage": float(cov),
            })

    summary_df = pd.DataFrame(summary_rows)
    per_slice_df = pd.DataFrame(per_slice_rows)


    # Merge semana desde XLSX (como en contactos)
    summary_df = summary_df.merge(group_df[["animal", "semana"]], on="animal", how="left")
    per_slice_df = per_slice_df.merge(group_df[["animal", "semana"]], on="animal", how="left")

    # Guardar CSVs
    out_summary = os.path.join(output_dir, "microglia_coverage_summary.csv")
    out_per_slice = os.path.join(output_dir, "microglia_coverage_per_slice.csv")
    summary_df.to_csv(out_summary, index=False)
    per_slice_df.to_csv(out_per_slice, index=False)

    # Plots (PDF): 1 página por animal (S1/S2/S4 con Ipsi/Contra)
    semana_order = {"S1": 1, "S2": 2, "S4": 4, "1": 1, "2": 2, "4": 4}
    summary_df["semana_num"] = summary_df["semana"].map(semana_order)

    out_pdf = os.path.join(output_dir, "microglia_coverage_plots.pdf")
    with PdfPages(out_pdf) as pdf:
        for animal, sub in summary_df.groupby("animal"):
            fig, ax = plt.subplots()

            if sub["semana_num"].notna().any():
                subp = sub.sort_values(["semana_num", "hemisferio"])
                for hemi, ss in subp.groupby("hemisferio"):
                    ax.plot(ss["semana_num"], ss["microglia_coverage"], marker="o", label=str(hemi))
                ax.set_xticks([1, 2, 4])
                ax.set_xticklabels(["S1", "S2", "S4"])
                ax.set_xlabel("Semana")
            else:
                # fallback si el XLSX no matcheó
                for hemi, ss in sub.groupby("hemisferio"):
                    ax.scatter([hemi]*len(ss), ss["microglia_coverage"], label=str(hemi))
                ax.set_xlabel("Hemisferio")

            ax.set_ylabel("Microglia coverage (stack)")
            ax.set_title(f"Animal {animal}")
            ax.grid(True, alpha=0.3)
            ax.legend()
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    # Report de animales sin semana
    missing = summary_df[summary_df["semana"].isna()]["animal"].dropna().unique().tolist()
    if missing:
        print("⚠️ Animales sin semana (no matchearon en el XLSX):", missing)

    print("OK ✅")
    print("Summary:", out_summary)
    print("Per-slice:", out_per_slice)
    print("Plots:", out_pdf)


if __name__ == "__main__":
    main()


# In[ ]:




