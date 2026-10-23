# Exploratory Data Analysis (EDA) Report
**Dataset**: Employment Scam Aegean Dataset (EMSCAD) / Kaggle Fake Job Postings  
**Total Records**: 17,880  
**Total Features**: 18  

---

## 1. Class Distribution & Imbalance Analysis

| Target Class | Count | Percentage |
| :--- | :--- | :--- |
| **Legitimate (0)** | 17,014 | 95.16% |
| **Fraudulent (1)** | 866 | 4.84% |
| **Total** | 17,880 | 100.00% |

- **Imbalance Ratio**: 19.65 : 1
- **Key Takeaway**: A baseline majority model achieves **95.16% accuracy** while missing 100% of scams. Models must be trained with balanced cost weights and evaluated with Precision-Recall AUC (PR-AUC) and F1-macro.

---

## 2. Missing Value Prevalence

| Feature | Missing Count | Missing Percentage |
| :--- | :--- | :--- |
| `salary_range` | 15,012 | 83.96% |
| `department` | 11,547 | 64.58% |
| `required_education` | 8,105 | 45.33% |
| `benefits` | 7,212 | 40.34% |
| `required_experience` | 7,050 | 39.43% |
| `function` | 6,455 | 36.10% |
| `industry` | 4,903 | 27.42% |
| `employment_type` | 3,471 | 19.41% |
| `company_profile` | 3,308 | 18.50% |
| `requirements` | 2,696 | 15.08% |
| `location` | 346 | 1.94% |
| `description` | 1 | 0.01% |

- **Key Takeaway**: `salary_range` is missing in 84.0% of postings, and `department` in 64.6%. Missingness is informative and should be preserved as binary indicator features (`has_company_profile`, `has_salary_specified`).

---

## 3. Linguistic & Text Complexity

- **Average Description Word Count (All)**: 170.5 words (Median: 146)
- **Legitimate Postings Average Word Count**: 171.0 words
- **Fraudulent Postings Average Word Count**: 158.9 words

---

## 4. Key Behavioral Signal Findings

- **Company Logo Signal**:
  - Fraud rate when logo is **ABSENT** (`has_company_logo == 0`): **15.93%**
  - Fraud rate when logo is **PRESENT** (`has_company_logo == 1`): **1.99%**
  - Listings without an uploaded company logo are substantially more likely to be scams.

---

## 5. Visual Artifacts Generated

The following figures were generated and saved to `ml/reports/figures/`:
- `class_imbalance.png`: Visual class representation.
- `missing_values_profile.png`: Missing value percentage across all columns.
- `binary_feature_fraud_rates.png`: Comparison of fraud rates by metadata presence.
- `text_length_distribution.png`: KDE plot of job description length.
