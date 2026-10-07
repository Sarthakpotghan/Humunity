# Humunity — Project Summary

> Donation-matching platform that connects **donors** (surplus clothes & educational stationery)
> with **NGOs** and **volunteers** who need them, using ML-powered matching, geospatial scoring,
> and end-to-end delivery tracking.

---

## 1. What the platform does

1. A **donor** lists surplus items (clothes / stationery).
2. The backend automatically **matches** the donation against active NGO requests using a
   weighted scoring model (semantic similarity, distance, urgency, condition, quantity, …).
3. An **NGO** accepts/rejects the match.
4. A **delivery** is created (self-drop, NGO pickup, or volunteer pickup) with live route tracking.
5. An **admin** oversees users, verifies NGOs, and views analytics (reduction metrics, trends, heatmap).

Four roles: `donor`, `ngo`, `volunteer`, `admin`.

---

## 2. Tech stack (and what each piece does)

### Backend

| Tech | Version/Notes | Why it's used |
|---|---|---|
| **FastAPI** | >= 0.110 | Async-ready Python web framework; auto-generates `/docs` (OpenAPI) API documentation |
| **Uvicorn** | >= 0.29 | ASGI server that runs FastAPI (`--reload` hot-reloads on file changes) |
| **SQLAlchemy** | ORM layer | Maps Python classes (`User`, `Donation`, …) to database tables |
| **SQLite** | current `.env` | Zero-setup file DB (`backend/humunity.db`) for local dev. The code stays PostgreSQL-compatible (Alembic migrations target PG) |
| **Alembic** | >= 1.13 | SQLAlchemy's migration tool — version-controlled schema changes (`backend/alembic/`) |
| **Pydantic v2** | + `pydantic-settings` | Request/response validation schemas; `.env` config loading (`app/config.py`) |
| **python-jose** | JWT | Creates/verifies access tokens for login (`app/utils/security.py`) |
| **passlib + bcrypt** | bcrypt **pinned 4.0.1** | Hashes passwords (bcrypt 5.x is incompatible with passlib 1.7.4) |
| **CORSMiddleware** | — | Lets the browser app at `localhost:5173` call the API at `127.0.0.1:8000` |
| **httpx / aiosmtplib** | — | Outgoing HTTP (geocoding/routing) and SMTP email notifications |
| **spaCy / sentence-transformers / scikit-learn** | optional ML deps | Text/semantic features used by the matching & NLP services and notebooks |

### Frontend

| Tech | Version | Why it's used |
|---|---|---|
| **React** | 19 | UI library — function components + hooks |
| **Vite** | 8 | Dev server & bundler (`npm run dev`, instant HMR) |
| **React Router** | 7 | Client-side routing (`/login`, `/donor/dashboard`, `/admin/*` …) |
| **Axios** | — | HTTP client; central `api.js` instance sets `baseURL` + JWT header + 401 interceptor |
| **Tailwind CSS** | 3.4 | Utility-first styling (`tailwind.config.js`, `postcss.config.js`) |
| **Chart.js + react-chartjs-2** | — | Admin analytics charts (trends, category breakdown) |
| **Leaflet + react-leaflet** | — | Interactive maps (delivery tracking, `MapView`) |
| **date-fns** | — | Date formatting |
| **oxlint** | — | Linter (`npm run lint`) |

### Matching / Maps / ML services (backend `app/services/`)

| Service | What it does |
|---|---|
| `matching.py` | **Core scoring engine.** Computes a 0–1 match score from 7 weighted signals (see §4). Runs automatically when a donation is created and returns top-5 matches with a full score breakdown |
| `maps.py` | **Geocoding & routing.** Nominatim (OSM) for address→lat/lng, OSRM for delivery routes/distances, haversine for proximity, delivery-mode suggestion by distance |
| `nlp.py` | Rule-based field extraction from free text (quantity, item type, age group, gender, season, condition) |
| `notifier.py` | In-app notifications + optional SMTP email on every lifecycle event (match created/accepted/rejected, pickup, in-transit, delivered, confirmed) |

### Data science (`data/` + `notebooks/`)

- **Synthetic data generator** (`generate_synthetic_data.py`) → `donations.csv`, `requests.csv`, `ngos.csv`, `ideal_matches.csv`
- **Notebooks:**
  - `01_synthetic_data_and_eda.ipynb` — data generation & exploration
  - `02_baseline_and_precision_at_k.ipynb` — baseline retrievers, Precision@K / NDCG@K
  - `03_ablation_and_weight_tuning.ipynb` — ablation study + grid search that produced the production weights (NDCG@5 +~0.11, mean match distance −~700 km)
  - `04_learning_to_rank.ipynb` — Learning-to-Rank model (`ltr_model.joblib`) vs weighted baseline
- **Artifacts:** `tuned_weights.json`, `ablation.json`, `baselines.json`, `ltr_results.json`, `features.json`

---

## 3. Project structure

```
Humunity/
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, CORS, routers, static /uploads
│   │   ├── config.py        # .env settings (DATABASE_URL, SECRET_KEY, …)
│   │   ├── database.py      # engine, SessionLocal, Base
│   │   ├── models/          # SQLAlchemy models (11 tables)
│   │   ├── schemas/         # Pydantic request/response contracts
│   │   ├── routers/         # auth, donations, requests, matches, deliveries,
│   │   │                    # notifications, analytics, admin, feedback
│   │   ├── services/        # matching, maps, nlp, notifier
│   │   └── utils/security.py# bcrypt, JWT, get_current_user, require_role
│   ├── alembic/             # DB migrations
│   ├── tests/               # pytest API tests (in-memory SQLite)
│   ├── .env                 # DATABASE_URL=sqlite:///./humunity.db
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx          # routes & role-based PrivateRoute guards
│       ├── context/AuthContext.jsx  # login/register/logout, JWT storage
│       ├── services/api.js  # axios instance (baseURL 127.0.0.1:8000)
│       ├── pages/           # Login, Register, donor/*, NGO, Admin, Volunteer,
│       │                    # DonationForm, RequestForm, MatchView, MapView
│       └── components/      # layout, modals, UI atoms
├── data/                    # synthetic datasets + eval artifacts
└── notebooks/               # ML evaluation & weight tuning
```

### Data model (11 tables)

```
User (role: donor|ngo|volunteer|admin, lat/lng, verified)
 ├─ Donation (category, item_type, qty, condition, status) ─ DonationPhoto
 ├─ Request  (category, qty_needed, urgency 1-5, deadline, status)
 ├─ NgoProfile (reg_number, focus_areas, reliability_score)
 ├─ Notification, Feedback, deliveries_as_volunteer
Match (donation_id, request_id, score 0-1, score_breakdown JSON, status)
 └─ Delivery (mode, status, scheduled_at, delivered_at)
      └─ DeliveryEvent (status history for live tracking)
```

### API surface (prefix → purpose)

| Router | Key endpoints |
|---|---|
| `/auth` | `POST /register`, `POST /login`, `GET /me`, NGO profile |
| `/donations` | CRUD + photos + `POST /{id}/match` (trigger matching) |
| `/requests` | CRUD + match listing for NGOs |
| `/matches` (under donations) | accept / reject |
| `/deliveries` | create, status updates, assign volunteer, route, events |
| `/notifications` | list, mark read, mark all read |
| `/analytics` | `summary`, `heatmap`, `trends` (admin only) |
| `/admin` | pending NGOs, verify/reject, list users, change roles |
| `/feedback` | rating 1-5 per completed match |

---

## 4. The matching engine (heart of the project)

When a donation is created, `run_matching_for_donation()` scores **every active request of the
same category** from a verified NGO and stores the **top 5** as `Match` rows.

```
score = 0.056·urgency + 0.111·similarity + 0.056·seasonal
      + 0.333·proximity + 0.111·quantity_fit + 0.222·condition
      + 0.111·reliability
```

| Signal | Meaning | Weight |
|---|---|---|
| `proximity` | Haversine distance donor↔NGO (largest weight — logistics dominate) | **0.333** |
| `condition` | Item condition quality | **0.222** |
| `similarity` | Semantic similarity (sentence-transformers) between donation & request text | 0.111 |
| `quantity_fit` | Donation quantity vs quantity needed | 0.111 |
| `reliability` | NGO profile reliability score | 0.111 |
| `urgency` | Request urgency (1–5) + deadline proximity | 0.056 |
| `seasonal` | Season match (e.g., winter coats in winter) | 0.056 |

Weights were **tuned offline** in `notebooks/03_ablation_and_weight_tuning.ipynb`.
Each `Match` row stores the full `score_breakdown` so the UI can explain *why* it matched.

---

## 5. End-to-end flow (for manual verification)

Run both servers first:

```bash
# Terminal 1 — backend (port 8000)
cd backend
venv\Scripts\activate          # if not already active
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — frontend (port 5173)
cd frontend
npm run dev
```

Open **http://localhost:5173**.

### Flow A — Donor gives → NGO receives → delivery completes

| # | Action | Where | Expected result |
|---|---|---|---|
| 1 | Register a **Donor** account | `/register`, pick "Donor" | "Account created" → redirected to `/login` |
| 2 | Log in as donor | `/login` | Lands on `/donor/dashboard` (Overview) |
| 3 | Create a donation | "Add item" → `DonationForm` | Item appears under **My Items**; backend auto-runs matching |
| 4 | Check matches | `/donor/dashboard/matches` | Top-5 matches with **score + breakdown** (why it matched) |
| 5 | Register an **NGO** account | `/register`, pick "NGO" | Created but **unverified** (pending admin) |
| 6 | NGO tries to log in | `/login` | ❌ 403 "pending admin approval" (expected) |
| 7 | Log in as **admin** | `admin@test.com` / `password123` | Lands on `/admin/dashboard` — summary card loads (no CORS errors), pending NGO listed |
| 8 | Approve the NGO | Admin dashboard → pending list → Approve | NGO row disappears from pending list |
| 9 | NGO logs in, creates a request | `/ngo/dashboard` → `RequestForm` | Request visible with status `active` |
| 10 | Donor accepts a match (or NGO accepts) | Match view / NGO dashboard | Match status → `accepted` → delivery can be created |
| 11 | Create delivery | delivery flow | Mode suggested by distance (self/volunteer/NGO pickup) |
| 12 | Track it | `/map/:deliveryId` | Leaflet map with OSRM route + status timeline (`DeliveryEvent`s) |
| 13 | Walk statuses | `scheduled → in_transit → delivered → confirmed` | Each step fires a **notification** (bell icon) + optional email |
| 14 | Give feedback | after `confirmed` | Rating 1-5 stored; feeds donor/NGO impact metrics |

### Flow B — Admin analytics (the endpoint we fixed)

| # | Action | Expected result |
|---|---|---|
| 1 | Log in as `admin@test.com` / `password123` | `/admin/dashboard` |
| 2 | Watch network tab: `GET /analytics/summary` | **200 OK** with `access-control-allow-origin: http://localhost:5173` |
| 3 | Summary card | total items redistributed, per-category counts, unmet requests, top NGOs, monthly trend |
| 4 | `GET /admin/users`, `/admin/ngos/pending`, `/deliveries` | All 200 — tables render |

### Flow C — Quick API smoke test (no UI)

```bash
# health
curl http://127.0.0.1:8000/health

# interactive API docs
# open http://127.0.0.1:8000/docs

# register + login
curl -X POST http://127.0.0.1:8000/auth/register -H "Content-Type: application/json" \
     -d "{\"email\":\"you@example.com\",\"password\":\"password123\",\"name\":\"You\",\"role\":\"donor\"}"
curl -X POST http://127.0.0.1:8000/auth/login -H "Content-Type: application/json" \
     -d "{\"email\":\"you@example.com\",\"password\":\"password123\"}"
# → {"access_token": "...", "token_type": "bearer"}
```

---

## 6. Current local state & known quirks

| Item | Value |
|---|---|
| Database | **SQLite** — `backend/humunity.db` (via `.env`; PostgreSQL also runs locally but has a separate, older schema) |
| Admin login | `admin@test.com` / `password123` |
| Test donor logins | `test@example.com`, `anna@test.com` / `password123` |
| `admin@test.com` in `tests/` | Test-only fixture — lives in in-memory SQLite during pytest, not in the real DB |
| bcrypt | **Pinned 4.0.1** (5.x breaks passlib 1.7.4 → registration 500) |
| SQLAlchemy | Code uses 1.4-style `declarative_base()`; installed version varies between system Python (1.4) and venv |
| SQLite vs PostgreSQL SQL | `analytics.py` is dialect-aware (`strftime` for SQLite, `date_trunc` for PG). Unhandled 500s surface as **CORS errors** in the browser because the exception bypasses CORS header injection |
| CORS origins | `http://localhost:5173`, `http://localhost:3000` (`app/main.py:21`) |
| Role strings | API expects **lowercase** (`donor`, `ngo`, `volunteer`, `admin`) |
| NGO registration | NGOs start `verified=false` → login blocked until admin approves |

### Recurring fixes applied during setup

1. `WinError 10013` — port 8000 held by an orphaned process → `taskkill` the PID.
2. `ModuleNotFoundError: app` — uvicorn must run from `backend/`.
3. `ImportError: DeclarativeBase` — SQLAlchemy 1.4 → use `declarative_base()`.
4. Registration 500 — bcrypt 5.0.0 vs passlib → `pip install bcrypt==4.0.1` (venv **and** system).
5. CORS on `/analytics/summary` — was a masked 500 (`date_trunc` missing on SQLite).

---

## 7. Tests

```bash
cd backend
pytest                    # tests/ — API tests on in-memory SQLite fixtures
```

Covers: auth (register/login/401), donation CRUD, matching, deliveries, admin role guards,
notifications & analytics. Test users (`admin@test.com`, `donor@test.com`, `ngo@test.com`,
password `password123`) are created per-test in fixtures — they never touch the real DB.
