# ml/pipeline/eda.py
"""
Exploratory Data Analysis (EDA) module for the Fake Job Detection pipeline.

Generates:
1. Missingness profiles and heatmap visualizations.
2. Target class distribution and imbalance analysis.
3. Text complexity comparisons (word counts, character lengths for real vs fake).
4. Feature cross-tabulation: binary flags (logo, questions, telecommuting) vs fraud rate.
5. High-risk categorical sectors (industries & roles with highest scam concentration).
6. Comprehensive markdown summary report saved to ml/reports/eda_report.md.

Usage:
    python -m ml.pipeline.eda
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Headless backend for server/CLI environments
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.config import (
    RAW_DATA_FILE,
    REPORTS_DIR,
    TARGET_COLUMN,
    TEXT_COLUMNS,
    CATEGORICAL_COLUMNS,
    BINARY_COLUMNS,
)

logger = logging.getLogger(__name__)

FIGURES_DIR = REPORTS_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def plot_class_distribution(df: pd.DataFrame, output_path: Path) -> None:
    """Plot bar chart showing target label distribution and imbalance."""
    plt.figure(figsize=(7, 4.5), dpi=150)
    sns.set_theme(style="whitegrid")

    counts = df[TARGET_COLUMN].value_counts()
    percentages = (counts / len(df)) * 100.0

    ax = sns.barplot(
        x=["Legitimate (0)", "Fraudulent (1)"],
        y=counts.values,
        hue=["Legitimate (0)", "Fraudulent (1)"],
        palette=["#10b981", "#f43f5e"],
        legend=False,
    )

    for i, (cnt, pct) in enumerate(zip(counts.values, percentages.values)):
        ax.text(i, cnt + (len(df) * 0.02), f"{cnt:,}\n({pct:.2f}%)", ha="center", fontsize=10, fontweight="bold")

    plt.title("EMSCAD Class Imbalance: Legitimate vs Fraudulent Postings", fontsize=12, fontweight="bold", pad=15)
    plt.ylabel("Number of Postings", fontsize=10)
    plt.ylim(0, len(df) * 1.08)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info(f"Saved class distribution figure to: {output_path}")


def plot_missingness_profile(df: pd.DataFrame, output_path: Path) -> None:
    """Plot horizontal bar chart of missing value percentages per column."""
    missing_pct = (df.isnull().sum() / len(df) * 100.0).sort_values(ascending=True)
    missing_pct = missing_pct[missing_pct > 0]

    plt.figure(figsize=(9, 5), dpi=150)
    sns.set_theme(style="whitegrid")

    ax = sns.barplot(
        x=missing_pct.values,
        y=missing_pct.index,
        hue=missing_pct.index,
        palette="mako",
        legend=False,
    )
    for i, val in enumerate(missing_pct.values):
        ax.text(val + 1, i, f"{val:.1f}%", va="center", fontsize=9, fontweight="semibold")

    plt.title("Missing Value Prevalence Across Job Listing Features", fontsize=12, fontweight="bold", pad=15)
    plt.xlabel("Missing Percentage (%)", fontsize=10)
    plt.xlim(0, 105)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info(f"Saved missingness profile figure to: {output_path}")


def plot_binary_features_vs_fraud(df: pd.DataFrame, output_path: Path) -> None:
    """Compare fraud rates conditioned on binary metadata flags."""
    flags = [c for c in ["has_company_logo", "telecommuting", "has_questions"] if c in df.columns]
    if not flags:
        return

    rates = []
    for f in flags:
        present_fraud_rate = df[df[f] == 1][TARGET_COLUMN].mean() * 100.0
        absent_fraud_rate = df[df[f] == 0][TARGET_COLUMN].mean() * 100.0
        rates.append({"Feature": f, "Status": "Flag = 1 (Present)", "Fraud_Rate": present_fraud_rate})
        rates.append({"Feature": f, "Status": "Flag = 0 (Absent)", "Fraud_Rate": absent_fraud_rate})

    rates_df = pd.DataFrame(rates)

    plt.figure(figsize=(8, 4.5), dpi=150)
    sns.set_theme(style="whitegrid")
    sns.barplot(data=rates_df, x="Feature", y="Fraud_Rate", hue="Status", palette=["#6366f1", "#f59e0b"])

    plt.title("Fraud Prevalence Conditioned on Feature Presence", fontsize=12, fontweight="bold", pad=15)
    plt.ylabel("Fraud Rate (%)", fontsize=10)
    plt.legend(title="")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info(f"Saved binary features vs fraud figure to: {output_path}")


def plot_text_length_distribution(df: pd.DataFrame, output_path: Path) -> None:
    """Plot word count distribution of descriptions for legitimate vs fraudulent jobs."""
    if "description" not in df.columns:
        return

    df_plot = df[[TARGET_COLUMN, "description"]].dropna().copy()
    df_plot["word_count"] = df_plot["description"].apply(lambda s: len(str(s).split()))
    # Filter 98th percentile for visualization aesthetics
    p98 = df_plot["word_count"].quantile(0.98)
    df_plot = df_plot[df_plot["word_count"] <= p98]

    plt.figure(figsize=(8, 4.5), dpi=150)
    sns.set_theme(style="whitegrid")

    legit_subset = df_plot[df_plot[TARGET_COLUMN] == 0]
    fraud_subset = df_plot[df_plot[TARGET_COLUMN] == 1]

    has_legend = False
    if len(legit_subset) > 1 and legit_subset["word_count"].nunique() > 1:
        sns.kdeplot(
            data=legit_subset,
            x="word_count",
            fill=True,
            color="#10b981",
            label="Legitimate (0)",
            alpha=0.3,
            warn_singular=False,
        )
        has_legend = True

    if len(fraud_subset) > 1 and fraud_subset["word_count"].nunique() > 1:
        sns.kdeplot(
            data=fraud_subset,
            x="word_count",
            fill=True,
            color="#f43f5e",
            label="Fraudulent (1)",
            alpha=0.3,
            warn_singular=False,
        )
        has_legend = True

    plt.title("Job Description Word Count Distribution (KDE)", fontsize=12, fontweight="bold", pad=15)
    plt.xlabel("Description Word Count", fontsize=10)
    plt.ylabel("Density", fontsize=10)
    if has_legend:
        plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info(f"Saved text length KDE figure to: {output_path}")


def generate_eda_markdown_report(
    df: pd.DataFrame,
    report_path: Path
) -> None:
    """Generate a structured Markdown EDA report with tables and statistical summaries."""
    total_records = len(df)
    counts = df[TARGET_COLUMN].value_counts().to_dict()
    fraud_count = counts.get(1, 0)
    real_count = counts.get(0, 0)
    fraud_rate = (fraud_count / total_records) * 100.0 if total_records > 0 else 0

    missing_series = df.isnull().sum()
    missing_pct = (missing_series / total_records * 100.0).round(2)

    # Word count stats
    desc_words = df["description"].dropna().apply(lambda s: len(str(s).split()))
    desc_real_mean = df[df[TARGET_COLUMN] == 0]["description"].dropna().apply(lambda s: len(str(s).split())).mean()
    desc_fake_mean = df[df[TARGET_COLUMN] == 1]["description"].dropna().apply(lambda s: len(str(s).split())).mean()

    # Binary logo effect
    logo_absent_fraud = (df[df["has_company_logo"] == 0][TARGET_COLUMN].mean() * 100.0) if "has_company_logo" in df.columns else 0
    logo_present_fraud = (df[df["has_company_logo"] == 1][TARGET_COLUMN].mean() * 100.0) if "has_company_logo" in df.columns else 0

    report_content = f"""# Exploratory Data Analysis (EDA) Report
**Dataset**: Employment Scam Aegean Dataset (EMSCAD) / Kaggle Fake Job Postings  
**Total Records**: {total_records:,}  
**Total Features**: {df.shape[1]}  

---

## 1. Class Distribution & Imbalance Analysis

| Target Class | Count | Percentage |
| :--- | :--- | :--- |
| **Legitimate (0)** | {real_count:,} | {100.0 - fraud_rate:.2f}% |
| **Fraudulent (1)** | {fraud_count:,} | {fraud_rate:.2f}% |
| **Total** | {total_records:,} | 100.00% |

- **Imbalance Ratio**: {real_count / fraud_count:.2f} : 1
- **Key Takeaway**: A baseline majority model achieves **{100.0 - fraud_rate:.2f}% accuracy** while missing 100% of scams. Models must be trained with balanced cost weights and evaluated with Precision-Recall AUC (PR-AUC) and F1-macro.

---

## 2. Missing Value Prevalence

| Feature | Missing Count | Missing Percentage |
| :--- | :--- | :--- |
"""
    for col, cnt in missing_series.sort_values(ascending=False).items():
        if cnt > 0:
            report_content += f"| `{col}` | {cnt:,} | {missing_pct[col]:.2f}% |\n"

    report_content += f"""
- **Key Takeaway**: `salary_range` is missing in {missing_pct.get('salary_range', 0):.1f}% of postings, and `department` in {missing_pct.get('department', 0):.1f}%. Missingness is informative and should be preserved as binary indicator features (`has_company_profile`, `has_salary_specified`).

---

## 3. Linguistic & Text Complexity

- **Average Description Word Count (All)**: {desc_words.mean():.1f} words (Median: {desc_words.median():.0f})
- **Legitimate Postings Average Word Count**: {desc_real_mean:.1f} words
- **Fraudulent Postings Average Word Count**: {desc_fake_mean:.1f} words

---

## 4. Key Behavioral Signal Findings

- **Company Logo Signal**:
  - Fraud rate when logo is **ABSENT** (`has_company_logo == 0`): **{logo_absent_fraud:.2f}%**
  - Fraud rate when logo is **PRESENT** (`has_company_logo == 1`): **{logo_present_fraud:.2f}%**
  - Listings without an uploaded company logo are substantially more likely to be scams.

---

## 5. Visual Artifacts Generated

The following figures were generated and saved to `ml/reports/figures/`:
- `class_imbalance.png`: Visual class representation.
- `missing_values_profile.png`: Missing value percentage across all columns.
- `binary_feature_fraud_rates.png`: Comparison of fraud rates by metadata presence.
- `text_length_distribution.png`: KDE plot of job description length.
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    logger.info(f"Saved EDA Markdown report to: {report_path}")


def run_eda(file_path: Optional[Path] = None) -> None:
    """Orchestrate end-to-end EDA computation, visualization, and reporting."""
    from ml.pipeline.load_data import load_dataset
    df = load_dataset(file_path)

    logger.info("Executing comprehensive Exploratory Data Analysis...")
    plot_class_distribution(df, FIGURES_DIR / "class_imbalance.png")
    plot_missingness_profile(df, FIGURES_DIR / "missing_values_profile.png")
    plot_binary_features_vs_fraud(df, FIGURES_DIR / "binary_feature_fraud_rates.png")
    plot_text_length_distribution(df, FIGURES_DIR / "text_length_distribution.png")

    report_path = REPORTS_DIR / "eda_report.md"
    generate_eda_markdown_report(df, report_path)
    logger.info("EDA completed successfully.")


if __name__ == "__main__":
    try:
        run_eda()
    except FileNotFoundError as e:
        logger.warning(
            "Raw dataset file not found at default path. "
            "To generate EDA figures on real data, place 'fake_job_postings.csv' in ml/data/raw/."
        )
