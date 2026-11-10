"""Run the planned moment/kernel x best/first feature-set search comparison."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_research_radial_search import main as run


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not any(arg.split("=")[0] in {"--suite", "--resume"} for arg in args):
        args = ["--suite", "ablation", *args]
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
