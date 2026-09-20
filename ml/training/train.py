"""
End-to-end training pipeline.

    python -m ml.training.train [data_dir] [artifacts_dir]

Loads MovieLens data -> trains content-based + collaborative models ->
builds a hybrid recommender -> evaluates all recommendation approaches ->
saves trained artifacts to disk.

Run this offline; the FastAPI backend only ever reads the resulting
artifacts and never retrains on request.
"""

import sys
from pathlib import Path

import joblib
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.preprocessing.load_movielens import load_movielens
from ml.models.content_based import train_content_based
from ml.models.collaborative import train_collaborative
from ml.models.popularity import train_popularity
from ml.models.hybrid import HybridRecommender

from ml.evaluation.evaluate import (
    temporal_holdout_indices,
    evaluate_popularity_baseline,
    evaluate_content_based,
    evaluate_collaborative,
    evaluate_hybrid,
)


def run_training(
    data_dir: str | Path,
    artifacts_dir: str | Path,
) -> pd.DataFrame:

    artifacts_dir = Path(artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # Load MovieLens
    # ---------------------------------------------------------
    print(f"Loading data from {data_dir} ...")
    data = load_movielens(data_dir)

    # ---------------------------------------------------------
    # Chronological holdout
    # ---------------------------------------------------------
    print("Creating chronological holdout indices (leakage-safe) ...")

    test_idx = temporal_holdout_indices(data.ratings)

    test_mask = data.ratings.index.isin(test_idx)

    test = data.ratings.loc[test_mask].copy()

    # We intentionally do not create:
    #
    #     train = data.ratings.loc[~test_mask].copy()
    #
    # because that would create another ~1.8GB DataFrame for MovieLens 32M.

    data.tags = None

    print(
        f"  train: {len(data.ratings) - len(test)} ratings "
        f"| test: {len(test)} ratings"
    )

    # ---------------------------------------------------------
    # Train Content-Based model
    # ---------------------------------------------------------
    print("Training content-based model ...")

    content_model = train_content_based(
        data.movies
    )

    # ---------------------------------------------------------
    # Train Collaborative Filtering model
    # ---------------------------------------------------------
    print("Training collaborative model (sparse SVD) ...")

    collab_model = train_collaborative(
        data.ratings,
        exclude_index=test_idx,
    )

    # ---------------------------------------------------------
    # Train Popularity model
    # ---------------------------------------------------------
    print("Training popularity baseline ...")

    popularity_model = train_popularity(
        data.movies,
        data.ratings,
        exclude_index=test_idx,
    )

    # ---------------------------------------------------------
    # Save individual models
    # ---------------------------------------------------------
    print(f"Saving trained artifacts to {artifacts_dir} ...")

    joblib.dump(
        content_model,
        artifacts_dir / "content_similarity.pkl",
    )

    joblib.dump(
        collab_model,
        artifacts_dir / "collaborative_model.pkl",
    )

    joblib.dump(
        popularity_model,
        artifacts_dir / "popularity_model.pkl",
    )

    joblib.dump(
        data.movies,
        artifacts_dir / "movie_metadata.pkl",
    )

    # ---------------------------------------------------------
    # Build Hybrid model
    # ---------------------------------------------------------
    print("Building hybrid recommender ...")

    hybrid_model = HybridRecommender(
        content_model=content_model,
        collaborative_model=collab_model,
        popularity_model=popularity_model,
        content_weight=0.4,
        collaborative_weight=0.6,
    )

    # ---------------------------------------------------------
    # Evaluate all models
    # ---------------------------------------------------------
    print(
        "Evaluating all recommendation models "
        "(ranking metrics sampled to 200 users) ..."
    )

    results = [
        # -----------------------------
        # Popularity
        # -----------------------------
        evaluate_popularity_baseline(
            data.ratings,
            test,
            max_users=200,
            excluded_indices=test_idx,
        ),

        # -----------------------------
        # Content-Based
        # -----------------------------
        evaluate_content_based(
            content_model,
            data.ratings,
            test,
            max_users=200,
            excluded_indices=test_idx,
        ),

        # -----------------------------
        # Collaborative Filtering
        # -----------------------------
        evaluate_collaborative(
            collab_model,
            data.ratings,
            test,
            max_users=200,
            excluded_indices=test_idx,
        ),

        # -----------------------------
        # Hybrid
        # -----------------------------
        evaluate_hybrid(
            hybrid_model,
            data.ratings,
            test,
            max_users=200,
            excluded_indices=test_idx,
        ),
    ]

    # ---------------------------------------------------------
    # Create evaluation DataFrame
    # ---------------------------------------------------------
    results_df = pd.DataFrame(
        [result.as_row() for result in results]
    )

    print()
    print("Evaluation Results")
    print("==================")
    print(results_df.to_string(index=False))

    # ---------------------------------------------------------
    # Save evaluation results
    # ---------------------------------------------------------
    results_df.to_csv(
        artifacts_dir / "evaluation_results.csv",
        index=False,
    )

    print()
    print(
        f"Evaluation results saved to "
        f"{artifacts_dir / 'evaluation_results.csv'}"
    )

    print("Done.")

    return results_df


if __name__ == "__main__":

    data_dir = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "ml/data/raw/ml-32m"
    )

    artifacts_dir = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "artifacts"
    )

    run_training(
        data_dir,
        artifacts_dir,
    )