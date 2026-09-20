from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd

from app.core.deps import get_current_user_id, get_db, get_ml_artifacts
from app.schemas.schemas import RecommendationOut, RecommendationResponse

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationResponse)
async def get_recommendations(
    top_k: int = Query(10, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
    artifacts=Depends(get_ml_artifacts),
):
    cursor = db.ratings.find({"user_id": user_id})
    my_ratings = [doc async for doc in cursor]

    rated_movie_ids = {int(r["movie_id"]) for r in my_ratings}
    liked_movie_ids = [int(r["movie_id"]) for r in my_ratings if r["rating"] >= 4]
    ratings_df = pd.DataFrame(
        [{"movie_id": int(r["movie_id"]), "rating": float(r["rating"])} for r in my_ratings],
        columns=["movie_id", "rating"],
    )

    recs = artifacts.hybrid.recommend_for_app_user(
        ratings=ratings_df,
        rated_movie_ids=rated_movie_ids,
        liked_movie_ids=liked_movie_ids,
        top_k=top_k,
    )

    title_by_id = dict(zip(artifacts.movies["movie_id"], artifacts.movies["title"]))
    is_cold_start = len(my_ratings) == 0

    return RecommendationResponse(
        recommendations=[
            RecommendationOut(
                movie_id=r["movie_id"],
                title=title_by_id.get(r["movie_id"], "Unknown"),
                score=r["score"],
                reason=r["reason"],
            )
            for r in recs
        ],
        is_cold_start=is_cold_start,
    )


@router.get("/similar/{movie_id}", response_model=list[RecommendationOut])
async def similar_movies(movie_id: int, top_k: int = Query(10, ge=1, le=50), artifacts=Depends(get_ml_artifacts)):
    if movie_id not in set(artifacts.movies["movie_id"]):
        raise HTTPException(status_code=404, detail="Movie not found")

    sims = artifacts.content.recommend_similar_movies(movie_id, top_k=top_k)
    title_by_id = dict(zip(artifacts.movies["movie_id"], artifacts.movies["title"]))
    return [
        RecommendationOut(
            movie_id=s["movie_id"],
            title=title_by_id.get(s["movie_id"], "Unknown"),
            score=s["score"],
            reason="Similar genres and metadata",
        )
        for s in sims
    ]
