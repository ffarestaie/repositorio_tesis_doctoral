#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
SCRIPT: CONTACTOS_EXP-002 – Métricas de contacto microglía–dendrita (slice-wise XY)

OBJETIVO
Este notebook cuantifica métricas de contacto entre microglía y dendrita a partir de
imágenes TIFF binarizadas multicanal (2 canales) en formato 3D (Z,Y,X), usando una
definición de contacto basada en vecindad en el plano XY por slice (ignorando vecindad en Z).

El pipeline:
1) Selecciona carpeta INPUT (TIFFs) y carpeta OUTPUT.
2) Carga un CSV de grupos con al menos columnas: ["animal", "tratamiento1", "tratamiento2"] (puede incluir otras).
3) Procesa cada TIFF: carga máscaras, calcula región de contacto por slice, deriva métricas.
4) Extrae metadata adicional desde el nombre del archivo (animal, msn_type) y mergea con el CSV.
5) Exporta tabla consolidada + genera un PDF con gráficos.

---------------------------------------------------------------------
FORMATO DE INPUT (IMÁGENES)
---------------------------------------------------------------------
- TIFF binario multicanal con shape (Z, C, Y, X) donde C=2.
  El script reordena a (Z, Y, X, C) internamente.
- Canal 0 (C=0): dendrita (máscara binaria, bool)
- Canal 1 (C=1): microglía (máscara binaria, bool)

---------------------------------------------------------------------
METADATA DESDE NOMBRE DE ARCHIVO
---------------------------------------------------------------------
- animal: se extrae con regex r"FFT\\d{6}-(\\d{3})-" (ej. "FFT240607-149-..." → animal=149)
- msn: se busca "D1" o "D2" como campo delimitado por guiones (p.ej. "-D1-" o "-D2-"):
    "D1" → "dMSN"
    "D2" → "iMSN"

Luego:
- Se mergea por "animal" contra el CSV de grupos.

---------------------------------------------------------------------
PARÁMETROS CLAVE
---------------------------------------------------------------------
- VOXEL_SIZE = [Z, Y, X] en µm. En este script:
    VOXEL_SIZE = [1.0, 0.16, 0.16]
  (Importante: la métrica de contacto usa solo Y y X).
- CONTACT_THRESHOLD_UM = 0.32 µm.
  Se interpreta como distancia máxima en XY para considerar “contacto”.

---------------------------------------------------------------------
DEFINICIÓN DE CONTACTO (IMPLEMENTACIÓN EXACTA)
---------------------------------------------------------------------
Se define contacto *slice-wise* (por cada z), considerando solo vecindad en XY:

Para cada slice z:
1) Sea m2 la máscara microglial 2D (bool).
2) Se calcula la Distance Transform 2D en µm sobre el complemento de m2:
       dt2 = distance_transform_edt(~m2, sampling=(dy, dx))
   donde dy=VOXEL_SIZE[Y], dx=VOXEL_SIZE[X].
   dt2(y,x) = distancia en XY al píxel microglial más cercano.
3) Sea d2 la máscara dendrítica 2D (bool).
4) Se define máscara de contacto del slice:
       contact2 = (dt2 <= CONTACT_THRESHOLD_UM) & d2
   Es decir: puntos dendríticos que están a ≤ umbral de microglía en el plano XY.
5) Se acumula una máscara 3D contact_region[z] = contact2.

---------------------------------------------------------------------
MÉTRICAS (DEFINICIONES EXACTAS)
---------------------------------------------------------------------
Definiciones base:
- dy = VOXEL_SIZE[1], dx = VOXEL_SIZE[2]
- pixel_area_um2 = dy * dx

1) dend_area_um2
   - dend_pixels = suma de True en la máscara dend 3D (Z,Y,X)
   - dend_area_um2 = dend_pixels * pixel_area_um2
   Nota: es “área acumulada por slice” (no volumen), porque no multiplica por voxel Z.

2) contact_area_um2
   - contact_pixels = suma de True en contact_region 3D
   - contact_area_um2 = contact_pixels * pixel_area_um2
   Nota: también es “área acumulada por slice”.

3) contact_area_fraction   (métrica principal en el script)
   - contact_area_fraction = contact_area_um2 / dend_area_um2
   Interpretación: fracción del “área dendrítica acumulada por slices” que cae dentro de la región
   a ≤ umbral de microglía en XY.

4) microglia_coverage_fraction
   - micro_pixels = suma de True en la máscara micro 3D
   - total_pixels_stack = micro.size (= Z*Y*X)
   - microglia_coverage_fraction = micro_pixels / total_pixels_stack
   Interpretación: fracción de voxeles del stack ocupados por microglía (sin ponderar por tamaño físico).

5) contact_efficiency_index
   - contact_efficiency_index = contact_area_fraction / microglia_coverage_fraction
   Interpretación: “contacto por unidad de cobertura global”, útil para normalizar contacto relativo
   a cuánta microglía hay en el stack.


Variables “debug” exportadas:
- dend_pixels
- contact_pixels

---------------------------------------------------------------------
SALIDAS
---------------------------------------------------------------------
- CSV consolidado con métricas por archivo (una fila por TIFF), más columnas del CSV de grupos.
- PDF: en la carpeta output, 2 pdf con gráficos de resumen.

---------------------------------------------------------------------
DEPENDENCIAS
---------------------------------------------------------------------
numpy, pandas, matplotlib, seaborn, skimage, scipy, tifffile, tqdm, statsmodels, tkinter.
"""


# In[ ]:


# Si falta instalar algo, descomentá las siguientes líneas:
# !pip install numpy scipy scikit-image tifffile matplotlib seaborn pandas tqdm

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns

from skimage import io
from scipy.ndimage import distance_transform_edt
import tkinter as tk
from tkinter import filedialog
from glob import glob
from tqdm import tqdm
import os
import re

sns.set(style="whitegrid", context="talk")

# voxel size en micrones (Z, Y, X)
VOXEL_SIZE = np.array([1.0, 0.16, 0.16])  # cuidado: EDT usa orden (z,y,x)

# distancia máxima para contar contacto microglial
CONTACT_THRESHOLD_UM = 0.32  # ~2x voxel XY


# In[ ]:


# FIX para Tkinter en Jupyter (ventanas de diálogo)
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)

print("Seleccioná la carpeta INPUT (imágenes TIFF binarizadas multicanal)…")
input_dir = filedialog.askdirectory(title="Carpeta INPUT")

print("Seleccioná la carpeta OUTPUT (CSV y resultados)…")
output_dir = filedialog.askdirectory(title="Carpeta OUTPUT")

print("Seleccioná el CSV con info de grupos (animal, tratamiento1, tratamiento2)…")
group_csv_path = filedialog.askopenfilename(
    title="CSV de grupos (animal, tratamiento1, tratamiento2)",
    filetypes=[("CSV files", "*.csv")]
)

out_pdf_grupos = os.path.join(output_dir, "graficos_contactos_exp_002.pdf")
out_pdf_msn = os.path.join(output_dir, "graficos_contactos_exp_002_d1_vs_d2.pdf")

# Leemos el CSV de grupos
group_df = pd.read_csv(group_csv_path)

# Aseguramos nombres de columnas esperados
expected_cols = {"animal", "tratamiento1", "tratamiento2"}
if not expected_cols.issubset(set(group_df.columns)):
    raise ValueError(f"El CSV de grupos debe tener columnas: {expected_cols}, "
                     f"pero tiene: {group_df.columns.tolist()}")

# Aseguramos que 'animal' es string
group_df["animal"] = group_df["animal"].astype(str).str.zfill(3)


# In[ ]:


# -----------------------------------------------------------
# EXTRAER CÓDIGO DE ANIMAL Y TIPO MSN DESDE EL NOMBRE
# -----------------------------------------------------------
def extraer_animal(path):
    m = re.search(r"FFT\d{6}-(\d{3})-", path)
    return m.group(1) if m else np.nan

def extraer_msn(path):
    m = re.search(r"(?<=[\-\+])(D1|D2)(?=[\-\+\.])", path)
    return m.group(1) if m else np.nan


# In[ ]:


def load_tiff(path):
    """
    Carga TIFF binario con dos canales en formato (Z,C,Y,X).
    Devuelve dend (GFP) y micro (IBA1) como booleanos (Z,Y,X).
    """
    img = io.imread(path)

    # Caso REAL de tus imágenes: (Z, C, Y, X)
    if img.ndim == 4 and img.shape[1] == 2:
        img = np.moveaxis(img, 1, -1)   # → (Z, Y, X, C)

    else:
        raise ValueError(f"Formato no reconocido para {path}: shape={img.shape}")

    # Extraer canales
    dend = img[..., 0].astype(bool)
    micro = img[..., 1].astype(bool)

    return dend, micro


# In[ ]:


def compute_contacts_xy_slicewise(dend_mask_bool, micro_mask_bool, contact_um=CONTACT_THRESHOLD_UM):
    """
    Contacto por vecindad en XY, slice-wise, ignorando vecindad en Z.

    Define contacto como: dendrita a distancia <= contact_um de microglia EN CADA SLICE.

    Inputs:
      - dend_mask_bool: bool, shape (Z,Y,X)
      - micro_mask_bool: bool, shape (Z,Y,X)

    Retorna:
    - surface_contact_um2: área total de contacto (sumatoria por slice) en µm²
    - num_patches: número total de parches (componentes conectados 2D por slice)
    - patch_sizes_um2: lista con tamaños de parches en µm²
    - contact_voxels: conteo total de voxeles/pixeles 3D marcados como contacto
    - contact_region: mask 3D bool (opcional, útil para debug)
    """
    if dend_mask_bool.shape != micro_mask_bool.shape:
        raise ValueError(f"Shapes distintas: dend {dend_mask_bool.shape} vs micro {micro_mask_bool.shape}")
    if dend_mask_bool.ndim != 3:
        raise ValueError(f"Se esperan masks 3D (Z,Y,X). ndim={dend_mask_bool.ndim}")

    dy, dx = float(VOXEL_SIZE[1]), float(VOXEL_SIZE[2])
    pixel_area_um2 = dy * dx

    Z = dend_mask_bool.shape[0]
    contact_region = np.zeros_like(dend_mask_bool, dtype=bool)

    for z in range(Z):
        d2 = dend_mask_bool[z]
        m2 = micro_mask_bool[z]

        # EDT 2D (en µm): distancia a microglia más cercana en el plano XY del slice
        dt2 = distance_transform_edt(~m2, sampling=(dy, dx))

        # contacto: solo dentro de dendrita, con umbral en XY
        contact2 = (dt2 <= contact_um) & d2
        contact_region[z] = contact2

    surface_contact_um2 = float(contact_region.sum()) * pixel_area_um2

    return {
        "surface_contact_um2": surface_contact_um2,
        "contact_voxels": int(contact_region.sum()),
        "contact_region": contact_region
    }

def process_image(path):
    dend, micro = load_tiff(path)  # arrays 3D (Z,Y,X)

    dend = dend.astype(bool)
    micro = micro.astype(bool)

    # --- contacto por vecindad slice-wise en XY ---
    contacts = compute_contacts_xy_slicewise(dend, micro, CONTACT_THRESHOLD_UM)

    # --- área total de dendrita en todo el stack (sin colapsar Z) ---
    dy, dx = float(VOXEL_SIZE[1]), float(VOXEL_SIZE[2])
    pixel_area_um2 = dy * dx

    dend_pixels = int(dend.sum())
    dend_area_um2 = float(dend_pixels) * pixel_area_um2

    # --- cobertura global de microglia sobre el área total del stack ---
    total_pixels_stack = micro.size  # Z * Y * X
    micro_pixels = int(micro.sum())

    microglia_coverage_fraction = micro_pixels / total_pixels_stack if total_pixels_stack > 0 else np.nan

    # --- métrica principal: fracción areal de contacto ---
    contact_area_um2 = float(contacts["surface_contact_um2"])
    contact_area_fraction = (contact_area_um2 / dend_area_um2) if dend_area_um2 > 0 else np.nan

    contact_efficiency_index = (
    contact_area_fraction / microglia_coverage_fraction
    if (microglia_coverage_fraction is not None and microglia_coverage_fraction > 0)
    else np.nan
    )


    return {
        "file": os.path.basename(path),
        "animal": extraer_animal(path),

        # áreas
        "dend_area_um2": dend_area_um2,
        "contact_area_um2": contact_area_um2,

        # métrica final
        "contact_area_fraction": float(contact_area_fraction),

        # debug útil (opcional)
        "dend_pixels": dend_pixels,
        "contact_pixels": int(contacts["contact_voxels"]),

        #cobertura de microglia
        "microglia_coverage_fraction": float(microglia_coverage_fraction),

        "contact_efficiency_index": float(contact_efficiency_index),

    }



# In[ ]:


results = []

files = sorted(
    glob(os.path.join(input_dir, "*.tif")) +
    glob(os.path.join(input_dir, "*.tiff"))
)

for f in tqdm(files, desc="Procesando imágenes"):
    try:
        metrics = process_image(f)
        results.append(metrics)
    except Exception as e:
        print(f"Error en: {f}")
        print(e)

df = pd.DataFrame(results)

df["file"] = df["file"].astype(str)
df["animal"] = df["file"].apply(extraer_animal)
df["msn_type"] = df["file"].apply(extraer_msn)

# Merge con info de grupos (animal, tratamiento1, tratamiento2)
group_df["animal"] = group_df["animal"].astype(str)
df = df.merge(group_df, on="animal", how="left")

# Columna de grupo combinado (opcional)
df["grupo"] = df["tratamiento1"].astype(str) + "_" + df["tratamiento2"].astype(str)

# Asegurar que animal es categórico
df["animal"] = df["animal"].astype("category")
df["msn_type"] = df["msn_type"].astype("category")

# Hacer categóricos los tratamientos
df["tratamiento1"] = df["tratamiento1"].astype("category")
df["tratamiento2"] = df["tratamiento2"].astype("category")

# Guardar
out_csv = os.path.join(output_dir, "metricas_contactos_exp_002.csv")
df.to_csv(out_csv, index=False)
print("Guardado CSV:", out_csv)

df.head()


# In[ ]:


metricas = [
    "dend_area_um2",
    "contact_area_um2",
    "contact_area_fraction",
    "microglia_coverage_fraction",
    "contact_efficiency_index",
]


# In[ ]:


with PdfPages(out_pdf_grupos) as pdf:
    sns.set(style="whitegrid")

    for metrica in metricas:

        plt.figure(figsize=(10,6))

        # Boxplot por grupo (sin hue)
        ax = sns.boxplot(
            data=df,
            x="grupo",
            y=metrica,
            palette="Set2",
            showfliers=False
        )

        # Stripplot con color por animal
        sns.stripplot(
            data=df,
            x="grupo",
            y=metrica,
            hue="animal",
            dodge=False,
            jitter=0.25,
            alpha=0.75,
            size=6
        )

        plt.title(f"Comparación entre grupos: {metrica}", fontsize=16)
        plt.xlabel("Grupo experimental", fontsize=14)
        plt.ylabel(metrica, fontsize=14)

        # Mover leyenda afuera (opcional)
        plt.legend(
            title="Animal",
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
            borderaxespad=0
        )

        plt.tight_layout()
        pdf.savefig()
        plt.close()



# In[ ]:


# GRAFICOS D1 VS D2

with PdfPages(out_pdf_msn) as pdf:
    sns.set(style="whitegrid", font_scale=1.2)

    for var in metricas:
        plt.figure(figsize=(10,6))

        # Boxplot por grupo y tipo MSN
        sns.boxplot(
            data=df,
            x="grupo",
            y=var,
            hue="msn_type",
            palette="Set2",
            showfliers=False
        )

        # Stripplot con color por animal (sin leyenda)
        sns.stripplot(
            data=df,
            x="grupo",
            y=var,
            hue="animal",
            dodge=True,
            jitter=0.25,
            alpha=0.75,
            size=6,
            legend=False
        )

        plt.title(f"{var} por tratamiento y tipo MSN")
        plt.xticks(rotation=45)

        # Mantener solo leyenda MSN (D1 vs D2)
        handles, labels = plt.gca().get_legend_handles_labels()
        if len(labels) > 0:
            # Quedarse solo con la primera leyenda (msn_type)
            plt.legend(handles[:2], labels[:2], title="MSN type")

        plt.tight_layout()
        pdf.savefig()
        plt.close()


