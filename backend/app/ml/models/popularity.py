"""Popularity baseline used for cold-start recommendations."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class PopularityModel:
    movie_ids: np.ndarray
    scores: np.ndarray

    def recommend(self, excluded_movie_ids: set[int] | None = None, top_k: int = 10) -> list[dict]:
        excluded = excluded_movie_ids or set()
        results = []
        for movie_id, score in zip(self.movie_ids, self.scores):
            movie_id = int(movie_id)
            if movie_id in excluded:
                continue
            results.append({"movie_id": movie_id, "score": float(score)})
            if len(results) >= top_k:
                break
        return results


def train_popularity(
    movies: pd.DataFrame,
    ratings: pd.DataFrame,
    min_ratings: int = 50,
    exclude_index: np.ndarray | None = None,
) -> PopularityModel:
    """Train a memory-efficient popularity baseline using bincount."""
    movie_ids = movies["movie_id"].to_numpy(dtype=np.int32)
    if exclude_index is not None and len(exclude_index):
        mask = ~ratings.index.isin(exclude_index)
    else:
        mask = np.ones(len(ratings), dtype=bool)
    mids = ratings["movie_id"].to_numpy(dtype=np.int32)[mask]
    vals = ratings["rating"].to_numpy(dtype=np.float32)[mask]
    max_id = int(max(movie_ids.max(), mids.max())) + 1
    counts = np.bincount(mids, minlength=max_id).astype(np.float64)
    sums = np.bincount(mids, weights=vals, minlength=max_id).astype(np.float64)
    global_mean = float(vals.mean())
    movie_counts = counts[movie_ids]
    movie_means = np.divide(sums[movie_ids], movie_counts,
                            out=np.full(len(movie_ids), global_mean),
                            where=movie_counts > 0)
    m = float(min_ratings)
    weighted = (movie_counts / (movie_counts + m)) * movie_means + (m / (movie_counts + m)) * global_mean
    order = np.argsort(-weighted)
    return PopularityModel(movie_ids=movie_ids[order], scores=weighted[order])
