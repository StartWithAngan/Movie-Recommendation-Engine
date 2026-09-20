"""
Scalable MovieLens CSV/DAT loaders.

Supports:
- MovieLens 1M: movies.dat, ratings.dat, users.dat
- MovieLens 32M: movies.csv, ratings.csv, tags.csv, links.csv

The 32M release contains 32,000,204 ratings, 87,585 movies and 200,948 users.
For 32M, ratings are read in chunks to avoid loading the full CSV into memory
when a caller requests a streaming path.
"""

from dataclasses import dataclass
from pathlib import Path
import pandas as pd


@dataclass
class MovieLensData:
    movies: pd.DataFrame
    ratings: pd.DataFrame
    users: pd.DataFrame | None = None
    tags: pd.DataFrame | None = None


def _read_dat(path: Path, columns: list[str], dtypes: dict) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"MovieLens file not found: {path}")
    df = pd.read_csv(path, sep="::", engine="python", header=None,
                     names=columns, encoding="latin-1")
    df = df.dropna(how="any").drop_duplicates()
    for col, dtype in dtypes.items():
        df[col] = df[col].astype(dtype)
    return df.reset_index(drop=True)


def load_movies_1m(data_dir: Path) -> pd.DataFrame:
    df = _read_dat(data_dir / "movies.dat",
                   ["movie_id", "title", "genres"], {"movie_id": "int32"})
    df["genres_list"] = df["genres"].str.split("|")
    return df


def load_ratings_1m(data_dir: Path) -> pd.DataFrame:
    df = _read_dat(data_dir / "ratings.dat",
                   ["user_id", "movie_id", "rating", "timestamp"],
                   {"user_id":"int32","movie_id":"int32","rating":"float32","timestamp":"int64"})
    return df[(df.rating >= 1) & (df.rating <= 5)].reset_index(drop=True)


def load_users_1m(data_dir: Path) -> pd.DataFrame:
    return _read_dat(data_dir / "users.dat",
                     ["user_id","gender","age","occupation","zip_code"],
                     {"user_id":"int32","age":"int32","occupation":"int32"})


def load_movielens_1m(data_dir: str | Path = "ml/data/raw/ml-1m") -> MovieLensData:
    data_dir = Path(data_dir)
    movies, ratings, users = load_movies_1m(data_dir), load_ratings_1m(data_dir), load_users_1m(data_dir)
    return MovieLensData(movies=movies, ratings=ratings, users=users)


def load_movies_32m(data_dir: str | Path) -> pd.DataFrame:
    data_dir = Path(data_dir)
    df = pd.read_csv(data_dir / "movies.csv")
    df["genres_list"] = df["genres"].fillna("(no genres listed)").str.split("|")
    return df[["movieId","title","genres","genres_list"]].rename(columns={"movieId":"movie_id"})


def iter_ratings_32m(data_dir: str | Path, chunksize: int = 1_000_000):
    """Yield validated 32M rating chunks without loading all ratings at once."""
    path = Path(data_dir) / "ratings.csv"
    for chunk in pd.read_csv(path, usecols=["userId","movieId","rating","timestamp"],
                             dtype={"userId":"int32","movieId":"int32","rating":"float32","timestamp":"int64"},
                             chunksize=chunksize):
        chunk = chunk[(chunk.rating >= 1) & (chunk.rating <= 5)]
        yield chunk.rename(columns={"userId":"user_id","movieId":"movie_id"})


def load_ratings_32m(data_dir: str | Path) -> pd.DataFrame:
    return pd.concat(iter_ratings_32m(data_dir), ignore_index=True)


def load_tags_32m(data_dir: str | Path, chunksize: int | None = None) -> pd.DataFrame:
    path = Path(data_dir) / "tags.csv"
    kwargs = {"dtype":{"userId":"int32","movieId":"int32","tag":"string","timestamp":"int64"}}
    if chunksize:
        kwargs["chunksize"] = chunksize
    df = pd.read_csv(path, **kwargs)
    if chunksize:
        return df
    return df.rename(columns={"userId":"user_id","movieId":"movie_id"})


def load_movielens_32m(data_dir: str | Path, include_tags: bool = False) -> MovieLensData:
    data_dir = Path(data_dir)
    return MovieLensData(
        movies=load_movies_32m(data_dir),
        ratings=load_ratings_32m(data_dir),
        users=None,
        tags=load_tags_32m(data_dir) if include_tags else None,
    )



# Backward-compatible 1M helper names used by the existing test suite.
def load_movies(data_dir: Path) -> pd.DataFrame:
    return load_movies_1m(Path(data_dir))


def load_ratings(data_dir: Path) -> pd.DataFrame:
    return load_ratings_1m(Path(data_dir))


def load_users(data_dir: Path) -> pd.DataFrame:
    return load_users_1m(Path(data_dir))

def detect_dataset(data_dir: str | Path) -> str:
    files = {p.name for p in Path(data_dir).iterdir()}
    if "ratings.csv" in files and "movies.csv" in files:
        return "32m"
    if "ratings.dat" in files and "movies.dat" in files:
        return "1m"
    raise ValueError("Could not identify MovieLens dataset in " + str(data_dir))


def load_movielens(data_dir: str | Path) -> MovieLensData:
    kind = detect_dataset(data_dir)
    return load_movielens_32m(data_dir, include_tags=False) if kind == "32m" else load_movielens_1m(data_dir)
