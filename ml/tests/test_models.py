"""
Tests for the recommendation models. Uses small hand-built fixtures rather
than the full dataset, so this runs fast and without any external data.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.models.content_based import train_content_based
from ml.models.collaborative import train_collaborative
from ml.models.hybrid import HybridRecommender


@pytest.fixture
def movies_df():
    return pd.DataFrame({
        "movie_id": [1, 2, 3, 4],
        "title": ["A", "B", "C", "D"],
        "genres_list": [
            ["Action", "Sci-Fi"],
            ["Action", "Sci-Fi"],
            ["Comedy"],
            ["Comedy", "Romance"],
        ],
    })


@pytest.fixture
def ratings_df():
    rows = []
    # 5 users each rate all 4 movies with some variation, enough for SVD to factorize.
    pattern = [
        [5, 4, 1, 1],
        [4, 5, 1, 2],
        [1, 1, 5, 4],
        [2, 1, 4, 5],
        [5, 5, 1, 1],
    ]
    for uid, row in enumerate(pattern, start=1):
        for mid, rating in enumerate(row, start=1):
            rows.append({"user_id": uid, "movie_id": mid, "rating": float(rating)})
    return pd.DataFrame(rows)


def test_content_based_groups_similar_genres(movies_df):
    model = train_content_based(movies_df)
    sims = model.recommend_similar_movies(movie_id=1, top_k=3)
    # Movie 2 shares identical genres with movie 1 -> should rank first.
    assert sims[0]["movie_id"] == 2
    assert sims[0]["score"] > sims[-1]["score"] or len(sims) == 1


def test_content_based_raises_on_unknown_movie(movies_df):
    model = train_content_based(movies_df)
    with pytest.raises(ValueError):
        model.recommend_similar_movies(movie_id=999)


def test_collaborative_predicts_within_rating_bounds(ratings_df):
    model = train_collaborative(ratings_df, n_factors=2)
    pred = model.predict(user_id=1, movie_id=3)
    assert 1.0 <= pred <= 5.0


def test_collaborative_cold_start_returns_global_mean(ratings_df):
    model = train_collaborative(ratings_df, n_factors=2)
    pred = model.predict(user_id=999, movie_id=1)  # unknown user
    assert pred == model.global_mean


def test_collaborative_excludes_rated_movies(ratings_df):
    model = train_collaborative(ratings_df, n_factors=2)
    recs = model.recommend_for_user(user_id=1, rated_movie_ids={1, 2}, top_k=10)
    recommended_ids = {r["movie_id"] for r in recs}
    assert recommended_ids.isdisjoint({1, 2})


def test_hybrid_weights_must_sum_to_one(movies_df, ratings_df):
    content = train_content_based(movies_df)
    collab = train_collaborative(ratings_df, n_factors=2)
    with pytest.raises(ValueError):
        HybridRecommender(content, collab, content_weight=0.5, collaborative_weight=0.6)


def test_hybrid_cold_start_uses_content_only(movies_df, ratings_df):
    content = train_content_based(movies_df)
    collab = train_collaborative(ratings_df, n_factors=2)
    hybrid = HybridRecommender(content, collab)

    recs = hybrid.recommend_for_user(
        user_id=999999,  # not in collaborative training data
        rated_movie_ids=set(),
        liked_movie_ids=[1],
        top_k=3,
    )
    assert all(r["reason"] == "Based on the genres of movies you selected" for r in recs)
    # Movie 2 (identical genres to liked movie 1) should be recommended.
    assert 2 in {r["movie_id"] for r in recs}


def test_hybrid_no_duplicate_recommendations(movies_df, ratings_df):
    content = train_content_based(movies_df)
    collab = train_collaborative(ratings_df, n_factors=2)
    hybrid = HybridRecommender(content, collab)

    recs = hybrid.recommend_for_user(user_id=1, rated_movie_ids=set(), liked_movie_ids=[1], top_k=10)
    ids = [r["movie_id"] for r in recs]
    assert len(ids) == len(set(ids))


def test_hybrid_user_id_only_requires_ratings(movies_df, ratings_df):
    content = train_content_based(movies_df)
    collab = train_collaborative(ratings_df, n_factors=2)
    hybrid = HybridRecommender(content, collab)
    with pytest.raises(ValueError):
        hybrid.recommend_for_user(user_id=1, top_n=3)


def test_hybrid_titles_from_metadata(movies_df, ratings_df):
    content = train_content_based(movies_df)
    collab = train_collaborative(ratings_df, n_factors=2)
    hybrid = HybridRecommender(content, collab, movie_metadata=movies_df)

    recs = hybrid.recommend_for_user(
        user_id=1, rated_movie_ids={1}, liked_movie_ids=[2], top_k=3
    )
    assert recs
    for rec in recs:
        assert rec["title"] in {"A", "B", "C", "D"}

    # top_n alias is honored and metadata is optional.
    hybrid_no_meta = HybridRecommender(content, collab)
    recs_no_meta = hybrid_no_meta.recommend_for_user(
        user_id=1, rated_movie_ids={1}, liked_movie_ids=[2], top_n=3
    )
    assert len(recs_no_meta) == 3
    assert "title" not in recs_no_meta[0]
