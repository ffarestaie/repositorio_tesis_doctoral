# PhD_project
PhD project analysis scripts

🧠 Microglia–Synapse Structural Analysis Workflows

This repository contains the complete computational workflows used to quantify and analyze structural remodeling in experimental models of Parkinson’s disease, with a focus on:

Microglia–dendrite spatial interactions

Microglial field coverage

Dendritic spine subtype distributions

Multivariate phenotypic clustering

Statistical modeling (ANOVA, GLM, LMM)

The codebase integrates image-derived metrics, categorical distribution analysis, unsupervised multivariate modeling, and mixed-effects statistical inference into a reproducible analysis framework.

🎯 Project Scope

The biological objective of these pipelines is to quantify structural plasticity and microglia-mediated remodeling under different experimental conditions.

The computational workflows are organized into three major analytical layers:

Image-derived structural metrics

Distributional / compositional statistics

Multivariate phenotypic modeling

Inferential statistical modeling

Each layer operates at a different level of biological abstraction and data structure.

🧩 Repository Architecture

The repository contains independent but interoperable notebooks and scripts grouped conceptually into:

1️⃣ Image-Based Quantification

These scripts operate on binarized TIFF images and produce quantitative structural metrics.

Microglia–Dendrite Contact

Slice-wise 2D proximity-based contact definition

Contact area fractions

Patch-level metrics

Contact efficiency indices

Microglial Field Coverage

Global field occupancy fraction

Area-normalized metrics

Outputs from this layer are structured tabular datasets designed for downstream statistical modeling.

2️⃣ Distributional Analysis of Spine Subtypes

Categorical analysis of spine subtype distributions across experimental conditions.

Methods include:

Contingency tables

Chi-square tests

Log-linear (Poisson GLM) modeling

Wald tests for interaction effects

This module evaluates compositional shifts rather than continuous structural changes.

3️⃣ Unsupervised Multivariate Modeling

Phenotypic state modeling using high-dimensional feature spaces.

Workflows include:

Feature filtering (variance + collinearity control)

Scaling strategies (global or baseline-anchored)

PCA dimensionality reduction

Clustering approaches:

K-means

Hierarchical clustering

Fuzzy C-means

These analyses model structural states and trajectories in latent space.

4️⃣ Statistical Modeling Framework

Centralized statistical workflow for hypothesis testing and visualization.

Includes:

Cell-level ANOVA

Animal-level ANOVA

Mixed Linear Models (random intercept by animal)

Cluster-robust standard errors

Holm-corrected post-hoc comparisons

Diagnostic residual analysis

The design explicitly addresses nested data structures (cells within animals).

📊 Data Hierarchy

The repository handles multiple biological scales:

Level	Unit of Analysis
Pixel	Binary masks
Field	Imaging field
Dendrite	Individual dendritic segment
Cell	Single neuron
Animal	Experimental subject
Group	Experimental condition

Statistical modeling decisions vary accordingly.

⚙️ Reproducibility Principles

All workflows follow these principles:

Explicit parameter blocks at top of scripts

Automated output directory generation

Snapshot of input dataset saved in each run

Export of QC tables and diagnostics

No silent data exclusion

Clear separation between:

preprocessing

metric computation

modeling

visualization

🧪 Experimental Modes

The code supports multiple experimental designs:

EXP-001

Week-based design

Optional hemisphere factor

Optional MSN subtype stratification

EXP-002

Factorial treatment1 × treatment2 design

Optional MSN subtype

The statistical workflow adapts formulas automatically to the detected structure.

🛠️ Requirements

Core dependencies:

Python ≥ 3.9

numpy

pandas

matplotlib

seaborn

scipy

scikit-learn

scikit-image

statsmodels

openpyxl

Recommended:

JupyterLab

🔁 Typical Workflow

Generate image-derived metrics (contact or coverage).

Export consolidated dataset.

Run graphs&stats for statistical modeling and figures.

(Optional) Run clustering workflows for multivariate state modeling.

(Optional) Run subtype distribution analysis for compositional statistics.

🧠 Conceptual Philosophy

The repository separates:

Geometric metrics (contact, coverage)

Compositional metrics (spine subtype distributions)

Latent multivariate states (clustering)

Inferential modeling (ANOVA / LMM)

Each analytical layer answers a different biological question.

📌 Notes

These workflows were developed for structural plasticity analysis in rodent models of dopaminergic degeneration.

The repository is organized for thesis-level reproducibility.

All scripts include detailed headers describing internal logic.
