# analisis_estadistico_general.py
# ------------------------------------------------------------
# Workflow estadístico general para métricas derivadas de los
# análisis de la tesis.
#
# Incluye:
# - ANOVA factorial (OLS) como análisis principal
# - Confirmación con modelos lineales mixtos (LMM)
# - Chequeo de supuestos en residuos
# - Comparaciones post hoc con Tukey cuando hay interacción
# - Tablas descriptivas (Mean + SEM + n animals + n obs)
# - Tablas de diseño y reportes exportables
# - Opción de split por msn_type (D1/D2) para EXP-002
#
# Requisitos:
#   pip install pandas numpy scipy statsmodels openpyxl
# ------------------------------------------------------------

from __future__ import annotations

import os
import re
import json
import warnings
import datetime as dt
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# GUI file picker (built-in)
import tkinter as tk
from tkinter import filedialog

# ============================================================
# I/O
# ============================================================

def pick_input_file() -> str:
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Seleccionar archivo de datos de entrada",
        filetypes=[
            ("Data files", "*.csv *.xlsx *.xls"),
            ("CSV", "*.csv"),
            ("Excel", "*.xlsx *.xls"),
            ("All files", "*.*"),
        ],
    )
    if not path:
        raise SystemExit("No se seleccionó ningún archivo de entrada.")
    return path


def read_table(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    raise ValueError(f"Extensión de archivo no soportada: {ext}")


def safe_sheet_name(name: str) -> str:
    # Excel: max 31 chars, disallow : \ / ? * [ ]
    name = re.sub(r"[:\\/?*\[\]]", "_", name)
    return name[:31] if len(name) > 31 else name



# ============================================================
# Normalización de categorías y detección de niveles no reconocidos
# ============================================================

def normalize_categories(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    df = df.copy()
    warnings_list: List[str] = []

    if "hemisferio" in df.columns:
        hemi_raw = (
            df["hemisferio"]
            .astype(str)
            .str.strip()
            .str.lower()
            .replace({"nan": np.nan, "none": np.nan, "": np.nan})
        )
        hemi_map = {
            "ipsi": "ipsi",
            "contra": "contra",
            "ipsilateral": "ipsi",
            "contralateral": "contra",
        }
        bad_hemi = sorted(set(hemi_raw.dropna()) - set(hemi_map.keys()))
        if bad_hemi:
            warnings_list.append(
                f"hemisferio: niveles no reconocidos convertidos a NA: {bad_hemi}"
            )
        df["hemisferio"] = hemi_raw.map(hemi_map).where(~hemi_raw.isna(), np.nan)

    if "msn_type" in df.columns:
        msn_raw = (
            df["msn_type"]
            .astype(str)
            .str.strip()
            .str.lower()
            .replace({"nan": np.nan, "none": np.nan, "": np.nan})
        )
        msn_map = {
            "d1": "D1",
            "d2": "D2",
        }
        bad_msn = sorted(set(msn_raw.dropna()) - set(msn_map.keys()))
        if bad_msn:
            warnings_list.append(
                f"msn_type: niveles no reconocidos convertidos a NA: {bad_msn}"
            )
        df["msn_type"] = msn_raw.map(msn_map).where(~msn_raw.isna(), np.nan)

    return df, warnings_list


# ============================================================
# Experiment specs
# ============================================================

@dataclass
class AnalysisSpec:
    name: str
    animal_col: str
    factors: List[str]  # fixed categorical factors
    paired_within: Optional[str] = None
    paired_required_levels: Optional[List[str]] = None
    alpha: float = 0.05
    anova_type: int = 2  # Type II by default
    shapiro_max_n: int = 5000
    levene_center: str = "median"


def make_spec_exp001() -> AnalysisSpec:
    return AnalysisSpec(
        name="EXP-001",
        animal_col="ID_animal",
        factors=["hemisferio", "semana"],
        paired_within="hemisferio",
        paired_required_levels=["ipsi", "contra"],
    )


def make_spec_exp002(include_msn: bool) -> AnalysisSpec:
    factors = ["tratamiento1", "tratamiento2"]
    paired_within = None
    paired_levels = None
    name = "EXP-002"
    if include_msn:
        name = "EXP-002_MSN"
        factors = ["tratamiento1", "tratamiento2", "msn_type"]
        paired_within = "msn_type"
        paired_levels = ["D1", "D2"]

    return AnalysisSpec(
        name=name,
        animal_col="ID_animal",
        factors=factors,
        paired_within=paired_within,
        paired_required_levels=paired_levels,
    )


# ============================================================
# Design summaries / filtering
# ============================================================

def ensure_categorical(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c not in out.columns:
            raise KeyError(f"Missing required column: {c}")
        out[c] = out[c].astype("category")
    return out


def design_summary(df: pd.DataFrame, animal_col: str, factors: List[str]) -> Dict[str, pd.DataFrame]:
    out: Dict[str, pd.DataFrame] = {}

    out["Global"] = pd.DataFrame([{
        "n_rows": int(df.shape[0]),
        "n_animals": int(df[animal_col].nunique(dropna=True)),
    }])

    for f in factors:
        out[f"Obs_by_{f}"] = df[f].value_counts(dropna=False).rename_axis(f).reset_index(name="n_obs")
        out[f"Animals_by_{f}"] = (
            df.dropna(subset=[animal_col, f])
              .groupby(f, observed=True)[animal_col].nunique()
              .rename("n_animals")
              .reset_index()
        )

    out["Obs_by_cell"] = (
        df.dropna(subset=factors)
          .groupby(factors, observed=True)
          .size()
          .rename("n_obs")
          .reset_index()
    )

    out["Animals_by_cell"] = (
        df.dropna(subset=[animal_col] + factors)
          .groupby(factors, observed=True)[animal_col]
          .nunique()
          .rename("n_animals")
          .reset_index()
    )

    out["Obs_per_animal"] = (
        df.dropna(subset=[animal_col])
          .groupby(animal_col, observed=True)
          .size()
          .rename("n_obs")
          .reset_index()
          .sort_values("n_obs", ascending=False)
    )

    return out


def filter_animals_minobs(df: pd.DataFrame, animal_col: str, min_obs: int = 2) -> Tuple[pd.DataFrame, List[str], pd.DataFrame]:
    counts = df.groupby(animal_col, observed=True).size().rename("n_obs").reset_index()
    keep = set(counts.loc[counts["n_obs"] >= min_obs, animal_col])
    removed = sorted([str(a) for a in set(df[animal_col].unique()) - keep])
    return df[df[animal_col].isin(keep)].copy(), removed, counts


def filter_paired_animals(
    df: pd.DataFrame,
    animal_col: str,
    within_col: str,
    required_levels: List[str],
    min_obs_per_level: int = 1,
) -> Tuple[pd.DataFrame, List[str], pd.DataFrame]:
    tmp = df.dropna(subset=[animal_col, within_col]).copy()
    ct = (
        tmp.groupby([animal_col, within_col], observed=True)
           .size()
           .rename("n_obs")
           .reset_index()
    )
    wide = ct.pivot_table(index=animal_col, columns=within_col, values="n_obs", fill_value=0, observed=True)

    for lvl in required_levels:
        if lvl not in wide.columns:
            wide[lvl] = 0

    ok = (wide[required_levels] >= min_obs_per_level).all(axis=1)
    keep = set(wide.index[ok])
    removed = sorted([str(a) for a in wide.index[~ok]])

    report = wide.copy()
    report["keep"] = ok
    report = report.reset_index()

    return df[df[animal_col].isin(keep)].copy(), removed, report


# ============================================================
# Descriptive table (Mean + SEM + n animals + n obs)
# ============================================================

def descriptive_table_sem(df: pd.DataFrame, metric: str, factors: List[str], animal_col: str) -> pd.DataFrame:
    """
    Returns one row per cell (combination of factors) with:
      Mean, SEM, Animals_n, Observations_n
    SEM computed as sd / sqrt(n_obs) within each cell.
    """
    tmp = df.dropna(subset=[metric] + factors + [animal_col]).copy()
    if tmp.empty:
        return pd.DataFrame(columns=factors + ["Mean", "SEM", "Animals_n", "Observations_n"])

    g = tmp.groupby(factors, observed=True)

    desc = g[metric].agg(["mean", "std", "count"]).reset_index()
    desc["sem"] = desc["std"] / np.sqrt(desc["count"].clip(lower=1))

    animals = g[animal_col].nunique().reset_index(name="Animals_n")

    out = desc.merge(animals, on=factors, how="left")
    out = out.rename(columns={
        "mean": "Mean",
        "sem": "SEM",
        "count": "Observations_n"
    })

    out = out[factors + ["Mean", "SEM", "Animals_n", "Observations_n"]]
    return out


# ============================================================
# Modeling + diagnostics
# ============================================================

def build_formula(y: str, factors: List[str]) -> str:
    term = " * ".join([f"C({f})" for f in factors])
    return f"{y} ~ {term}"


def fit_anova_ols(df: pd.DataFrame, formula: str, anova_type: int) -> Tuple[object, pd.DataFrame]:
    ols = smf.ols(formula, data=df).fit()
    aov = anova_lm(ols, typ=anova_type).reset_index().rename(columns={"index": "term"})
    return ols, aov



def fit_lmm(df: pd.DataFrame, formula: str, animal_col: str):
    md = smf.mixedlm(formula, data=df, groups=df[animal_col])

    optimizers = [
        ("lbfgs", 300),
        ("powell", 600),
        ("bfgs", 400),
        ("cg", 400),
        ("nm", 600),
    ]

    attempts = []
    fitted_any = None

    for method, maxiter in optimizers:
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                model = md.fit(reml=False, method=method, maxiter=maxiter, disp=False)
            warning_msgs = [str(w.message) for w in caught]
            converged = bool(getattr(model, "converged", False))
            attempts.append({
                "method": method,
                "maxiter": maxiter,
                "status": "ok",
                "converged": converged,
                "warnings": warning_msgs,
            })
            fitted_any = model
            if converged:
                return model, attempts
        except Exception as e:
            attempts.append({
                "method": method,
                "maxiter": maxiter,
                "status": "error",
                "converged": False,
                "warnings": [str(e)],
            })

    return fitted_any, attempts


def lmm_fixed_only_residuals(m) -> np.ndarray:
    X = m.model.exog
    beta = m.fe_params.to_numpy()
    y = m.model.endog
    fitted = X @ beta
    return y - fitted


def normality_test(resid: np.ndarray, shapiro_max_n: int) -> Dict[str, float]:
    resid = resid[np.isfinite(resid)]
    n = resid.size
    if n < 3:
        return {"n": float(n), "test": "NA", "stat": np.nan, "p": np.nan}
    if n <= shapiro_max_n:
        stat, p = stats.shapiro(resid)
        test = "Shapiro-Wilk"
    else:
        stat, p = stats.normaltest(resid)  # D’Agostino-Pearson
        test = "D’Agostino-Pearson"
    return {"n": float(n), "test": test, "stat": float(stat), "p": float(p)}


def levene_test_by_cells(df: pd.DataFrame, y: str, factors: List[str], center: str) -> Dict[str, float]:
    tmp = df.dropna(subset=[y] + factors).copy()
    if tmp.empty:
        return {"test": "Levene", "stat": np.nan, "p": np.nan, "k_groups": 0.0}

    groups = []
    for _, g in tmp.groupby(factors, observed=True):
        vals = g[y].to_numpy()
        vals = vals[np.isfinite(vals)]
        if vals.size >= 2:
            groups.append(vals)

    if len(groups) < 2:
        return {"test": "Levene", "stat": np.nan, "p": np.nan, "k_groups": float(len(groups))}

    stat, p = stats.levene(*groups, center=center)
    return {"test": "Levene", "stat": float(stat), "p": float(p), "k_groups": float(len(groups))}


# ============================================================
# Post hoc utilities
# ============================================================

def combined_cell_factor(df: pd.DataFrame, factors: List[str], sep: str = " | ") -> pd.Series:
    return df[factors].astype(str).agg(sep.join, axis=1)


def tukey_on_cells(df: pd.DataFrame, y: str, cell_factors: List[str], alpha: float) -> pd.DataFrame:
    tmp = df.dropna(subset=[y] + cell_factors).copy()
    if tmp.empty:
        return pd.DataFrame()

    cell = combined_cell_factor(tmp, cell_factors)
    if cell.nunique(dropna=True) < 2:
        return pd.DataFrame()

    res = pairwise_tukeyhsd(endog=tmp[y].to_numpy(), groups=cell.to_numpy(), alpha=alpha)
    return pd.DataFrame(res._results_table.data[1:], columns=res._results_table.data[0])



def get_pvalue_from_anova(aov: pd.DataFrame, term: str) -> float:
    if "PR(>F)" not in aov.columns:
        return np.nan
    hit = aov.loc[aov["term"].astype(str) == term, "PR(>F)"]
    return float(hit.iloc[0]) if len(hit) else np.nan


# ============================================================
# Core analysis runner (one dataset/spec)
# ============================================================

@dataclass
class RunOutputs:
    meta: dict
    warnings: List[str]
    df_final: pd.DataFrame
    design_before: Dict[str, pd.DataFrame]
    design_after: Dict[str, pd.DataFrame]
    descriptive_sem: pd.DataFrame
    removed_minobs: List[str]
    removed_paired: List[str]
    animal_counts: pd.DataFrame
    paired_report: Optional[pd.DataFrame]
    formula: str
    ols_summary: str
    anova_table: pd.DataFrame
    lmm_summary: str
    lmm_fixed_effects: pd.DataFrame
    lmm_fit_attempts: pd.DataFrame
    diag_ols_norm: Dict[str, float]
    diag_ols_lev: Dict[str, float]
    diag_lmm_norm: Dict[str, float]
    diag_lmm_lev: Dict[str, float]
    posthoc_tables: Dict[str, pd.DataFrame]


def run_one_analysis(df_raw: pd.DataFrame, spec: AnalysisSpec, metric_col: str) -> RunOutputs:
    df, warnings = normalize_categories(df_raw)

    needed = [spec.animal_col] + spec.factors + [metric_col]
    for c in needed:
        if c not in df.columns:
            raise KeyError(f"Missing required column '{c}' for {spec.name}")

    df = df[needed].copy()
    df[metric_col] = pd.to_numeric(df[metric_col], errors="coerce")

    df0 = df.dropna(subset=[metric_col, spec.animal_col]).copy()
    df0 = ensure_categorical(df0, [spec.animal_col] + spec.factors)

    design_before = design_summary(df0, spec.animal_col, spec.factors)

    df_ge2, removed_minobs, animal_counts = filter_animals_minobs(df0, spec.animal_col, min_obs=2)

    removed_paired = []
    paired_report = None
    df_final = df_ge2
    if spec.paired_within is not None:
        df_final, removed_paired, paired_report = filter_paired_animals(
            df_ge2,
            animal_col=spec.animal_col,
            within_col=spec.paired_within,
            required_levels=spec.paired_required_levels or [],
            min_obs_per_level=1,
        )

    design_after = design_summary(df_final, spec.animal_col, spec.factors)

    # Descriptives on final dataset (Mean + SEM)
    desc_sem = descriptive_table_sem(df_final, metric_col, spec.factors, spec.animal_col)

    formula = build_formula(metric_col, spec.factors)

    ols, aov = fit_anova_ols(df_final, formula, spec.anova_type)
    lmm, lmm_attempts = fit_lmm(df_final, formula, spec.animal_col)

    diag_ols_norm = normality_test(ols.resid.to_numpy(), spec.shapiro_max_n)
    diag_ols_lev = levene_test_by_cells(df_final, metric_col, spec.factors, center=spec.levene_center)

    if lmm is not None:
        lmm_resid = lmm_fixed_only_residuals(lmm)
        diag_lmm_norm = normality_test(lmm_resid, spec.shapiro_max_n)
        diag_lmm_lev = levene_test_by_cells(df_final, metric_col, spec.factors, center=spec.levene_center)

        lmm_fe = pd.DataFrame({
            "term": lmm.fe_params.index.astype(str),
            "beta": lmm.fe_params.to_numpy(),
            "se": lmm.bse_fe.to_numpy(),
            "z_or_t": lmm.tvalues[:len(lmm.fe_params)].to_numpy(),
            "p": lmm.pvalues[:len(lmm.fe_params)].to_numpy(),
        })
        lmm_summary_text = lmm.summary().as_text()
    else:
        diag_lmm_norm = {"n": np.nan, "test": "NA", "stat": np.nan, "p": np.nan}
        diag_lmm_lev = {"test": "Levene", "stat": np.nan, "p": np.nan, "k_groups": np.nan}
        lmm_fe = pd.DataFrame(columns=["term", "beta", "se", "z_or_t", "p"])
        lmm_summary_text = "LMM no pudo ajustarse con los optimizadores intentados."

    lmm_attempts_df = pd.DataFrame(lmm_attempts)

    posthoc: Dict[str, pd.DataFrame] = {}

    interaction_terms = [t for t in aov["term"].astype(str) if ":" in t]
    hay_interaccion_significativa = any(
        np.isfinite(get_pvalue_from_anova(aov, t)) and get_pvalue_from_anova(aov, t) < spec.alpha
        for t in interaction_terms
    )

    if hay_interaccion_significativa:
        tuk_cells = tukey_on_cells(df_final, metric_col, spec.factors, spec.alpha)
        if not tuk_cells.empty:
            posthoc["Tukey_cells_" + "_x_".join(spec.factors)] = tuk_cells

    if lmm_attempts_df.empty:
        warnings.append("LMM: no se registraron intentos de ajuste.")
    elif not bool(lmm_attempts_df.get("converged", pd.Series(dtype=bool)).fillna(False).any()):
        warnings.append("LMM: ningún optimizador alcanzó convergencia; se reporta el mejor ajuste disponible o se deja constancia del fallo.")

    meta = {
        "spec": {
            "name": spec.name,
            "animal_col": spec.animal_col,
            "factors": spec.factors,
            "paired_within": spec.paired_within,
            "paired_required_levels": spec.paired_required_levels,
            "alpha": spec.alpha,
            "anova_type": spec.anova_type,
        },
        "metric_col": metric_col,
        "formula": formula,
        "n_rows_input": int(df_raw.shape[0]),
        "n_rows_used_before_filters": int(df0.shape[0]),
        "n_rows_used_final": int(df_final.shape[0]),
        "n_animals_before_filters": int(df0[spec.animal_col].nunique()),
        "n_animals_final": int(df_final[spec.animal_col].nunique()),
        "removed_minobs(<2obs)": removed_minobs,
        "removed_paired_incomplete": removed_paired,
        "warnings": warnings,
        "lmm_fit_attempts": lmm_attempts,
    }

    return RunOutputs(
        meta=meta,
        warnings=warnings,
        df_final=df_final,
        design_before=design_before,
        design_after=design_after,
        descriptive_sem=desc_sem,
        removed_minobs=removed_minobs,
        removed_paired=removed_paired,
        animal_counts=animal_counts,
        paired_report=paired_report,
        formula=formula,
        ols_summary=ols.summary().as_text(),
        anova_table=aov,
        lmm_summary=lmm_summary_text,
        lmm_fixed_effects=lmm_fe,
        lmm_fit_attempts=lmm_attempts_df,
        diag_ols_norm=diag_ols_norm,
        diag_ols_lev=diag_ols_lev,
        diag_lmm_norm=diag_lmm_norm,
        diag_lmm_lev=diag_lmm_lev,
        posthoc_tables=posthoc,
    )


# ============================================================
# Reporting / exporting
# ============================================================

def write_outputs(out_dir: str, name: str, outputs: RunOutputs) -> None:
    os.makedirs(out_dir, exist_ok=True)

    # JSON meta
    with open(os.path.join(out_dir, f"{name}_run_meta.json"), "w", encoding="utf-8") as f:
        json.dump(outputs.meta, f, indent=2, ensure_ascii=False)

    # TXT report (human-readable)
    lines = []
    lines.append(f"REPORTE ESTADÍSTICO - {name}")
    lines.append(f"Métrica: {outputs.meta['metric_col']}")
    lines.append(f"Fórmula: {outputs.formula}")
    lines.append("")
    lines.append("ADVERTENCIAS:")
    lines.extend(outputs.warnings if outputs.warnings else ["(ninguna)"])
    lines.append("")
    lines.append("RESUMEN DE FILTRADO:")
    lines.append(f"- Animales antes de filtros: {outputs.meta['n_animals_before_filters']}")
    lines.append(f"- Animales finales: {outputs.meta['n_animals_final']}")
    lines.append(f"- Filas antes de filtros: {outputs.meta['n_rows_used_before_filters']}")
    lines.append(f"- Filas finales: {outputs.meta['n_rows_used_final']}")
    lines.append(f"- Removidos (obs mínimas <2): {len(outputs.removed_minobs)}")
    lines.append(f"- Removidos (pareado incompleto): {len(outputs.removed_paired)}")
    if outputs.removed_minobs:
        lines.append(f"  * IDs (obs mínimas <2): {', '.join(outputs.removed_minobs)}")
    if outputs.removed_paired:
        lines.append(f"  * IDs (pareado incompleto): {', '.join(outputs.removed_paired)}")
    lines.append("")
    lines.append("CHEQUEO DE SUPUESTOS (sobre residuos):")
    lines.append(f"- OLS normality ({outputs.diag_ols_norm['test']}): stat={outputs.diag_ols_norm['stat']:.4g}, p={outputs.diag_ols_norm['p']:.4g}, n={int(outputs.diag_ols_norm['n'])}")
    lines.append(f"- OLS Levene (cells): stat={outputs.diag_ols_lev['stat']:.4g}, p={outputs.diag_ols_lev['p']:.4g}, k_groups={int(outputs.diag_ols_lev['k_groups'])}")
    lines.append(f"- LMM normality ({outputs.diag_lmm_norm['test']}): stat={outputs.diag_lmm_norm['stat']:.4g}, p={outputs.diag_lmm_norm['p']:.4g}, n={int(outputs.diag_lmm_norm['n'])}")
    lines.append(f"- LMM Levene (cells): stat={outputs.diag_lmm_lev['stat']:.4g}, p={outputs.diag_lmm_lev['p']:.4g}, k_groups={int(outputs.diag_lmm_lev['k_groups'])}")
    lines.append("")
    lines.append("TABLA ANOVA (OLS):")
    lines.append(outputs.anova_table.to_string(index=False))
    lines.append("")
    lines.append("EFECTOS FIJOS DEL LMM (tabla en xlsx):")
    lines.append("INTENTOS DE AJUSTE DEL LMM (tabla en xlsx):")
    lines.append("")
    lines.append("TABLAS POST HOC (en xlsx):")
    if outputs.posthoc_tables:
        for k, v in outputs.posthoc_tables.items():
            lines.append(f"- {k}: {v.shape[0]} rows")
    else:
        lines.append("(ninguna)")
    lines.append("")
    lines.append("RESUMEN OLS (completo):")
    lines.append(outputs.ols_summary)
    lines.append("")
    lines.append("RESUMEN LMM (completo):")
    lines.append(outputs.lmm_summary)

    with open(os.path.join(out_dir, f"{name}_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # XLSX workbook
    xlsx_path = os.path.join(out_dir, f"{name}_stats_outputs.xlsx")
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as xl:
        # Descriptives (Mean + SEM)
        outputs.descriptive_sem.to_excel(xl, index=False, sheet_name="Descriptive_stats_SEM")

        # Design summaries
        for k, tab in outputs.design_before.items():
            tab.to_excel(xl, index=False, sheet_name=safe_sheet_name(f"Design_BEFORE_{k}"))
        for k, tab in outputs.design_after.items():
            tab.to_excel(xl, index=False, sheet_name=safe_sheet_name(f"Design_AFTER_{k}"))

        # Filtering reports
        pd.DataFrame({"removed_minobs(<2obs)": outputs.removed_minobs}).to_excel(
            xl, index=False, sheet_name="Removed_MinObs"
        )
        pd.DataFrame({"removed_paired_incomplete": outputs.removed_paired}).to_excel(
            xl, index=False, sheet_name="Removed_Paired"
        )
        outputs.animal_counts.to_excel(xl, index=False, sheet_name="Animal_nObs")
        if outputs.paired_report is not None and not outputs.paired_report.empty:
            outputs.paired_report.to_excel(xl, index=False, sheet_name="Paired_Check")

        # Models
        outputs.anova_table.to_excel(xl, index=False, sheet_name="ANOVA_OLS")
        outputs.lmm_fixed_effects.to_excel(xl, index=False, sheet_name="LMM_FixedEffects")
        outputs.lmm_fit_attempts.to_excel(xl, index=False, sheet_name="LMM_FitAttempts")
        pd.DataFrame({"OLS_summary": [outputs.ols_summary]}).to_excel(xl, index=False, sheet_name="OLS_Summary")
        pd.DataFrame({"LMM_summary": [outputs.lmm_summary]}).to_excel(xl, index=False, sheet_name="LMM_Summary")

        # Diagnostics
        pd.DataFrame([
            {"model": "OLS", **outputs.diag_ols_norm},
            {"model": "LMM_fixed_only", **outputs.diag_lmm_norm},
        ]).to_excel(xl, index=False, sheet_name="Diag_Normality")

        pd.DataFrame([
            {"model": "OLS", **outputs.diag_ols_lev},
            {"model": "LMM_fixed_only", **outputs.diag_lmm_lev},
        ]).to_excel(xl, index=False, sheet_name="Diag_Levene")

        # Post hoc
        if outputs.posthoc_tables:
            for k, tab in outputs.posthoc_tables.items():
                tab.to_excel(xl, index=False, sheet_name=safe_sheet_name("PH_" + k))
        else:
            pd.DataFrame([{"nota": "No se generaron tablas post hoc."}]).to_excel(
                xl, index=False, sheet_name="Posthoc_NOTE"
            )

        # Run info + warnings
        pd.DataFrame([{
            "spec_name": outputs.meta["spec"]["name"],
            "metric_col": outputs.meta["metric_col"],
            "formula": outputs.formula,
            "alpha": outputs.meta["spec"]["alpha"],
            "anova_type": outputs.meta["spec"]["anova_type"],
        }]).to_excel(xl, index=False, sheet_name="Run_Info")

        pd.DataFrame({"warnings": outputs.warnings if outputs.warnings else ["(none)"]}).to_excel(
            xl, index=False, sheet_name="Warnings"
        )


# ============================================================
# CLI flow
# ============================================================

def choose_experiment() -> AnalysisSpec:
    print("\nSeleccionar diseño experimental:")
    print("  1) EXP-001 (hemisferio + semana; pareado en hemisferio)")
    print("  2) EXP-002 (tratamiento1 + tratamiento2)")
    print("  3) EXP-002 + msn_type (tratamiento1 + tratamiento2 + msn_type; pareado en msn_type)")
    print("  4) Personalizado")

    choice = input("Ingresar 1/2/3/4 [default=1]: ").strip() or "1"

    if choice == "1":
        return make_spec_exp001()
    if choice == "2":
        return make_spec_exp002(include_msn=False)
    if choice == "3":
        return make_spec_exp002(include_msn=True)
    if choice == "4":
        animal = input("Columna de animal [default=ID_animal]: ").strip() or "ID_animal"
        factors = input("Columnas de factores (separadas por coma), por ejemplo semana,hemisferio: ").strip()
        if not factors:
            raise SystemExit("El diseño personalizado requiere al menos un factor.")
        factors_list = [c.strip() for c in factors.split(",") if c.strip()]

        paired = input("Columna de factor pareado dentro de sujeto (dejar en blanco si no aplica): ").strip() or None
        required_levels = None
        if paired:
            lv = input("Niveles requeridos para el factor pareado (separados por coma), por ejemplo ipsi,contra: ").strip()
            required_levels = [x.strip() for x in lv.split(",") if x.strip()] if lv else None

        return AnalysisSpec(
            name="CUSTOM",
            animal_col=animal,
            factors=factors_list,
            paired_within=paired,
            paired_required_levels=required_levels,
        )

    print("Opción inválida; se usará EXP-001 por defecto.")
    return make_spec_exp001()


def choose_metric_column(df: pd.DataFrame) -> str:
    print("\nColumnas detectadas:")
    print(", ".join(df.columns.astype(str).tolist()))
    metric = input("Nombre de la columna de la métrica (vacío = usar la última columna): ").strip()
    if metric == "":
        metric = str(df.columns[-1])
        print(f"Usando la última columna como métrica: {metric}")
    if metric not in df.columns:
        raise KeyError(f"La columna de métrica '{metric}' no fue encontrada.")
    return metric


def ask_yes_no(prompt: str, default: str = "n") -> bool:
    default = default.lower().strip()
    if default not in ("y", "n"):
        default = "n"
    ans = input(f"{prompt} [s/n] (default={default}): ").strip().lower()
    if ans == "":
        ans = default
    return ans.startswith("y") or ans.startswith("s")


def main():
    in_path = pick_input_file()
    df_raw = read_table(in_path)

    spec = choose_experiment()
    metric_col = choose_metric_column(df_raw)

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_out_dir = os.path.join(os.path.dirname(in_path), f"stats_outputs_{spec.name}_{ts}")
    os.makedirs(base_out_dir, exist_ok=True)

    # Run main analysis (full model)
    out_main = run_one_analysis(df_raw, spec, metric_col)
    write_outputs(base_out_dir, "FULL_MODEL", out_main)

    # If msn_type in model, ask for split analyses (D1/D2) with 2-way model
    if "msn_type" in spec.factors:
        do_split = ask_yes_no(
            "El modelo completo incluye msn_type. ¿Correr análisis separados para D1 y D2 con modelo 2-way (tratamiento1 x tratamiento2)?",
            default="n"
        )
        if do_split:
            split_spec = AnalysisSpec(
                name="EXP-002_SPLIT",
                animal_col=spec.animal_col,
                factors=["tratamiento1", "tratamiento2"],
                paired_within=None,
                paired_required_levels=None,
                alpha=spec.alpha,
                anova_type=spec.anova_type,
                shapiro_max_n=spec.shapiro_max_n,
                levene_center=spec.levene_center,
            )

            df_norm = normalize_categories(df_raw)
            if "msn_type" not in df_norm.columns:
                print("No se encontró la columna msn_type; no es posible realizar el split.")
            else:
                for subtype in ["D1", "D2"]:
                    df_sub = df_norm[df_norm["msn_type"] == subtype].copy()
                    if df_sub.empty:
                        continue
                    out_sub = run_one_analysis(df_sub, split_spec, metric_col)
                    write_outputs(base_out_dir, f"SPLIT_{subtype}", out_sub)

    print("\nListo.")
    print(f"Carpeta de salida: {base_out_dir}")
    print("Archivos generados:")
    print("- FULL_MODEL_report.txt / FULL_MODEL_stats_outputs.xlsx / FULL_MODEL_run_meta.json")
    if "msn_type" in spec.factors:
        print("- (opcional) archivos SPLIT_D1_* y SPLIT_D2_* si elegiste correr el split")


if __name__ == "__main__":
    main()