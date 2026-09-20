"""
Hybrid recommendation model.

Combines content-based and collaborative scores:

    final_score = content_weight * content_score_norm
                + collaborative_weight * collaborative_score_norm

Both component scores are normalized to [0, 1] per user before combining,
since content similarity lives in [0, 1] (cosine similarity) while
collaborative scores live in [1, 5] (predicted rating scale) — combining
them unnormalized would let the collaborative term dominate purely because
of its larger numeric range, not because it's more informative.

``_normalize`` maps each component's scores to fractional ranks rather than
min-max rescaling. Per-user collaborative predictions are tightly clustered
around the global mean (only the tails spread out), so min-max rescaling
squashes the great majority of candidates onto nearly the same value and
the collaborative term degrades into a roughly constant offset that barely
influences the final ranking. Rank normalization spreads every candidate
over [0, 1] and lets each model's ordering -- not the shape or magnitude of
its raw scores -- drive the blend.
"""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ml.models.collaborative import CollaborativeModel
from ml.models.content_based import ContentBasedModel
from ml.models.popularity import PopularityModel


@dataclass
class HybridRecommender:
    content_model: ContentBasedModel
    collaborative_model: CollaborativeModel
    popularity_model: PopularityModel | None = None
    content_weight: float = 0.4
    collaborative_weight: float = 0.6
    movie_metadata: pd.DataFrame | None = None
    ratings: pd.DataFrame | None = None
    _title_by_id: dict | None = field(default=None, init=False, repr=False)

    def __post_init__(self):
        total = self.content_weight + self.collaborative_weight
        if not np.isclose(total, 1.0):
            raise ValueError(f"content_weight + collaborative_weight must sum to 1.0, got {total}")
        if self.movie_metadata is not None:
            self._title_by_id = dict(
                zip(self.movie_metadata["movie_id"].astype(int), self.movie_metadata["title"])
            )

    def _with_title(self, rec: dict) -> dict:
        """Attach the movie title if movie metadata was provided."""
        if self._title_by_id is None:
            return rec
        out = dict(rec)
        out["title"] = self._title_by_id.get(int(out["movie_id"]), "Unknown")
        return out

    @staticmethod
    def _normalize(scores: dict) -> dict:
        """Map scores to fractional ranks in [0, 1].

        Each candidate gets ``(rank - 1) / (n - 1)`` where ``rank`` is its
        average rank by score among the ``n`` candidates (ties share rank).
        Unlike min-max rescaling, this makes the value spread independent of
        how concentrated the underlying distribution is, so a tightly
        clustered collaborative signal still discriminates between
        candidates after blending.
        """
        if not scores:
            return {}
        n = len(scores)
        if n == 1:
            return {k: 1.0 for k in scores}

        sorted_items = sorted(scores.items(), key=lambda kv: kv[1])
        ranks = {}
        start = 0
        while start < n:
            end = start + 1
            while end < n and sorted_items[end][1] == sorted_items[start][1]:
                end += 1
            avg_rank = (start + end - 1) / 2.0  # average of 0-based positions
            for i in range(start, end):
                ranks[sorted_items[i][0]] = avg_rank / (n - 1)
            start = end
        return ranks

    def recommend_for_user(
        self,
        user_id: int,
        rated_movie_ids: set[int] | None = None,
        liked_movie_ids: list[int] | None = None,
        top_k: int = 10,
        top_n: int | None = None,
    ) -> list[dict]:
        """
        liked_movie_ids: movies the user rated highly, used both to build a
        content-based signal (averaged similarity to these movies) and to
        populate "because you liked X" explanations.

        If rated_movie_ids/liked_movie_ids are omitted, they are derived from
        the ``ratings`` frame passed to the constructor (evaluators and callers
        with explicit history should keep passing them explicitly).
        """
        k = top_n if top_n is not None else top_k

        if rated_movie_ids is None or liked_movie_ids is None:
            if self.ratings is None:
                raise ValueError(
                    "rated_movie_ids/liked_movie_ids are required unless the "
                    "hybrid was constructed with a ratings frame."
                )
            history = self.ratings[self.ratings["user_id"] == int(user_id)]
            rated_movie_ids = set(history["movie_id"].astype(int))
            liked_movie_ids = (
                history.loc[history["rating"] >= 4.0, "movie_id"]
                .astype(int)
                .tolist()
            )

        collab_scores = self.collaborative_model.score_all_for_user(user_id)

        # Average content similarity to the user's liked movies -- this is
        # what lets content-based signal contribute even for known users.
        content_scores: dict[int, float] = {}
        if liked_movie_ids:
            per_movie = [self.content_model.score_all(mid) for mid in liked_movie_ids if mid in self.content_model.movie_ids]
            if per_movie:
                all_ids = set().union(*[d.keys() for d in per_movie])
                content_scores = {mid: float(np.mean([d.get(mid, 0.0) for d in per_movie])) for mid in all_ids}

        is_cold_start = user_id not in self.collaborative_model.user_id_to_row

        if is_cold_start:
            # New user: no collaborative signal at all -> content-based + popularity only.
            ranked = sorted(content_scores.items(), key=lambda kv: -kv[1])
            results = []
            for mid, score in ranked:
                if mid in rated_movie_ids:
                    continue
                results.append({
                    "movie_id": mid,
                    "score": round(score, 4),
                    "reason": self._explain(mid, liked_movie_ids, is_cold_start=True),
                })
                if len(results) >= k:
                    break
            return [self._with_title(r) for r in results]

        content_norm = self._normalize(content_scores)
        collab_norm = self._normalize(collab_scores)

        all_movie_ids = set(collab_norm) | set(content_norm)
        all_movie_ids -= rated_movie_ids

        scored = []
        for mid in all_movie_ids:
            c_score = content_norm.get(mid, 0.0)
            cf_score = collab_norm.get(mid, 0.0)
            final = self.content_weight * c_score + self.collaborative_weight * cf_score
            scored.append((mid, final, c_score, cf_score))

        scored.sort(key=lambda t: -t[1])

        results = []
        for mid, final, c_score, cf_score in scored[:k]:
            results.append({
                "movie_id": mid,
                "score": round(float(final), 4),
                "reason": self._explain(mid, liked_movie_ids, c_score=c_score, cf_score=cf_score),
            })
        return [self._with_title(r) for r in results]

    def recommend_for_app_user(
        self,
        ratings: pd.DataFrame,
        rated_movie_ids: set[int],
        liked_movie_ids: list[int],
        top_k: int = 10,
    ) -> list[dict]:
        """Hybrid recommendations for real application users.

        Uses content similarity plus collaborative latent-factor fold-in.
        Users with no usable history fall back to the popularity model.
        """
        content_scores: dict[int, float] = {}
        if liked_movie_ids:
            per_movie = [
                self.content_model.score_all(mid)
                for mid in liked_movie_ids
                if mid in self.content_model.movie_ids
            ]
            if per_movie:
                all_ids = set().union(*(d.keys() for d in per_movie))
                content_scores = {
                    mid: float(np.mean([d.get(mid, 0.0) for d in per_movie]))
                    for mid in all_ids
                }

        collab_list = self.collaborative_model.recommend_for_ratings(
            ratings, rated_movie_ids, top_k=max(top_k * 5, 50)
        )
        collab_scores = {r["movie_id"]: r["score"] for r in collab_list}

        if not content_scores and not collab_scores:
            if self.popularity_model is None:
                return []
            return [
                self._with_title({**r, "reason": "Popular movies recommended for new users"})
                for r in self.popularity_model.recommend(rated_movie_ids, top_k)
            ]

        content_norm = self._normalize(content_scores)
        collab_norm = self._normalize(collab_scores)
        all_movie_ids = (set(content_norm) | set(collab_norm)) - rated_movie_ids

        scored = []
        for mid in all_movie_ids:
            c = content_norm.get(mid, 0.0)
            cf = collab_norm.get(mid, 0.0)
            final = self.content_weight * c + self.collaborative_weight * cf
            scored.append((mid, final, c, cf))
        scored.sort(key=lambda x: (-x[1], x[0]))

        results = []
        for mid, final, c, cf in scored[:top_k]:
            reason = (
                "Similar to movies you rated highly"
                if c > cf and liked_movie_ids
                else "Based on your rating patterns"
            )
            results.append(
                {"movie_id": int(mid), "score": round(float(final), 4), "reason": reason}
            )
        return [self._with_title(r) for r in results]

    def _explain(self, movie_id: int, liked_movie_ids: list[int], is_cold_start: bool = False,
                 c_score: float = 0.0, cf_score: float = 0.0) -> str:
        if is_cold_start:
            return "Based on the genres of movies you selected"
        if c_score > cf_score and liked_movie_ids:
            return "Similar to movies you rated highly"
        if cf_score >= c_score:
            return "Users with similar rating patterns also liked this movie"
        return "Recommended for you"
