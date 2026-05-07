#!/usr/bin/env python3
"""Build data/adult_census_income.csv from UCI Adult train/test files."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
# Raw UCI files live in Submission/others/data/ (moved from adult/ for the capstone bundle).
ADULT_DIR = ROOT / "Submission" / "others" / "data"
OUT_DIR = ROOT / "data"
OUT_PATH = OUT_DIR / "adult_census_income.csv"
SUBMISSION_CSV = ROOT / "Submission" / "others" / "data" / "adult_census_income.csv"

COLUMNS = [
    "age",
    "workclass",
    "fnlwgt",
    "education",
    "education-num",
    "marital-status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "capital-gain",
    "capital-loss",
    "hours-per-week",
    "native-country",
    "income",
]


def load_train(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=COLUMNS, skipinitialspace=True)
    df["dataset_split"] = "train"
    return df


def load_test(path: Path) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        header=None,
        names=COLUMNS,
        skiprows=1,
        skipinitialspace=True,
    )
    df["income"] = df["income"].astype(str).str.rstrip(".").str.strip()
    df["dataset_split"] = "test"
    return df


def main() -> None:
    if not (ADULT_DIR / "adult.data").is_file():
        raise FileNotFoundError(
            f"Missing {ADULT_DIR}/adult.data — raw UCI Adult files should be under Submission/others/data/."
        )
    train = load_train(ADULT_DIR / "adult.data")
    test = load_test(ADULT_DIR / "adult.test")
    combined = pd.concat([train, test], ignore_index=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUT_PATH, index=False)
    print(f"Wrote {OUT_PATH} ({len(combined)} rows)")
    SUBMISSION_CSV.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(SUBMISSION_CSV, index=False)
    print(f"Wrote {SUBMISSION_CSV} ({len(combined)} rows)")


if __name__ == "__main__":
    main()
