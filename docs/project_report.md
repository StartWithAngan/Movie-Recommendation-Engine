# Project Report — Movie Recommendation Engine Using Machine Learning
### A Hybrid Recommendation System Using Content-Based and Collaborative Filtering

## Abstract
This project implements a hybrid movie recommendation platform combining
content-based filtering (TF-IDF over genre metadata + cosine similarity)
and collaborative filtering (TruncatedSVD matrix factorization over the
user-item rating matrix), trained on the MovieLens 1M dataset. The system
is exposed through a FastAPI backend and a Next.js frontend, supporting
user registration, rating, watchlisting, and personalized, explainable
recommendations.

## Problem Statement
Users face an overwhelming number of movie choices. A system that
personalizes recommendations based on both a movie's own attributes and
patterns across similar users' preferences reduces choice overload and
improves content discovery.

## Objectives
- Build a working hybrid recommender combining content-based and
  collaborative approaches.
- Handle the cold-start problem for new users and new movies.
- Provide human-readable explanations for each recommendation.
- Evaluate recommendation quality against a non-personalized baseline
  using appropriate metrics (RMSE, MAE, Precision@K, Recall@K).
- Deliver the system as a deployable full-stack web application.

## Existing System
Naive approaches typically use only one signal — either genre-matching
(content-based) or purely popularity-based ranking — neither of which
personalizes well on its own: genre-matching ignores actual taste
patterns across users, and popularity ranking isn't personalized at all.

## Proposed System
A hybrid recommender that computes both a content-based score (genre
similarity to movies the user liked) and a collaborative score (latent
factor model of the user-item rating matrix), combines them with
configurable weights, and falls back gracefully to content-based scoring
alone when collaborative data is unavailable (cold start).

## System Architecture
See `docs/architecture.md` for the full data-flow diagram and technology
rationale. In summary:

```
MovieLens 1M -> preprocessing -> {content-based model, collaborative model}
             -> hybrid ranker -> trained artifacts -> FastAPI -> Next.js
```

## Module Description
- **`ml/preprocessing/`** — MovieLens `.dat` parsing, validation, and EDA.
- **`ml/models/content_based.py`** — TF-IDF + cosine similarity over genres.
- **`ml/models/collaborative.py`** — TruncatedSVD matrix factorization.
- **`ml/models/hybrid.py`** — weighted combination, explanations, cold-start routing.
- **`ml/evaluation/evaluate.py`** — leakage-safe split, RMSE/MAE, Precision@K/Recall@K.
- **`ml/training/train.py`** — end-to-end offline training pipeline, persists artifacts.
- **`backend/`** — FastAPI REST API: auth, movies, ratings, recommendations, watchlist, profile.
- **`frontend/`** — Next.js UI: home, discover, movie details, recommendations, watchlist, profile.

## Dataset Description
MovieLens 1M: ~1,000,000 ratings from ~6,000 users on ~4,000 movies,
distributed as `movies.dat`, `ratings.dat`, `users.dat` with a `::`
delimiter and Latin-1 encoding.

## Data Preprocessing
Handled in `ml/preprocessing/load_movielens.py`: delimiter parsing,
missing-value removal, duplicate removal, type casting, and cross-table
consistency checks (ratings referencing unknown users/movies).

## Algorithms Used
- **TF-IDF vectorization** over genre tokens.
- **Cosine similarity** for movie-to-movie content similarity.
- **TruncatedSVD** for collaborative matrix factorization.
- **Weighted linear combination** for the hybrid ranker.

## Mathematical Concepts
- TF-IDF weighting: `tfidf(t,d) = tf(t,d) * log(N / df(t))`
- Cosine similarity: `cos(A,B) = (A·B) / (||A|| ||B||)`
- Matrix factorization: `R ≈ U · Vᵀ`, minimizing reconstruction error via SVD.
- Rank normalization: `x' = (rank(x) - 1) / (n - 1)` (average rank, ties share), applied before combining hybrid scores.

## Model Training
See `ml/training/train.py`. The pipeline loads data, performs a per-user
leakage-safe train/test split, trains both models on the training split,
evaluates on the held-out test split, and persists artifacts to `artifacts/`.

## Evaluation
Metrics: RMSE and MAE for rating prediction; Precision@K and Recall@K for
top-K recommendation quality, each compared against a popularity baseline.
**Note:** the sample run recorded in `docs/architecture.md` and this
project's development used a small synthetic dataset (this sandbox had no
network access to download the real 111MB MovieLens 1M archive) — re-run
`ml/training/train.py` against the real dataset before citing final
numbers in a submission.

## Results
Run `python -m ml.training.train` after placing the real MovieLens 1M
files under `ml/data/raw/ml-1m/` to generate `artifacts/evaluation_results.csv`
with real, current numbers — do not copy numbers from development runs
into a final report.

## Advantages
- Personalized, explainable recommendations.
- Handles both new-user and new-movie cold-start cases.
- Modular: each model can be evaluated, swapped, or extended independently.

## Limitations
- Content features are genre-only (no plot/cast text).
- The collaborative model is trained on MovieLens's own user IDs; mapping
  real app-registered users onto that matrix requires periodic retraining
  (not yet implemented — see `backend/app/api/recommendations.py` comments).
- No background/scheduled retraining as new ratings arrive.

## Future Scope
Richer content features, real-time retraining, deep learning-based
sequence models (e.g. session-based recommenders), A/B testing of hybrid
weights, and diversity/novelty-aware re-ranking.

## Conclusion
The system demonstrates a genuine hybrid recommendation pipeline —
distinct content-based and collaborative components, evaluated against a
baseline with standard metrics, combined transparently with explainable
output — packaged as a deployable full-stack application.

## Content-Based vs. Collaborative vs. Hybrid — Summary

| | Content-Based | Collaborative | Hybrid |
|---|---|---|---|
| Signal used | Item metadata (genres) | User-item rating patterns | Both, weighted |
| New-movie cold start | Handles well | Fails (no ratings yet) | Falls back to content |
| New-user cold start | Handles well (needs a few likes) | Fails (no history) | Falls back to content |
| Captures taste beyond stated genres | No | Yes | Yes |
| Explainability | High ("similar genres") | Lower ("similar users") | Both, per recommendation |
