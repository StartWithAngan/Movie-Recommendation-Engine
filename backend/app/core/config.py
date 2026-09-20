"""
Central application configuration.

All values are read from environment variables (see .env.example at the
project root). Nothing here should ever contain a real secret, password,
or connection string — those live only in a local .env file that is
gitignored.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    app_name: str = "Movie Recommendation Engine"
    environment: str = "development"  # development | production
    api_prefix: str = "/api"

    # --- Database ---
    mongodb_uri: str
    mongodb_db_name: str = "movie_recommender"

    # --- Auth ---
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # --- ML artifacts ---
    # Directory the backend loads trained model artifacts from at startup.
    # Relative paths are resolved against the project root.
    # See ml/training/ for the pipeline that produces these files.
    artifacts_dir: str = "artifacts"

    # --- CORS ---
    # Comma-separated list of allowed origins, e.g.
    # "http://localhost:3000,https://your-frontend.vercel.app"
    cors_allowed_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor. FastAPI dependencies should call this rather
    than instantiating Settings() directly, so the environment is only
    parsed once per process.
    """
    return Settings()
