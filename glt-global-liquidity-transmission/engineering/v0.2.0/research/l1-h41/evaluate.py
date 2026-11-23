import csv
import sys

import numpy as np


def main(path, selected_candidates=None):
    with open(path, newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    candidates = selected_candidates or (
        "tga_change",
        "other_reverse_repo_change",
        "total_assets_wednesday_change",
    )
    reserves = np.array([float(row["reserves_change"]) for row in rows])
    for candidate in (None, *candidates):
        columns = [reserves]
        if candidate:
            columns.append(np.array([float(row[candidate]) for row in rows]))
        features = np.column_stack(columns)[:-1]
        target = reserves[1:]
        predictions = []
        for cutoff in range(12, len(target)):
            train = features[:cutoff]
            mean, scale = train.mean(axis=0), train.std(axis=0)
            scale[scale == 0] = 1
            design = np.column_stack((np.ones(cutoff), (train - mean) / scale))
            penalty = np.diag([0] + [1] * len(columns))
            coefficients = np.linalg.solve(
                design.T @ design + penalty, design.T @ target[:cutoff]
            )
            point = np.r_[1, (features[cutoff] - mean) / scale]
            predictions.append(point @ coefficients)
        actual = target[12:]
        print(candidate or "reserves_only", len(actual),
              round(np.mean(np.abs(actual - predictions)), 2),
              int(np.sum(np.sign(actual) == np.sign(predictions))))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
