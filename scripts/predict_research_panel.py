"""Apply a saved research candidate's reduced kNN rule to a new feature CSV.

Input is in the loader's pre-scaling units (Levine: arcsinh(count/5), not raw
counts). This command does not establish that a candidate is a meaningful split.
"""
from pathlib import Path
import argparse
import json

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from threadpoolctl import threadpool_limits


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("run_directory", type=Path)
    cli.add_argument("method")
    cli.add_argument("input_csv", type=Path)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    if args.output.exists():
        cli.error("Output already exists; choose another path")
    protocol = json.loads((args.run_directory / "data_protocol.json").read_text())
    saved = np.load(args.run_directory / f"{args.method}_assignment.npz", allow_pickle=False)
    panel = saved["panel"]
    names = [protocol["features"][j] for j in panel]
    frame = pd.read_csv(args.input_csv)
    missing = [name for name in names if name not in frame.columns]
    if missing:
        cli.error(f"Missing features: {missing}")
    X = frame.loc[:, names].to_numpy(float)
    prep = protocol["preprocessing"]
    med, mean, scale = (np.asarray(prep[k])[panel] for k in ("median", "mean", "scale"))
    X = (np.where(np.isfinite(X), X, med) - mean) / scale
    model = KNeighborsClassifier(n_neighbors=min(7, len(saved["X"])), weights="distance")
    with threadpool_limits(limits=1):
        prediction = model.fit(saved["X"], saved["labels"]).predict(X)
    # Input rows are preserved in order; probabilities would imply unwarranted calibration.
    pd.DataFrame({"input_row": np.arange(len(X)), "algorithm_cluster": prediction}).to_csv(args.output, index=False)
    print(args.output)


if __name__ == "__main__":
    main()
