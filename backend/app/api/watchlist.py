from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user_id, get_db, get_ml_artifacts
from app.schemas.schemas import WatchlistItemCreate, WatchlistOut

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.post("", status_code=201)
async def add_to_watchlist(
    payload: WatchlistItemCreate,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
    artifacts=Depends(get_ml_artifacts),
):
    if payload.movie_id not in set(artifacts.movies["movie_id"]):
        raise HTTPException(status_code=404, detail="Invalid movie_id")

    await db.watchlist.update_one(
        {"user_id": user_id, "movie_id": payload.movie_id},
        {"$set": {"user_id": user_id, "movie_id": payload.movie_id}},
        upsert=True,
    )
    return {"status": "ok"}


@router.get("", response_model=list[WatchlistOut])
async def get_watchlist(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
    artifacts=Depends(get_ml_artifacts),
):
    cursor = db.watchlist.find({"user_id": user_id})
    items = [doc async for doc in cursor]
    title_by_id = dict(zip(artifacts.movies["movie_id"], artifacts.movies["title"]))
    return [WatchlistOut(movie_id=i["movie_id"], title=title_by_id.get(i["movie_id"], "Unknown")) for i in items]


@router.delete("/{movie_id}", status_code=204)
async def remove_from_watchlist(
    movie_id: int,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    await db.watchlist.delete_one({"user_id": user_id, "movie_id": movie_id})
