# Architecture — Phase 1

## Data flow

```
MovieLens 1M (.dat files, ml/data/raw/ml-1m/)
        |
        v
ml/preprocessing/load_movielens.py   (parse, clean, validate)
        |
        v
ml/preprocessing/  ->  feature engineering (TF-IDF on genres, user-item matrix)
        |
        +-------------------------+
        |                         |
        v                         v
ml/models/content_based.py   ml/models/collaborative.py
        |                         |
        +-----------+-------------+
                    v
        ml/models/hybrid.py  (weighted combination)
                    |
                    v
        ml/training/train.py  -> artifacts/*.pkl
                    |
                    v
        backend/app/main.py loads artifacts at startup (lifespan hook)
                    |
                    v
        FastAPI REST endpoints (/api/recommendations, /api/movies, ...)
                    |
                    v
        Next.js frontend consumes the API
```

Application state (users, ratings/interactions, watchlist, recommendation
history) lives in **MongoDB**. The MovieLens dataset itself is treated as
a static ML input, not duplicated into Mongo — see section 4 of the
original spec.

## Why this stack

| Layer | Choice | Why |
|---|---|---|
| ML | Python + pandas/NumPy/scikit-learn | Standard, well-documented tooling for TF-IDF, cosine similarity, and matrix factorization (TruncatedSVD); no need for a deep learning framework at MovieLens-1M scale. |
| Backend | FastAPI | Async-native, Pydantic validation built in, auto-generated OpenAPI docs — good fit for a Python ML backend that needs a clean REST boundary. |
| Backend DB driver | Motor (async MongoDB) | Matches FastAPI's async request handling; avoids blocking the event loop on DB calls. |
| App DB | MongoDB | Flexible schema for users/ratings/watchlist; MongoDB Atlas gives a free-tier path to deployment. |
| Frontend | Next.js + TypeScript + Tailwind | Component-based, server-rendering where useful for movie pages, strong ecosystem fit with Vercel deployment. |
| Auth | JWT + bcrypt password hashing | Stateless auth appropriate for a decoupled frontend/backend; no session store needed. |
| Deployment | Vercel (frontend) + Render (backend) + Atlas (DB) | All have workable free tiers, matching a student-project budget. |

## Why this ML pipeline shape

- **Content-based and collaborative models are kept as separate, independently
  testable modules** (`ml/models/content_based.py`, `ml/models/collaborative.py`)
  so each can be evaluated on its own (see section 15 of the spec) before being
  combined in `ml/models/hybrid.py`. This also satisfies engineering rule #6
  (keep ML, backend, frontend modular).
- **Artifacts are trained offline and persisted** (`artifacts/*.pkl`), not
  recomputed per request — the FastAPI app loads them once at startup via the
  `lifespan` context manager in `backend/app/main.py`. This is what makes
  `/api/recommendations` fast instead of recomputing a similarity matrix on
  every call.
- **MovieLens's `::`-delimited, Latin-1-encoded `.dat` files are parsed
  explicitly** in `load_movielens.py` rather than assumed to behave like a
  standard CSV — this is a common failure point when people first touch this
  dataset.

## What Phase 1 delivers

- Full repository skeleton (frontend/backend/ml/scripts/notebooks/artifacts/docs)
- FastAPI app that boots, connects to MongoDB, and exposes `/api/health`
- MovieLens 1M loader with delimiter/encoding/duplicate/type handling
  (`ml/preprocessing/load_movielens.py`) — this is real, runnable code, not a stub
- Docker + docker-compose for local `mongo` + `backend`
- `.env.example` with no real secrets
- This document

## What Phase 1 does **not** yet include

Per the phased plan: EDA, content-based model, collaborative model, hybrid
model, evaluation, remaining API endpoints, the Next.js frontend, auth,
watchlist/ratings endpoints, tests, and final docs/viva material. Each of
those is its own phase — see the original spec's section 29 for the full
sequence.

## Setup commands (Phase 1)

```bash
# 1. Get the dataset (not committed to the repo — see .gitignore)
mkdir -p ml/data/raw
cd ml/data/raw
curl -O https://files.grouplens.org/datasets/movielens/ml-1m.zip
unzip ml-1m.zip
cd ../../..

# 2. Backend env
cp .env.example backend/.env
# then edit backend/.env: set JWT_SECRET_KEY, and MONGODB_URI if not using Docker's mongo

# 3a. Run with Docker (recommended — starts Mongo + backend together)
docker compose up --build

# 3b. Or run backend locally without Docker
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 4. Verify
curl http://localhost:8000/api/health

# 5. Try the MovieLens loader standalone
cd ../ml/preprocessing
python load_movielens.py
```

Expected `/api/health` response once Mongo is reachable:

```json
{
  "status": "ok",
  "environment": "development",
  "database": "connected",
  "ml_artifacts_loaded": false
}
```

`ml_artifacts_loaded` will stay `false` until Phase 8, when the training
pipeline exists and the backend has real artifacts to load.
