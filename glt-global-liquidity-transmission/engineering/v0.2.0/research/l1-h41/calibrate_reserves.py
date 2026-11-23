import csv
import sys

import numpy as np


def read(path):
    with open(path, encoding="utf-8", newline="") as source:
        return [(r["release_date"], float(r["reserves_change"])) for r in csv.DictReader(source)]


def main(training_path, validation_path):
    training, validation = read(training_path), read(validation_path)
    if max(date for date, _ in training) >= min(date for date, _ in validation):
        raise ValueError("Training must end before validation starts")
    low, high = np.percentile([v for _, v in training], (5, 95))
    values = np.array([v for _, v in validation])
    scores = np.clip(100 * (values - low) / (high - low), 0, 100)
    print(f"P05={low:.2f}, P95={high:.2f}, clipped={sum((values < low) | (values > high))}/{len(values)}")
    print(f"{validation[-1][0]} observed={values[-1]:.2f}, research_score={scores[-1]:.2f}")


if __name__ == "__main__":
    main(*sys.argv[1:])
