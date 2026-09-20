# Movie Recommendation Engine Using Machine Learning
### A Hybrid Recommendation System Using Content-Based and Collaborative Filtering

## Features
- Hybrid recommendations: TF-IDF/cosine content-based model + sparse low-rank SVD collaborative filtering
  collaborative model, combined with configurable weights.
- Explainable output — every recommendation carries a plain-English reason.
- Cold-start handling for new users and new movies, including a popularity fallback and latent-factor fold-in for real app users.
- Full-stack app: FastAPI + MongoDB backend, Next.js + Tailwind frontend.
- Auth (JWT), ratings, watchlist, profile analytics.
- Offline training pipeline with leakage-safe evaluation against a
  popularity baseline (RMSE, MAE, Precision@K, Recall@K).
- Docker Compose for local Mongo + backend + frontend.

## Architecture
See [`docs/architecture.md`](docs/architecture.md) for the full data-flow
diagram and technology rationale.

## Tech Stack
- **ML:** Python, pandas, NumPy, scikit-learn, SciPy
- **Backend:** FastAPI, Motor (async MongoDB), JWT auth
- **Database:** MongoDB
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS
- **Deployment:** Vercel (frontend), Render (backend), MongoDB Atlas

## Dataset
MovieLens 32M (with 1M compatibility) — see [`docs/architecture.md`](docs/architecture.md) for
download instructions. Not committed to this repo (see `.gitignore`).

## Machine Learning Approach
- **Content-based:** `ml/models/content_based.py`
- **Collaborative:** `ml/models/collaborative.py` (sparse `svds` factorization + user fold-in for application users)
- **Hybrid:** `ml/models/hybrid.py`
- **Evaluation:** `ml/evaluation/evaluate.py`
- **Training pipeline:** `ml/training/train.py`

Full explanation of each approach and their trade-offs:
[`docs/project_report.md`](docs/project_report.md).

## API Documentation
Once the backend is running, interactive docs are at `http://localhost:8000/docs`
(FastAPI's auto-generated Swagger UI).

## Installation & Running Locally

```bash
# 1. Dataset
mkdir -p ml/data/raw && cd ml/data/raw
curl -O https://files.grouplens.org/datasets/movielens/ml-1m.zip && unzip ml-1m.zip
cd ../../..

# 2. Environment variables
cp .env.example backend/.env        # set a real JWT_SECRET_KEY
cp frontend/.env.local.example frontend/.env.local

# 3. Train the models (produces artifacts/*.pkl the backend loads at startup)
cd backend && pip install -r requirements.txt && cd ..
python -m ml.training.train

# 4. Run everything
docker compose up --build

# 5. Verify
curl http://localhost:8000/api/health
open http://localhost:3000
```

Running without Docker: see [`docs/architecture.md`](docs/architecture.md).

## Environment Variables
See `.env.example` (backend) and `frontend/.env.local.example` (frontend).
Never commit real secrets.

## Docker Setup
`docker-compose.yml` runs MongoDB, the FastAPI backend, and the Next.js
frontend together. Individual Dockerfiles live in `backend/Dockerfile`
and `frontend/Dockerfile`.

## Deployment
- Frontend → Vercel (set `NEXT_PUBLIC_API_BASE_URL` to your deployed backend URL)
- Backend → Render or any Python-compatible host (set the same env vars as `.env.example`)
- Database → MongoDB Atlas

## Testing
```bash
pip install pytest
python -m pytest ml/tests/
```
Covers the MovieLens loader, content-based similarity, collaborative
filtering bounds/cold-start/exclusion behavior, and hybrid weight
validation, cold-start routing, and duplicate-free ranking.

## Documentation
- [`docs/architecture.md`](docs/architecture.md) — architecture, data flow, tech rationale, setup
- [`docs/project_report.md`](docs/project_report.md) — full college project report
- [`docs/viva_questions.md`](docs/viva_questions.md) — 30 viva Q&A

## Known Limitations
- Content features use genres only (no plot/cast text) — see project report.
- Application users are not required to share MovieLens user IDs. Their ratings are folded into the trained item-factor space to infer a latent user vector, so collaborative recommendations can work without retraining after every new user.
- Development/testing in this environment used a small synthetic dataset,
  since the sandbox had no network access to download the real ~111MB
  MovieLens 1M archive — re-run the training pipeline against the real
  dataset before treating any metric as final.

## Future Enhancements
See `docs/project_report.md` § Future Scope.

## Screenshots
_(Add screenshots here once running locally.)_

## Authors
_(Add your name(s) here.)_


## Dataset: MovieLens 32M

The project supports MovieLens 32M. Extract it to `ml/data/raw/ml-32m/`.
The loader automatically detects the CSV-based 32M format.

Run the streaming dataset audit with:

```bash
python -m ml.preprocessing.eda_32m ml/data/raw/ml-32m
```

The 32M dataset is intentionally not bundled into project archives because
of its size.

## Phase 5 — Application Layer

The project now includes the core application layer: FastAPI authentication, MongoDB indexes, movie discovery/search, ratings, watchlist, profile analytics, recommendation endpoints, and a polished Next.js interface for sign-in, discovery, movie details, recommendations, watchlist, and profile views.

Run locally with MongoDB available:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

and in another terminal:

```bash
cd frontend
npm install
npm run dev
```
