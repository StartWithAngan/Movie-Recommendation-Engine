from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user_id, get_db, get_ml_artifacts
from app.schemas.schemas import RatingCreate, RatingOut

router = APIRouter(prefix="/api/ratings", tags=["ratings"])


@router.post("", status_code=201)
async def rate_movie(
    payload: RatingCreate,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
    artifacts=Depends(get_ml_artifacts),
):
    if payload.movie_id not in set(artifacts.movies["movie_id"]):
        raise HTTPException(status_code=404, detail="Invalid movie_id")

    await db.ratings.update_one(
        {"user_id": user_id, "movie_id": payload.movie_id},
        {"$set": {"rating": payload.rating, "updated_at": datetime.now(timezone.utc)}, "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return {"status": "ok"}


@router.get("", response_model=list[RatingOut])
async def list_my_ratings(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
    artifacts=Depends(get_ml_artifacts),
):
    cursor = db.ratings.find({"user_id": user_id})
    ratings = [doc async for doc in cursor]

    title_by_id = dict(zip(artifacts.movies["movie_id"], artifacts.movies["title"]))
    return [
        RatingOut(movie_id=r["movie_id"], rating=r["rating"], title=title_by_id.get(r["movie_id"]))
        for r in ratings
    ]
