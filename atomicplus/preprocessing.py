"""Preprocessing exactly as the paper specifies (§3.1): 2-NN imputation of missing
values, then min-max scaling of every variable to [0, 1]."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler


def knn_impute(data, n_neighbors: int = 2):
    arr = KNNImputer(n_neighbors=n_neighbors).fit_transform(np.asarray(data, dtype=float))
    if isinstance(data, pd.DataFrame):
        return pd.DataFrame(arr, columns=data.columns, index=data.index)
    return arr


def minmax01(data):
    arr = MinMaxScaler().fit_transform(np.asarray(data, dtype=float))
    if isinstance(data, pd.DataFrame):
        return pd.DataFrame(arr, columns=data.columns, index=data.index)
    return arr


def preprocess(data, n_neighbors: int = 2):
    """2-NN impute then scale to [0, 1] (paper §3.1)."""
    return minmax01(knn_impute(data, n_neighbors))
