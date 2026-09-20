"""Streaming EDA for MovieLens 32M.

Usage:
    python -m ml.preprocessing.eda_32m ml/data/raw/ml-32m
"""
from pathlib import Path
import json
import pandas as pd


def analyze(data_dir: str | Path) -> dict:
    data_dir = Path(data_dir)
    movies = pd.read_csv(data_dir / "movies.csv")
    rating_count = 0
    rating_sum = 0.0
    rating_sq_sum = 0.0
    user_ids = set()
    min_ts = max_ts = None

    for chunk in pd.read_csv(
        data_dir / "ratings.csv",
        usecols=["userId", "movieId", "rating", "timestamp"],
        dtype={"userId": "int32", "movieId": "int32", "rating": "float32", "timestamp": "int64"},
        chunksize=1_000_000,
    ):
        rating_count += len(chunk)
        rating_sum += float(chunk.rating.sum())
        rating_sq_sum += float((chunk.rating.astype("float64") ** 2).sum())
        user_ids.update(chunk.userId.unique().tolist())
        cmin, cmax = int(chunk.timestamp.min()), int(chunk.timestamp.max())
        min_ts = cmin if min_ts is None else min(min_ts, cmin)
        max_ts = cmax if max_ts is None else max(max_ts, cmax)

    mean = rating_sum / rating_count
    variance = max(0.0, rating_sq_sum / rating_count - mean ** 2)
    return {
        "movies": int(len(movies)),
        "ratings": rating_count,
        "users": len(user_ids),
        "mean_rating": round(mean, 4),
        "rating_std": round(variance ** 0.5, 4),
        "min_timestamp": min_ts,
        "max_timestamp": max_ts,
        "genre_count": int(movies.genres.fillna("").str.split("|").explode().nunique()),
    }


if __name__ == "__main__":
    import sys
    print(json.dumps(analyze(sys.argv[1] if len(sys.argv) > 1 else "ml/data/raw/ml-32m"), indent=2))
