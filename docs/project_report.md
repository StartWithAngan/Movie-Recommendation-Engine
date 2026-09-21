Next: **`docs/project_report.md`**.

This is the main technical report, so we need to bring it completely in line with the **final MovieLens 32M implementation**.

Replace the entire contents of `docs/project_report.md` with:

````markdown
# Project Report — Movie Recommendation Engine Using Machine Learning

## A Hybrid Recommendation System Using Content-Based and Collaborative Filtering

---

# 1. Abstract

The Movie Recommendation Engine is a full-stack machine learning application designed to provide personalized movie recommendations.

The system combines two major recommendation approaches:

1. **Content-based filtering** using TF-IDF and cosine similarity over movie genres.
2. **Collaborative filtering** using sparse SVD matrix factorization over the MovieLens 32M user-item rating matrix.

These signals are combined through a hybrid ranking system using rank/percentile normalization.

The machine learning pipeline is trained and evaluated using the MovieLens 32M dataset containing more than 32 million ratings. The trained models are persisted as artifacts and integrated into a FastAPI backend.

The application provides user authentication, movie discovery, ratings, personalized recommendations, similar-movie recommendations, watchlists, profile information, and recommendation explanations.

A Next.js frontend provides the user interface, while MongoDB stores application-level user data.

---

# 2. Problem Statement

The large number of movies available to users makes it difficult to identify movies that match individual preferences.

A recommendation system can reduce this choice overload by analyzing:

- Movie characteristics
- User rating behavior
- Patterns across users
- Historical interactions

A single recommendation technique has limitations.

A content-based system can identify movies with similar characteristics but may not capture broader user behavior.

A collaborative system can learn patterns from user interactions but can struggle when users or movies have limited historical information.

Therefore, this project implements a hybrid recommendation system combining both approaches.

---

# 3. Objectives

The main objectives are:

- Build a working movie recommendation system using machine learning.
- Use the MovieLens 32M dataset for training and evaluation.
- Implement content-based movie recommendation.
- Implement collaborative filtering using sparse matrix factorization.
- Combine recommendation signals using a hybrid ranking approach.
- Handle cold-start situations.
- Provide human-readable recommendation explanations.
- Evaluate recommendation quality using standard metrics.
- Integrate the trained models into a FastAPI application.
- Build a full-stack interface using Next.js.
- Store application data using MongoDB.
- Deploy the application for real-world demonstration.

---

# 4. Scope

The project covers:

```text
Dataset Processing
        ↓
Machine Learning
        ↓
Model Evaluation
        ↓
Recommendation API
        ↓
Web Application
        ↓
Production Deployment
````

The machine learning system focuses primarily on movie genres and user rating behavior.

The application layer additionally supports:

* User accounts
* Authentication
* Ratings
* Watchlists
* Movie search
* Movie discovery
* Personalized recommendations
* Similar movies
* Profile information

---

# 5. Dataset

The project uses the **MovieLens 32M** dataset.

The final dataset audit produced:

| Property                  |      Value |
| ------------------------- | ---------: |
| Movies                    |     87,585 |
| Ratings                   | 32,000,204 |
| Users                     |    200,948 |
| Mean Rating               |     3.5404 |
| Rating Standard Deviation |     1.0590 |
| Genres                    |         20 |

The primary dataset files are:

```text
movies.csv
ratings.csv
links.csv
tags.csv
```

The dataset is stored locally under:

```text
ml/data/raw/ml-32m/
```

The dataset is not committed to the Git repository because of its large size.

---

# 6. System Architecture

The complete system consists of four major layers:

```text
┌───────────────────────────────────────────┐
│              Next.js Frontend             │
│       React + TypeScript + Tailwind       │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│              FastAPI Backend              │
│ Auth • Movies • Ratings • Recommendations │
│ Watchlist • Profile • Analytics           │
└───────────────┬─────────────────┬─────────┘
                │                 │
                ▼                 ▼
       ┌────────────────┐  ┌─────────────────┐
       │    MongoDB     │  │  ML Artifacts   │
       │ Users          │  │ Content Model   │
       │ Ratings        │  │ SVD Model       │
       │ Watchlists     │  │ Popularity      │
       └────────────────┘  └────────┬────────┘
                                    │
                                    ▼
                            ┌────────────────┐
                            │ ML Training    │
                            │ MovieLens 32M  │
                            └────────────────┘
```

Detailed architecture is documented in:

```text
docs/architecture.md
```

---

# 7. Technology Stack

| Component            | Technology                         |
| -------------------- | ---------------------------------- |
| Programming Language | Python                             |
| ML                   | pandas, NumPy, scikit-learn, SciPy |
| Dataset              | MovieLens 32M                      |
| Content Model        | TF-IDF + cosine similarity         |
| Collaborative Model  | Sparse SVD                         |
| Backend              | FastAPI                            |
| Database             | MongoDB                            |
| MongoDB Driver       | Motor                              |
| Authentication       | JWT + bcrypt                       |
| Frontend             | Next.js 14                         |
| UI                   | React + TypeScript + Tailwind CSS  |
| Testing              | pytest                             |
| Containerization     | Docker                             |
| Production           | Vercel                             |

---

# 8. Machine Learning Methodology

The recommendation engine contains four main models:

```text
Popularity Baseline
        │
        ├──────────────┐
        │              │
Content-Based     Collaborative
        │              │
        └──────┬───────┘
               ▼
         Hybrid Ranker
```

The popularity model is primarily used as a baseline and fallback strategy.

---

# 9. Content-Based Filtering

## 9.1 Concept

Content-based filtering recommends movies based on their characteristics.

In this project, movie genres are used as the primary content features.

Example:

```text
Toy Story
→ Animation
→ Children
→ Comedy
```

Movies are transformed into numerical feature vectors.

---

## 9.2 TF-IDF

The project uses TF-IDF to represent genre information.

Conceptually:

```text
TF-IDF(t,d) = TF(t,d) × log(N / DF(t))
```

where:

* `t` = term/genre
* `d` = movie
* `N` = number of movies
* `DF(t)` = number of movies containing that genre

TF-IDF gives greater importance to relatively distinctive genres.

---

## 9.3 Cosine Similarity

Movie vectors are compared using cosine similarity.

```text
cos(A,B) = (A · B) / (||A|| ||B||)
```

A higher cosine similarity means the two movie feature vectors point in more similar directions.

This allows the system to identify movies with similar genre profiles.

---

# 10. Collaborative Filtering

## 10.1 Concept

Collaborative filtering uses user-item interaction patterns instead of relying only on movie metadata.

The MovieLens rating data can be represented as:

```text
             Movie
          M1 M2 M3 M4
       ┌────────────────
User 1 │ 5  4  0  0
User 2 │ 4  0  5  0
User 3 │ 0  5  4  3
```

A zero/missing entry represents an unknown interaction rather than a negative rating.

---

# 11. Sparse Matrix Factorization

The project uses SciPy's sparse SVD implementation:

```python
scipy.sparse.linalg.svds
```

The rating matrix is approximated as:

```text
R ≈ U × Vᵀ
```

where:

* `R` = user-item rating matrix
* `U` = user latent factors
* `V` = item latent factors

The final model uses **12 latent factors**.

The latent representation allows the model to capture hidden preference patterns that are not explicitly represented by movie genres.

---

# 12. Application-User Fold-In

The application has its own users stored in MongoDB.

These users do not necessarily correspond to MovieLens user IDs.

To support personalized collaborative recommendations, the system can infer an application user's latent preference vector from their ratings using the trained item-factor space.

```text
Application User
       │
       ▼
MongoDB Ratings
       │
       ▼
Rated Movie IDs
       │
       ▼
Known Item Factors
       │
       ▼
Infer User Vector
       │
       ▼
Score Candidate Movies
```

This allows application users to receive personalized recommendations without retraining the entire MovieLens model after every rating.

---

# 13. Popularity Baseline

The popularity model provides a non-personalized recommendation strategy.

It is useful for:

* Baseline evaluation
* New-user recommendations
* Situations where insufficient personalization information exists

The baseline provides a reference against which personalized recommendation methods can be evaluated.

---

# 14. Hybrid Recommendation

The hybrid model combines content and collaborative signals.

The final process is:

```text
Content Scores
      │
      ▼
Rank Normalization
      │
      ├───────────────┐
      │               │
      │               ▼
      │         Hybrid Score
      │               │
      │               ▼
      │        Final Ranking
      │               ▲
      │               │
      └───────────────┘
                      ▲
                      │
              Collaborative Scores
                      │
                      ▼
               Rank Normalization
```

---

# 15. Rank Normalization

The two models produce scores with different distributions.

The final implementation uses rank/percentile normalization.

Conceptually:

```text
normalized_rank = (rank - 1) / (n - 1)
```

Ties receive the same average rank.

This converts model rankings into comparable values.

---

## Why rank normalization?

An earlier min-max implementation caused collaborative scores to become nearly constant for some users because predicted ratings were tightly clustered.

This reduced the contribution of the collaborative signal.

Rank normalization instead preserves the relative ordering of candidates from each model.

---

# 16. Recommendation Explanations

The recommendation API returns a human-readable explanation for recommendations.

Examples include:

```text
Similar to movies you rated highly
```

and:

```text
Based on your rating patterns
```

The explanation is selected based on the recommendation signals contributing to the result.

This improves the interpretability of the recommendation system.

---

# 17. Cold-Start Problem

Cold start occurs when there is insufficient historical information about a user or item.

## 17.1 New User

A new user initially has no rating history.

The system uses a popularity-based fallback.

After the user provides ratings, personalized recommendation signals become available.

```text
New User
   ↓
No History
   ↓
Popular Recommendations
   ↓
User Rates Movies
   ↓
Personalized Recommendations
```

---

## 17.2 New Movie

A new movie may have little or no collaborative interaction history.

Its metadata can still be used by the content-based model.

```text
New Movie
   ↓
Genre Metadata
   ↓
TF-IDF Representation
   ↓
Content Similarity
   ↓
Recommendation Candidate
```

---

# 18. Data Preprocessing

The preprocessing pipeline performs:

* Dataset loading
* Schema validation
* Type validation
* Duplicate handling
* Movie/rating consistency checks
* Genre processing
* Rating matrix preparation
* Exploratory data analysis

The dataset audit can be run using:

```bash
python -m ml.preprocessing.eda_32m ml/data/raw/ml-32m
```

---

# 19. Model Training

The training pipeline is implemented in:

```text
ml/training/train.py
```

The overall training process is:

```text
MovieLens 32M
      ↓
Load and Validate
      ↓
Chronological Train/Test Split
      ↓
Popularity Model
      ↓
Content-Based Model
      ↓
Collaborative SVD
      ↓
Hybrid Model
      ↓
Evaluation
      ↓
Persist Artifacts
```

The final artifacts are stored in:

```text
artifacts/
```

---

# 20. Model Artifacts

The final artifact set includes:

```text
artifacts/
├── collaborative_model.pkl
├── content_similarity.pkl
├── evaluation_results.csv
├── movie_metadata.pkl
└── popularity_model.pkl
```

The backend loads the artifacts during startup.

This avoids retraining models or reconstructing expensive recommendation structures during API requests.

---

# 21. Evaluation Methodology

The system uses a chronological per-user holdout.

Each user's rating history is ordered by timestamp.

The latest eligible interaction is held out for evaluation while earlier interactions are used for training.

```text
User History
     │
     ▼
Sort by Timestamp
     │
     ├──────────────┐
     │              │
     ▼              ▼
Training Data   Held-Out Data
     │              │
     ▼              │
Train Models         │
     │              │
     ▼              │
Generate Ranking     │
     │              │
     └──────┬───────┘
            ▼
       Calculate Metrics
```

This prevents the held-out interaction from leaking into the recommendation generation process.

---

# 22. Evaluation Metrics

## RMSE

Root Mean Squared Error measures rating prediction error.

```text
RMSE = √(Σ(y - ŷ)² / n)
```

---

## MAE

Mean Absolute Error measures the average absolute prediction error.

```text
MAE = Σ|y - ŷ| / n
```

---

## Precision@10

Measures the proportion of relevant items among the top 10 recommendations.

```text
Precision@10 =
Relevant items in top 10
------------------------
10
```

---

## Recall@10

Measures the proportion of relevant items retrieved in the top 10.

```text
Recall@10 =
Relevant items retrieved in top 10
----------------------------------
All relevant items
```

---

# 23. Final Evaluation Results

The final measured results are:

| Model               |   RMSE |    MAE | Precision@10 | Recall@10 |
| ------------------- | -----: | -----: | -----------: | --------: |
| Popularity Baseline |      — |      — |       0.0025 |    0.0246 |
| Content-Based       |      — |      — |       0.0016 |    0.0164 |
| Collaborative SVD   | 0.9819 | 0.8040 |       0.0106 |    0.1057 |
| Hybrid              |      — |      — |       0.0049 |    0.0492 |

The evaluation results are stored in:

```text
artifacts/evaluation_results.csv
```

These results are specific to the project's dataset, split strategy, relevance definition, and evaluation configuration.

---

# 24. Backend

The backend is implemented using FastAPI.

Main modules include:

```text
backend/app/api/
├── auth.py
├── health.py
├── movies.py
├── profile.py
├── ratings.py
├── recommendations.py
└── watchlist.py
```

The backend provides:

* Authentication
* Movie browsing
* Movie search
* Movie details
* Ratings
* Recommendations
* Similar movies
* Watchlists
* Profile information
* Analytics
* Health monitoring

---

# 25. Authentication

The application uses JWT authentication.

Authentication flow:

```text
User
 │
 ▼
Login
 │
 ▼
FastAPI
 │
 ├── Validate email/password
 │
 └── Generate JWT
       │
       ▼
Frontend stores token
       │
       ▼
Protected API requests
```

Passwords are hashed using bcrypt.

The backend validates JWT tokens for protected user-specific endpoints.

---

# 26. MongoDB

MongoDB stores application-specific data.

Examples include:

```text
Users
Ratings
Watchlists
Profile information
```

The MovieLens dataset remains separate as the ML training source.

This provides a clear separation between:

```text
Static ML Dataset
        │
        └── MovieLens 32M

Application State
        │
        └── MongoDB
```

---

# 27. Frontend

The frontend is built using:

* Next.js 14
* React
* TypeScript
* Tailwind CSS

The frontend provides interfaces for:

* Login
* Registration
* Movie discovery
* Search
* Movie details
* Ratings
* Recommendations
* Watchlist
* Profile

The frontend communicates with the FastAPI backend using REST APIs.

---

# 28. API Endpoints

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

# 29. Deployment

The production application is deployed through Vercel.

Production routing is:

```text
Browser
   │
   ▼
Vercel
   │
   ├── Frontend routes → Next.js
   │
   └── /api/* → FastAPI
                    │
                    ├── MongoDB
                    │
                    └── ML Artifacts
```

The production application has been verified for:

* Registration
* Login
* JWT authentication
* Movie browsing
* Movie search
* Ratings
* Personalized recommendations
* Similar movie recommendations
* Cold-start recommendations
* MongoDB connectivity
* ML artifact loading

---

# 30. Docker

Docker Compose provides a local development environment containing:

```text
MongoDB
FastAPI Backend
Next.js Frontend
```

Start the local stack using:

```bash
docker compose up --build
```

---

# 31. Testing

The project contains automated ML and backend tests.

ML test suite:

```text
13 passed
```

Backend test suite:

```text
10 passed
```

The tests cover areas including:

* Dataset loading
* Content similarity
* Collaborative filtering
* Cold-start behavior
* Recommendation exclusion
* Hybrid ranking
* Authentication
* Database integration
* Movie APIs
* Ratings
* Recommendation APIs

---

# 32. Advantages

The system provides:

* Personalized recommendations
* Multiple recommendation signals
* Explainable recommendations
* Cold-start handling
* Modular ML architecture
* Offline model training
* Persisted artifacts
* REST API integration
* Full-stack web interface
* MongoDB-backed application state
* Automated testing
* Production deployment

---

# 33. Limitations

The current implementation has several limitations.

### Limited Content Features

The content model primarily uses movie genres.

It does not currently use:

* Plot summaries
* Cast
* Directors
* Reviews
* Natural-language descriptions

### Static Collaborative Training

The global collaborative model is trained on MovieLens 32M.

Application-user ratings can be used for user-factor inference, but the global factorization is not automatically retrained after each application rating.

### No Automated Retraining

There is currently no scheduled production model retraining pipeline.

### Recommendation Diversity

The current system focuses primarily on relevance and personalization. Explicit diversity and novelty optimization are not yet implemented.

---

# 34. Future Scope

Potential future improvements include:

1. Richer movie metadata
2. Plot-based NLP features
3. Cast and director features
4. Text embeddings
5. Neural collaborative filtering
6. Automated model retraining
7. Model versioning
8. A/B testing
9. Diversity-aware recommendation
10. Novelty-aware recommendation
11. Real-time feedback loops
12. Recommendation monitoring
13. Advanced user profiling

---

# 35. Conclusion

The Movie Recommendation Engine demonstrates the integration of machine learning with a complete full-stack application.

The final system combines:

```text
MovieLens 32M
      ↓
Preprocessing
      ↓
Content-Based Filtering
      +
Collaborative Filtering
      ↓
Hybrid Ranking
      ↓
Evaluation
      ↓
Persisted ML Artifacts
      ↓
FastAPI
      ↓
MongoDB
      ↓
Next.js
      ↓
Production Deployment
```

The project demonstrates how traditional recommendation algorithms can be combined with modern web application technologies to create a complete, deployable machine learning system.

The final implementation includes machine learning, evaluation, backend APIs, authentication, database integration, frontend functionality, automated testing, and production deployment.
