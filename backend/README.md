# BehaviorLens AI - Backend (Step 2)

Explainable AI-powered behavioral and lifestyle disease risk detection system.

## 🚀 Step 2: Data-Driven ML Backend

This version transitions from mock endpoints to a real data-driven architecture.

### Key Changes:
- **SQLAlchemy 2.x Models**: Added `User`, `Assessment`, and `Prediction` models with relationships.
- **ML Pipeline**: Structured `ml/` directory with preprocessing, prediction, and SHAP-based explanations.
- **Prediction Service**: Orchestrates the flow between input, ML inference, and DB persistence.
- **Clean Architecture**: Strict separation between routes, services, models, and ML logic.

## 📁 Project Structure

```text
backend/
├── app/
│   ├── api/                # API routes
│   ├── core/               # App configuration
│   ├── db/                 # DB session and Base model
│   ├── ml/                 # ML pipeline (Preprocess, Predict, Explain)
│   ├── models/             # SQLAlchemy 2.x models
│   ├── schemas/            # Pydantic v2 schemas
│   ├── services/           # Orchestration services
│   └── main.py             # Entry point
├── requirements.txt
└── README.md
```

## 🛠️ Getting Started

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the application**:
    ```bash
    uvicorn app.main:app --reload
    ```

## 🔌 API Endpoints (v1)

- **Assessment**:
  - `POST /api/v1/assessment/predict`: Accepts lifestyle data, runs ML inference, saves to DB, and returns results.
