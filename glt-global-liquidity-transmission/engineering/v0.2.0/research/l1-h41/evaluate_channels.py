"""Compare one candidate at a time against reserves and TGA."""
import csv
import sys

import numpy as np

CANDIDATES = ("on_rrp_change", "treasury_change", "mbs_change", "loans_change")


def evaluate(path):
    with open(path, encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    target = np.array([float(row["reserves_change"]) for row in rows[1:]])
    for candidate in (None, *CANDIDATES):
        columns = ("reserves_change", "tga_change")
        if candidate is not None:
            columns += (candidate,)
        features = np.array([[float(row[key]) for key in columns] for row in rows[:-1]])
        predictions = []
        for cutoff in range(12, len(target)):
            training = features[:cutoff]
            mean, scale = training.mean(axis=0), training.std(axis=0)
            scale[scale == 0] = 1
            design = np.column_stack((np.ones(cutoff), (training - mean) / scale))
            penalty = np.diag([0] + [1] * len(columns))
            coefficients = np.linalg.solve(
                design.T @ design + penalty, design.T @ target[:cutoff]
            )
            predictions.append(np.r_[1, (features[cutoff] - mean) / scale] @ coefficients)
        actual = target[12:]
        mae = np.mean(np.abs(actual - predictions))
        hits = np.sum(np.sign(actual) == np.sign(predictions))
        print(f"{path} {candidate or 'baseline'} {mae:.2f} {hits}/{len(actual)}")


if __name__ == "__main__":
    for filename in sys.argv[1:]:
        evaluate(filename)
