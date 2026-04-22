#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Imports + funciones auxiliares (I/O, carpetas)

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tkinter import Tk, filedialog

from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

import skfuzzy as fuzz


# In[ ]:


def pick_input_xlsx(title="Select input .xlsx file"):
    """Open a file dialog to select an .xlsx input."""
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title=title,
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
    )
    root.destroy()
    if not path:
        raise RuntimeError("❌ No input file selected.")
    return path


def make_output_dirs(input_path):
    """
    Create an output folder structure next to the input file:
    <input_dir>/behavior_cluster_results/main/{tables,figures,logs}
    and processed data in:
    <input_dir>/behavior_cluster_results/data_processed
    """
    base_dir = os.path.dirname(os.path.abspath(input_path))
    root_out = os.path.join(base_dir, "behavior_cluster_results")
    main_out = os.path.join(root_out, "main")
    tables_dir = os.path.join(main_out, "tables")
    figures_dir = os.path.join(main_out, "figures")
    logs_dir = os.path.join(main_out, "logs")
    processed_dir = os.path.join(root_out, "data_processed")

    for d in [tables_dir, figures_dir, logs_dir, processed_dir]:
        os.makedirs(d, exist_ok=True)

    return {
        "root_out": root_out,
        "main_out": main_out,
        "tables": tables_dir,
        "figures": figures_dir,
        "logs": logs_dir,
        "processed": processed_dir,
    }


def write_xlsx(df, path, sheet_name="Sheet1"):
    """Save a dataframe to .xlsx (single sheet)."""
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)


def save_plot(path):
    """Convenience: tight layout + save png."""
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def split_metadata_features(df, meta_cols):
    meta = df[meta_cols].copy()
    feat_cols = [c for c in df.columns if c not in meta_cols]
    feats = df[feat_cols].copy()

    # enforce numeric features
    non_numeric = [c for c in feats.columns if not pd.api.types.is_numeric_dtype(feats[c])]
    if non_numeric:
        raise ValueError(f"❌ Non-numeric feature columns found: {non_numeric[:10]} (showing up to 10).")
    return meta, feats


# In[ ]:


# Frozen settings (Main Workflow)

META_COLS = ["ID animal", "tratamiento 1", "tratamiento 2", "semana"]
WEEK_COL = "semana"
WEEK_MIN, WEEK_MAX = 1, 6

# Filtering
VARIANCE_QUANTILE = 0.1       # bottom 10%
CORR_THRESHOLD = 0.95          # |r| > 0.95

# Scaling
BASELINE_T1_VALUE = "SHAM"
BASELINE_WEEK = 1
SCALING_METHOD = "zscore"      # main workflow (robustness later can test min-max)

# PCA
PCA_TRAIN_WEEK = 1             # train on all animals at week 1
PCA_TARGET_CUMVAR = 0.80       # retain PCs explaining >=80%

# Clustering
K_MIN, K_MAX = 2, 8
FUZZY_M = 2.0
FUZZY_MAXITER = 300
FUZZY_ERROR = 1e-5
RANDOM_STATE = 42


# In[ ]:


# =============================
# Step 01
# =============================

#Seleccionar input .xlsx + cargar dataset + checks básicos

input_path = pick_input_xlsx("Select your input dataset (.xlsx)")
out = make_output_dirs(input_path)

print("Input:", input_path)
print("Outputs root:", out["root_out"])

# Load first sheet (default behavior)
df = pd.read_excel(input_path, engine="openpyxl")
print("Loaded shape:", df.shape)

# ---- Schema checks ----
missing_meta = [c for c in META_COLS if c not in df.columns]
if missing_meta:
    raise ValueError(f"❌ Missing required metadata columns: {missing_meta}")

if not pd.api.types.is_numeric_dtype(df[WEEK_COL]):
    raise ValueError("❌ 'semana' must be numeric (1..6).")

bad_weeks = df.loc[~df[WEEK_COL].between(WEEK_MIN, WEEK_MAX), WEEK_COL]
if len(bad_weeks) > 0:
    raise ValueError(f"❌ Found 'semana' values outside 1..6. Examples: {bad_weeks.head().tolist()}")

# ---- Step 01 tables ----
schema_report = pd.DataFrame({
    "column": df.columns,
    "dtype": [str(t) for t in df.dtypes],
    "n_missing": df.isna().sum().values,
    "missing_frac": df.isna().mean().values,
}).sort_values("missing_frac", ascending=False)

missing_by_feature = pd.DataFrame({
    "feature": df.columns,
    "n_missing": df.isna().sum().values,
    "missing_frac": df.isna().mean().values,
}).sort_values("missing_frac", ascending=False)

missing_by_week = (
    df.groupby(WEEK_COL)
      .apply(lambda g: g.isna().mean())
      .reset_index()
)

counts_per_animal = df.groupby("ID animal")[WEEK_COL].nunique().reset_index()
counts_per_animal.columns = ["ID animal", "n_weeks_observed"]
counts_per_animal = counts_per_animal.sort_values("n_weeks_observed")

write_xlsx(schema_report, os.path.join(out["tables"], "01_schema_report.xlsx"))
write_xlsx(missing_by_feature, os.path.join(out["tables"], "01_missingness_by_feature.xlsx"))
write_xlsx(missing_by_week, os.path.join(out["tables"], "01_missingness_by_week.xlsx"))
write_xlsx(counts_per_animal, os.path.join(out["tables"], "01_counts_per_animal.xlsx"))

print("✅ Step 01 saved tables.")


# In[ ]:


# =============================
# Step 02A
# =============================

# Filtrado por varianza

meta_df, feat_df = split_metadata_features(df, META_COLS)
print("Initial features:", feat_df.shape[1])

variances = feat_df.var(axis=0, ddof=1)
var_threshold = float(variances.quantile(VARIANCE_QUANTILE))
keep_var = variances >= var_threshold

variance_table = pd.DataFrame({
    "feature": variances.index,
    "variance": variances.values,
    "keep": keep_var.values
}).sort_values("variance", ascending=True)

removed_low_var = variance_table.loc[~variance_table["keep"], ["feature", "variance"]].copy()

var_summary = pd.DataFrame([{
    "variance_quantile": VARIANCE_QUANTILE,
    "threshold_value": var_threshold,
    "n_in": feat_df.shape[1],
    "n_removed": int((~keep_var).sum()),
    "n_out": int(keep_var.sum())
}])

feat_var = feat_df.loc[:, keep_var.values].copy()
print("After variance filter:", feat_var.shape[1])

write_xlsx(variance_table, os.path.join(out["tables"], "02A_variance_table.xlsx"))
write_xlsx(removed_low_var, os.path.join(out["tables"], "02A_removed_low_variance.xlsx"))
write_xlsx(var_summary, os.path.join(out["tables"], "02A_variance_filter_summary.xlsx"))

# Plot variance histogram
plt.figure(figsize=(6,4))
plt.hist(variances.values, bins=30)
plt.axvline(var_threshold, linestyle="--")
plt.xlabel("Variance")
plt.ylabel("Count")
plt.title("Feature variance distribution (cutoff marked)")
save_plot(os.path.join(out["figures"], "02A_variance_histogram.png"))

print("✅ Step 02A completed.")


# In[ ]:


# =============================
# Step 02B
# =============================

# Filtrado por correlación

def mean_abs_corr(corr_matrix: pd.DataFrame) -> pd.Series:
    c = corr_matrix.abs().copy()
    np.fill_diagonal(c.values, np.nan)
    return c.mean(axis=1, skipna=True)

def flagged_pairs(corr_matrix: pd.DataFrame, thr: float) -> pd.DataFrame:
    c = corr_matrix.copy()
    mask = np.triu(np.ones(c.shape), k=1).astype(bool)
    vals = c.where(mask).stack().reset_index()
    vals.columns = ["feature_a", "feature_b", "r"]
    vals["abs_r"] = vals["r"].abs()
    outp = vals.loc[vals["abs_r"] > thr].sort_values("abs_r", ascending=False)
    return outp.drop(columns=["abs_r"])

# Correlation matrix pre (after variance filter)
corr_pre = feat_var.corr(method="pearson")
pairs_pre = flagged_pairs(corr_pre, CORR_THRESHOLD)

# Iterative removal
current = feat_var.copy()
removal_log = []

while True:
    corr = current.corr(method="pearson")
    pairs = flagged_pairs(corr, CORR_THRESHOLD)
    if pairs.empty:
        break

    mac = mean_abs_corr(corr)
    worst = mac.idxmax()

    removal_log.append({
        "removed_feature": worst,
        "mean_abs_corr": float(mac.loc[worst]),
        "reason": f"Removed feature with max mean(|r|); threshold={CORR_THRESHOLD}"
    })
    current = current.drop(columns=[worst])

    if current.shape[1] <= 1:
        break

feat_filt = current.copy()

feature_set_final = pd.DataFrame({"feature": feat_filt.columns})
corr_summary = pd.DataFrame([{
    "corr_threshold": CORR_THRESHOLD,
    "n_in": feat_var.shape[1],
    "n_removed": feat_var.shape[1] - feat_filt.shape[1],
    "n_out": feat_filt.shape[1]
}])

print("After correlation filter:", feat_filt.shape[1])

write_xlsx(pairs_pre, os.path.join(out["tables"], "02B_corr_pairs_flagged.xlsx"))
write_xlsx(pd.DataFrame(removal_log), os.path.join(out["tables"], "02B_corr_removal_log.xlsx"))
write_xlsx(feature_set_final, os.path.join(out["tables"], "02B_feature_set_final.xlsx"))
write_xlsx(corr_summary, os.path.join(out["tables"], "02_filtering_summary.xlsx"))

# Save datasets
df_filtered = pd.concat([meta_df, feat_filt], axis=1)
write_xlsx(df_filtered, os.path.join(out["processed"], "dataset_filtered.xlsx"))

# Corr heatmaps (optional but useful)
plt.figure(figsize=(8,6))
plt.imshow(corr_pre.values, aspect="auto")
plt.title("Correlation heatmap (pre-corr-filter)")
plt.colorbar()
save_plot(os.path.join(out["figures"], "02B_corr_heatmap_pre.png"))

corr_post = feat_filt.corr(method="pearson")
plt.figure(figsize=(8,6))
plt.imshow(corr_post.values, aspect="auto")
plt.title("Correlation heatmap (post-corr-filter)")
plt.colorbar()
save_plot(os.path.join(out["figures"], "02B_corr_heatmap_post.png"))

print("✅ Step 02B completed and saved.")


# In[ ]:


# =============================
# Step 03
# =============================

# Scaling

baseline_mask = (meta_df["tratamiento 1"] == BASELINE_T1_VALUE) & (meta_df[WEEK_COL] == BASELINE_WEEK)
n_base = int(baseline_mask.sum())
print("Baseline rows (SHAM S1):", n_base)
if n_base == 0:
    raise ValueError("❌ Baseline subset is empty (no SHAM S1 rows).")

baseline = feat_filt.loc[baseline_mask].copy()
means = baseline.mean(axis=0)
sds = baseline.std(axis=0, ddof=1)

scaling_params = pd.DataFrame({
    "feature": feat_filt.columns,
    "mean_baseline": means.values,
    "sd_baseline": sds.values
})

# Drop sd==0 or NaN
bad = (sds.isna()) | (sds == 0)
dropped_scaling = pd.DataFrame({
    "feature": sds.index[bad].tolist(),
    "reason": ["sd_baseline==0_or_nan"] * int(bad.sum())
})

good_features = sds.index[~bad].tolist()
feat_scaled = (feat_filt[good_features] - means[good_features]) / sds[good_features]

write_xlsx(scaling_params, os.path.join(out["tables"], "03_scaling_parameters.xlsx"))
write_xlsx(dropped_scaling, os.path.join(out["tables"], "03_scaling_dropped_features.xlsx"))

df_scaled = pd.concat([meta_df, feat_scaled], axis=1)
write_xlsx(df_scaled, os.path.join(out["processed"], "dataset_filtered_scaled.xlsx"))

print("✅ Step 03 scaling completed.")
print("Scaled features:", feat_scaled.shape[1])


# In[ ]:


# =============================
# Step 04
# =============================

# OUTLIER SCREENING (robust, MAD-based)
# Marks outliers per feature and ranks animals by outlier frequency

features_for_outliers = feat_scaled.copy()

meta_for_outliers = meta_df.copy()  # keeps: ID animal, tratamiento1, tratamiento2, semana

def mad(arr):
    med = np.median(arr)
    return np.median(np.abs(arr - med))

outlier_rows = []
feature_cols = list(features_for_outliers.columns)

for feat in feature_cols:
    x = features_for_outliers[feat].values.astype(float)
    med = np.nanmedian(x)
    mad_val = mad(x[np.isfinite(x)])
    if (mad_val == 0) or (not np.isfinite(mad_val)):
        # cannot compute robust z; skip or mark none
        continue

    robust_z = 0.6745 * (x - med) / mad_val
    flag = np.abs(robust_z) > 3.5

    idx = np.where(flag)[0]
    for i in idx:
        outlier_rows.append({
            "feature": feat,
            "ID animal": meta_for_outliers.iloc[i]["ID animal"],
            "tratamiento 1": meta_for_outliers.iloc[i]["tratamiento 1"],
            "tratamiento 2": meta_for_outliers.iloc[i]["tratamiento 2"],
            "semana": int(meta_for_outliers.iloc[i]["semana"]),
            "value": float(x[i]),
            "robust_z": float(robust_z[i]),
        })

if len(outlier_rows) > 0:
    outliers_df = (
        pd.DataFrame(outlier_rows)
        .sort_values(["feature", "robust_z"], ascending=[True, False])
        .reset_index(drop=True)
    )
else:
    outliers_df = pd.DataFrame(
        columns=[
            "feature",
            "ID animal",
            "tratamiento 1",
            "tratamiento 2",
            "semana",
            "value",
            "robust_z",
        ]
    )

write_xlsx(outliers_df, os.path.join(out["tables"], "04_outliers_MAD_flags.xlsx"))
print("✅ Saved outlier flags table:", outliers_df.shape)

# Rank animals by how often they appear as outliers
if len(outliers_df) > 0:
    animal_rank = (
        outliers_df.groupby("ID animal")
        .size()
        .reset_index(name="n_outlier_flags")
        .sort_values("n_outlier_flags", ascending=False)
    )
else:
    animal_rank = pd.DataFrame(columns=["ID animal", "n_outlier_flags"])

write_xlsx(animal_rank, os.path.join(out["tables"], "04_outliers_animal_ranking.xlsx"))
print("✅ Saved animal outlier ranking.")
animal_rank.head(10)

# =========================
# HISTOGRAM OVERLAY BY WEEK (all filtered features)
# =========================

plot_base = pd.concat([meta_df.reset_index(drop=True), feat_scaled.reset_index(drop=True)], axis=1)
weeks = sorted(plot_base["semana"].unique())

feature_cols = list(feat_scaled.columns)
print("Plotting histograms for features:", len(feature_cols))

for feat in feature_cols:
    plt.figure(figsize=(8,5))

    for w in weeks:
        vals = plot_base.loc[plot_base["semana"] == w, feat].dropna().values
        if len(vals) == 0:
            continue
        plt.hist(vals, bins=20, alpha=0.35, label=f"Week {w}")

    plt.xlabel(feat)
    plt.ylabel("Count")
    plt.title(f"Histogram overlay by week: {feat}")
    plt.legend(fontsize=8)

    fname = f"02_hist_by_week_{feat}".replace(" ", "_").replace("/", "_") + ".png"
    save_plot(os.path.join(out["figures"], fname))

print("✅ Saved histogram overlays by week for all filtered features.")

# =========================
# BOXPLOTS BY WEEK + MAD OUTLIER HIGHLIGHT
# =========================

plot_base = pd.concat([meta_df.reset_index(drop=True), feat_scaled.reset_index(drop=True)], axis=1)
plot_base["group"] = plot_base["tratamiento 1"].astype(str) + " | " + plot_base["tratamiento 2"].astype(str)

weeks = sorted(plot_base["semana"].unique())
feature_cols = list(feat_scaled.columns)

# Build a fast lookup set for outliers: (feature, animal, week)
outlier_key = set()
if "outliers_df" in globals() and len(outliers_df) > 0:
    for _, r in outliers_df.iterrows():
        outlier_key.add((str(r["feature"]), str(r["ID animal"]), int(r["semana"])))

print("Outlier highlight enabled:", len(outlier_key) > 0)

rng = np.random.default_rng(RANDOM_STATE)

for feat in feature_cols:
    plt.figure(figsize=(9,5))

    data_by_week = [plot_base.loc[plot_base["semana"] == w, feat].dropna().values for w in weeks]

    # Boxplot
    plt.boxplot(
        data_by_week,
        positions=list(range(1, len(weeks)+1)),
        widths=0.6,
        showfliers=False
    )

    # Overlay points + highlight outliers
    for i, w in enumerate(weeks, start=1):
        sub = plot_base.loc[plot_base["semana"] == w, ["ID animal", feat]].dropna()
        if sub.empty:
            continue

        x_jitter = i + rng.normal(0, 0.06, size=len(sub))
        y = sub[feat].values
        animals = sub["ID animal"].astype(str).values

        # normal points
        plt.scatter(x_jitter, y, alpha=0.55, s=25)

        # highlight outliers (MAD)
        if len(outlier_key) > 0:
            mask_out = np.array([(feat, a, int(w)) in outlier_key for a in animals], dtype=bool)
            if mask_out.any():
                plt.scatter(x_jitter[mask_out], y[mask_out], marker="x", s=120, linewidths=2)

    plt.xticks(range(1, len(weeks)+1), [f"W{w}" for w in weeks])
    plt.xlabel("Week")
    plt.ylabel(feat)
    plt.title(f"Boxplot by week with MAD outlier highlight: {feat}")

    fname = f"02_box_by_week_{feat}".replace(" ", "_").replace("/", "_") + ".png"
    save_plot(os.path.join(out["figures"], fname))

print("✅ Saved boxplots by week with MAD outlier highlights for all filtered features.")


# In[ ]:


# =============================
# Step 05
# =============================

#PCA
train_mask = meta_df[WEEK_COL] == PCA_TRAIN_WEEK
if int(train_mask.sum()) == 0:
    raise ValueError("❌ No rows found for PCA train week.")

X_train = feat_scaled.loc[train_mask].values
X_all = feat_scaled.values

pca = PCA(random_state=RANDOM_STATE)
pca.fit(X_train)

explained_ratio = pca.explained_variance_ratio_
cum = np.cumsum(explained_ratio)
n_components = int(np.searchsorted(cum, PCA_TARGET_CUMVAR) + 1)

print(f"PCA retains {n_components} PCs to reach ≥{int(PCA_TARGET_CUMVAR*100)}% variance")

# Transform all rows
scores_all_full = pca.transform(X_all)

# pc_cols must match what will be present in scores_df (i.e., only retained PCs)
pc_cols = [f"PC{i+1}" for i in range(n_components)]

# Create the dataframe only with retained PCs to avoid PC4/PC5 errors later
scores_df_full = pd.DataFrame(scores_all_full[:, :n_components], columns=pc_cols)

scores_df = pd.concat([meta_df.reset_index(drop=True), scores_df_full], axis=1)

# Loadings (keep full internal labels separate so explained_full stays correct)
pc_cols_full = [f"PC{i+1}" for i in range(scores_all_full.shape[1])]

loadings_full = pd.DataFrame(
    pca.components_.T,
    index=feat_scaled.columns,
    columns=pc_cols_full
)

# keep only retained PCs, and keep the same output variable name "loadings"
loadings = loadings_full.loc[:, pc_cols].reset_index().rename(columns={"index": "feature"})

# Explained variance tables:
explained_full = pd.DataFrame({
    "PC": pc_cols_full,
    "explained_variance_ratio": explained_ratio,
    "explained_variance_ratio_cum": cum
})

explained = explained_full.loc[explained_full["PC"].isin(pc_cols)].copy()
explained_trunc = explained.copy()  # same content now, kept for compatibility

write_xlsx(explained_full, os.path.join(out["tables"], "05_pca_explained_variance_full.xlsx"))
write_xlsx(explained_trunc, os.path.join(out["tables"], "05_pca_explained_variance.xlsx"))
write_xlsx(scores_df, os.path.join(out["tables"], "05_pca_scores_all.xlsx"))
write_xlsx(loadings, os.path.join(out["tables"], "05_pca_loadings.xlsx"))

# Scree plot (full, so you still see the elbow)
plt.figure(figsize=(6,4))
plt.plot(range(1, len(explained_ratio)+1), explained_ratio, marker="o")
plt.axvline(n_components, linestyle="--")
plt.xlabel("PC")
plt.ylabel("Explained variance ratio")
plt.title("Scree plot (PC variance explained)")
save_plot(os.path.join(out["figures"], "05_scree_plot.png"))

# PCA visualization: color by experimental group, fade by week, plus group trajectory
plot_df = scores_df.copy()
plot_df["group"] = plot_df["tratamiento 1"].astype(str) + " | " + plot_df["tratamiento 2"].astype(str)

groups = sorted(plot_df["group"].unique())
cmap = plt.get_cmap("tab10")
color_map = {g: cmap(i % 10) for i, g in enumerate(groups)}

week_vals = np.array(sorted(plot_df["semana"].unique()))
wmin, wmax = week_vals.min(), week_vals.max()

def alpha_for_week(w):
    if wmax == wmin:
        return 0.9
    return float(0.90 - (w - wmin) * (0.90 - 0.25) / (wmax - wmin))

# Only plot if we have at least 2 PCs retained
if ("PC1" in plot_df.columns) and ("PC2" in plot_df.columns):
    plt.figure(figsize=(7,6))

    # points
    for w in sorted(plot_df["semana"].unique()):
        subw = plot_df[plot_df["semana"] == w]
        for g in groups:
            sub = subw[subw["group"] == g]
            if len(sub) == 0:
                continue
            plt.scatter(
                sub["PC1"], sub["PC2"],
                s=25,
                alpha=alpha_for_week(w),
                color=color_map[g],
                edgecolors="none"
            )

    # trajectories (group centroids per week)
    for g in groups:
        sub = plot_df[plot_df["group"] == g]
        cent = sub.groupby("semana")[["PC1", "PC2"]].mean().reset_index().sort_values("semana")
        plt.plot(cent["PC1"], cent["PC2"], color=color_map[g], linewidth=2, label=g)
        plt.scatter(cent["PC1"], cent["PC2"], color=color_map[g], s=60)

    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.title("PCA space: groups (color) + longitudinal trajectory (centroids by week)")
    plt.legend(fontsize=8)
    save_plot(os.path.join(out["figures"], "05_pca_scatter_PC1_PC2_group_trajectory.png"))

print("✅ Step 05 PCA completed.")

# =====================================================
# TOP FEATURES PER PC (by absolute loading)
# =====================================================

TOP_N = 10

# loadings currently has a "feature" column (not index) -> set it as index for selection
if "feature" not in loadings.columns:
    raise ValueError("❌ 'feature' column not found in loadings. Check how loadings was built.")

loadings_idx = loadings.set_index("feature")

top_rows = []

for pc in pc_cols:

    if pc not in loadings_idx.columns:
        raise KeyError(f"❌ {pc} not found in loadings columns. Available: {list(loadings_idx.columns)}")

    abs_sorted = loadings_idx[pc].abs().sort_values(ascending=False)

    for rank, feat in enumerate(abs_sorted.head(TOP_N).index, start=1):

        val = float(loadings_idx.loc[feat, pc])

        top_rows.append({
            "PC": pc,
            "rank": rank,
            "feature": feat,
            "loading_signed": val,
            "loading_abs": float(abs(val))
        })

top_df = pd.DataFrame(top_rows)

write_xlsx(
    top_df,
    os.path.join(out["tables"], "PCA_top_features_per_PC.xlsx")
)

print("✅ Top features per PC table saved")

# =====================================================
# BARPLOT — Top features PC1 / PC2  [FIXED]
# =====================================================

for pc in pc_cols[:min(2, len(pc_cols))]:

    sub = top_df[top_df["PC"] == pc].sort_values("loading_abs", ascending=True)

    plt.figure(figsize=(6,5))
    plt.barh(sub["feature"], sub["loading_signed"])
    plt.xlabel("Loading (signed)")
    plt.title(f"Top contributing features — {pc}")

    save_plot(os.path.join(out["figures"], f"PCA_top_features_barplot_{pc}.png"))

print("✅ PCA loadings block completed")


# In[ ]:


# PCA loadings heatmap (Top N features per PC by |loading|)

TOP_N = 20

# loadings table: your saved 'loadings' has columns: feature, PC1..PCn
# Reconstruct a matrix:
load_mat = loadings.set_index("feature")[pc_cols].copy()

# pick top features per PC
top_features = set()
for pc in pc_cols:
    top = load_mat[pc].abs().sort_values(ascending=False).head(TOP_N).index.tolist()
    top_features.update(top)

top_features = sorted(top_features)
heat = load_mat.loc[top_features, pc_cols]

# Save the table
heat_tbl = heat.reset_index().rename(columns={"index": "feature"})
write_xlsx(heat_tbl, os.path.join(out["tables"], "05_pca_loadings_heatmap_top_features.xlsx"))

# Plot heatmap
plt.figure(figsize=(1.2*len(pc_cols)+3, 0.35*len(top_features)+3))
plt.imshow(heat.values, aspect="auto")
plt.colorbar(label="Loading")
plt.xticks(range(len(pc_cols)), pc_cols, rotation=0)
plt.yticks(range(len(top_features)), top_features)
plt.title(f"PCA Loadings Heatmap (Top {TOP_N} per PC by |loading|)")
save_plot(os.path.join(out["figures"], "05_pca_loadings_heatmap.png"))

print("✅ Saved PCA loadings heatmap (top features).")


# In[ ]:


# =============================
# Step 06
# =============================

# K selection (1–8) + fuzzy clustering
#funciones auxiliares fuzzy + WSS + silhouette

def run_fuzzy_cmeans_train(X_train, k, m=2.0, maxiter=300, error=1e-5, seed=42):
    # scikit-fuzzy expects (n_features, n_samples)
    data = X_train.T
    cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
        data, c=k, m=m, error=error, maxiter=maxiter, init=None, seed=seed
    )
    return cntr, u, fpc

def run_fuzzy_predict(X_all, cntr, m=2.0, error=1e-5, maxiter=300):
    data = X_all.T
    u, u0, d, jm, p, fpc = fuzz.cluster.cmeans_predict(
        test_data=data, cntr_trained=cntr, m=m, error=error, maxiter=maxiter
    )
    return u, fpc

def hard_labels_from_u(u):
    return np.argmax(u, axis=0)

def compute_wss(X, centroids, labels):
    wss = 0.0
    for c in range(centroids.shape[0]):
        idx = np.where(labels == c)[0]
        if len(idx) == 0:
            continue
        diffs = X[idx] - centroids[c]
        wss += float((diffs**2).sum())
    return wss

# --- K selection uses ONLY Week 1 points ---
week1_mask = (scores_df["semana"].values == 1)
X_all = scores_df[pc_cols].values
X_w1 = X_all[week1_mask]

k_values = list(range(K_MIN, K_MAX + 1))
rows = []

for k in k_values:
    cntr, u_w1, fpc = run_fuzzy_cmeans_train(
        X_w1, k=k, m=FUZZY_M, maxiter=FUZZY_MAXITER, error=FUZZY_ERROR, seed=RANDOM_STATE
    )
    labels = hard_labels_from_u(u_w1)  # 0..k-1, Week 1 only

    # silhouette on Week 1 only
    sil = np.nan
    try:
        if len(np.unique(labels)) >= 2:
            sil = float(silhouette_score(X_w1, labels))
    except Exception:
        sil = np.nan

    wss = compute_wss(X_w1, cntr, labels)

    rows.append({
        "K": k,
        "WSS_week1": wss,
        "Silhouette_week1": sil,
        "FPC_week1": float(fpc),
        "n_unique_hard_clusters_week1": int(len(np.unique(labels))),
    })

k_metrics = pd.DataFrame(rows).sort_values("K")
write_xlsx(k_metrics, os.path.join(out["tables"], "06_k_selection_metrics_week1.xlsx"))

# Plots
plt.figure(figsize=(5,4))
plt.plot(k_metrics["K"], k_metrics["WSS_week1"], marker="o")
plt.xlabel("K"); plt.ylabel("WSS (Week 1)")
plt.title("K selection on Week 1: WSS")
save_plot(os.path.join(out["figures"], "06_k_selection_wss_week1.png"))

plt.figure(figsize=(5,4))
plt.plot(k_metrics["K"], k_metrics["Silhouette_week1"], marker="o")
plt.xlabel("K"); plt.ylabel("Silhouette (Week 1)")
plt.title("K selection on Week 1: Silhouette")
save_plot(os.path.join(out["figures"], "06_k_selection_silhouette_week1.png"))

print("✅ K selection (Week 1) computed. Inspect k_metrics and the two plots.")
k_metrics



# In[ ]:


# correr clustering final con un K elegido

K_FINAL = int(k_metrics.loc[k_metrics["Silhouette_week1"].idxmax(), "K"])
print("Auto-selected K_FINAL (max silhouette on Week 1):", K_FINAL)

# If you want to force a different choice, uncomment and set:
# K_FINAL = 2

# Train fuzzy on Week 1
cntr, u_w1, fpc_w1 = run_fuzzy_cmeans_train(
    X_w1, k=K_FINAL, m=FUZZY_M, maxiter=FUZZY_MAXITER, error=FUZZY_ERROR, seed=RANDOM_STATE
)

# Predict membership for all weeks using trained centroids
u_all, fpc_all = run_fuzzy_predict(
    X_all, cntr=cntr, m=FUZZY_M, error=FUZZY_ERROR, maxiter=FUZZY_MAXITER
)

labels_all = hard_labels_from_u(u_all)  # 0..K-1

prob_cols = [f"cluster_{i+1}_prob" for i in range(K_FINAL)]
membership_df = pd.DataFrame(u_all.T, columns=prob_cols)
membership_df = pd.concat([scores_df[META_COLS].reset_index(drop=True), membership_df], axis=1)

hard_df = scores_df[META_COLS].copy().reset_index(drop=True)
hard_df["cluster_hard"] = labels_all + 1  # 1..K

centroids_df = pd.DataFrame(cntr, columns=pc_cols)
centroids_df.insert(0, "cluster", np.arange(1, K_FINAL+1))

write_xlsx(membership_df, os.path.join(out["tables"], "06_fuzzy_membership.xlsx"))
write_xlsx(hard_df, os.path.join(out["tables"], "06_cluster_assignments_hard.xlsx"))
write_xlsx(centroids_df, os.path.join(out["tables"], "06_cluster_centroids.xlsx"))

# Cluster visualization: group (color) + cluster (marker) + week (alpha)
plot_df = scores_df.copy()
plot_df["group"] = plot_df["tratamiento 1"].astype(str) + " | " + plot_df["tratamiento 2"].astype(str)
plot_df["cluster_hard"] = hard_df["cluster_hard"].values

groups = sorted(plot_df["group"].unique())
cmap = plt.get_cmap("tab10")
color_map = {g: cmap(i % 10) for i, g in enumerate(groups)}

markers = {1: "o", 2: "^"}  # cluster 1, 2 (extend if needed)

def alpha_for_week(w):
    return float(0.90 - (w - 1) * (0.90 - 0.25) / (6 - 1))

plt.figure(figsize=(7,6))
for w in sorted(plot_df["semana"].unique()):
    subw = plot_df[plot_df["semana"] == w]
    for g in groups:
        subg = subw[subw["group"] == g]
        for c in sorted(subg["cluster_hard"].unique()):
            sub = subg[subg["cluster_hard"] == c]
            if len(sub) == 0:
                continue
            plt.scatter(
                sub["PC1"], sub["PC2"],
                s=28,
                alpha=alpha_for_week(w),
                color=color_map[g],
                marker=markers.get(int(c), "o"),
                edgecolors="none"
            )

# centroids
plt.scatter(centroids_df["PC1"], centroids_df["PC2"], marker="x", s=180, label="Centroids")

plt.xlabel("PC1"); plt.ylabel("PC2")
plt.title("PCA space with Group (color), Cluster (marker), Week (fade)")
save_plot(os.path.join(out["figures"], "06_clusters_on_pca_PC1_PC2.png"))

print("✅ Step 06 final fuzzy clustering saved.")


# In[ ]:


# =============================
# Step 07A
# =============================

# Healthy cluster
# Definition: cluster with highest aggregate membership among SHAM across weeks 1

# Identify SHAM rows across week 1
sham_w1_mask = (membership_df["tratamiento 1"] == BASELINE_T1_VALUE) & (membership_df["semana"] == 1)
n_sham_w1 = int(sham_w1_mask.sum())
print("SHAM Week 1 rows:", n_sham_w1)
if n_sham_w1 == 0:
    raise ValueError("❌ No SHAM Week 1 rows found.")

agg = membership_df.loc[sham_w1_mask, prob_cols].sum(axis=0)
healthy_prob_col = agg.idxmax()
healthy_cluster_num = int(healthy_prob_col.split("_")[1])

healthy_def_table = pd.DataFrame({
    "cluster_prob_column": prob_cols,
    "aggregate_membership_SHAM_week1": agg.values,
})
healthy_def_table["is_healthy_cluster"] = healthy_def_table["cluster_prob_column"].eq(healthy_prob_col)

write_xlsx(healthy_def_table, os.path.join(out["tables"], "07_healthy_cluster_definition.xlsx"))

membership_df = membership_df.copy()
membership_df["Phealthy"] = membership_df[healthy_prob_col]

print("✅ Step 07A completed. Saved healthy cluster definition.")


# In[ ]:


# =============================
# Step 07B
# =============================

# Mahalanobis distance to healthy cluster (probability-weighted)

def weighted_mean(X, w):
    w = np.asarray(w).reshape(-1)
    wsum = w.sum()
    if wsum == 0:
        raise ValueError("All weights are zero. Cannot compute weighted mean.")
    return (X * w[:, None]).sum(axis=0) / wsum

def weighted_covariance(X, w, mu=None, ridge=1e-6):
    """
    Probability-weighted covariance.
    Uses a numerically stable normalization and adds a small ridge on the diagonal.
    """
    X = np.asarray(X)
    w = np.asarray(w).reshape(-1)
    if mu is None:
        mu = weighted_mean(X, w)

    wsum = w.sum()
    if wsum == 0:
        raise ValueError("All weights are zero. Cannot compute weighted covariance.")

    Xc = X - mu
    # normalize weights
    wn = w / wsum

    # effective degrees-of-freedom correction (avoids severe bias if weights are concentrated)
    denom = 1.0 - (wn**2).sum()
    if denom <= 1e-12:
        denom = 1e-12

    cov = (Xc * wn[:, None]).T @ Xc / denom

    # ridge for invertibility
    cov = cov + ridge * np.eye(cov.shape[0])
    return cov

def mahalanobis_distance(X, mu, cov):
    """
    Compute Mahalanobis distance for each row in X to (mu, cov).
    Uses pseudo-inverse for numerical stability.
    """
    X = np.asarray(X)
    mu = np.asarray(mu)
    cov_inv = np.linalg.pinv(cov)
    dif = X - mu
    # (x-mu)^T cov_inv (x-mu)
    d2 = np.einsum("ij,jk,ik->i", dif, cov_inv, dif)
    d2 = np.maximum(d2, 0)  # avoid tiny negative due to numeric noise
    return np.sqrt(d2)

# PCA coordinates used for distances
X_pca = scores_df[pc_cols].values
w_all = membership_df["Phealthy"].values

# Estimate mu/cov using SHAM Week 1 subset (weighted)
ref_mask = ((membership_df["tratamiento 1"] == BASELINE_T1_VALUE) & (membership_df["semana"] == 1)).values
X_ref = X_pca[ref_mask]
w_ref = w_all[ref_mask]

mu_h = weighted_mean(X_ref, w_ref)
cov_h = weighted_covariance(X_ref, w_ref, mu=mu_h, ridge=1e-6)

dist = mahalanobis_distance(X_pca, mu_h, cov_h)

mahal_df = membership_df[META_COLS].copy()
mahal_df["Mahalanobis_to_healthy"] = dist
mahal_df["group"] = mahal_df["tratamiento 1"].astype(str) + " | " + mahal_df["tratamiento 2"].astype(str)

write_xlsx(mahal_df, os.path.join(out["tables"], "07_mahalanobis_to_healthy.xlsx"))

summary = (
    mahal_df
    .groupby(["group", "semana"])["Mahalanobis_to_healthy"]
    .agg(["count", "mean", "median", "std"])
    .reset_index()
)
summary["sem"] = summary["std"] / np.sqrt(summary["count"].clip(lower=1))
write_xlsx(summary, os.path.join(out["tables"], "07_mahalanobis_summary_by_week_group.xlsx"))

plt.figure(figsize=(7,5))
for g in summary["group"].unique():
    sub = summary[summary["group"] == g].sort_values("semana")
    plt.errorbar(sub["semana"], sub["mean"], yerr=sub["sem"], marker="o", label=g)
plt.xlabel("Week")
plt.ylabel("Mahalanobis distance to SHAM Week 1 healthy reference")
plt.title("Distance to healthy reference over time (mean ± SEM)")
plt.legend(fontsize=8)
save_plot(os.path.join(out["figures"], "07_mahalanobis_over_time_by_group.png"))

print("✅ Step 07B updated Mahalanobis completed.")


# In[ ]:


# =============================
# Step 07C
# =============================

# Membership change metrics (Phealthy): ΔPhealthy = week6 - week1 (per animal)

# Build a compact dataframe: animal, week, Phealthy, group
ph = membership_df[["ID animal", "semana", "Phealthy", "tratamiento 1", "tratamiento 2"]].copy()
ph["group"] = ph["tratamiento 1"].astype(str) + " | " + ph["tratamiento 2"].astype(str)

# ΔPhealthy: week6 - week1 per animal
w1 = ph[ph["semana"] == 1][["ID animal", "Phealthy"]].rename(columns={"Phealthy": "Phealthy_w1"})
w6 = ph[ph["semana"] == 6][["ID animal", "Phealthy"]].rename(columns={"Phealthy": "Phealthy_w6"})

delta = pd.merge(w1, w6, on="ID animal", how="inner")
delta["Delta_Phealthy_w6_minus_w1"] = delta["Phealthy_w6"] - delta["Phealthy_w1"]

write_xlsx(delta, os.path.join(out["tables"], "07_membership_delta_week6_vs_week1.xlsx"))

# attach group info (from any row; week1 is fine)
group_map = ph.drop_duplicates("ID animal")[["ID animal", "group", "tratamiento 1", "tratamiento 2"]]
delta = pd.merge(delta, group_map, on="ID animal", how="left")

summ = (
    ph.groupby(["group", "semana"])["Phealthy"]
      .agg(["count", "mean", "std"])
      .reset_index()
)
summ["sem"] = summ["std"] / np.sqrt(summ["count"].clip(lower=1))

write_xlsx(summ, os.path.join(out["tables"], "07_Phealthy_group_summary_by_week.xlsx"))

# Optional slope: Phealthy ~ week per animal (simple linear fit)
slopes = []
for animal, g in ph.groupby("ID animal"):
    g = g.sort_values("semana")
    if g["semana"].nunique() < 2:
        continue
    x = g["semana"].values.astype(float)
    y = g["Phealthy"].values.astype(float)
    # slope from linear regression via polyfit degree 1
    slope, intercept = np.polyfit(x, y, 1)
    slopes.append({"ID animal": animal, "Phealthy_slope_per_week": slope})

slopes_df = pd.DataFrame(slopes)
slopes_df = pd.merge(slopes_df, group_map, on="ID animal", how="left")
write_xlsx(slopes_df, os.path.join(out["tables"], "07_membership_slope_per_animal.xlsx"))

# Plot spaghetti of Phealthy by group
plt.figure(figsize=(7,5))
for g in sorted(summ["group"].unique()):
    sub = summ[summ["group"] == g].sort_values("semana")
    plt.errorbar(sub["semana"], sub["mean"], yerr=sub["sem"], marker="o", label=g)
plt.xlabel("Week")
plt.ylabel("Mean P(healthy)")
plt.title("Phealthy over time by experimental group (mean ± SEM)")
plt.legend(fontsize=8)
save_plot(os.path.join(out["figures"], "07_membership_spaghetti_healthy.png"))

# Plot delta summary by group (box-like via scatter + mean)
plt.figure(figsize=(7,4))
groups = delta["group"].unique().tolist()
for i, g in enumerate(groups):
    vals = delta.loc[delta["group"] == g, "Delta_Phealthy_w6_minus_w1"].values
    x = np.ones_like(vals) * i
    plt.scatter(x, vals, alpha=0.7)
    plt.scatter([i], [np.mean(vals)], marker="x", s=120)
plt.xticks(range(len(groups)), groups, rotation=45, ha="right")
plt.ylabel("ΔPhealthy (week6 - week1)")
plt.title("Change in healthy membership probability by group")
save_plot(os.path.join(out["figures"], "07_membership_delta_summary.png"))

print("✅ Step 07C completed: ΔPhealthy + slope tables saved, plus plots.")


# In[ ]:




