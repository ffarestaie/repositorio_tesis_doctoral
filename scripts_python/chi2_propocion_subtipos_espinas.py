#!/usr/bin/env python
# coding: utf-8

# In[2]:


# chi_square_contribution_analysis.py

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency


def select_excel_file():
    """Open a file dialog to select an Excel input file."""
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo Excel con tabla de conteos",
        filetypes=[
            ("Excel files", "*.xlsx *.xls"),
            ("All files", "*.*")
        ]
    )

    root.destroy()

    if not file_path:
        print("No se seleccionó ningún archivo. Análisis cancelado.")
        sys.exit()

    return file_path


def read_count_table(file_path):
    """
    Read an Excel file assuming:
    - first column contains row labels, e.g. spine subtypes
    - remaining columns contain count data
    """

    df = pd.read_excel(file_path)

    if df.shape[1] < 2:
        raise ValueError("El archivo debe tener al menos una columna de etiquetas y una columna de datos.")

    # First column as row names
    df = df.set_index(df.columns[0])

    # Convert all values to numeric
    df = df.apply(pd.to_numeric, errors="coerce")

    if df.isna().any().any():
        raise ValueError(
            "La tabla contiene valores no numéricos o celdas vacías. "
            "Revisar el archivo de entrada."
        )

    if (df < 0).any().any():
        raise ValueError("La tabla contiene valores negativos. Los conteos deben ser >= 0.")

    if df.values.sum() == 0:
        raise ValueError("La suma total de la tabla es 0. No se puede calcular chi-cuadrado.")

    return df


def calculate_chi_square_contributions(observed_df):
    """
    Calculate:
    - chi-square test
    - expected counts
    - absolute cell contribution: (O - E)^2 / E
    - percentage cell contribution: 100 * cell contribution / total chi-square
    """

    observed = observed_df.values

    chi2, p_value, dof, expected = chi2_contingency(observed)

    expected_df = pd.DataFrame(
        expected,
        index=observed_df.index,
        columns=observed_df.columns
    )

    cell_contribution = (observed_df - expected_df) ** 2 / expected_df

    percent_contribution = 100 * cell_contribution / chi2

    return {
        "chi2": chi2,
        "p_value": p_value,
        "dof": dof,
        "observed": observed_df,
        "expected": expected_df,
        "cell_contribution": cell_contribution,
        "percent_contribution": percent_contribution
    }


def save_results(results, input_file):
    """Save all result tables to an Excel file."""

    input_dir = os.path.dirname(input_file)
    input_name = os.path.splitext(os.path.basename(input_file))[0]

    output_excel = os.path.join(
        input_dir,
        f"{input_name}_chi_square_contributions.xlsx"
    )

    summary = pd.DataFrame({
        "Statistic": ["Chi-square", "Degrees of freedom", "p-value"],
        "Value": [results["chi2"], results["dof"], results["p_value"]]
    })

    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="summary", index=False)
        results["observed"].to_excel(writer, sheet_name="observed")
        results["expected"].to_excel(writer, sheet_name="expected")
        results["cell_contribution"].to_excel(writer, sheet_name="chi2_cell_contribution")
        results["percent_contribution"].to_excel(writer, sheet_name="percent_contribution")

    return output_excel


def plot_percent_contribution(percent_df, input_file):
    """Generate a heatmap of percentage contribution to total chi-square."""

    input_dir = os.path.dirname(input_file)
    input_name = os.path.splitext(os.path.basename(input_file))[0]

    output_png = os.path.join(
        input_dir,
        f"{input_name}_percent_contribution_heatmap.png"
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    im = ax.imshow(percent_df.values)

    ax.set_xticks(np.arange(len(percent_df.columns)))
    ax.set_yticks(np.arange(len(percent_df.index)))

    ax.set_xticklabels(percent_df.columns, rotation=45, ha="right")
    ax.set_yticklabels(percent_df.index)

    ax.set_xlabel("Grupo experimental")
    ax.set_ylabel("Subtipo")
    ax.set_title("Aporte porcentual al chi-cuadrado total")

    # Add values inside cells
    for i in range(percent_df.shape[0]):
        for j in range(percent_df.shape[1]):
            value = percent_df.iloc[i, j]
            ax.text(
                j,
                i,
                f"{value:.1f}%",
                ha="center",
                va="center"
            )

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Aporte al χ² total (%)")

    plt.tight_layout()
    plt.savefig(output_png, dpi=300, bbox_inches="tight")
    plt.close()

    return output_png


def main():
    try:
        input_file = select_excel_file()

        observed_df = read_count_table(input_file)

        results = calculate_chi_square_contributions(observed_df)

        output_excel = save_results(results, input_file)
        output_png = plot_percent_contribution(
            results["percent_contribution"],
            input_file
        )

        print("\nAnálisis completado.")
        print(f"Chi-square: {results['chi2']:.4f}")
        print(f"Degrees of freedom: {results['dof']}")
        print(f"p-value: {results['p_value']:.4e}")
        print("\nTabla de aporte porcentual:")
        print(results["percent_contribution"].round(3))
        print(f"\nArchivo Excel guardado en:\n{output_excel}")
        print(f"\nGráfico guardado en:\n{output_png}")

        messagebox.showinfo(
            "Análisis completado",
            f"Chi-square = {results['chi2']:.4f}\n"
            f"df = {results['dof']}\n"
            f"p-value = {results['p_value']:.4e}\n\n"
            f"Excel:\n{output_excel}\n\n"
            f"Gráfico:\n{output_png}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))
        raise


if __name__ == "__main__":
    main()


# In[ ]:




