"""
Unit tests for ml/preprocessing/load_movielens.py.

Uses small hand-written .dat fixtures (written to a tmp_path) rather than
the full MovieLens 1M download, so this test suite runs fast and doesn't
require the dataset to be present.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ml" / "preprocessing"))

from load_movielens import load_movies, load_ratings, load_users  # noqa: E402


def _write(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines), encoding="latin-1")


def test_load_movies_parses_genres_and_drops_duplicates(tmp_path: Path):
    _write(
        tmp_path / "movies.dat",
        [
            "1::Toy Story (1995)::Animation|Children's|Comedy",
            "2::Jumanji (1995)::Adventure|Children's|Fantasy",
            "1::Toy Story (1995)::Animation|Children's|Comedy",  # duplicate
        ],
    )
    df = load_movies(tmp_path)
    assert len(df) == 2
    assert df.loc[df["movie_id"] == 1, "genres_list"].iloc[0] == ["Animation", "Children's", "Comedy"]


def test_load_ratings_drops_out_of_range_values(tmp_path: Path):
    _write(
        tmp_path / "ratings.dat",
        [
            "1::1::5::978300760",
            "1::2::4::978300761",
            "2::1::7::978300762",  # invalid: rating out of 1-5 range
        ],
    )
    df = load_ratings(tmp_path)
    assert len(df) == 2
    assert df["rating"].max() <= 5
    assert df["rating"].min() >= 1


def test_load_users_casts_types(tmp_path: Path):
    _write(
        tmp_path / "users.dat",
        [
            "1::F::1::10::48067",
            "2::M::56::16::94110",
        ],
    )
    df = load_users(tmp_path)
    assert df["age"].dtype.name == "int32"
    assert df["occupation"].dtype.name == "int32"
    assert len(df) == 2
