import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

ARTIFACTS_ROOT = Path(__file__).resolve().parent / "artifacts"

from app.core.config import get_settings
from app.api import auth, movies, ratings, recommendations, watchlist, profile

@dataclass
class MLArtifacts:
    content: object
    collaborative: object
    movies: object
    popularity: object
    hybrid: object


def _load_artifacts(artifacts_dir: Path):
    from app.ml.models.hybrid import HybridRecommender
    content = joblib.load(artifacts_dir / "content_similarity.pkl")
    collaborative = joblib.load(artifacts_dir / "collaborative_model.pkl")
    popularity = joblib.load(artifacts_dir / "popularity_model.pkl")
    movies = joblib.load(artifacts_dir / "movie_metadata.pkl")
    return MLArtifacts(content, collaborative, movies, popularity,
                       HybridRecommender(content, collaborative, popularity))

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = settings
    app.state.mongo_client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    app.state.db = app.state.mongo_client[settings.mongodb_db_name]
    await app.state.db.users.create_index("email", unique=True)
    await app.state.db.ratings.create_index([("user_id", 1), ("movie_id", 1)], unique=True)
    await app.state.db.watchlist.create_index([("user_id", 1), ("movie_id", 1)], unique=True)
    artifacts_dir = ARTIFACTS_ROOT
    try:
        app.state.ml_artifacts = _load_artifacts(artifacts_dir)
    except FileNotFoundError:
        app.state.ml_artifacts = None
    yield
    app.state.mongo_client.close()

app = FastAPI(title=settings.app_name, version="0.5.0", description="Hybrid movie recommendation API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(ratings.router)
app.include_router(recommendations.router)
app.include_router(watchlist.router)
app.include_router(profile.router)

@app.get("/api/health", tags=["health"])
async def health_check():
    try:
        await app.state.db.command("ping")
        db_status = "connected"
    except Exception as exc:
        db_status = f"error: {exc}"
    return {"status": "ok", "environment": settings.environment, "database": db_status, "ml_artifacts_loaded": app.state.ml_artifacts is not None}
