# Actual Model Evaluation Results: Baseline Fake Job Classifier

**Timestamp**: 2026-10-23T16:24:48.671953  
**Model Family**: Scikit-Learn TF-IDF + Logistic Regression (`class_weight='balanced'`)  
**Holdout Test Samples**: 3,576 (3,403 Legitimate, 173 Fraudulent)  

---

## 1. Classification Performance by Class

| Class Label | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| **Legitimate (0)** | 0.9949 | 0.9838 | 0.9894 | 3,403 |
| **Fraudulent (1)** | **0.7393** | **0.9017** | **0.8125** | 173 |
| **Macro Average** | 0.9009 | &mdash; | 0.9009 | 3,576 |
| **Weighted Average**| 0.9808 | &mdash; | 0.9808 | 3,576 |

---

## 2. Confusion Matrix Breakdown

| | Predicted Legitimate (0) | Predicted Fraudulent (1) |
| :--- | :--- | :--- |
| **Actual Legitimate (0)** | **TN = 3,348** | **FP = 55** |
| **Actual Fraudulent (1)** | **FN = 17** | **TP = 156** |

- **True Positives (Scams Caught)**: 156 of 173 (90.17%)
- **False Negatives (Scams Missed)**: 17 of 173
- **False Positives (False Alarms)**: 55 of 3,403
- **True Negatives (Legitimate Cleared)**: 3,348 of 3,403

---

## 3. Discrimination & Imbalance Metrics

- **ROC-AUC**: **0.9884** (indicates strong ranking separation across probability thresholds)
- **PR-AUC (Average Precision)**: **0.9239** (vs baseline 0.0484)
- **Balanced Accuracy**: **0.9428**
- **Raw Accuracy**: **0.9799**

---

## 4. Observations & Real-World Trade-Offs

1. **Balanced Class Weighting Trade-off**:
   Using `class_weight='balanced'` penalizes false negatives heavily, yielding high **recall (90.17%)** on fraudulent job offers at the cost of a moderate false-positive rate. In recruitment cybersecurity, catching scam postings is prioritized over perfect precision.
2. **Decision Threshold Tuning**:
   The default decision boundary is 0.50. For production environments requiring higher precision, the threshold can be elevated to 0.70–0.80 to reduce false alerts on legitimate employers.
