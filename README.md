# 🔍 AI-Powered Fake Job Detection and Job Risk Analytics System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248.svg)](https://www.mongodb.com/atlas)

A full-stack, production-ready system that uses machine learning to detect fraudulent job postings and provide risk analytics for job seekers and recruiters.

---

## 📁 Project Structure

```
AI-Powered-Fake-Job/
├── frontend/          # React + Vite + Tailwind CSS
├── backend/           # Python FastAPI REST API
├── ml/                # Scikit-learn ML pipeline & model artifacts
├── .gitignore
├── .env.example
└── README.md
```

---

## 🧩 Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | React 18, Vite, Tailwind CSS        |
| Backend    | Python 3.11+, FastAPI, Uvicorn      |
| Database   | MongoDB Atlas (via Motor async ODM) |
| ML Engine  | Scikit-learn, Pandas, NumPy         |
| Auth       | JWT (python-jose)                   |
| Validation | Pydantic v2                         |

---

## 🚀 Quick Start

### Prerequisites

- Node.js >= 18
- Python >= 3.11
- MongoDB Atlas account
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Srikanth28202/AI-Powered-Fake-Job.git
cd AI-Powered-Fake-Job
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Fill in your values in .env
```

### 3. Start the Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Verify backend health and database connectivity:
- **Liveness Probe**: `http://localhost:8000/health` (or `/api/v1/health`)
- **MongoDB Atlas Connectivity**: `http://localhost:8000/health/db` (or `/api/v1/health/db`)
- **Full System Health Check**: `http://localhost:8000/api/v1/health/full` (probes API, DB, and ML model availability)
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

### 4. ML Data Preparation & Pipeline

For comprehensive details on the EMSCAD dataset, licensing, schema, and limitations, refer to [ml/data/DATASET.md](file:///c:/Users/Srika/OneDrive/Desktop/Fake%20Job/ml/data/DATASET.md).

```bash
cd ml
pip install -r requirements.txt

# 1. Place raw dataset at ml/data/raw/fake_job_postings.csv (downloaded from Kaggle / EMSCAD)
# 2. Run exploratory data analysis and generate report + charts
python -m ml.pipeline.eda

# 3. Execute master data preparation pipeline (imputation, deduplication, cleaning, stratified split)
python -m ml.pipeline.prepare_data

# 4. Run automated test suite
python -m pytest ml/tests/ -v
```

### 5. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## 📖 API Documentation

Once the backend is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🧪 Running Tests

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm run test
```

---

## 📦 Environment Variables

See `.env.example` for all required variables.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to the branch and open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.
