# Phase 3 — MovieLens 32M Results

## Dataset

The uploaded MovieLens 32M release was used. The local EDA pipeline measured:

- Movies: 87,585
- Ratings: 32,000,204 raw ratings; 31,475,072 valid ratings after the loader's validation/deduplication step
- Users: 200,948
- Mean rating: 3.5404
- Rating standard deviation: 1.0590
- Genres: 20

## Evaluation protocol

A temporal leave-one-out split holds out each eligible user's latest timestamped interaction. Rating prediction metrics (RMSE/MAE) use the full held-out set. Ranking metrics are computed on a deterministic 50-user sample because scoring the full 87,585-item catalog for every one of ~200k users is unnecessarily expensive for a development run.

## Measured results

| Model | RMSE | MAE | Precision@10 | Recall@10 |
|---|---:|---:|---:|---:|
| Popularity baseline | — | — | 0.0000 | 0.0000 |
| Collaborative SVD | 0.9819 | 0.8040 | 0.0069 | 0.0690 |

The popularity baseline does not produce RMSE/MAE because it is a ranking-only baseline. The ranking sample was intentionally kept small during this development run. These values should be presented as the current measured development benchmark, not as a universal or production-quality benchmark.

## Artifacts

The trained artifacts are in `artifacts-32m/`:

- `collaborative_model.pkl`
- `content_similarity.pkl`
- `popularity_model.pkl`
- `hybrid_model.pkl`
- `movie_metadata.pkl`
- `evaluation_results.csv`

## Engineering note

The collaborative model uses SciPy sparse SVD (`svds`) rather than a dense similarity matrix. This was selected after benchmarking the 32M dataset on a constrained development environment: the initial randomized-SVD path exceeded the available memory, while the sparse SVD implementation trained successfully with a substantially lower peak memory footprint.
