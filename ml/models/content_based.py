"""
Scalable content-based recommender.

MovieLens 1M/32M can have tens of thousands of movies. A dense NxN cosine
similarity matrix is therefore not viable for the 32M release. This model
keeps TF-IDF vectors sparse and uses nearest-neighbor search over that sparse
matrix.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


@dataclass
class ContentBasedModel:
    movie_ids: np.ndarray
    tfidf_matrix: object
    vectorizer: TfidfVectorizer
    nn_model: NearestNeighbors
    movie_id_to_row: dict

    def score_all(self, movie_id: int, top_n: int = 250) -> dict:
        if movie_id not in self.movie_id_to_row:
            raise ValueError(f"movie_id {movie_id} not found in content-based model")
        row = self.movie_id_to_row[movie_id]
        n = min(top_n + 1, len(self.movie_ids))
        distances, indices = self.nn_model.kneighbors(self.tfidf_matrix[row], n_neighbors=n)
        return {int(self.movie_ids[i]): float(1.0 - d)
                for i, d in zip(indices[0], distances[0]) if int(self.movie_ids[i]) != movie_id}

    def recommend_similar_movies(self, movie_id: int, top_k: int = 10) -> list[dict]:
        scores = self.score_all(movie_id, top_n=top_k)
        return [{"movie_id": mid, "score": round(score, 4)}
                for mid, score in sorted(scores.items(), key=lambda x: -x[1])[:top_k]]


def _build_corpus(movies: pd.DataFrame) -> pd.Series:
    # Use title + genres. This remains available in both MovieLens 1M and 32M
    # and gives the content model more signal than genres alone.
    return movies.apply(
        lambda r: f"{str(r.get('title', ''))} {' '.join(r.get('genres_list', []))}",
        axis=1,
    )


def train_content_based(movies: pd.DataFrame, neighbors: int = 250) -> ContentBasedModel:
    corpus = _build_corpus(movies)
    vectorizer = TfidfVectorizer(token_pattern=r"[^\s]+")
    tfidf = vectorizer.fit_transform(corpus)
    nn = NearestNeighbors(n_neighbors=min(neighbors, len(movies)), metric="cosine", algorithm="brute", n_jobs=-1)
    nn.fit(tfidf)
    ids = movies["movie_id"].to_numpy()
    return ContentBasedModel(ids, tfidf, vectorizer, nn, {int(mid): i for i, mid in enumerate(ids)})
