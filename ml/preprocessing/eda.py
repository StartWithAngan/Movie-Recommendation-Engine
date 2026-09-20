"""
Exploratory data analysis for MovieLens-style ratings data.

Computes real statistics from whatever data is loaded — no hardcoded or
invented numbers. Run standalone:

    python ml/preprocessing/eda.py [data_dir]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_movielens import load_movielens_1m  # noqa: E402


def run_eda(data_dir: str | Path) -> dict:
    data = load_movielens_1m(data_dir)
    movies, ratings, users = data.movies, data.ratings, data.users

    n_users = ratings["user_id"].nunique()
    n_movies = ratings["movie_id"].nunique()
    n_ratings = len(ratings)
    # Sparsity = fraction of the user-item matrix that is EMPTY.
    sparsity = 1 - (n_ratings / (n_users * n_movies))

    genre_counts = (
        movies["genres_list"].explode().value_counts()
    )

    most_rated = (
        ratings.groupby("movie_id").size().sort_values(ascending=False).head(10)
    )
    most_rated = most_rated.rename("num_ratings").reset_index().merge(
        movies[["movie_id", "title"]], on="movie_id"
    )

    per_user_counts = ratings.groupby("user_id").size()

    stats = {
        "n_users": int(n_users),
        "n_movies": int(n_movies),
        "n_ratings": int(n_ratings),
        "sparsity": round(float(sparsity), 6),
        "avg_rating": round(float(ratings["rating"].mean()), 4),
        "rating_distribution": ratings["rating"].value_counts().sort_index().to_dict(),
        "avg_ratings_per_user": round(float(per_user_counts.mean()), 2),
        "median_ratings_per_user": float(per_user_counts.median()),
        "top_genres": genre_counts.head(10).to_dict(),
        "most_rated_movies": most_rated[["title", "num_ratings"]].to_dict("records"),
    }
    return stats


def print_report(stats: dict) -> None:
    print("=" * 60)
    print("MovieLens EDA report")
    print("=" * 60)
    print(f"Users:            {stats['n_users']:,}")
    print(f"Movies:           {stats['n_movies']:,}")
    print(f"Ratings:          {stats['n_ratings']:,}")
    print(f"Sparsity:         {stats['sparsity']:.4%}  (fraction of user-item matrix that's empty)")
    print(f"Avg rating:       {stats['avg_rating']}")
    print(f"Avg ratings/user: {stats['avg_ratings_per_user']}")
    print(f"Median/user:      {stats['median_ratings_per_user']}")
    print("\nRating distribution:")
    for r, c in stats["rating_distribution"].items():
        print(f"  {r}: {c}")
    print("\nTop genres:")
    for g, c in stats["top_genres"].items():
        print(f"  {g}: {c}")
    print("\nMost-rated movies:")
    for row in stats["most_rated_movies"]:
        print(f"  {row['title']}: {row['num_ratings']} ratings")


if __name__ == "__main__":
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "ml/data/raw/ml-1m"
    stats = run_eda(data_dir)
    print_report(stats)
