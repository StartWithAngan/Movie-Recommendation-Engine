from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.deps import get_ml_artifacts
from app.schemas.schemas import MovieOut, MovieSearchResult

router = APIRouter(prefix="/api/movies", tags=["movies"])

def _rows(df):
    return [MovieOut(movie_id=int(r.movie_id), title=r.title, genres=r.genres_list) for r in df.itertuples()]

@router.get("", response_model=MovieSearchResult)
async def list_movies(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), artifacts=Depends(get_ml_artifacts)):
    start = (page - 1) * page_size
    return MovieSearchResult(results=_rows(artifacts.movies.iloc[start:start+page_size]), total=len(artifacts.movies))

@router.get("/search", response_model=MovieSearchResult)
async def search_movies(q: str = Query(..., min_length=1), genre: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), artifacts=Depends(get_ml_artifacts)):
    mask = artifacts.movies["title"].str.contains(q, case=False, na=False, regex=False)
    if genre:
        mask &= artifacts.movies["genres_list"].apply(lambda gs: genre.lower() in [g.lower() for g in gs])
    filtered = artifacts.movies[mask]
    start = (page - 1) * page_size
    return MovieSearchResult(results=_rows(filtered.iloc[start:start+page_size]), total=len(filtered))

@router.get("/{movie_id}", response_model=MovieOut)
async def get_movie(movie_id: int, artifacts=Depends(get_ml_artifacts)):
    row = artifacts.movies[artifacts.movies.movie_id == movie_id]
    if row.empty:
        raise HTTPException(404, "Movie not found")
    return _rows(row)[0]
