"""Experimental native radial-band models on fixed original-feature panels.

This is a supplied-panel mechanism, not an autonomous clustering algorithm.
Spatial densities are normalized in the panel's dimension. A Gaussian marginal
from one frozen joint background permits a common-full-space density comparison.
Neither a likelihood improvement nor a fitted density valley is a calibrated
test of cluster existence. See docs/research/trait-first-method-review-2026-10-14.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from time import perf_counter

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import minimize
from scipy.signal import find_peaks
from scipy.special import expit, gammaln, logsumexp
from sklearn.covariance import LedoitWolf


def _matrix(X):
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or not X.shape[1] or not np.isfinite(X).all():
        raise ValueError("X must be a finite two-dimensional matrix; no implicit imputation")
    return X


def _support(support, p):
    raw = np.asarray(support)
    if raw.ndim != 1 or not len(raw) or raw.dtype.kind not in 'iu':
        raise ValueError("support must be a nonempty one-dimensional integer array")
    if len(set(raw.tolist())) != len(raw) or np.any(raw < 0) or np.any(raw >= p):
        raise ValueError("support must contain unique, in-range columns")
    return raw.astype(int)


@lru_cache(maxsize=8)
def _quadrature(order):
    if order < 32:
        raise ValueError("quadrature order must be at least 32")
    return leggauss(order)


def _normalizer_stats(dimension, location, width, order=128):
    """Log Z and analytic log-Z derivatives using radius quadrature.

    Integrate in y=r/sqrt(width), truncating |y²-location/width| at 14
    where possible. Radius powers are integral even for odd dimensions, so
    there is no endpoint singularity. The model currently restricts location
    to nonnegative values. Numerical checks use an independent infinite-range
    integral, rather than this same truncation.
    """
    if (not isinstance(dimension, (int, np.integer)) or dimension < 1
            or not np.isfinite(location) or location < 0
            or not np.isfinite(width) or width <= 0):
        raise ValueError("dimension >= 1, location >= 0 and width > 0 required")
    nodes, weights = _quadrature(order)
    ratio = location / width
    lower, upper = np.sqrt(max(0., ratio - 14.)), np.sqrt(ratio + 14.)
    y = lower + (nodes + 1.) * (upper - lower) / 2.
    delta = y * y - ratio
    log_terms = np.log(weights) + (dimension - 1) * np.log(y) - .5 * delta**2
    log_sum = logsumexp(log_terms)
    normalized = np.exp(log_terms - log_sum)
    log_area = np.log(2.) + dimension / 2. * np.log(np.pi) - gammaln(dimension / 2.)
    log_z = (log_area + dimension / 2. * np.log(width)
             + np.log((upper - lower) / 2.) + log_sum)
    # Derivatives in the original t=r² coordinate, not a radius histogram.
    return float(log_z), float(normalized @ delta / width), float(normalized @ delta**2)


def log_normalizer(dimension, location, width, order=128):
    return _normalizer_stats(dimension, location, width, order)[0]


def _component_logpdf(t, locations, width, log_z):
    return -.5 * ((t[:, None] - locations[None, :]) / width)**2 - log_z[None, :]


@dataclass
class RadialPanel:
    input_feature_count: int
    support: np.ndarray
    center: np.ndarray
    scale: np.ndarray
    locations: np.ndarray
    width: float
    weights: np.ndarray
    log_z: np.ndarray
    diagnostics: dict

    @property
    def components(self):
        return len(self.locations)

    def squared_radius(self, X):
        X = _matrix(X)
        if X.shape[1] != self.input_feature_count:
            raise ValueError("input feature count differs from fitted model")
        return np.sum(((X[:, self.support] - self.center) / self.scale)**2, axis=1)

    def component_logpdf(self, X):
        return (_component_logpdf(self.squared_radius(X), self.locations, self.width, self.log_z)
                - np.log(self.scale).sum())

    def logpdf(self, X):
        return logsumexp(self.component_logpdf(X) + np.log(self.weights), axis=1)

    def rule(self):
        result = {
            "type": "native_squared_radius", "input_feature_count": self.input_feature_count,
            "support": self.support.tolist(),
            "feature_names": [f"f{j:04d}" for j in self.support],
            "center": self.center.tolist(), "scale": self.scale.tolist(),
            "missing_values": "reject nonfinite input", "tie_label": 0,
            "cluster_existence_established": False,
        }
        if self.components == 1 or self.locations[1] == self.locations[0]:
            result.update(constant_label=int(np.argmax(self.weights)), threshold=None)
        else:
            difference = self.locations[1] - self.locations[0]
            threshold = (float(self.locations.mean()) + self.width**2 / difference
                         * (np.log(self.weights[0] / self.weights[1]) + self.log_z[1] - self.log_z[0]))
            result.update(constant_label=None, threshold=float(threshold))
        result["assignment"] = "outer label 1 if sum(((x_j-center_j)/scale_j)^2) > threshold; otherwise 0"
        return result

    def predict(self, X):
        return predict_radial_rule(self.rule(), X)

    def spatial_profile(self, points=1201):
        """Fitted shape diagnostics, not a test of a population density valley.

        Raw density differs from standardized density by a constant Jacobian.
        Radial probability density additionally has the sphere-area/volume
        factor. Only the spatial profile is used to locate the fitted bands.
        """
        if points < 32:
            raise ValueError("at least 32 profile grid points required")
        high = np.sqrt(float(self.locations.max()) + 10 * self.width)
        radii = np.linspace(0., high, points)
        spatial = logsumexp(_component_logpdf(radii**2, self.locations, self.width, self.log_z)
                            + np.log(self.weights), axis=1)
        peaks = list(find_peaks(spatial)[0])
        if spatial[0] > spatial[1]:
            peaks.insert(0, 0)
        valley_ratio = None
        if len(peaks) >= 2:
            # Retain the two largest spatial modes, ordered along the radius.
            chosen = sorted(sorted(peaks, key=lambda i: spatial[i], reverse=True)[:2])
            valley = float(np.min(spatial[chosen[0]:chosen[1] + 1]))
            valley_ratio = float(np.exp(valley - min(spatial[chosen[0]], spatial[chosen[1]])))
        dimension = len(self.support)
        log_area = np.log(2.) + dimension / 2. * np.log(np.pi) - gammaln(dimension / 2.)
        with np.errstate(divide='ignore'):
            radial = spatial + log_area + (dimension - 1) * np.log(np.maximum(radii, np.finfo(float).tiny))
        # Represent log(0) as JSON null rather than nonstandard -Infinity.
        radial_list = radial.tolist()
        if dimension > 1:
            radial_list[0] = None
        return {"radii": radii.tolist(), "log_spatial_density": spatial.tolist(),
                "log_radial_density": radial_list, "spatial_mode_count": len(peaks),
                "spatial_mode_radii": radii[peaks].tolist(),
                "two_spatial_modes": len(peaks) >= 2, "valley_ratio": valley_ratio,
                "profile_scope": "standardized selected coordinates; numerical fitted-shape diagnostic only"}

    def to_dict(self):
        return {"method": "fixed_panel_radial_band_v1", "input_feature_count": self.input_feature_count,
                "support": self.support.tolist(), "center": self.center.tolist(), "scale": self.scale.tolist(),
                "locations": self.locations.tolist(), "width": float(self.width),
                "weights": self.weights.tolist(), "log_z": self.log_z.tolist(),
                "diagnostics": self.diagnostics, "rule": self.rule()}

    @classmethod
    def from_dict(cls, saved):
        model = cls(int(saved["input_feature_count"]), np.asarray(saved["support"], dtype=int),
                    np.asarray(saved["center"], dtype=float), np.asarray(saved["scale"], dtype=float),
                    np.asarray(saved["locations"], dtype=float), float(saved["width"]),
                    np.asarray(saved["weights"], dtype=float), np.asarray(saved["log_z"], dtype=float),
                    saved.get("diagnostics", {}))
        _support(model.support, model.input_feature_count)
        finite = np.concatenate([model.center, model.scale, model.locations, model.weights,
                                 model.log_z, [model.width]])
        if (not np.isfinite(finite).all() or model.components not in (1, 2)
                or len(model.center) != len(model.support) or len(model.scale) != len(model.support)
                or len(model.weights) != model.components or len(model.log_z) != model.components
                or np.any(model.scale <= 0) or model.width <= 0
                or np.any(model.locations < 0)
                or np.any(model.weights <= 0) or not np.isclose(model.weights.sum(), 1.)
                or np.any(np.diff(model.locations) < 0)):
            raise ValueError("invalid saved radial model")
        return model


def predict_radial_rule(rule, X):
    X = _matrix(X)
    if X.shape[1] != rule["input_feature_count"]:
        raise ValueError("input feature count differs from exported rule")
    support = _support(rule["support"], X.shape[1])
    if rule["constant_label"] is not None:
        return np.full(len(X), rule["constant_label"], dtype=int)
    radius = np.sum(((X[:, support] - np.asarray(rule["center"])) / np.asarray(rule["scale"]))**2, axis=1)
    return (radius > rule["threshold"]).astype(int)


def fit_radial_panel(X_fit, support, components=2, *, maxiter=160, quadrature_order=128):
    """Deterministic multi-start maximum likelihood on discovery rows only.

    Means/standard deviations are frozen discovery preprocessing, not jointly
    optimized centres. Fits use nonnegative band locations, a discovery-fixed
    width floor, and 0.05 <= mixture weight <= 0.95. These are prototype model
    restrictions; neither weight bounds nor this forced component count imply
    actual native assignment occupancy or evidence of distinct clusters.
    """
    started = perf_counter()
    X = _matrix(X_fit)
    S = _support(support, X.shape[1])
    if len(X) < 20 or components not in (1, 2) or maxiter < 1:
        raise ValueError("at least 20 discovery rows, one/two components, and positive maxiter required")
    _quadrature(quadrature_order)
    center, scale = X[:, S].mean(0), X[:, S].std(0)
    if np.any(scale <= np.finfo(float).eps):
        raise ValueError("constant selected columns cannot define a radial panel")
    t = np.sum(((X[:, S] - center) / scale)**2, axis=1)
    dimension = len(S)
    mean_t, sd_t = float(t.mean()), float(t.std())
    b_floor = max(.02 * float(np.median(t)), .001)
    b_upper = max(4 * sd_t, 2 * mean_t, 10 * b_floor)
    a_upper = max(float(np.quantile(t, .995)) * 1.25, 4 * mean_t)
    bounds = [(0., a_upper)] * components + [(np.log(b_floor), np.log(b_upper))]
    if components == 2:
        bounds.append((float(np.log(.05 / .95)), float(np.log(.95 / .05))))

    def unpack(theta):
        a = theta[:components]
        b = float(np.exp(theta[components]))
        weights = np.ones(1) if components == 1 else np.array([1. - expit(theta[-1]), expit(theta[-1])])
        return a, b, weights

    def objective(theta):
        a, b, weights = unpack(theta)
        stats = np.asarray([_normalizer_stats(dimension, ai, b, quadrature_order) for ai in a])
        logs = _component_logpdf(t, a, b, stats[:, 0]) + np.log(weights)
        logpdf = logsumexp(logs, axis=1)
        responsibility = np.exp(logs - logpdf[:, None])
        delta = (t[:, None] - a) / b
        da = np.mean(responsibility * (delta / b - stats[:, 1]), axis=0)
        db = np.mean(np.sum(responsibility * (delta**2 - stats[:, 2]), axis=1))
        gradient = [*da, db]
        if components == 2:
            gradient.append(float(np.mean(responsibility[:, 1]) - weights[1]))
        return -float(logpdf.mean()), -np.asarray(gradient)

    initial = []
    if components == 1:
        for a, b in [(mean_t, sd_t), (max(0., mean_t - sd_t), sd_t), (0., mean_t)]:
            initial.append([a, np.log(np.clip(b, b_floor, b_upper))])
    else:
        for quantiles in ((.2, .8), (.35, .65), (.1, .6)):
            a = np.quantile(t, quantiles)
            labels = t > a.mean()
            within = np.mean([np.var(t[labels == label]) if np.sum(labels == label) > 1 else sd_t**2
                              for label in (0, 1)])
            b = np.clip(np.sqrt(within), b_floor * 2., b_upper)
            initial.append([*a, np.log(b), 0.])
        # An equal-location start keeps the one-band-like region accessible.
        initial.append([mean_t, mean_t, np.log(np.clip(sd_t, b_floor, b_upper)), 0.])

    attempts, candidates = [], []
    for index, theta in enumerate(initial):
        theta = np.clip(theta, np.asarray(bounds)[:, 0], np.asarray(bounds)[:, 1])
        fit = minimize(objective, theta, jac=True, bounds=bounds, method='L-BFGS-B',
                       options={"maxiter": maxiter, "ftol": 1e-10, "gtol": 1e-6})
        attempts.append({"start": index, "success": bool(fit.success), "message": str(fit.message),
                         "iterations": int(fit.nit), "evaluations": int(fit.nfev), "loss": float(fit.fun)})
        if np.isfinite(fit.fun) and np.isfinite(fit.x).all():
            candidates.append((float(fit.fun), fit, index))
    if not candidates:
        raise RuntimeError("all radial fit starts failed to return a finite model")
    loss, chosen, index = min(candidates, key=lambda item: item[0])
    locations, width, weights = unpack(chosen.x)
    order = np.argsort(locations, kind='stable')
    locations, weights = locations[order], weights[order]
    log_z = np.asarray([log_normalizer(dimension, a, width, quadrature_order) for a in locations])
    diagnostic = {"optimizer_success": bool(chosen.success), "chosen_status": str(chosen.message),
                  "selected_start": index, "attempts": attempts,
                  "normalized_discovery_nll": loss, "quadrature_order": quadrature_order,
                  "quadrature_tail_in_squared_radius_widths": 14,
                  "location_upper_bound": a_upper, "width_bounds": [b_floor, b_upper],
                  "location_upper_bound_hit": bool(np.any(locations >= a_upper * (1 - 1e-6))),
                  "width_bound_hit": bool(width <= b_floor * (1 + 1e-6) or width >= b_upper * (1 - 1e-6)),
                  "mixing_weight_bound_hit": bool(components == 2 and np.min(weights) <= .050001),
                  "fit_seconds": perf_counter() - started,
                  "scope": "supplied-panel candidate fit; no autonomous support search or split certification"}
    result = RadialPanel(X.shape[1], S, center, scale, locations, width, weights, log_z, diagnostic)
    diagnostic["native_discovery_counts"] = np.bincount(result.predict(X), minlength=components).tolist()
    return result


@dataclass
class GaussianBackground:
    """One joint shrinkage-Gaussian fit; panel evaluation uses covariance marginals."""
    mean: np.ndarray
    covariance: np.ndarray
    shrinkage: float
    scale: np.ndarray

    @classmethod
    def fit(cls, X_fit):
        X = _matrix(X_fit)
        if len(X) < 3:
            raise ValueError("at least three discovery rows required")
        scale = X.std(0)
        if np.any(scale <= np.finfo(float).eps):
            raise ValueError("constant features not supported by the background")
        mean = X.mean(0)
        fitted = LedoitWolf(assume_centered=True).fit((X - mean) / scale)
        # Shrink in standardized coordinates so changing physical units does
        # not change the fitted background or the model comparison.
        covariance = fitted.covariance_ * scale[:, None] * scale[None, :]
        return cls(mean, covariance, float(fitted.shrinkage_), scale)

    def logpdf_panel(self, X, support):
        X = _matrix(X)
        if X.shape[1] != len(self.mean):
            raise ValueError("input feature count differs from background")
        S = _support(support, len(self.mean))
        covariance = self.covariance[np.ix_(S, S)]
        chol = np.linalg.cholesky(covariance)
        standardized = np.linalg.solve(chol, (X[:, S] - self.mean[S]).T)
        return -.5 * (len(S) * np.log(2 * np.pi) + 2 * np.log(np.diag(chol)).sum()
                      + np.sum(standardized**2, axis=0))

    def to_dict(self):
        return {"method": "joint_standardized_ledoit_wolf_gaussian_v1", "mean": self.mean.tolist(),
                "covariance": self.covariance.tolist(), "shrinkage": self.shrinkage,
                "scale": self.scale.tolist(), "scope": "one joint discovery fit; covariance submatrices are marginals"}
