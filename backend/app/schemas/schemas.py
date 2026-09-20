from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str = Field(min_length=1, max_length=80)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: str
    email: EmailStr
    display_name: str

class MovieOut(BaseModel):
    movie_id: int
    title: str
    genres: list[str]

class MovieSearchResult(BaseModel):
    results: list[MovieOut]
    total: int

class RatingCreate(BaseModel):
    movie_id: int
    rating: float = Field(ge=0.5, le=5)

class RatingOut(BaseModel):
    movie_id: int
    rating: float
    title: str | None = None

class RecommendationOut(BaseModel):
    movie_id: int
    title: str
    score: float
    reason: str

class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationOut]
    is_cold_start: bool

class WatchlistItemCreate(BaseModel):
    movie_id: int

class WatchlistOut(BaseModel):
    movie_id: int
    title: str

class ProfileStats(BaseModel):
    ratings_count: int
    avg_rating_given: float
    favorite_genres: list[str]
    top_rated_movies: list[RatingOut]
