# Viva Questions

### 1. What is a recommendation system?
A system that predicts which items a user is likely to prefer, using their past behavior, item attributes, or the behavior of similar users.

### 2. What is content-based filtering?
Recommending items similar to ones the user already liked, based on item attributes (here, movie genres).

### 3. What is collaborative filtering?
Recommending items based on patterns across many users' interactions, without needing item metadata — "users like you also liked this."

### 4. What is hybrid recommendation, and why use it here?
Combining content-based and collaborative scores. It's used here because each compensates for the other's weakness: content-based works for new movies (no rating history needed), collaborative captures taste patterns content alone can't see.

### 5. What is cosine similarity, and why use it for movies?
The cosine of the angle between two vectors, in [0,1] for non-negative vectors. It measures direction (proportion of shared genres) rather than magnitude, so a movie with fewer genres isn't penalized for having a "smaller" vector.

### 6. What is TF-IDF, and why apply it to genres instead of a simple one-hot encoding?
Term Frequency–Inverse Document Frequency weights terms by how distinctive they are. Applied to genres, it downweights very common genres (e.g. "Drama") relative to rarer, more distinguishing ones, which one-hot encoding cannot do.

### 7. What is matrix factorization?
Decomposing the sparse user-item rating matrix into two smaller matrices (user factors and item factors) whose product approximates the known ratings — capturing latent taste dimensions.

### 8. Why TruncatedSVD specifically?
It works directly on sparse matrices (scipy.sparse), doesn't require centering to dense form, and is a standard, explainable baseline for matrix-factorization CF at this dataset scale.

### 9. What is the cold-start problem?
The inability to make good recommendations for a new user (no rating history) or a new item (no interaction history).

### 10. How does this project handle a new user?
Falls back to content-based similarity to movies the user explicitly selects/rates during onboarding, since collaborative filtering has no signal for them yet.

### 11. How does this project handle a new movie?
Falls back to content-based similarity via genre metadata, since no user has rated it yet for collaborative signal.

### 12. What is sparsity, and why does it matter?
The fraction of the user-item matrix with no rating. High sparsity (typically >95% for MovieLens) is why naive dense similarity computations are impractical and why factorization-based approaches are preferred.

### 13. Why MovieLens 1M for this project?
It's a standard, well-documented, appropriately-sized academic benchmark (1M ratings, ~6,000 users, ~4,000 movies) — large enough to be meaningful, small enough to train and evaluate quickly.

### 14. What is RMSE, and what does it measure here?
Root Mean Squared Error — the square root of the average squared difference between predicted and actual ratings. Penalizes large errors more than MAE.

### 15. What is MAE, and how does it differ from RMSE?
Mean Absolute Error — the average absolute difference between predicted and actual ratings. Unlike RMSE, it weights all errors linearly, so it's less sensitive to outliers.

### 16. What is Precision@K?
Of the top-K recommended items, the fraction that the user actually rated highly (relevant). Measures recommendation quality, not rating-prediction accuracy.

### 17. What is Recall@K?
Of all items the user actually rated highly, the fraction that appeared in the top-K recommendations.

### 18. Why use ranking metrics (Precision@K/Recall@K) in addition to RMSE/MAE?
RMSE/MAE only evaluate rating-prediction accuracy; they say nothing about whether the *ranked list* the user actually sees is good. A model can have low RMSE but still rank irrelevant items highly.

### 19. How is data leakage avoided in evaluation?
Using a per-user train/test split — every user has training history, and their held-out test ratings are never used when generating that same user's recommendations.

### 20. Why per-user split instead of a global random split?
A global random split can leave some users entirely in the test set with zero training history, making it impossible to evaluate them fairly and effectively testing an unsolvable cold-start case as if it were a normal case.

### 21. What is the popularity baseline, and why include it?
Recommending the same globally most-rated movies to everyone. It's included so the ML-based approaches can be shown to outperform a trivial non-personalized method — without it, there's no evidence the ML adds value.

### 22. Why normalize scores before combining them in the hybrid model?
Content similarity is in [0,1] and predicted ratings are in [1,5]; combining unnormalized would let the collaborative term dominate purely due to its larger numeric range, not because it's more informative. The hybrid therefore normalizes each component to [0,1] first. It uses **rank normalization** (`x' = (rank(x)-1)/(n-1)`) rather than min-max rescaling because per-user collaborative predictions are tightly clustered around the global mean; min-max rescaling would squash most candidates onto nearly the same value, making the collaborative signal effectively invisible in the final ranking. Ranking by fractional percentile preserves each model's ordering, which is what drives recommendation quality.

### 23. How are content_weight and collaborative_weight chosen?
They're configurable parameters (default 0.4/0.6) rather than fixed constants, so they can be tuned based on evaluation results rather than guessed.

### 24. How does the system explain a recommendation?
Each recommendation carries a `reason` field — e.g. "Similar to movies you rated highly" or "Users with similar rating patterns also liked this movie" — chosen by comparing the relative contribution of the content vs. collaborative score.

### 25. Why are model artifacts trained offline and persisted, rather than computed per request?
Recomputing a similarity matrix or refactorizing the rating matrix on every API call would be far too slow for a responsive UI; training is done once via the pipeline and the backend loads the resulting `.pkl` files at startup.

### 26. What are the current limitations of this system?
It uses genres only for content-based features (no plot/cast text), the collaborative model doesn't yet map real app user accounts onto MovieLens's training user IDs, and there's no background retraining as new ratings arrive.

### 27. How would you extend the content-based model?
Add richer text (plot summaries, cast, director) via full TF-IDF over natural-language fields, not just genre tokens.

### 28. How would you address the app-user-to-collaborative-model mapping limitation?
Periodically retrain the collaborative model including real app users' ratings (not just the static MovieLens matrix), assigning each app user a stable row.

### 29. Why FastAPI instead of Flask/Django for the backend?
Native async support (matches the async Mongo driver), Pydantic-based validation, and automatic OpenAPI docs — reduces boilerplate for a REST-first ML backend.

### 30. Why JWT instead of session-based auth?
Stateless — no server-side session store needed, which fits a decoupled frontend/backend architecture deployed to separate platforms (Vercel + Render).
