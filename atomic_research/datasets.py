"""Raw benchmark populations and label-blind discovery/validation/test splits.

Real-data contrasts are predeclared using annotations, as a scoped benchmark.
The subsequent row sampling, preprocessing, proposal and selection see no y.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import json
import warnings

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Dataset:
    X: np.ndarray
    y: np.ndarray
    names: list[str]
    reference_panel: tuple[int, ...] = ()
    reference_kind: str = "none"
    metadata: dict = field(default_factory=dict)


class DiscoveryScaler:
    """Median imputation then standardization, fitted on discovery rows only."""

    def fit(self, X):
        X = np.asarray(X, dtype=float)
        X = np.where(np.isfinite(X), X, np.nan)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            self.median = np.nanmedian(X, axis=0)
        self.median = np.nan_to_num(self.median)
        filled = np.where(np.isfinite(X), X, self.median)
        self.mean = filled.mean(axis=0)
        self.scale = filled.std(axis=0)
        self.scale[self.scale < 1e-12] = 1.0
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=float)
        return (np.where(np.isfinite(X), X, self.median) - self.mean) / self.scale

    def to_dict(self):
        return {k: getattr(self, k).tolist() for k in ("median", "mean", "scale")}


def split_rows(n: int, seed: int):
    """Fixed 50/25/25 split, without stratification or label-dependent retries."""
    if n < 40:
        raise ValueError("At least 40 independent rows required for three-way diagnostics")
    order = np.random.default_rng(seed).permutation(n)
    return order[:n // 2], order[n // 2:3 * n // 4], order[3 * n // 4:]


def _file_info(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return {"path": str(path.relative_to(ROOT)), "sha256": h.hexdigest()}


def synthetic(case: str, n=480, p=50, signal_features=5, seed=0, separation=3.0):
    """Two-group controls; planted columns shuffled so names do not reveal them.

    mean_shift: norm of the difference between group means is separation.
    shells: two spherical surfaces with radii 1 and 2; nuisance has the SAME
    univariate distribution as each signal coordinate but independent draws.
    All proper subsets of a shell can retain some signal: no parity claim.
    """
    if n < 40 or not 1 <= signal_features <= p:
        raise ValueError("Need n>=40 and 1<=signal_features<=p")
    rng = np.random.default_rng(seed)
    s = signal_features
    y = rng.integers(0, 2, n)
    X = rng.normal(size=(n, p))
    reference = tuple(range(s))
    kind = "planted"
    if case == "mean_shift":
        X[:, :s] += (2 * y - 1)[:, None] * separation / (2 * np.sqrt(s))
    elif case == "shells":
        if s < 2:
            raise ValueError("shells needs at least two signal features")
        direction = rng.normal(size=(n, s))
        direction /= np.linalg.norm(direction, axis=1, keepdims=True)
        X[:, :s] = direction * (1 + y + rng.normal(0, .035, n))[:, None]
        # Independently generated population marginals; never shuffle across splits.
        for j in range(s, p):
            coordinate = rng.normal(size=n)
            norm2 = coordinate**2 + rng.chisquare(s - 1, n)
            radius = 1 + rng.integers(0, 2, n) + rng.normal(0, .035, n)
            X[:, j] = coordinate / np.sqrt(norm2) * radius
    elif case == "bimodal":
        X[:, 0] += (2 * y - 1) * 3.0
        reference = (0,)
    elif case in ("null_independent", "null_correlated"):
        y = np.zeros(n, dtype=int)
        reference, kind = tuple(range(min(2, p))), "negative_control"
        if case == "null_correlated":
            X = np.sqrt(.8) * rng.normal(size=(n, 1)) + np.sqrt(.2) * X
    else:
        raise ValueError(f"Unknown synthetic case: {case}")
    permutation = rng.permutation(p)
    inverse = np.argsort(permutation)
    return Dataset(X[:, permutation], y, [f"f{j:04d}" for j in range(p)],
                   tuple(sorted(int(inverse[j]) for j in reference)), kind,
                   {"case": case, "n": n, "p": p, "signal_features": s,
                    "separation": separation, "generator_seed": seed,
                    "sampling_unit": "independent generated observation",
                    "reference_is_unique_minimal_panel": False})


def load_dataset(case: str, n=480, p=50, signal_features=5, seed=0,
                 separation=3.0, contrast=None):
    if case not in ("metabric", "levine", "mice"):
        return synthetic(case, n, p, signal_features, seed, separation)
    import pandas as pd
    reference_names = []
    if case == "metabric":
        contrast = contrast or "lumA_lumB"
        groups = {"lumA_lumB": (["LumA"], ["LumB"]),
                  "basal_luminal": (["Basal"], ["LumA", "LumB"]),
                  "her2_luminal": (["Her2"], ["LumA", "LumB"]),
                  "claudinlow_basal": (["claudin-low"], ["Basal"])}
        a, b = groups[contrast]
        path = ROOT / "data/brca_metabric/reduced_pam50_plus200.csv"
        frame = pd.read_csv(path, index_col=0)
        if not frame.index.is_unique:
            raise ValueError("Duplicate METABRIC sample identifiers; group before splitting")
        labels = frame.pop("CLAUDIN_SUBTYPE")
        keep = labels.isin(a + b)
        X, y = frame.loc[keep].to_numpy(float), labels.loc[keep].isin(a).to_numpy(int)
        names = list(frame.columns)
        reference_names = json.loads(path.with_suffix(".meta.json").read_text())["pam50_found"]
        unit = "sample/patient identifier in cached matrix; no new cohort replication"
        note = ("PAM50-enriched 250-gene matrix; PAM50 overlap is contextual, not a unique answer key. "
                "Cached feature-universe construction used an all-patient variance filter before this split. "
                "New imputation/scaling alone is discovery-fitted; this is a development dataset.")
    elif case == "levine":
        try:
            import flowio
        except ImportError as exc:
            raise ImportError("Levine requires: .venv-research/Scripts/python.exe -m pip install flowio") from exc
        contrast = contrast or "cd4t_cd8t"
        groups = {"cd4t_cd8t": ((7, 8), ["CD4", "CD8"]),
                  "basophil_pdc": ((1, 11), ["HLA-DR", "CD123"]),
                  "nk16neg_nk16pos": ((2, 3), ["CD16", "CD7"]),
                  "preb_prob": ((13, 14), ["CD34", "CD19"]),
                  "monocyte_bcell": ((10, 9), ["CD19", "CD64"])}
        pops, reference_names = groups[contrast]
        path = ROOT / "data/Levine_32dim.fcs"
        fd = flowio.FlowData(str(path))
        values = np.asarray(fd.events).reshape(-1, fd.channel_count)
        columns = [fd.text[f"p{i}n"] for i in range(1, fd.channel_count + 1)]
        excluded = {"Time", "Cell_length", "DNA1", "DNA2", "Viability",
                    "file_number", "event_number", "label", "individual"}
        names = [c for c in columns if c not in excluded]
        labels = values[:, columns.index("label")]
        keep = np.isfinite(labels) & np.isin(labels, pops)
        X = np.arcsinh(values[np.ix_(keep, [columns.index(c) for c in names])] / 5)
        y = (labels[keep] == pops[0]).astype(int)
        unit = "cell within existing specimen(s); cell holdout is NOT donor replication"
        note = "Population-name mapping is repo-derived; marker set is contextual, not uniquely necessary"
    else:
        contrast = contrast or "Genotype"
        path = ROOT / "data/uci/raw/mice+protein+expression/Data_Cortex_Nuclear.cached.csv"
        if path.exists():
            frame = pd.read_csv(path)
        else:
            path = path.with_name("Data_Cortex_Nuclear.xls")
            frame = pd.read_excel(path)
        if contrast not in ("Genotype", "Treatment", "Behavior"):
            raise ValueError("Mice single-node cases require a binary factor")
        animal = frame.MouseID.astype(str).str.rsplit("_", n=1).str[0]
        if (frame.groupby(animal)[contrast].nunique() != 1).any():
            raise ValueError("Within-animal labels inconsistent")
        numeric = frame.select_dtypes("number").groupby(animal).median()
        labels = frame.groupby(animal)[contrast].first().loc[numeric.index]
        X, y, names = numeric.to_numpy(float), pd.Categorical(labels).codes, list(numeric.columns)
        unit = "animal, median of technical replicates"
        note = "Only 72 independent animals; small held-out groups limit geometric diagnostics"
    available = len(X)
    take = np.random.default_rng(seed).permutation(available)[:min(n, available)]
    reference = tuple(i for i, name in enumerate(names) if name in reference_names)
    return Dataset(X[take], y[take], names, reference,
                   "contextual_reference" if reference else "none",
                   {"case": case, "contrast": contrast, "n": len(take), "p": len(names),
                    "available_rows": available, "sampling_unit": unit, "note": note,
                    "population_filter_uses_labels": True, "row_sampling_uses_labels": False,
                    "source": _file_info(path), "sample_indices": take.tolist()})
