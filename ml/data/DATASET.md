# Dataset Specification: Employment Scam Aegean Dataset (EMSCAD)

## 1. Overview & Provenance

The **Employment Scam Aegean Dataset (EMSCAD)** is a benchmark dataset for researching fraudulent job advertisements and employment scams. It was created and curated by the Laboratory of Information & Communication Systems Security (Info-Sec-Lab) at the University of the Aegean, Greece.

- **Primary Academic Reference**:
  > Vidros, S., Kolias, C., Kambourakis, G., & Akoglu, L. (2017).
  > *"AuthentiCare: A machine learning approach for uncovering fake job offers."*
  > *Future Internet*, 9(4), 74. https://doi.org/10.3390/fi9040074

- **Dataset Mirrors & Access**:
  - **University Portal**: `http://emscad.samos.aegean.gr/`
  - **Kaggle Verified Mirror**: [Real / Fake Job Posting Prediction (Shivam Bansal)](https://www.kaggle.com/datasets/shivamb/real-fake-job-posting-prediction)
  - **Filename**: `fake_job_postings.csv`
  - **Recommended Placement**: `ml/data/raw/fake_job_postings.csv`

---

## 2. Licensing & Terms of Use

- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0) / Academic & Educational Use.
- **Attribution**: Any published work utilizing this dataset must cite the original publication by Vidros et al. (2017).
- **Redistribution Policy**: The raw data file must not be committed directly into public version control without compliance with repository size limits and upstream source terms. Users must download the verified archive directly from the accredited repository.

---

## 3. Schema & Feature Definitions

The dataset contains **17,880 observations** across **18 columns**:

| Column Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `job_id` | Integer | Unique identifier for each posting | `1`, `2` |
| `title` | Text | The headline title of the job listing | `"Customer Service Associate"` |
| `location` | Text | Comma-separated Country, State, City | `"US, NY, New York"` |
| `department` | Text | Functional corporate department | `"Corporate Communications"` |
| `salary_range` | Text | Reported min-max salary boundary | `"100000-120000"` |
| `company_profile`| Text | Overview and background of the company | `"We are a global SaaS leader..."` |
| `description` | Text | Full job duties, scope, and responsibilities | `"You will manage inbound leads..."` |
| `requirements` | Text | Necessary qualifications, skills, and tools | `"Bachelor's degree in CS..."` |
| `benefits` | Text | Compensation perks, health, 401(k), PTO | `"Full medical, 401(k) matching"` |
| `telecommuting` | Binary | Whether position allows remote work (0 or 1)| `1` |
| `has_company_logo`| Binary | Whether company uploaded an official logo | `0` |
| `has_questions` | Binary | Whether listing includes screening questions | `1` |
| `employment_type`| Categorical | Work engagement arrangement | `"Full-time"`, `"Part-time"` |
| `required_experience`| Categorical | Minimum experience tier | `"Entry level"`, `"Mid-Senior"` |
| `required_education`| Categorical | Educational prerequisite | `"Bachelor's Degree"`, `"High School"`|
| `industry` | Categorical | Industrial business domain | `"Computer Software"`, `"Marketing"` |
| `function` | Categorical | Primary job responsibility family | `"Engineering"`, `"Sales"` |
| `fraudulent` | Binary | **Target Variable**: 0 = Real, 1 = Fake | `0` or `1` |

---

## 4. Ground Truth Label Mapping

The target column is **`fraudulent`**:

- **`0` -> Legitimate / Authentic Posting**:
  - Sample Count: **17,014** (~95.16%)
  - Characteristics: Verified corporate domain, verifiable recruiter contacts, normal market compensation, complete company background.

- **`1` -> Fraudulent / Scam Posting**:
  - Sample Count: **866** (~4.84%)
  - Characteristics: Upfront fee/check demands, wire transfers, Telegram/WhatsApp interviews, missing company logos, non-existent corporate registry.

---

## 5. Dataset Limitations, Imbalance & Biases

1. **Extreme Class Imbalance (Imbalance Ratio ~19.6 : 1)**:
   - Fraudulent postings make up only 4.84% of the dataset.
   - **Critical Warning**: A trivial "dummy classifier" that always predicts legitimate achieves **95.16% accuracy** while detecting 0 scams. Models must be evaluated using **Precision-Recall AUC (PR-AUC)**, **F1-Score (macro / minority)**, and **Recall (True Positive Rate)** rather than standard accuracy.

2. **Severe Missingness in Key Features**:
   - `salary_range`: ~83.8% missing
   - `department`: ~64.6% missing
   - `benefits`: ~40.5% missing
   - `company_profile`: ~18.5% missing
   - `requirements`: ~15.1% missing
   *Note: Missingness is not random (MNAR). Fraudulent job postings are statistically far more likely to omit company profiles and official logos.*

3. **Temporal Drift & Modern Scam Evolution**:
   - EMSCAD was collected between 2012 and 2014. Modern deceptive campaigns frequently employ modern patterns not present in older datasets, including cryptocurrency payment forwarding, generative AI job descriptions, and disposable cloud domain clones.
   - Production systems must supplement historical EMSCAD models with rule-based heuristics and live threat telemetry.

4. **Geographic & Linguistic Bias**:
   - Postings are predominantly written in English.
   - The majority of listings originate from the United States (~60%), followed by the UK, Greece, and Canada. Performance on non-English postings will be degraded without translation or multilingual embeddings.
