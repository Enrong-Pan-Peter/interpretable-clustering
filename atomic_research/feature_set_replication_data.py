"""Frozen synthetic conditions for the feature-set replication/stress batch.

The original generator remains unchanged. Feature maps and target labels are
diagnostic metadata; the search must receive observation matrices only.
"""
from __future__ import annotations

import numpy as np

from .radial_diagnostics import CASES, generate_synthetic_splits


CONDITIONS = ("baseline", "more_nuisance", "weak_separation", "dependent_nuisance")


def _integer(name, value, minimum):
    if (isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer))
            or value < minimum):
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _seed_record(sequence):
    return {"entropy": sequence.entropy, "spawn_key": list(sequence.spawn_key)}


def _weak_shell_block(rng, n, dimension):
    """Same random draw order as the original shell population."""
    direction = rng.normal(size=(n, dimension))
    direction /= np.maximum(np.linalg.norm(direction, axis=1, keepdims=True), 1e-15)
    labels = rng.integers(0, 2, size=n)
    radius = np.where(labels == 0, 2.0, 3.0) * np.sqrt(dimension)
    radius *= np.exp(rng.normal(-.5 * .12 ** 2, .12, size=n))
    return direction * radius[:, None], labels


def generate_replication_splits(case, dimension, p, n_fit, n_validation, n_test, seed, *,
                                condition="baseline"):
    """Return the original generator schema under one fixed population condition.

    The returned fit block may subsequently be divided into fit/search rows by
    the experiment runner. Baseline and more_nuisance delegate exactly to the
    original generator; more_nuisance increases feature count only through the
    caller's p argument. The other two conditions apply only to shell cases.

    Weak separation changes radii to [2,3]*sqrt(d) and log-radius SD to .12.
    Dependent nuisance preserves the baseline signal exactly, replacing 2*d
    nuisance coordinates with two independent, single equicorrelated Gaussian
    blocks. Their population coordinate variance matches the signal, although
    their full marginal distributions differ. No distractor labels are created.
    """
    if not isinstance(case, str) or case not in CASES:
        raise ValueError("unsupported population case")
    if not isinstance(condition, str) or condition not in CONDITIONS:
        raise ValueError("unsupported replication condition")
    dimension = _integer("dimension", dimension, 2)
    p = _integer("p", p, dimension)
    n_fit = _integer("n_fit", n_fit, 2)
    n_validation = _integer("n_validation", n_validation, 2)
    n_test = _integer("n_test", n_test, 2)
    seed = _integer("seed", seed, 0)
    if condition in {"weak_separation", "dependent_nuisance"} and case != "shells":
        raise ValueError(f"{condition} is defined only for shells")
    if condition == "dependent_nuisance" and p < 3 * dimension:
        raise ValueError("dependent_nuisance requires p >= 3*dimension")

    generated = generate_synthetic_splits(case, dimension, p, n_fit, n_validation, n_test, seed)
    population = generated["population"]
    population["condition"] = condition
    if condition in {"baseline", "more_nuisance"}:
        return generated

    permutation = np.asarray(generated["feature_map"]["original_column_to_latent_column"])
    location, scale = population["location"], population["scale"]
    split_names = ("fit", "validation", "test")
    sizes = (n_fit, n_validation, n_test)
    if condition == "weak_separation":
        # Replaying with the original split streams keeps the population map,
        # direction draws and target label draws paired with baseline data.
        children = np.random.SeedSequence(seed).spawn(4)
        for name, n, child in zip(split_names, sizes, children[1:]):
            rng = np.random.default_rng(child)
            signal, labels = _weak_shell_block(rng, n, dimension)
            nuisance = np.empty((n, p - dimension))
            for j in range(p - dimension):
                nuisance[:, j] = _weak_shell_block(rng, n, dimension)[0][:, 0]
            raw = np.column_stack((signal, nuisance))
            generated["splits"][name] = {"X": location + scale * raw[:, permutation], "y": labels}
        population.update(shell_radii_per_sqrt_dimension=[2.0, 3.0],
                          shell_log_radius_sd=.12,
                          signal_coordinate_variance_before_transform=float(6.5 * np.exp(.12 ** 2)),
                          nuisance_marginal_matching="exact one-coordinate population marginals; independent draws",
                          stress_scope="closer and thicker shell bands; same feature map and random draw order")
        return generated

    rho = .7
    # If log-radius noise is N(-s²/2,s²), E[exp(2*noise)] = exp(s²).
    # Uniform sphere directions have E[u_j²]=1/d, cancelling the d in R².
    signal_variance = float(.5 * (1.5 ** 2 + 3.5 ** 2) * np.exp(.06 ** 2))
    latent_blocks = [list(range(dimension, 2 * dimension)), list(range(2 * dimension, 3 * dimension))]
    supports = [np.flatnonzero((permutation >= block[0]) & (permutation <= block[-1])).tolist()
                for block in latent_blocks]
    # The baseline consumes children 0..3. Independent child 4 leaves every
    # baseline signal observation, target label and unchanged nuisance intact.
    distractor_root = np.random.SeedSequence(seed).spawn(5)[4]
    for name, n, split_sequence in zip(split_names, sizes, distractor_root.spawn(3)):
        block_sequences = split_sequence.spawn(2)
        for latent, support, block_sequence in zip(latent_blocks, supports, block_sequences):
            rng = np.random.default_rng(block_sequence)
            common = rng.normal(size=(n, 1))
            residual = rng.normal(size=(n, dimension))
            block = np.sqrt(signal_variance) * (np.sqrt(rho) * common + np.sqrt(1 - rho) * residual)
            component_order = permutation[support] - latent[0]
            generated["splits"][name]["X"][:, support] = location + scale * block[:, component_order]
        generated["split_seeds"][name]["distractor_blocks"] = [_seed_record(s) for s in block_sequences]

    population.update(
        nuisance="two independent correlated Gaussian blocks; remaining coordinates from independent shell blocks",
        nuisance_marginal_matching="Gaussian blocks match population mean/variance only; distributions differ from shell marginals",
        signal_coordinate_variance_before_transform=signal_variance,
        distractor_supports=supports,
        distractor_latent_column_blocks=latent_blocks,
        remaining_matched_nuisance_support=np.flatnonzero(permutation >= 3 * dimension).tolist(),
        distractor_seed_root=_seed_record(distractor_root),
        dependent_nuisance={
            "number_of_blocks": 2, "block_dimension": dimension, "rho": rho,
            "distribution": "single multivariate Gaussian per block",
            "mean_before_transform": 0.0, "mean_after_transform": location,
            "coordinate_variance_before_transform": signal_variance,
            "coordinate_variance_after_transform": float(scale ** 2 * signal_variance),
            "independent_blocks": True, "independent_of_signal_and_labels": True,
            "alternative_cluster_labels_created": False,
        },
    )
    return generated
