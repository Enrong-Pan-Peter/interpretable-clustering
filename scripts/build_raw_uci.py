"""Parse the manually-downloaded raw files (data/uci/raw/) into the clean cached CSVs
that load_uci() consumes. Run once after dropping the raw downloads in place.

  biodeg.csv                         -> ';'-sep, no header, 41 numeric feats + RB/NRB
  Chemical Compos*on of Ceramic.csv  -> ','-sep, header; drop name/part, 17 oxide feats,
                                        label = Part (Body/Glaze)
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(HERE, "data", "uci", "raw")
OUT = os.path.join(HERE, "data", "uci")


def _write(name, X, y):
    X = X.apply(pd.to_numeric, errors="coerce")
    X.columns = [f"f{i}" for i in range(X.shape[1])]
    X.to_csv(os.path.join(OUT, f"{name}.csv"), index=False)
    if y is not None:
        pd.Series(y, name="target").to_csv(os.path.join(OUT, f"{name}_target.csv"), index=False)
    print(f"  {name}: {X.shape[0]} rows x {X.shape[1]} feats, "
          f"{'labels ('+str(len(np.unique(y)))+' classes)' if y is not None else 'no labels'}")


def main():
    # Biodegradation
    bio = glob.glob(os.path.join(RAW, "biodeg*.csv"))
    if bio:
        df = pd.read_csv(bio[0], sep=";", header=None)
        _write("biodegradation", df.iloc[:, :41], pd.factorize(df.iloc[:, 41])[0])
    else:
        print("  biodegradation: raw file not found")

    # Ceramic
    cer = glob.glob(os.path.join(RAW, "*eramic*.csv"))
    if cer:
        c = pd.read_csv(cer[0])
        drop = [col for col in c.columns if col.strip().lower() in ("ceramic name", "part")]
        y = pd.factorize(c[[col for col in c.columns if col.strip().lower() == "part"][0]])[0]
        _write("ceramic", c.drop(columns=drop), y)
    else:
        print("  ceramic: raw file not found")


if __name__ == "__main__":
    print("Building cached CSVs from data/uci/raw/ ...")
    main()
