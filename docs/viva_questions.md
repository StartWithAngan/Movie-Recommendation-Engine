Next, let’s finish the documentation with **`docs/viva_questions.md`**.

Replace the entire file with:

````markdown
# Viva Questions — Movie Recommendation Engine Using Machine Learning

## 1. Project Overview

### Q1. What is the title of your project?

**Answer:**  
The title of the project is **Movie Recommendation Engine Using Machine Learning**.

---

### Q2. What is the main objective of the project?

**Answer:**  
The main objective is to build a personalized movie recommendation system that recommends movies to users based on movie content, user-rating patterns, and overall movie popularity.

The system combines:

- Content-based filtering
- Collaborative filtering
- Popularity-based recommendation
- Hybrid ranking
- Cold-start handling
- Recommendation explanations

---

### Q3. Why did you choose this project?

**Answer:**  
Movie recommendation is a practical application of machine learning and information retrieval. Streaming platforms contain thousands of movies, making it difficult for users to discover relevant content.

A recommendation system can reduce this discovery problem by ranking movies according to predicted user relevance.

---

# 2. Dataset

### Q4. Which dataset did you use?

**Answer:**  
The project uses the **MovieLens 32M** dataset.

---

### Q5. How large is the dataset?

**Answer:**

The dataset contains:

- **87,585 movies**
- **32,000,204 ratings**
- **200,948 users**
- **20 genres**

The average rating is approximately **3.5404**.

---

### Q6. Why did you use MovieLens?

**Answer:**  
MovieLens provides a large collection of real user-movie rating interactions along with movie metadata.

This makes it suitable for experimenting with both:

- Content-based recommendation
- Collaborative filtering

---

### Q7. What information is available for movies?

**Answer:**  
The dataset contains movie titles and genres in `movies.csv`.

Additional files provide ratings, tags, and external movie identifiers.

---

# 3. Recommendation Systems

### Q8. What is a recommendation system?

**Answer:**  
A recommendation system is a software system that predicts or ranks items that may be relevant to a user based on available information about the user, items, and previous interactions.

In this project, the items are movies.

---

### Q9. What recommendation techniques did you implement?

**Answer:**  

The project implements:

1. Popularity-based recommendation
2. Content-based recommendation
3. Collaborative filtering using sparse SVD
4. Hybrid recommendation

---

### Q10. What is content-based filtering?

**Answer:**  
Content-based filtering recommends items that are similar to items a user has previously liked.

In this project, movie titles and genres are converted into TF-IDF feature representations, and cosine similarity is used to measure movie similarity.

---

### Q11. What is TF-IDF?

**Answer:**  
TF-IDF stands for **Term Frequency-Inverse Document Frequency**.

It assigns importance to terms based on:

- How frequently a term occurs in a document
- How common or rare that term is across the collection

In this project, it is used to convert movie metadata into numerical feature vectors.

---

### Q12. What is cosine similarity?

**Answer:**  
Cosine similarity measures the similarity between two vectors based on the angle between them.

The formula is:

\[
\text{Cosine Similarity}(A,B)
=
\frac{A \cdot B}
{\|A\|\|B\|}
\]

A larger cosine similarity indicates that the vectors are more similar.

---

### Q13. What is collaborative filtering?

**Answer:**  
Collaborative filtering uses user-item interaction information rather than relying only on item metadata.

The basic idea is that users with similar rating patterns may have similar preferences.

---

### Q14. What type of collaborative filtering did you use?

**Answer:**  
The project uses a latent-factor collaborative filtering approach based on **sparse Singular Value Decomposition (SVD)**.

---

### Q15. Why use sparse matrices?

**Answer:**  
A user-movie matrix can become extremely large because there are many possible user-movie combinations.

Most users have rated only a small portion of all available movies, so most matrix entries are empty.

Sparse matrices store only the meaningful entries and therefore reduce memory usage.

---

### Q16. How many latent factors are used?

**Answer:**  
The final collaborative model uses **12 latent factors**.

These factors provide a lower-dimensional representation of users and movies.

---

### Q17. What is the purpose of latent factors?

**Answer:**  
Latent factors represent hidden preference patterns in the rating data.

For example, a latent factor may indirectly capture preference patterns related to certain types of movies, although the factors are learned mathematically rather than manually assigned human meanings.

---

# 4. Hybrid Recommendation

### Q18. Why did you combine multiple recommendation models?

**Answer:**  
Different recommendation approaches capture different types of information.

- Content-based filtering uses movie characteristics.
- Collaborative filtering uses rating behavior.
- Popularity provides a useful baseline and fallback.

Combining these signals can provide a more balanced recommendation strategy.

---

### Q19. How does your hybrid recommender work?

**Answer:**  
The hybrid recommender obtains scores from the content and collaborative models.

Instead of directly combining their raw scores, the scores are converted into rank/percentile-based normalized values.

The normalized signals are then combined to produce the final recommendation ranking.

---

### Q20. Why did you use rank normalization?

**Answer:**  
The content and collaborative models produce scores on different scales.

Directly combining raw scores can cause one model to dominate the other.

Rank normalization converts the scores into comparable relative rankings, allowing both recommendation signals to contribute to the final ranking.

---

### Q21. What problem did you encounter with the original hybrid approach?

**Answer:**  
The initial hybrid implementation used min-max normalization.

The collaborative scores became almost constant for a particular recommendation set, causing the hybrid results to be dominated by the content signal.

Rank-based normalization was introduced so that both signals contributed more meaningfully to the final ranking.

---

# 5. Cold Start

### Q22. What is the cold-start problem?

**Answer:**  
Cold start occurs when the system has insufficient information about a new user or item to generate personalized recommendations.

For example, a newly registered user has no rating history.

---

### Q23. How do you handle a new user?

**Answer:**  
The system uses popularity-based recommendations for users without sufficient interaction history.

After the user provides ratings, those ratings can be used to generate personalized recommendations.

---

### Q24. How does personalization work for application users?

**Answer:**  
Application users are separate from the original MovieLens users.

When an application user submits ratings, the system uses those ratings to infer a user representation in the learned collaborative latent space.

This representation is then used to generate personalized recommendations.

---

# 6. Evaluation

### Q25. How did you evaluate the recommendation system?

**Answer:**  
The evaluation uses a chronological train/test split.

The earlier interactions are used for training, while later interactions are used as the test set.

This better represents future recommendation behavior.

---

### Q26. What metrics did you use?

**Answer:**  

For recommendation ranking:

- Precision@10
- Recall@10

For collaborative rating prediction:

- RMSE
- MAE

---

### Q27. What is Precision@10?

**Answer:**  
Precision@10 measures the proportion of the top 10 recommended movies that are relevant according to the evaluation criterion.

\[
Precision@10 =
\frac{\text{Relevant recommendations in top 10}}
{10}
\]

---

### Q28. What is Recall@10?

**Answer:**  
Recall@10 measures how much of the relevant test-item set was successfully retrieved within the top 10 recommendations.

\[
Recall@10 =
\frac{\text{Relevant recommendations in top 10}}
{\text{Total relevant items}}
\]

---

### Q29. What is RMSE?

**Answer:**  
RMSE stands for Root Mean Squared Error.

It measures the difference between predicted and actual ratings.

\[
RMSE =
\sqrt{
\frac{1}{n}
\sum_{i=1}^{n}(y_i-\hat{y_i})^2
}
\]

Lower RMSE indicates smaller prediction errors.

---

### Q30. What is MAE?

**Answer:**  
MAE stands for Mean Absolute Error.

It measures the average absolute difference between predicted and actual ratings.

\[
MAE =
\frac{1}{n}
\sum_{i=1}^{n}|y_i-\hat{y_i}|
\]

---

# 7. Final Results

### Q31. What were the final evaluation results?

**Answer:**

| Model | Precision@10 | Recall@10 | RMSE | MAE |
|---|---:|---:|---:|---:|
| Popularity | 0.0025 | 0.0246 | — | — |
| Content-Based | 0.0016 | 0.0164 | — | — |
| Collaborative SVD | 0.0106 | 0.1057 | 0.9819 | 0.8040 |
| Hybrid | 0.0049 | 0.0492 | — | — |

These results are from the project's final chronological evaluation.

---

### Q32. Why does the collaborative model have RMSE and MAE while the other ranking models do not?

**Answer:**  
RMSE and MAE are rating-prediction metrics.

The collaborative model explicitly predicts user-rating values, so these metrics can be calculated directly.

The content and hybrid components are primarily ranking systems, so Precision@10 and Recall@10 are used for their evaluation.

---

### Q33. Why is the hybrid model not simply the highest-scoring model?

**Answer:**  
The purpose of the hybrid model is to combine different recommendation signals rather than optimize a single metric in isolation.

Its ranking combines content and collaborative information, while the collaborative component itself has a different objective and scoring behavior.

The evaluation metrics should therefore be interpreted according to the role of each component.

---

# 8. Backend

### Q34. Which backend framework did you use?

**Answer:**  
The backend is implemented using **FastAPI**.

---

### Q35. Why did you use FastAPI?

**Answer:**  
FastAPI provides:

- Python-based API development
- Automatic request validation
- Type hints
- Fast asynchronous support
- Easy integration with Python machine-learning components

It also fits naturally with the Python-based ML pipeline.

---

### Q36. What database did you use?

**Answer:**  
The application uses **MongoDB**.

MongoDB stores application-level information such as:

- Users
- Authentication information
- User ratings
- Application data

---

### Q37. Why use MongoDB?

**Answer:**  
MongoDB provides a document-oriented data model that works well for application data and integrates easily with the FastAPI backend.

It is used separately from the offline MovieLens training data.

---

# 9. Authentication

### Q38. How does authentication work?

**Answer:**  
The application uses JWT-based authentication.

After successful login, the backend generates an access token.

The token is then used to authenticate protected API requests.

---

### Q39. Why are passwords not stored directly?

**Answer:**  
Passwords should not be stored as plain text.

The application uses password hashing so that the stored representation cannot directly reveal the original password.

---

# 10. API

### Q40. What are some important API endpoints?

**Answer:**  

Examples include:

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me

GET  /api/movies
GET  /api/movies/search

GET  /api/recommendations
GET  /api/recommendations/similar/{movie_id}

POST /api/ratings
````

These endpoints support authentication, movie discovery, recommendations, similar-movie functionality, and user ratings.

---

# 11. Frontend

### Q41. Which frontend technology did you use?

**Answer:**
The frontend uses:

* Next.js
* React
* TypeScript
* Tailwind CSS

---

### Q42. What does the frontend do?

**Answer:**
The frontend provides the user interface for:

* Registration and login
* Browsing movies
* Searching movies
* Viewing recommendations
* Viewing similar movies
* Rating movies
* Receiving personalized recommendations

---

# 12. Deployment

### Q43. How is the application deployed?

**Answer:**
The project is deployed using **Vercel**.

The frontend is deployed as a Next.js application and the FastAPI backend is exposed through the project's `/api` routing configuration.

---

### Q44. Why did you use Docker?

**Answer:**
Docker provides a reproducible environment for running project services.

The project uses Docker Compose to manage local services such as MongoDB and the application containers.

---

### Q45. What is the purpose of `docker-compose.yml`?

**Answer:**
The Docker Compose configuration defines the services required for local development.

The project configuration includes:

* MongoDB
* FastAPI backend
* Next.js frontend

It also defines networking, ports, environment variables, volumes, and service dependencies.

---

# 13. Testing

### Q46. Did you perform testing?

**Answer:**
Yes.

The machine-learning test suite contains:

**13 passing tests**

The backend integration test suite contains:

**10 passing tests**

---

### Q47. What did you test in the ML layer?

**Answer:**
The ML tests cover important model behavior such as:

* Recommendation generation
* Similarity functionality
* Collaborative recommendations
* Hybrid recommendations
* Cold-start behavior
* Model-related edge cases

---

### Q48. What did you test in the backend?

**Answer:**
Backend integration tests cover application functionality such as:

* Authentication
* User operations
* Movie APIs
* Ratings
* Recommendation endpoints
* Database integration

---

# 14. Model Artifacts

### Q49. What are model artifacts?

**Answer:**
Model artifacts are saved outputs produced during the training process.

They allow the application to load trained models without retraining them every time the backend starts.

---

### Q50. What artifacts does your project generate?

**Answer:**

The final artifact directory contains:

```text
artifacts/
├── collaborative_model.pkl
├── content_similarity.pkl
├── evaluation_results.csv
├── movie_metadata.pkl
└── popularity_model.pkl
```

---

### Q51. Why save the trained models?

**Answer:**
Training a recommendation model on millions of ratings can be computationally expensive.

Saving the trained artifacts allows the production application to load the models directly and generate recommendations without repeating the complete training process.

---

# 15. Technical Questions

### Q52. What is overfitting?

**Answer:**
Overfitting occurs when a model learns the training data too closely and performs poorly on unseen data.

Using a separate test set helps evaluate how well the model generalizes.

---

### Q53. Why did you use a chronological split instead of a random split?

**Answer:**
A chronological split better represents the real recommendation scenario.

The system should learn from past interactions and recommend items that occur later.

A random split can allow information from the future to appear in training, which can make evaluation less representative of real deployment.

---

### Q54. What happens if a user has no ratings?

**Answer:**
The system uses the popularity-based recommendation strategy as a cold-start fallback.

---

### Q55. What happens after the user starts rating movies?

**Answer:**
The user's rating history becomes available to the recommendation system.

The application can then use those interactions to infer a personalized collaborative representation and combine it with other recommendation signals.

---

### Q56. Can the system recommend movies similar to a particular movie?

**Answer:**
Yes.

The content-based model calculates movie similarity using TF-IDF representations and cosine similarity.

The API exposes a similar-movie endpoint for this functionality.

---

# 16. Limitations

### Q57. What are the limitations of the project?

**Answer:**

The current system has several limitations:

* Content similarity is based primarily on available title and genre information.
* MovieLens ratings do not contain complete real-world streaming behavior.
* New movies with limited metadata or interactions can still present a cold-start challenge.
* The collaborative model is trained offline.
* The current hybrid weighting is a fixed strategy rather than a learned ranking model.
* Recommendation quality depends on the available user-rating history.

---

### Q58. How can the project be improved in the future?

**Answer:**

Possible improvements include:

* Incorporating richer movie metadata
* Adding cast, director, plot, and keyword information
* Using neural recommendation models
* Learning hybrid weights automatically
* Adding implicit-feedback signals
* Incorporating time-aware preferences
* Adding online model updates
* Improving recommendation explanations
* Adding larger-scale distributed training
* Performing more extensive hyperparameter optimization

---

# 17. Final Viva Questions

### Q59. What is the main machine-learning concept demonstrated by your project?

**Answer:**
The project demonstrates how multiple machine-learning recommendation techniques can be combined to solve a real-world personalization problem.

It specifically demonstrates:

* Feature representation using TF-IDF
* Similarity-based recommendation
* Matrix factorization
* Sparse linear algebra
* Ranking
* Evaluation metrics
* Cold-start handling
* Hybrid recommendation

---

### Q60. What is the most important difference between content-based and collaborative filtering?

**Answer:**

**Content-based filtering** focuses on item characteristics.

**Collaborative filtering** focuses on user-item interaction patterns.

For example:

```text
Content-Based
Movie metadata → Similar movies

Collaborative
User ratings → Learned preference patterns
```

---

### Q61. Why is a hybrid system useful?

**Answer:**
A hybrid system can combine information from multiple recommendation approaches.

Content information can help when item characteristics are important, while collaborative information can capture patterns that are not directly visible in movie metadata.

---

### Q62. Explain your complete project in one answer.

**Answer:**

The project is a machine-learning-based movie recommendation engine built using the MovieLens 32M dataset.

The system uses movie titles and genres with TF-IDF and cosine similarity for content-based recommendations. It also uses sparse SVD-based collaborative filtering to learn latent user and movie representations from more than 32 million ratings.

A popularity model provides a baseline and handles cold-start users.

The content and collaborative signals are combined using rank-based normalization to create a hybrid recommendation strategy.

The trained models are saved as artifacts and integrated into a FastAPI backend. MongoDB stores application users and their ratings, while JWT authentication protects user-specific functionality.

A Next.js, React, TypeScript, and Tailwind frontend provides movie browsing, search, ratings, authentication, and personalized recommendations.

The complete system was tested using automated ML and backend tests and deployed using Docker for local development and Vercel for production.

---

# 18. Quick Revision Sheet

## Dataset

```text
MovieLens 32M
87,585 movies
32,000,204 ratings
200,948 users
20 genres
```

## Models

```text
Content-Based
→ TF-IDF
→ Cosine Similarity

Collaborative
→ Sparse User-Movie Matrix
→ SVD
→ 12 Latent Factors

Popularity
→ Baseline / Cold Start

Hybrid
→ Rank Normalization
→ Combined Content + Collaborative Ranking
```

## Evaluation

```text
Popularity
P@10 = 0.0025
R@10 = 0.0246

Content
P@10 = 0.0016
R@10 = 0.0164

Collaborative
RMSE = 0.9819
MAE  = 0.8040
P@10 = 0.0106
R@10 = 0.1057

Hybrid
P@10 = 0.0049
R@10 = 0.0492
```

## Technology Stack

```text
Python
FastAPI
MongoDB
Next.js
React
TypeScript
Tailwind CSS
scikit-learn
SciPy
NumPy
Pandas
Docker
Vercel
Git/GitHub
```

## Testing

```text
ML Tests      → 13 passed
Backend Tests → 10 passed
```

## Key Concepts to Remember

```text
TF-IDF
Cosine Similarity
Collaborative Filtering
Matrix Factorization
SVD
Sparse Matrix
Latent Factors
Hybrid Recommendation
Rank Normalization
Cold Start
Precision@10
Recall@10
RMSE
MAE
JWT
REST API
MongoDB
Docker
```