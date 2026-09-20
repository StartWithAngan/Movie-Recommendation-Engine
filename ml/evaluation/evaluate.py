"""Evaluation utilities for leakage-safe recommender evaluation."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


def train_test_split_per_user(
    ratings: pd.DataFrame,
    test_frac: float = 0.2,
    min_ratings: int = 5,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Chronological leave-one-out split."""
    test_idx = temporal_holdout_indices(ratings, min_ratings=min_ratings)
    test_mask = ratings.index.isin(test_idx)
    return (
        ratings.loc[~test_mask].reset_index(drop=True),
        ratings.loc[test_mask].reset_index(drop=True),
    )


def temporal_holdout_indices(
    ratings: pd.DataFrame,
    min_ratings: int = 5,
) -> np.ndarray:
    """Return row indices for each eligible user's latest interaction."""
    counts = ratings.groupby("user_id")["movie_id"].transform("size")
    eligible = ratings.loc[counts >= min_ratings]

    if eligible.empty:
        return np.array([], dtype=np.int64)

    return eligible.groupby("user_id")["timestamp"].idxmax().to_numpy(
        dtype=np.int64
    )


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(
        np.sqrt(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2))
    )


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(
        np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred)))
    )


def precision_recall_at_k(
    recommended: list[int],
    relevant: set[int],
    k: int,
) -> tuple[float, float]:
    """Calculate Precision@K and Recall@K."""
    top_k = recommended[:k]

    if not top_k:
        return 0.0, 0.0

    hits = len(set(top_k) & relevant)

    precision = hits / len(top_k)
    recall = hits / len(relevant) if relevant else 0.0

    return precision, recall


@dataclass
class EvalResult:
    name: str
    rmse: float | None = None
    mae: float | None = None
    precision_at_k: float | None = None
    recall_at_k: float | None = None

    def as_row(self) -> dict:
        return {
            "model": self.name,
            "RMSE": round(self.rmse, 4)
            if self.rmse is not None
            else None,
            "MAE": round(self.mae, 4)
            if self.mae is not None
            else None,
            "Precision@K": round(self.precision_at_k, 4)
            if self.precision_at_k is not None
            else None,
            "Recall@K": round(self.recall_at_k, 4)
            if self.recall_at_k is not None
            else None,
        }


def _sample_users(
    test: pd.DataFrame,
    max_users: int,
    random_state: int,
) -> pd.Series:
    """Select a deterministic user sample shared by evaluations."""
    users = test["user_id"].drop_duplicates()

    if len(users) > max_users:
        users = users.sample(max_users, random_state=random_state)

    return users


def _build_train_history(
    train: pd.DataFrame,
    users: pd.Series,
    excluded_indices: np.ndarray | None = None,
) -> dict[int, set[int]]:
    """Build movie history for sampled users."""
    train_work = train

    if excluded_indices is not None and len(excluded_indices):
        train_work = train_work.loc[
            ~train_work.index.isin(excluded_indices)
        ]

    train_work = train_work[
        train_work["user_id"].isin(users)
    ][["user_id", "movie_id"]]

    return train_work.groupby("user_id")["movie_id"].agg(set).to_dict()


def evaluate_popularity_baseline(
    train: pd.DataFrame,
    test: pd.DataFrame,
    k: int = 10,
    relevance_threshold: float = 4.0,
    max_users: int = 1000,
    random_state: int = 42,
    excluded_indices: np.ndarray | None = None,
) -> EvalResult:
    """Evaluate popularity ranking."""
    if excluded_indices is not None and len(excluded_indices):
        train_work = train.loc[
            ~train.index.isin(excluded_indices),
            ["user_id", "movie_id"],
        ]
    else:
        train_work = train[["user_id", "movie_id"]]

    popularity = (
        train_work.groupby("movie_id")
        .size()
        .sort_values(ascending=False)
    )

    ranked_all = popularity.index.to_numpy()

    users = _sample_users(test, max_users, random_state)

    sampled = test[test["user_id"].isin(users)]
    train_by_user = _build_train_history(
        train,
        users,
        excluded_indices,
    )

    precisions = []
    recalls = []

    for user_id, group in sampled.groupby("user_id"):
        rated_in_train = train_by_user.get(user_id, set())

        recommended = [
            int(movie_id)
            for movie_id in ranked_all
            if int(movie_id) not in rated_in_train
        ][:k]

        relevant = set(
            group.loc[
                group["rating"] >= relevance_threshold,
                "movie_id",
            ].astype(int)
        )

        if not relevant:
            continue

        precision, recall = precision_recall_at_k(
            recommended,
            relevant,
            k,
        )

        precisions.append(precision)
        recalls.append(recall)

    return EvalResult(
        name="Popularity Baseline",
        precision_at_k=float(np.mean(precisions))
        if precisions
        else 0.0,
        recall_at_k=float(np.mean(recalls))
        if recalls
        else 0.0,
    )


def evaluate_content_based(
    model,
    train: pd.DataFrame,
    test: pd.DataFrame,
    k: int = 10,
    relevance_threshold: float = 4.0,
    max_users: int = 200,
    random_state: int = 42,
    excluded_indices: np.ndarray | None = None,
) -> EvalResult:
    """
    Evaluate content-based recommendations.

    For each sampled user, highly-rated training movies are used as
    the user's content profile. Recommendations are the movies with
    highest average similarity to those liked movies.
    """
    users = _sample_users(test, max_users, random_state)

    sampled = test[test["user_id"].isin(users)]
    train_history = _build_train_history(
        train,
        users,
        excluded_indices,
    )

    # Ratings are needed to determine which training movies the user liked.
    train_work = train

    if excluded_indices is not None and len(excluded_indices):
        train_work = train_work.loc[
            ~train_work.index.isin(excluded_indices)
        ]

    train_work = train_work[
        train_work["user_id"].isin(users)
    ]

    liked_by_user = (
        train_work[train_work["rating"] >= relevance_threshold]
        .groupby("user_id")["movie_id"]
        .apply(lambda x: [int(v) for v in x])
        .to_dict()
    )

    precisions = []
    recalls = []

    for user_id, group in sampled.groupby("user_id"):
        liked_movies = liked_by_user.get(user_id, [])

        if not liked_movies:
            continue

        scores: dict[int, list[float]] = {}

        for movie_id in liked_movies:
            if movie_id not in model.movie_id_to_row:
                continue

            similar = model.score_all(movie_id)

            for candidate_id, score in similar.items():
                scores.setdefault(candidate_id, []).append(score)

        if not scores:
            continue

        averaged_scores = {
            movie_id: float(np.mean(values))
            for movie_id, values in scores.items()
        }

        rated = train_history.get(user_id, set())

        recommended = [
            movie_id
            for movie_id, _ in sorted(
                averaged_scores.items(),
                key=lambda x: (-x[1], x[0]),
            )
            if movie_id not in rated
        ][:k]

        relevant = set(
            group.loc[
                group["rating"] >= relevance_threshold,
                "movie_id",
            ].astype(int)
        )

        if not relevant:
            continue

        precision, recall = precision_recall_at_k(
            recommended,
            relevant,
            k,
        )

        precisions.append(precision)
        recalls.append(recall)

    return EvalResult(
        name="Content-Based",
        precision_at_k=float(np.mean(precisions))
        if precisions
        else 0.0,
        recall_at_k=float(np.mean(recalls))
        if recalls
        else 0.0,
    )


def evaluate_collaborative(
    model,
    train: pd.DataFrame,
    test: pd.DataFrame,
    k: int = 10,
    relevance_threshold: float = 4.0,
    max_users: int = 200,
    random_state: int = 42,
    excluded_indices: np.ndarray | None = None,
) -> EvalResult:
    """Evaluate collaborative filtering."""
    known = (
        test["user_id"].isin(model.user_id_to_row)
        & test["movie_id"].isin(model.movie_id_to_col)
    )

    eval_test = test.loc[known]

    if eval_test.empty:
        return EvalResult(
            name="Collaborative Filtering (SVD)"
        )

    uidx = eval_test["user_id"].map(
        model.user_id_to_row
    ).to_numpy()

    iidx = eval_test["movie_id"].map(
        model.movie_id_to_col
    ).to_numpy()

    preds = (
        model.global_mean
        + np.sum(
            model.user_factors[uidx]
            * model.item_factors[iidx],
            axis=1,
        )
    )

    preds = np.clip(preds, 1.0, 5.0)

    rmse_val = rmse(
        eval_test["rating"].to_numpy(),
        preds,
    )

    mae_val = mae(
        eval_test["rating"].to_numpy(),
        preds,
    )

    users = _sample_users(
        eval_test,
        max_users,
        random_state,
    )

    train_by_user = _build_train_history(
        train,
        users,
        excluded_indices,
    )

    test_sample = eval_test[
        eval_test["user_id"].isin(users)
    ]

    precisions = []
    recalls = []

    for user_id, group in test_sample.groupby("user_id"):
        row = model.user_id_to_row[int(user_id)]

        scores = (
            model.global_mean
            + model.item_factors
            @ model.user_factors[row]
        )

        rated = train_by_user.get(user_id, set())

        if rated:
            cols = [
                model.movie_id_to_col[movie_id]
                for movie_id in rated
                if movie_id in model.movie_id_to_col
            ]

            scores[cols] = -np.inf

        kk = min(k, len(scores))

        top_idx = np.argpartition(
            -scores,
            kk - 1,
        )[:kk]

        top_idx = top_idx[
            np.argsort(-scores[top_idx])
        ]

        recommended = [
            int(model.movie_ids[i])
            for i in top_idx
        ]

        relevant = set(
            group.loc[
                group["rating"] >= relevance_threshold,
                "movie_id",
            ].astype(int)
        )

        if not relevant:
            continue

        precision, recall = precision_recall_at_k(
            recommended,
            relevant,
            k,
        )

        precisions.append(precision)
        recalls.append(recall)

    return EvalResult(
        name="Collaborative Filtering (SVD)",
        rmse=rmse_val,
        mae=mae_val,
        precision_at_k=float(np.mean(precisions))
        if precisions
        else 0.0,
        recall_at_k=float(np.mean(recalls))
        if recalls
        else 0.0,
    )


def evaluate_hybrid(
    hybrid_model,
    train: pd.DataFrame,
    test: pd.DataFrame,
    k: int = 10,
    relevance_threshold: float = 4.0,
    max_users: int = 200,
    random_state: int = 42,
    excluded_indices: np.ndarray | None = None,
) -> EvalResult:
    """
    Evaluate the hybrid recommender.

    The user's training ratings are used to create:
      - liked movies for the content signal
      - collaborative user representation

    The held-out latest interaction is never used to construct the
    recommendation.
    """
    users = _sample_users(test, max_users, random_state)

    sampled = test[test["user_id"].isin(users)]

    train_work = train

    if excluded_indices is not None and len(excluded_indices):
        train_work = train_work.loc[
            ~train_work.index.isin(excluded_indices)
        ]

    train_work = train_work[
        train_work["user_id"].isin(users)
    ]

    precisions = []
    recalls = []

    for user_id, group in sampled.groupby("user_id"):
        user_history = train_work[
            train_work["user_id"] == user_id
        ]

        rated_movie_ids = set(
            user_history["movie_id"].astype(int)
        )

        liked_movie_ids = (
            user_history.loc[
                user_history["rating"] >= relevance_threshold,
                "movie_id",
            ]
            .astype(int)
            .tolist()
        )

        if not liked_movie_ids:
            continue

        recommendations = hybrid_model.recommend_for_user(
            int(user_id),
            rated_movie_ids,
            liked_movie_ids,
            top_k=k,
        )

        recommended = [
            int(item["movie_id"])
            for item in recommendations
        ]

        relevant = set(
            group.loc[
                group["rating"] >= relevance_threshold,
                "movie_id",
            ].astype(int)
        )

        if not relevant:
            continue

        precision, recall = precision_recall_at_k(
            recommended,
            relevant,
            k,
        )

        precisions.append(precision)
        recalls.append(recall)

    return EvalResult(
        name="Hybrid",
        precision_at_k=float(np.mean(precisions))
        if precisions
        else 0.0,
        recall_at_k=float(np.mean(recalls))
        if recalls
        else 0.0,
    )