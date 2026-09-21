"""
Collaborative filtering via sparse low-rank SVD matrix factorization.

Why sparse SVD over user-based or item-based neighborhood CF:
MovieLens 1M has ~6,000 users x ~4,000 movies with >95% sparsity. A dense
neighborhood approach (computing all pairwise user or item similarities)
is O(n^2) in whichever axis you pick and doesn't generalize well at this
sparsity. Sparse SVD factorizes the rating matrix into low-rank
user and item latent factor matrices, which handles sparsity gracefully,
is fast with scipy.sparse, and is the standard practical baseline for
matrix-factorization-based CF (a simplified stand-in for the SVD++ /
funk-SVD family used in production recommenders).
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from sklearn.linear_model import Ridge


@dataclass
class CollaborativeModel:
    user_ids: np.ndarray            # row index -> user_id
    movie_ids: np.ndarray           # column index -> movie_id
    user_factors: np.ndarray        # n_users x k
    item_factors: np.ndarray        # n_movies x k
    global_mean: float
    user_id_to_row: dict
    movie_id_to_col: dict

    def predict(self, user_id: int, movie_id: int) -> float:
        """Predicted rating for a (user, movie) pair, clipped to [1, 5]."""
        if user_id not in self.user_id_to_row or movie_id not in self.movie_id_to_col:
            return self.global_mean  # cold-start fallback
        u = self.user_id_to_row[user_id]
        i = self.movie_id_to_col[movie_id]
        pred = self.global_mean + float(np.dot(self.user_factors[u], self.item_factors[i]))
        return float(np.clip(pred, 1.0, 5.0))

    def infer_user_factors(self, ratings: pd.DataFrame, alpha: float = 1.0) -> np.ndarray | None:
        """Infer a new app user's latent vector from their ratings (fold-in)."""
        known = ratings[ratings["movie_id"].isin(self.movie_id_to_col)].copy()
        if known.empty:
            return None
        cols = [self.movie_id_to_col[int(mid)] for mid in known["movie_id"]]
        X = self.item_factors[cols]
        y = known["rating"].to_numpy(dtype=float) - self.global_mean
        model = Ridge(alpha=alpha, fit_intercept=False)
        model.fit(X, y)
        return model.coef_.astype(float)

    def recommend_for_ratings(
        self,
        ratings: pd.DataFrame,
        rated_movie_ids: set[int],
        top_k: int = 10,
    ) -> list[dict]:
        """Recommend for an arbitrary application user using fold-in."""
        factors = self.infer_user_factors(ratings)
        if factors is None:
            return []
        scores = self.global_mean + self.item_factors @ factors
        ranked_cols = np.argsort(-scores)
        results = []
        for col in ranked_cols:
            mid = int(self.movie_ids[col])
            if mid in rated_movie_ids:
                continue
            results.append(
                {"movie_id": mid, "score": round(float(np.clip(scores[col], 1, 5)), 4)}
            )
            if len(results) >= top_k:
                break
        return results

    def recommend_for_user(self, user_id: int, rated_movie_ids: set[int], top_k: int = 10) -> list[dict]:
        """Top-k movies for a known user, excluding already-rated movies."""
        if user_id not in self.user_id_to_row:
            return []  # cold-start: caller should fall back to content-based/popularity

        u = self.user_id_to_row[user_id]
        scores = self.global_mean + self.item_factors @ self.user_factors[u]

        ranked_cols = np.argsort(-scores)
        results = []
        for col in ranked_cols:
            mid = int(self.movie_ids[col])
            if mid in rated_movie_ids:
                continue
            results.append({"movie_id": mid, "score": round(float(np.clip(scores[col], 1, 5)), 4)})
            if len(results) >= top_k:
                break
        return results

    def score_all_for_user(self, user_id: int) -> dict:
        """movie_id -> predicted score, for use by the hybrid ranker."""
        if user_id not in self.user_id_to_row:
            return {}
        u = self.user_id_to_row[user_id]
        scores = self.global_mean + self.item_factors @ self.user_factors[u]
        return {int(mid): float(np.clip(s, 1, 5)) for mid, s in zip(self.movie_ids, scores)}


def train_collaborative(
    ratings: pd.DataFrame, n_factors: int = 12, random_state: int = 42,
    maxiter: int = 300, tol: float = 1e-4, exclude_index: np.ndarray | None = None
) -> CollaborativeModel:
    """Train a memory-conscious sparse matrix-factorization model.

    Uses SciPy's sparse ``svds`` instead of sklearn's randomized SVD. The
    latter can require several temporary dense work arrays at MovieLens 32M
    scale. ``svds`` works directly on the CSR matrix and returns only the
    requested low-rank factors.
    """
    if exclude_index is not None and len(exclude_index):
        mask = ~ratings.index.isin(exclude_index)
    else:
        mask = np.ones(len(ratings), dtype=bool)
    user_values = ratings["user_id"].to_numpy(dtype=np.int32)[mask]
    movie_values = ratings["movie_id"].to_numpy(dtype=np.int32)[mask]
    rating_values = ratings["rating"].to_numpy(dtype=np.float32)[mask]
    user_ids, user_codes = np.unique(user_values, return_inverse=True)
    movie_ids, movie_codes = np.unique(movie_values, return_inverse=True)
    user_id_to_row = {int(uid): i for i, uid in enumerate(user_ids)}
    movie_id_to_col = {int(mid): i for i, mid in enumerate(movie_ids)}

    global_mean = float(rating_values.mean())
    vals = rating_values - np.float32(global_mean)
    matrix = csr_matrix((vals, (user_codes, movie_codes)),
                        shape=(len(user_ids), len(movie_ids)), dtype=np.float32)

    k = min(int(n_factors), min(matrix.shape) - 1)
    k = max(k, 1)
    u, singular_values, vt = svds(matrix, k=k, which="LM", tol=tol, maxiter=maxiter, random_state=random_state)
    order = np.argsort(singular_values)[::-1]
    singular_values = singular_values[order]
    u = u[:, order]
    vt = vt[order, :]

    # Fold singular values into user factors so dot(user_factors, item_factors)
    # reconstructs the centered matrix approximation.
    user_factors = (u * singular_values[np.newaxis, :]).astype(np.float32)
    item_factors = vt.T.astype(np.float32)

    return CollaborativeModel(
        user_ids=user_ids, movie_ids=movie_ids,
        user_factors=user_factors, item_factors=item_factors,
        global_mean=global_mean, user_id_to_row=user_id_to_row,
        movie_id_to_col=movie_id_to_col,
    )
