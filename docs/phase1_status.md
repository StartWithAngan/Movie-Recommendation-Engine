# Phase 1 Implementation Status

## Completed

- Repository structure for ML, FastAPI backend, Next.js frontend, tests, artifacts, and docs.
- MovieLens 1M loader with `::` parsing, Latin-1 decoding, validation, duplicate removal, and cross-reference checks.
- Content-based recommender using TF-IDF over genres and cosine similarity.
- Collaborative filtering using TruncatedSVD over the sparse user-item matrix.
- Application-user latent-factor fold-in using the trained item factors, so MongoDB users do not need MovieLens IDs.
- Popularity baseline with Bayesian weighting for cold-start recommendations.
- Hybrid ranking with normalized content/collaborative scores.
- FastAPI startup loading of trained artifacts.
- Docker artifact path configuration.
- Existing unit tests pass.

## Verification

```text
11 passed
```

The real MovieLens 1M dataset still needs to be placed under:

```text
ml/data/raw/ml-1m/
```

before running the full training pipeline and producing final evaluation numbers.
