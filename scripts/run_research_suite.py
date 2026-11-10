"""Serial experiment presets; stop with Ctrl+C, completed run folders survive."""
from pathlib import Path
import argparse
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def jobs(suite, seeds):
    if suite in ("pilot", "fitness"):
        for case in ("null_independent", "null_correlated", "bimodal"):
            yield ["null-audit", "--dataset", case, "--seed", str(seeds[0]), "--permutations", "39"]
        for case in ("mean_shift", "shells", "metabric", "levine"):
            yield ["score-audit", "--dataset", case, "--seed", str(seeds[0]), "--budget", "64"]
    if suite == "pilot":
        for seed in seeds:
            for case in ("mean_shift", "shells", "metabric", "levine"):
                yield ["search", "--dataset", case, "--seed", str(seed), "--budget", "100"]
    if suite == "scaling":
        for seed in seeds:
            for case in ("mean_shift", "shells"):
                for p in (50, 200):
                    for s in (5, 8):
                        yield ["search", "--dataset", case, "--p", str(p), "--signal-features", str(s),
                               "--max-features", "12", "--n", "800", "--budget", "160", "--seed", str(seed)]


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--suite", choices=["pilot", "fitness", "scaling"], default="pilot")
    cli.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    cli.add_argument("--output", default="results/research_diagnostics")
    cli.add_argument("--list-only", action="store_true", help="Show exact jobs without running")
    args = cli.parse_args()
    commands = list(jobs(args.suite, args.seeds))
    print(f"{args.suite}: {len(commands)} serial jobs; output {args.output}", flush=True)
    started = time.perf_counter()
    for index, options in enumerate(commands, 1):
        print(f"[{index}/{len(commands)}] " + " ".join(options), flush=True)
        if not args.list_only:
            subprocess.run([sys.executable, str(ROOT / "scripts/run_research_diagnostics.py"),
                            *options, "--output", args.output], cwd=ROOT, check=True)
    if not args.list_only:
        subprocess.run([sys.executable, str(ROOT / "scripts/summarize_research_results.py"),
                        "--root", args.output], cwd=ROOT, check=True)
        print(f"Suite complete in {(time.perf_counter() - started)/60:.1f} minutes", flush=True)


if __name__ == "__main__":
    main()
