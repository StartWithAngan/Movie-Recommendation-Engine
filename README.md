# Movie Recommendation Engine Using Machine Learning

### A Hybrid Movie Recommendation System Using Content-Based and Collaborative Filtering

A full-stack movie recommendation platform that combines **content-based filtering**, **collaborative filtering**, and **hybrid ranking** to generate personalized movie recommendations.

The system is trained and evaluated using the **MovieLens 32M dataset** and is exposed through a FastAPI backend with a Next.js frontend.

---

## Features

- 🎬 Personalized movie recommendations
- 🧠 Hybrid recommendation using:
  - TF-IDF + cosine similarity
  - Sparse SVD collaborative filtering
  - Rank-normalized hybrid scoring
- 👤 User registration and JWT authentication
- ⭐ Movie rating system
- 📋 Watchlist management
- 🔎 Movie browsing and search
- 📊 User profile and recommendation analytics
- 🆕 Cold-start handling for new users
- 💡 Explainable recommendations with human-readable reasons
- ⚡ Offline ML training with persisted model artifacts
- 🧪 Automated ML and backend tests
- 🐳 Docker Compose support for local development
- ☁️ Production deployment through Vercel
- 🗄️ MongoDB for application data

---

## System Overview

The system combines two primary recommendation signals.

### 1. Content-Based Filtering

The content-based model represents each movie using its genre information.

The pipeline is:

```text
Movie genres
     ↓
TF-IDF vectorization
     ↓
Movie feature vectors
     ↓
Cosine similarity
     ↓
Similar movies
````

This allows the system to recommend movies with metadata similar to movies a user has rated highly.

---

### 2. Collaborative Filtering

The collaborative model learns patterns from the MovieLens user-item rating matrix.

```text
User-Movie Rating Matrix
          ↓
Sparse Matrix Factorization
          ↓
Latent User / Item Factors
          ↓
Predicted Preferences
          ↓
Collaborative Recommendations
```

The implementation uses SciPy's sparse `svds` factorization so that the large MovieLens 32M dataset can be handled without constructing a dense user-item matrix.

---

### 3. Hybrid Recommendation

The final recommender combines content and collaborative signals.

The two model outputs are first converted into comparable **rank/percentile scores** and then combined using configurable weights.

```text
             ┌─────────────────────┐
             │   Content Model     │
             │ TF-IDF + Cosine     │
             └──────────┬──────────┘
                        │
                        ▼
                 Rank Normalization
                        │
                        │
                        ├──────────────┐
                        │              │
                        ▼              ▼
                 Hybrid Ranking   Recommendation
                        ▲
                        │
                        │
                 Rank Normalization
                        │
             ┌──────────┴──────────┐
             │ Collaborative Model │
             │    Sparse SVD       │
             └─────────────────────┘
```

Rank normalization is used instead of simple min-max normalization because collaborative predictions can be tightly clustered. Ranking preserves the relative ordering of candidates from each model before combining them.

---

# Architecture

```text
                    ┌──────────────────────┐
                    │  MovieLens 32M       │
                    │  ratings + movies    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   ML Preprocessing   │
                    │ validation + EDA     │
                    └──────────┬───────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
    ┌──────────────────┐              ┌───────────────────┐
    │ Content-Based    │              │ Collaborative     │
    │ TF-IDF + Cosine  │              │ Sparse SVD        │
    └────────┬─────────┘              └─────────┬─────────┘
             │                                  │
             └────────────────┬─────────────────┘
                              ▼
                    ┌──────────────────────┐
                    │   Hybrid Ranker     │
                    │ rank normalization  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Persisted Artifacts  │
                    │      *.pkl           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │ authentication       │
                    │ movies / ratings     │
                    │ recommendations      │
                    │ watchlist / profile  │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴───────────┐
                    │                      │
                    ▼                      ▼
          ┌──────────────────┐   ┌──────────────────┐
          │    MongoDB       │   │ Next.js Frontend │
          │ users / ratings  │   │ React + Tailwind │
          │ watchlists       │   └──────────────────┘
          └──────────────────┘
```

For a detailed explanation, see:

* [`docs/architecture.md`](docs/architecture.md)
* [`docs/project_report.md`](docs/project_report.md)

---

# Tech Stack

| Layer               | Technology                                 |
| ------------------- | ------------------------------------------ |
| Machine Learning    | Python, NumPy, pandas, scikit-learn, SciPy |
| Dataset             | MovieLens 32M                              |
| Content Model       | TF-IDF + cosine similarity                 |
| Collaborative Model | Sparse SVD (`scipy.sparse.linalg.svds`)    |
| Backend             | FastAPI                                    |
| Authentication      | JWT + bcrypt                               |
| Database            | MongoDB                                    |
| MongoDB Driver      | Motor                                      |
| Frontend            | Next.js 14, React, TypeScript              |
| Styling             | Tailwind CSS                               |
| Testing             | pytest                                     |
| Containerization    | Docker + Docker Compose                    |
| Production          | Vercel                                     |

---

# Dataset

The project uses the **MovieLens 32M** dataset released by GroupLens.

The dataset contains:

| Property         |      Value |
| ---------------- | ---------: |
| Movies           |     87,585 |
| Ratings          | 32,000,204 |
| Users            |    200,948 |
| Mean Rating      |     3.5404 |
| Rating Std. Dev. |      1.059 |
| Genres           |         20 |

The dataset is **not committed to this repository** because of its size.

Expected location:

```text
ml/data/raw/ml-32m/
```

Expected files:

```text
ml-32m/
├── checksums.txt
├── links.csv
├── movies.csv
├── ratings.csv
├── README.txt
└── tags.csv
```

The project includes an EDA/audit pipeline:

```bash
python -m ml.preprocessing.eda_32m ml/data/raw/ml-32m
```

---

# Machine Learning Pipeline

## Data Processing

The training pipeline performs:

1. Dataset loading
2. Validation
3. Duplicate/type handling
4. Chronological train/test splitting
5. Content feature generation
6. Sparse collaborative matrix construction
7. Model training
8. Recommendation evaluation
9. Artifact persistence

The evaluation split is designed to avoid using a user's held-out interaction when generating recommendations for that same evaluation user.

---

## Content-Based Model

File:

```text
ml/models/content_based.py
```

Movie genres are transformed using TF-IDF.

For a term `t` and document/movie `d`:

```text
TF-IDF(t,d) = TF(t,d) × log(N / DF(t))
```

Movie similarity is calculated using cosine similarity:

```text
cos(A,B) = (A · B) / (||A|| ||B||)
```

The model uses a sparse representation and nearest-neighbor search to retrieve similar movies efficiently.

---

## Collaborative Model

File:

```text
ml/models/collaborative.py
```

The rating data is represented as a sparse user-item matrix.

The system performs sparse matrix factorization using:

```python
scipy.sparse.linalg.svds
```

The factorization learns latent representations for users and movies.

Conceptually:

```text
R ≈ U × Vᵀ
```

where:

* `R` = user-item rating matrix
* `U` = user latent factors
* `V` = item latent factors

The trained model can score movies for existing MovieLens users and can also infer a latent vector for application users from their ratings.

---

## Hybrid Model

File:

```text
ml/models/hybrid.py
```

The hybrid recommender combines:

```text
Content Score
      +
Collaborative Score
      ↓
Rank / Percentile Normalization
      ↓
Weighted Combination
      ↓
Final Recommendation Ranking
```

The default model weights are configurable.

The hybrid model also produces recommendation explanations such as:

```text
Similar to movies you rated highly
```

or:

```text
Based on your rating patterns
```

---

# Cold-Start Handling

The system handles users and movies for which collaborative information is unavailable.

### New User

A new user initially has no rating history.

The system can use popular movies as the initial recommendation signal.

After the user begins rating movies, those ratings can be used to generate personalized recommendations.

### New Movie

A movie without sufficient interaction history can still be recommended using its metadata through the content-based model.

This allows the system to provide recommendations without requiring every movie to have an established collaborative history.

---

# Evaluation

The final evaluation compares four approaches:

1. Popularity baseline
2. Content-based model
3. Collaborative SVD
4. Hybrid model

## Final Results

| Model               |   RMSE |    MAE | Precision@10 | Recall@10 |
| ------------------- | -----: | -----: | -----------: | --------: |
| Popularity Baseline |      — |      — |       0.0025 |    0.0246 |
| Content-Based       |      — |      — |       0.0016 |    0.0164 |
| Collaborative SVD   | 0.9819 | 0.8040 |       0.0106 |    0.1057 |
| Hybrid              |      — |      — |       0.0049 |    0.0492 |

RMSE and MAE are applicable to the collaborative rating-prediction model in this evaluation. The ranking metrics evaluate the quality of the top-10 recommendation list.

The evaluation results are stored in:

```text
artifacts/evaluation_results.csv
```

Detailed methodology and results:

[`docs/phase3_results.md`](docs/phase3_results.md)

---

# Model Artifacts

The trained models are persisted under:

```text
artifacts/
```

The final artifact set includes:

```text
artifacts/
├── collaborative_model.pkl
├── content_similarity.pkl
├── evaluation_results.csv
├── movie_metadata.pkl
└── popularity_model.pkl
```

The backend loads these artifacts during application startup instead of retraining models for every API request.

---

# Backend API

The backend is implemented using FastAPI.

Main API groups include:

```text
/api/auth
/api/movies
/api/ratings
/api/recommendations
/api/watchlist
/api/profile
/api/health
```

## Authentication

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

## Movies

```text
GET /api/movies
GET /api/movies/search
GET /api/movies/{movie_id}
```

## Ratings

```text
POST /api/ratings
GET  /api/ratings
```

## Recommendations

```text
GET /api/recommendations
GET /api/recommendations/similar/{movie_id}
```

## Watchlist

```text
POST   /api/watchlist
GET    /api/watchlist
DELETE /api/watchlist/{movie_id}
```

## Profile

```text
GET /api/profile
GET /api/profile/analytics
```

## Health

```text
GET /api/health
```

---

# Local Setup

## Prerequisites

Recommended environment:

* Python 3.12+
* Node.js
* npm
* Docker
* Docker Compose
* Git
* MongoDB

---

## 1. Clone the repository

```bash
git clone https://github.com/StartWithAngan/Movie-Recommendation-Engine.git
cd Movie-Recommendation-Engine
```

---

## 2. Dataset

Place the extracted MovieLens 32M dataset at:

```text
ml/data/raw/ml-32m/
```

Verify:

```bash
ls ml/data/raw/ml-32m
```

You should see:

```text
movies.csv
ratings.csv
links.csv
tags.csv
```

---

## 3. Backend environment

Create:

```text
backend/.env
```

Use the example configuration as a starting point:

```text
backend/.env.example
```

Set a strong JWT secret.

Never commit real credentials or secrets.

---

## 4. Python environment

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install ML dependencies:

```bash
pip install -r backend/requirements.txt
```

---

## 5. Train the models

Run:

```bash
python -m ml.training.train
```

This generates the trained artifacts under:

```text
artifacts/
```

---

## 6. Start MongoDB

Using Docker:

```bash
docker compose up -d mongo
```

Verify MongoDB:

```bash
docker exec movie-rec-mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```

Expected:

```text
{ ok: 1 }
```

---

## 7. Start the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API is available at:

```text
http://localhost:8000
```

Health check:

```bash
curl http://localhost:8000/api/health
```

---

## 8. Start the frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

For local development, the frontend can use:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Production uses Vercel's `/api` routing and does not require this variable to be set.

---

# Docker

The project includes Docker Compose configuration for local development.

```bash
docker compose up --build
```

The Compose setup includes:

```text
MongoDB
FastAPI backend
Next.js frontend
```

The ML artifacts and source directories are mounted so the application can use the trained models locally.

---

# Testing

The project contains separate ML and backend test suites.

## ML tests

```bash
pytest -q ml/tests
```

Final ML test status:

```text
13 passed
```

The tests cover areas including:

* MovieLens loading
* Content-based similarity
* Collaborative filtering
* Cold-start behavior
* Recommendation exclusion
* Hybrid ranking
* Weight validation
* Duplicate-free recommendations

## Backend tests

```bash
pytest -q backend/tests
```

Final backend integration test status:

```text
10 passed
```

The backend tests cover authentication, database integration, API behavior, movies, ratings, and recommendation flows.

---

# Production Deployment

The application is deployed using **Vercel**.

The deployed architecture uses Vercel routing to connect the Next.js frontend and FastAPI backend through the `/api` path.

Production request flow:

```text
Browser
   ↓
Next.js Frontend
   ↓
/api/*
   ↓
FastAPI Backend
   ↓
MongoDB + ML Artifacts
```

The production backend has been verified for:

* Health checks
* Authentication
* JWT-protected endpoints
* Movie search
* Movie retrieval
* Ratings
* Similar-movie recommendations
* Personalized recommendations
* Cold-start recommendations
* ML artifact loading
* MongoDB connectivity

---

# Security

The application uses:

* JWT-based authentication
* bcrypt password hashing
* Environment variables for secrets
* CORS configuration
* MongoDB-backed user accounts

Real secrets should never be committed to Git.

The following files are intentionally excluded from version control:

```text
.env
backend/.env
frontend/.env.local
```

---

# Project Structure

```text
movie-recommendation-engine-latest/
│
├── artifacts/
│   ├── collaborative_model.pkl
│   ├── content_similarity.pkl
│   ├── evaluation_results.csv
│   ├── movie_metadata.pkl
│   └── popularity_model.pkl
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── ml/
│   │   ├── schemas/
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── docs/
│   ├── architecture.md
│   ├── phase1_status.md
│   ├── phase3_results.md
│   ├── project_report.md
│   └── viva_questions.md
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── Dockerfile
│   └── package.json
│
├── ml/
│   ├── evaluation/
│   ├── models/
│   ├── preprocessing/
│   ├── tests/
│   └── training/
│
├── docker-compose.yml
├── README.md
└── vercel.json
```

---

# Documentation

| Document                                           | Description                              |
| -------------------------------------------------- | ---------------------------------------- |
| [`docs/architecture.md`](docs/architecture.md)     | System architecture and data flow        |
| [`docs/project_report.md`](docs/project_report.md) | Detailed technical project report        |
| [`docs/phase3_results.md`](docs/phase3_results.md) | Dataset, training and evaluation results |
| [`docs/phase1_status.md`](docs/phase1_status.md)   | Overall implementation status            |
| [`docs/viva_questions.md`](docs/viva_questions.md) | Viva questions and answers               |

---

# Limitations

The current implementation has several limitations:

* Content-based recommendations primarily use movie genres.
* Movie plot, cast, director, reviews, and other rich textual metadata are not currently used by the content model.
* Collaborative learning is based on the static MovieLens training data.
* New application-user ratings can be folded into the existing item-factor space, but the global MovieLens collaborative model is not automatically retrained after every new rating.
* There is currently no scheduled background model retraining pipeline.
* Recommendation quality could be improved with additional ranking, diversity, novelty, and personalization techniques.

---

# Future Enhancements

Potential future improvements include:

* Richer movie metadata and plot-based NLP features
* Cast/director similarity
* More advanced collaborative filtering
* Neural recommendation models
* Real-time or scheduled model retraining
* Personalized hybrid-weight tuning
* Recommendation diversity and novelty optimization
* A/B testing
* User feedback loops
* Improved recommendation explanations
* Larger-scale production monitoring
* Recommendation performance dashboards

---

# Screenshots

Screenshots of the deployed application can be added here.

Suggested screenshots:

1. Login / registration
2. Home page
3. Movie search
4. Movie details
5. Rating interaction
6. Personalized recommendations
7. Watchlist
8. User profile / analytics

---

# Authors

**Angan Maity**

---

# Project Status

**Status: Completed — working full-stack ML application**

The current implementation includes the complete pipeline:

```text
Dataset
   ↓
Preprocessing
   ↓
ML Training
   ↓
Evaluation
   ↓
Persisted Artifacts
   ↓
FastAPI
   ↓
MongoDB
   ↓
Next.js
   ↓
Production Deployment
```

The application has been tested locally and its core production functionality has been verified e
