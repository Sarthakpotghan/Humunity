# Humunity

Donation matching platform for clothes and educational stationery.

> **Full guide:** [summary.md](summary.md) — architecture, tech stack, matching engine,
> end-to-end flow, and step-by-step manual verification checklist.

## Stack

- **Backend:** FastAPI (Python), SQLAlchemy, Alembic, PostgreSQL
- **Frontend:** React + Vite + Tailwind CSS
- **Services:** Sentence-Transformer matching, Nominatim geocoding, OSRM routing

## Getting started

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at http://localhost:5173