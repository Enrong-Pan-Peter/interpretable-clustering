"""Run bounded, reproducible feature-panel experiments. See docs/research plan."""
from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from atomic_research.experiment import run


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=["score-audit", "search", "null-audit"])
    p.add_argument("--dataset", default="mean_shift", choices=["mean_shift", "shells", "bimodal", "null_independent", "null_correlated", "metabric", "levine", "mice"])
    p.add_argument("--contrast")
    p.add_argument("--n", type=int, default=480, help="Total rows before discovery/validation/test split")
    p.add_argument("--p", type=int, default=50, help="Synthetic feature count; real data keep all loaded features")
    p.add_argument("--signal-features", type=int, default=5)
    p.add_argument("--separation", type=float, default=3.0, help="Mean difference L2 norm in mean_shift")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--max-features", type=int, default=8)
    p.add_argument("--budget", type=int, default=100, help="Unique panel score cap per search method; random bank size in score-audit")
    p.add_argument("--reference-budget", type=int, default=32)
    p.add_argument("--methods", nargs="+", default=["random", "forward", "evolutionary", "soft_graph", "sparse_kmeans"], choices=["random", "forward", "evolutionary", "soft_graph", "sparse_kmeans"])
    p.add_argument("--objective", choices=["consistent", "legacy", "graphcut", "density"], default="consistent")
    p.add_argument("--splitter", choices=["spectral", "mst"], default="spectral")
    p.add_argument("--k", type=int, default=10)
    p.add_argument("--steps", type=int, default=80)
    p.add_argument("--restarts", type=int, default=3)
    p.add_argument("--proposal-rows", type=int, default=128, help="Soft graph optimization subsample only")
    p.add_argument("--proposal-seconds", type=float, default=None, help="Optional proposal optimizer cap; panel scoring extra")
    p.add_argument("--fidelity", type=float, default=.95, help="Validation ARI tolerance for backward compression")
    p.add_argument("--permutations", type=int, default=39)
    p.add_argument("--output", default="results/research_diagnostics")
    return p


if __name__ == "__main__":
    cli = parser()
    args = cli.parse_args()
    for name in ("n", "p", "signal_features", "max_features", "budget", "reference_budget", "k", "steps", "restarts", "proposal_rows", "permutations"):
        if getattr(args, name) < 1:
            cli.error(f"--{name.replace('_', '-')} must be positive")
    if not 0 < args.fidelity <= 1:
        cli.error("--fidelity must be in (0,1]")
    run(args)
