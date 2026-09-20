import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.main import app
from app.core.deps import get_current_user_id, get_db, get_ml_artifacts


class FakeCursor:
    def __init__(self, docs):
        self.docs = docs

    def __aiter__(self):
        self._it = iter(self.docs)
        return self

    async def __anext__(self):
        try:
            return next(self._it)
        except StopIteration:
            raise StopAsyncIteration


class FakeCollection:
    def __init__(self, docs=None):
        self.docs = docs or []

    async def create_index(self, *args, **kwargs):
        return None

    async def find_one(self, query, projection=None):
        for doc in self.docs:
            if all(doc.get(k) == v for k, v in query.items()):
                if projection:
                    return {k: v for k, v in doc.items() if projection.get(k, 1) != 0}
                return doc
        return None

    def find(self, query):
        return FakeCursor([
            d for d in self.docs
            if all(d.get(k) == v for k, v in query.items())
        ])

    async def insert_one(self, doc):
        self.docs.append(dict(doc))
        return SimpleNamespace(inserted_id="507f1f77bcf86cd799439011")

    async def update_one(self, query, update, upsert=False):
        for doc in self.docs:
            if all(doc.get(k) == v for k, v in query.items()):
                doc.update(update.get("$set", {}))
                return SimpleNamespace(upserted_id=None)
        if upsert:
            new_doc = dict(query)
            new_doc.update(update.get("$set", {}))
            new_doc.update(update.get("$setOnInsert", {}))
            self.docs.append(new_doc)
        return SimpleNamespace(upserted_id=None)

    async def delete_one(self, query):
        self.docs[:] = [
            d for d in self.docs
            if not all(d.get(k) == v for k, v in query.items())
        ]


class FakeDB:
    def __init__(self):
        self.users = FakeCollection()
        self.ratings = FakeCollection()
        self.watchlist = FakeCollection()


movies = pd.DataFrame([
    {"movie_id": 1, "title": "The Matrix", "genres_list": ["Action", "Sci-Fi"]},
    {"movie_id": 2, "title": "Toy Story", "genres_list": ["Animation", "Children"]},
    {"movie_id": 3, "title": "Arrival", "genres_list": ["Drama", "Sci-Fi"]},
    {"movie_id": 4, "title": "Alien", "genres_list": ["Horror", "Sci-Fi"]},
])


class FakeContent:
    def recommend_similar_movies(self, movie_id, top_k=10):
        return [{"movie_id": 3, "score": 0.91}][:top_k]


class FakeHybrid:
    def recommend_for_app_user(self, ratings, rated_movie_ids, liked_movie_ids, top_k=10):
        candidates = [
            {"movie_id": 3, "score": 0.91, "reason": "Similar to movies you rated highly"},
            {"movie_id": 4, "score": 0.82, "reason": "Based on your rating history"},
        ]
        return [x for x in candidates if x["movie_id"] not in rated_movie_ids][:top_k]


fake_artifacts = SimpleNamespace(
    content=FakeContent(),
    collaborative=object(),
    movies=movies,
    popularity=object(),
    hybrid=FakeHybrid(),
)


@pytest.fixture()
def client():
    db = FakeDB()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user_id] = lambda: "507f1f77bcf86cd799439011"
    app.dependency_overrides[get_ml_artifacts] = lambda: fake_artifacts
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_movie_search_and_detail(client):
    response = client.get("/api/movies/search?q=matrix")
    assert response.status_code == 200
    assert response.json()["results"][0]["movie_id"] == 1

    response = client.get("/api/movies/1")
    assert response.status_code == 200
    assert response.json()["title"] == "The Matrix"


def test_missing_movie_returns_404(client):
    response = client.get("/api/movies/999")
    assert response.status_code == 404


def test_invalid_rating_movie_returns_404(client):
    response = client.post("/api/ratings", json={"movie_id": 999, "rating": 5})
    assert response.status_code == 404


def test_rating_upsert_and_list(client):
    response = client.post("/api/ratings", json={"movie_id": 1, "rating": 5})
    assert response.status_code == 201

    response = client.get("/api/ratings")
    assert response.status_code == 200
    assert response.json()[0]["movie_id"] == 1
    assert response.json()[0]["rating"] == 5


def test_personalized_recommendations_exclude_rated_movies(client):
    client.post("/api/ratings", json={"movie_id": 1, "rating": 5})
    response = client.get("/api/recommendations?top_k=2")
    assert response.status_code == 200
    payload = response.json()
    assert payload["is_cold_start"] is False
    assert all(x["movie_id"] != 1 for x in payload["recommendations"])


def test_similar_movie_endpoint(client):
    response = client.get("/api/recommendations/similar/1?top_k=1")
    assert response.status_code == 200
    assert response.json()[0]["movie_id"] == 3


def test_similar_missing_movie_returns_404(client):
    response = client.get("/api/recommendations/similar/999")
    assert response.status_code == 404


def test_watchlist_add_list_delete(client):
    response = client.post("/api/watchlist", json={"movie_id": 2})
    assert response.status_code == 201

    response = client.get("/api/watchlist")
    assert response.status_code == 200
    assert response.json()[0]["movie_id"] == 2

    response = client.delete("/api/watchlist/2")
    assert response.status_code == 204

    response = client.get("/api/watchlist")
    assert response.json() == []


def test_invalid_rating_validation(client):
    response = client.post("/api/ratings", json={"movie_id": 1, "rating": 6})
    assert response.status_code == 422
