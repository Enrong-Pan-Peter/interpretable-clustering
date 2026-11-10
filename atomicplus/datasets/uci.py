"""The paper's seven UCI datasets (§3.1), loaded via `ucimlrepo` with a local-CSV cache.

Usage (on a machine with internet):

    from atomicplus.datasets import uci
    X, y = uci.load_uci("ionosphere")          # fetches + caches to data/uci/
    uci.fetch_all()                             # download & cache all seven

`ucimlrepo` IDs are best-known values; `load_uci` reports clearly if a fetch fails
so you can drop a CSV into the cache dir instead. Features are coerced to numeric
(non-numeric columns dropped); the target is factorised to integer codes.
"""
from __future__ import annotations

import os
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

# name -> UCI ML Repository dataset id (for ucimlrepo.fetch_ucirepo)
PAPER_UCI: Dict[str, int] = {
    "biodegradation": 254,    # QSAR biodegradation
    "ceramic": 583,           # Chemical Composition of Ceramic Samples
    "cervical_cancer": 383,   # Cervical Cancer (Risk Factors)
    "glass": 42,              # Glass Identification
    "ionosphere": 52,         # Ionosphere
    "ozone": 172,             # Ozone Level Detection (8-hour set)
    "wholesale": 292,         # Wholesale customers
}

DEFAULT_CACHE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "uci")


def _numeric_features(df: pd.DataFrame) -> pd.DataFrame:
    num = df.apply(pd.to_numeric, errors="coerce")
    num = num.dropna(axis=1, how="all")           # drop fully non-numeric columns
    return num


def load_uci(name: str, cache_dir: str = DEFAULT_CACHE, force_download: bool = False
             ) -> Tuple[pd.DataFrame, Optional[np.ndarray]]:
    """Return (features_df, target_codes | None). Uses the CSV cache when present."""
    cache_dir = os.path.abspath(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)
    fpath = os.path.join(cache_dir, f"{name}.csv")
    ypath = os.path.join(cache_dir, f"{name}_target.csv")

    if os.path.exists(fpath) and not force_download:
        X = _numeric_features(pd.read_csv(fpath))
        y = pd.read_csv(ypath).iloc[:, 0].to_numpy() if os.path.exists(ypath) else None
        return X, y

    if name not in PAPER_UCI:
        raise KeyError(f"unknown dataset {name!r}; known: {sorted(PAPER_UCI)}")
    try:
        from ucimlrepo import fetch_ucirepo
    except ImportError as e:
        raise ImportError("pip install ucimlrepo  (or place a CSV at %s)" % fpath) from e

    ds = fetch_ucirepo(id=PAPER_UCI[name])
    X = _numeric_features(ds.data.features)
    y = None
    if ds.data.targets is not None and ds.data.targets.shape[1] >= 1:
        y = pd.factorize(ds.data.targets.iloc[:, 0])[0]
    X.to_csv(fpath, index=False)
    if y is not None:
        pd.Series(y, name="target").to_csv(ypath, index=False)
    return X, y


def fetch_all(cache_dir: str = DEFAULT_CACHE) -> Dict[str, str]:
    """Download & cache all seven datasets. Returns {name: status}."""
    status = {}
    for name in PAPER_UCI:
        try:
            X, y = load_uci(name, cache_dir=cache_dir, force_download=True)
            status[name] = f"ok  ({X.shape[0]} rows x {X.shape[1]} numeric feats, "
            status[name] += "labels" if y is not None else "no labels"
            status[name] += ")"
        except Exception as e:  # noqa: BLE001
            status[name] = f"FAILED: {type(e).__name__}: {e}"
    return status
