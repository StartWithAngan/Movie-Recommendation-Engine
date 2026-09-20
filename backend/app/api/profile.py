from collections import Counter

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user_id, get_db, get_ml_artifacts
from app.schemas.schemas import ProfileStats, RatingOut

router = APIRouter(prefix="/api", tags=["profile"])


async def _load_ratings_with_titles(user_id: str, db, artifacts) -> list[dict]:
    cursor = db.ratings.find({"user_id": user_id})
    ratings = [doc async for doc in cursor]
    genre_by_id = dict(zip(artifacts.movies["movie_id"], artifacts.movies["genres_list"]))
    title_by_id = dict(zip(artifacts.movies["movie_id"], artifacts.movies["title"]))
    for r in ratings:
        r["title"] = title_by_id.get(r["movie_id"], "Unknown")
        r["genres"] = genre_by_id.get(r["movie_id"], [])
    return ratings


@router.get("/profile", response_model=ProfileStats)
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
    artifacts=Depends(get_ml_artifacts),
):
    ratings = await _load_ratings_with_titles(user_id, db, artifacts)

    if not ratings:
        return ProfileStats(ratings_count=0, avg_rating_given=0.0, favorite_genres=[], top_rated_movies=[])

    genre_counter = Counter(g for r in ratings for g in r["genres"])
    top_rated = sorted(ratings, key=lambda r: -r["rating"])[:5]

    return ProfileStats(
        ratings_count=len(ratings),
        avg_rating_given=round(sum(r["rating"] for r in ratings) / len(ratings), 2),
        favorite_genres=[g for g, _ in genre_counter.most_common(5)],
        top_rated_movies=[RatingOut(movie_id=r["movie_id"], rating=r["rating"], title=r["title"]) for r in top_rated],
    )


@router.get("/analytics")
async def get_analytics(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
    artifacts=Depends(get_ml_artifacts),
):
    ratings = await _load_ratings_with_titles(user_id, db, artifacts)
    if not ratings:
        return {"ratings_count": 0, "rating_distribution": {}, "favorite_genres": []}

    distribution = Counter(r["rating"] for r in ratings)
    genre_counter = Counter(g for r in ratings for g in r["genres"])

    return {
        "ratings_count": len(ratings),
        "rating_distribution": dict(distribution),
        "favorite_genres": dict(genre_counter.most_common(10)),
        "avg_rating_given": round(sum(r["rating"] for r in ratings) / len(ratings), 2),
    }
