# BehaviorLens AI - Backend

Explainable AI-powered behavioral and lifestyle disease risk detection system.

## 🚀 Tech Stack

- **FastAPI**: Modern, fast (high-performance) web framework for building APIs with Python 3.10+.
- **Pydantic v2**: Data validation and settings management using Python type annotations.
- **SQLAlchemy 2.x**: SQL Toolkit and Object Relational Mapper.
- **PostgreSQL**: Production-ready database (structure ready).
- **ML Stack**: Scikit-learn, XGBoost, SHAP for explainable AI.

## 📁 Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── routes/         # API endpoints
│   ├── core/               # Configuration and security
│   ├── db/                 # Database session and base models
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic models
│   ├── services/           # Business logic
│   ├── utils/              # Helper functions
│   └── main.py             # App entry point
├── requirements.txt
└── README.md
```

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+
- Virtual environment (recommended)

### Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.
Documentation (Swagger UI) is at `http://localhost:8000/docs`.

## 🔌 API Endpoints (v1)

- **Health**: `GET /api/v1/health/`
- **Auth**:
  - `POST /api/v1/auth/register` (Skeleton)
  - `POST /api/v1/auth/login` (Skeleton)
- **Assessment**:
  - `POST /api/v1/assessment/predict` (Mock ML Output)
