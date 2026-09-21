Next: **`docs/architecture.md`**.

Replace the entire contents of `docs/architecture.md` with this:

````markdown
# System Architecture — Movie Recommendation Engine

## 1. Overview

The Movie Recommendation Engine is a full-stack machine learning application that combines content-based filtering, collaborative filtering, and hybrid ranking to generate personalized movie recommendations.

The system is divided into four major layers:

```text
┌───────────────────────────────────────────────────────────┐
│                     Next.js Frontend                      │
│                 React + TypeScript + Tailwind             │
└──────────────────────────┬────────────────────────────────┘
                           │
                           │ REST API
                           ▼
┌───────────────────────────────────────────────────────────┐
│                     FastAPI Backend                       │
│ Authentication • Movies • Ratings • Recommendations      │
│ Watchlist • Profile • Analytics                           │
└───────────────┬───────────────────────────────┬───────────┘
                │                               │
                ▼                               ▼
┌─────────────────────────┐          ┌──────────────────────┐
│        MongoDB          │          │   ML Model Artifacts │
│ Users                   │          │ Content Model        │
│ Ratings                 │          │ Collaborative Model  │
│ Watchlists              │          │ Popularity Model     │
│ Application data        │          │ Movie Metadata       │
└─────────────────────────┘          └──────────┬───────────┘
                                                 │
                                                 │ trained offline
                                                 ▼
                                      ┌──────────────────────┐
                                      │    ML Pipeline       │
                                      │ MovieLens 32M        │
                                      │ Preprocessing        │
                                      │ Content TF-IDF       │
                                      │ Sparse SVD           │
                                      │ Hybrid Ranking       │
                                      │ Evaluation           │
                                      └──────────────────────┘
````

---

# 2. High-Level Data Flow

The complete data flow is:

```text
MovieLens 32M
     │
     ▼
Data Loading & Validation
     │
     ▼
Exploratory Data Analysis
     │
     ├──────────────────────┐
     │                      │
     ▼                      ▼
Content Features      User-Item Matrix
     │                      │
     ▼                      ▼
TF-IDF                Sparse SVD
     │                      │
     ▼                      ▼
Cosine Similarity     Latent Factors
     │                      │
     └──────────┬───────────┘
                ▼
         Hybrid Ranker
                │
                ▼
       Evaluation Pipeline
                │
                ▼
       Persisted Artifacts
                │
                ▼
          FastAPI Backend
                │
       ┌────────┴────────┐
       ▼                 ▼
   MongoDB          Next.js Frontend
```

The ML pipeline is executed offline. The trained artifacts are then loaded by the backend at startup and reused during recommendation requests.

---

# 3. Repository Architecture

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
│   │   │   ├── auth.py
│   │   │   ├── health.py
│   │   │   ├── movies.py
│   │   │   ├── profile.py
│   │   │   ├── ratings.py
│   │   │   ├── recommendations.py
│   │   │   └── watchlist.py
│   │   │
│   │   ├── core/
│   │   ├── db/
│   │   ├── ml/
│   │   ├── schemas/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── docs/
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

# 4. Machine Learning Layer

The ML layer is responsible for training, evaluating, and persisting recommendation models.

```text
ml/
├── preprocessing/
│   ├── load_movielens.py
│   └── eda_32m.py
│
├── models/
│   ├── content_based.py
│   ├── collaborative.py
│   ├── hybrid.py
│   └── popularity.py
│
├── evaluation/
│   └── evaluate.py
│
├── training/
│   └── train.py
│
└── tests/
```

The ML layer is intentionally separated from the application layer so that models can be trained and evaluated independently of the web application.

---

# 5. Dataset Layer

The system uses the MovieLens 32M dataset.

The expected local location is:

```text
ml/data/raw/ml-32m/
```

The dataset contains:

* 87,585 movies
* 32,000,204 ratings
* 200,948 users
* 20 genres

The primary files are:

```text
movies.csv
ratings.csv
links.csv
tags.csv
```

The dataset is treated as a static ML training source and is not copied into MongoDB.

MongoDB stores application-specific data such as:

* Registered users
* Password hashes
* User ratings
* Watchlists
* Application profile information

---

# 6. Data Preprocessing

The preprocessing pipeline validates and prepares the MovieLens data before model training.

The process includes:

```text
Raw Dataset
     │
     ▼
Load CSV files
     │
     ▼
Validate columns and data types
     │
     ▼
Handle duplicates / invalid records
     │
     ▼
Validate movie and rating relationships
     │
     ▼
Prepare movie metadata
     │
     ▼
Prepare rating matrix
```

Exploratory analysis is available through:

```bash
python -m ml.preprocessing.eda_32m ml/data/raw/ml-32m
```

---

# 7. Content-Based Recommendation

## 7.1 Feature Representation

The content-based model uses movie genres as the primary content features.

Example:

```text
Toy Story → Animation Children Comedy
```

Genres are converted into TF-IDF vectors.

```text
Movie
  │
  ▼
Genre tokens
  │
  ▼
TF-IDF Vectorizer
  │
  ▼
Sparse feature matrix
```

---

## 7.2 TF-IDF

TF-IDF assigns greater importance to terms that are relatively distinctive.

Conceptually:

```text
TF-IDF(t,d) = TF(t,d) × log(N / DF(t))
```

where:

* `t` = genre term
* `d` = movie
* `N` = number of movies
* `DF(t)` = number of movies containing the genre

---

## 7.3 Cosine Similarity

The similarity between two movie vectors is calculated using cosine similarity:

```text
cos(A,B) = (A · B) / (||A|| ||B||)
```

This produces a similarity value used to retrieve movies with similar genre profiles.

The implementation uses sparse representations and nearest-neighbor search rather than creating an unnecessary dense similarity structure.

---

# 8. Collaborative Filtering

The collaborative model uses the MovieLens rating data.

Conceptually:

```text
             Movies
          M1 M2 M3 M4 ...
       ┌─────────────────
User 1 │ 5  4  0  0 ...
User 2 │ 4  0  5  0 ...
User 3 │ 0  5  4  3 ...
...    │ ...
```

Most entries are missing, making the matrix highly sparse.

The project therefore uses sparse matrix operations.

---

## 8.1 Sparse SVD

The model uses:

```python
scipy.sparse.linalg.svds
```

to obtain a low-rank approximation of the rating matrix.

Conceptually:

```text
R ≈ U × Vᵀ
```

where:

* `R` = user-item rating matrix
* `U` = user latent factors
* `V` = item latent factors

The latent factors capture hidden preference dimensions that cannot be represented directly using movie genres.

---

## 8.2 Why Sparse SVD?

A dense representation of the complete MovieLens 32M user-item matrix would require substantially more memory.

Sparse SVD works directly with sparse structures and was therefore selected for the final implementation.

The trained model uses 12 latent factors.

---

# 9. Application-User Fold-In

The MovieLens dataset contains its own historical users, while the application has its own MongoDB users.

The system does not require an application user to have a MovieLens user ID.

When an application user has ratings, the collaborative model can infer a user latent vector from those ratings using the trained item-factor space.

Conceptually:

```text
Application User Ratings
          │
          ▼
Rated Movie IDs
          │
          ▼
Known Item Factors
          │
          ▼
Infer User Latent Vector
          │
          ▼
Score Candidate Movies
```

This allows collaborative-style personalization without retraining the entire MovieLens model after every application rating.

---

# 10. Popularity Model

The popularity model provides a non-personalized recommendation strategy.

It is used as a baseline during evaluation and as a fallback signal for users who do not yet have sufficient preference information.

Conceptually:

```text
Movie Rating History
        │
        ▼
Popularity Calculation
        │
        ▼
Globally Popular Movies
```

This provides a simple reference point against which personalized models can be evaluated.

---

# 11. Hybrid Recommendation

The hybrid model combines content-based and collaborative signals.

```text
Content Model
     │
     ▼
Content Scores
     │
     ▼
Rank Normalization
     │
     ├──────────────┐
     │              │
     │              ▼
     │        Weighted Hybrid
     │              │
     │              ▼
     │        Final Ranking
     │              ▲
     │              │
     └──────────────┘
                    ▲
                    │
             Rank Normalization
                    ▲
                    │
           Collaborative Scores
                    ▲
                    │
          Collaborative Model
```

---

## 11.1 Rank Normalization

The content and collaborative models produce scores on different scales and distributions.

Instead of combining raw scores directly, the system ranks candidates within each model.

The normalized rank can be represented as:

```text
rank_score = (rank - 1) / (n - 1)
```

with tied values receiving the same average rank.

This produces comparable values between 0 and 1.

---

## 11.2 Why Rank Normalization?

An earlier min-max approach caused collaborative scores to become too compressed for some users.

As a result, the collaborative signal contributed very little to the final hybrid ranking.

Rank normalization preserves the relative ordering produced by each model and allows both recommendation signals to influence the final ranking.

---

# 12. Recommendation Explanation

The backend returns an explanation with recommendations.

Examples include:

```text
Similar to movies you rated highly
```

and:

```text
Based on your rating patterns
```

The explanation is selected according to the recommendation signal contributing to the final result.

This makes the recommendation system more interpretable to users.

---

# 13. Cold-Start Strategy

## New Users

A user without ratings has insufficient collaborative information.

The system therefore uses a fallback strategy based on popular movies.

Once the user starts rating movies, the system can use those ratings to produce personalized recommendations.

```text
New User
   │
   ▼
No Rating History
   │
   ▼
Popularity / Initial Recommendations
   │
   ▼
User Rates Movies
   │
   ▼
Personalized Recommendations
```

---

## New Movies

A movie with little or no collaborative interaction can still be processed using its genre metadata.

```text
New Movie
   │
   ▼
Genre Metadata
   │
   ▼
TF-IDF Representation
   │
   ▼
Content Similarity
   │
   ▼
Recommendation Candidate
```

---

# 14. Evaluation Architecture

The evaluation pipeline uses a chronological per-user holdout.

```text
User Rating History
       │
       ▼
Chronological Ordering
       │
       ├───────────────┐
       │               │
       ▼               ▼
   Training          Test
   Ratings           Rating
       │
       ▼
Train Models
       │
       ▼
Generate Recommendations
       │
       ▼
Compare Against Held-Out Data
       │
       ▼
Evaluation Metrics
```

This prevents the held-out interaction from being used when generating recommendations for that evaluation case.

---

# 15. Evaluation Metrics

The system evaluates both rating prediction and ranking quality.

### RMSE

```text
RMSE = √(Σ(y - ŷ)² / n)
```

RMSE penalizes larger prediction errors more strongly.

### MAE

```text
MAE = Σ|y - ŷ| / n
```

MAE represents the average absolute prediction error.

### Precision@10

```text
Precision@10 =
Relevant recommendations in top 10
----------------------------------
10
```

### Recall@10

```text
Recall@10 =
Relevant recommendations in top 10
----------------------------------
All relevant items
```

---

# 16. Final Evaluation Results

The final measured results are:

| Model               |   RMSE |    MAE | Precision@10 | Recall@10 |
| ------------------- | -----: | -----: | -----------: | --------: |
| Popularity Baseline |      — |      — |       0.0025 |    0.0246 |
| Content-Based       |      — |      — |       0.0016 |    0.0164 |
| Collaborative SVD   | 0.9819 | 0.8040 |       0.0106 |    0.1057 |
| Hybrid              |      — |      — |       0.0049 |    0.0492 |

The results are stored in:

```text
artifacts/evaluation_results.csv
```

---

# 17. Backend Architecture

The backend is implemented with FastAPI.

The main application entry point is:

```text
backend/app/main.py
```

The backend is divided into API modules.

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

---

# 18. API Flow

A typical authenticated recommendation request follows this flow:

```text
Browser
   │
   │ JWT
   ▼
FastAPI
   │
   ├── Validate JWT
   │
   ├── Identify application user
   │
   ├── Read user's ratings from MongoDB
   │
   ├── Load/use trained ML artifacts
   │
   ├── Generate candidate recommendations
   │
   └── Return recommendation response
   │
   ▼
Next.js Frontend
```

---

# 19. Authentication Architecture

Authentication uses JWT tokens.

```text
Registration / Login
        │
        ▼
FastAPI Auth Endpoint
        │
        ▼
Validate Credentials
        │
        ▼
JWT Access Token
        │
        ▼
Frontend
        │
        ▼
Authenticated API Requests
```

Passwords are hashed using bcrypt rather than stored as plaintext.

Protected API endpoints validate the JWT before accessing user-specific information.

---

# 20. MongoDB Architecture

MongoDB stores application state.

Application data includes:

```text
Users
Ratings
Watchlists
Profile / analytics data
```

The MovieLens dataset remains a static ML training source and is not copied into MongoDB.

This separates:

```text
Static ML Data
       │
       └── MovieLens

Application Data
       │
       └── MongoDB
```

---

# 21. Frontend Architecture

The frontend is implemented using:

* Next.js 14
* React
* TypeScript
* Tailwind CSS

The frontend communicates with the backend through REST API calls.

Production request routing uses:

```text
Browser
   │
   ▼
Vercel
   │
   ├── Frontend routes → Next.js
   │
   └── /api/* → FastAPI backend
```

This allows the frontend to use relative production API paths such as:

```text
/api/auth/login
/api/movies
/api/recommendations
```

For local development, the API base can point to:

```text
http://localhost:8000
```

---

# 22. Deployment Architecture

The production application is deployed through Vercel.

The production flow is:

```text
                        Internet
                           │
                           ▼
                  ┌─────────────────┐
                  │     Vercel      │
                  └────────┬────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
      Next.js Frontend             /api/* Routing
                                         │
                                         ▼
                                  FastAPI Backend
                                         │
                           ┌─────────────┴─────────────┐
                           │                           │
                           ▼                           ▼
                       MongoDB                  ML Artifacts
```

The deployed application has been verified for:

* Authentication
* Movie retrieval
* Movie search
* Ratings
* Personalized recommendations
* Similar-movie recommendations
* Cold-start recommendations
* MongoDB connectivity
* ML artifact loading

---

# 23. Local Docker Architecture

Docker Compose provides a local multi-service environment.

```text
docker-compose.yml
       │
       ├── MongoDB
       │
       ├── FastAPI Backend
       │
       └── Next.js Frontend
```

The ML source and artifacts are mounted into the backend environment so that the API can use the locally trained models.

---

# 24. Model Artifact Loading

Models are trained offline rather than during API requests.

```text
Training
   │
   ▼
*.pkl Artifacts
   │
   ▼
Backend Startup
   │
   ▼
Load Artifacts
   │
   ▼
Keep Models Available
   │
   ▼
Fast Recommendation Requests
```

This avoids expensive model training or similarity computation during every request.

---

# 25. Testing Architecture

The project uses pytest for automated testing.

ML tests:

```text
ml/tests/
```

Backend tests:

```text
backend/tests/
```

Final verification:

```text
ML tests       → 13 passed
Backend tests  → 10 passed
```

The tests verify model behavior, API functionality, authentication, recommendation behavior, and database integration.

---

# 26. Design Decisions

## Why separate ML and backend?

Separating the ML layer from the API layer makes the models independently testable and allows the recommendation engine to evolve without tightly coupling it to the web application.

## Why offline training?

Training the large MovieLens models during API requests would introduce unacceptable latency.

## Why sparse representations?

MovieLens contains millions of ratings but the user-item matrix is sparse. Sparse data structures significantly reduce unnecessary memory usage.

## Why a hybrid model?

Content-based filtering and collaborative filtering capture different types of information. Combining their rankings allows the application to use both movie metadata and rating behavior.

## Why MongoDB?

Application data such as user accounts, ratings, and watchlists is naturally represented as flexible documents and does not need to be mixed with the static MovieLens training dataset.

---

# 27. Current Limitations

The current architecture has several limitations:

* Content features primarily use genres.
* The collaborative model is trained from the static MovieLens dataset.
* Application-user ratings can be folded into the trained item-factor space, but the global collaborative model is not automatically retrained after every new application rating.
* No automated background retraining pipeline is currently implemented.
* Recommendation diversity and novelty are not yet explicitly optimized.

---

# 28. Future Architecture Improvements

Future versions could add:

```text
Real User Feedback
        │
        ▼
Event / Rating Storage
        │
        ▼
Scheduled Retraining
        │
        ▼
Model Validation
        │
        ▼
Model Registry
        │
        ▼
Production Model
```

Additional improvements could include:

* Rich movie text embeddings
* Cast and director features
* Neural collaborative filtering
* Real-time feature updates
* Automated retraining
* Model versioning
* A/B testing
* Diversity-aware ranking
* Recommendation monitoring
* User feedback loops

---

# 29. Conclusion

The final architecture separates the system into clear and independently maintainable components:

```text
MovieLens 32M
     ↓
Preprocessing
     ↓
Content + Collaborative Models
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
Vercel
```

This architecture provides a complete pipeline from dataset processing and machine learning through to a functional full-stack recommendation application.
