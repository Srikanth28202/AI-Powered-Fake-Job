# Exploratory Data Analysis (EDA) Report
**Dataset**: Employment Scam Aegean Dataset (EMSCAD) / Kaggle Fake Job Postings  
**Total Records**: 45  
**Total Features**: 18  

---

## 1. Class Distribution & Imbalance Analysis

| Target Class | Count | Percentage |
| :--- | :--- | :--- |
| **Legitimate (0)** | 40 | 88.89% |
| **Fraudulent (1)** | 5 | 11.11% |
| **Total** | 45 | 100.00% |

- **Imbalance Ratio**: 8.00 : 1
- **Key Takeaway**: A baseline majority model achieves **88.89% accuracy** while missing 100% of scams. Models must be trained with balanced cost weights and evaluated with Precision-Recall AUC (PR-AUC) and F1-macro.

---

## 2. Missing Value Prevalence

| Feature | Missing Count | Missing Percentage |
| :--- | :--- | :--- |
| `company_profile` | 5 | 11.11% |
| `requirements` | 5 | 11.11% |
| `benefits` | 5 | 11.11% |

- **Key Takeaway**: `salary_range` is missing in 0.0% of postings, and `department` in 0.0%. Missingness is informative and should be preserved as binary indicator features (`has_company_profile`, `has_salary_specified`).

---

## 3. Linguistic & Text Complexity

- **Average Description Word Count (All)**: 8.0 words (Median: 8)
- **Legitimate Postings Average Word Count**: 8.0 words
- **Fraudulent Postings Average Word Count**: 8.0 words

---

## 4. Key Behavioral Signal Findings

- **Company Logo Signal**:
  - Fraud rate when logo is **ABSENT** (`has_company_logo == 0`): **100.00%**
  - Fraud rate when logo is **PRESENT** (`has_company_logo == 1`): **0.00%**
  - Listings without an uploaded company logo are substantially more likely to be scams.

---

## 5. Visual Artifacts Generated

The following figures were generated and saved to `ml/reports/figures/`:
- `class_imbalance.png`: Visual class representation.
- `missing_values_profile.png`: Missing value percentage across all columns.
- `binary_feature_fraud_rates.png`: Comparison of fraud rates by metadata presence.
- `text_length_distribution.png`: KDE plot of job description length.
