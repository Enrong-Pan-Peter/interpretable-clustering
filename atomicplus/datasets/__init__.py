"""Datasets for ATOMIC+.

`synthetic` — clean known-answer generators (labels + true defining features) for
validation and the fairness demo. `uci` — the paper's seven UCI benchmark sets via
`ucimlrepo` (with a local-CSV cache/fallback).
"""
from . import synthetic  # noqa: F401

__all__ = ["synthetic"]
