"""Download & cache the paper's seven UCI datasets via ucimlrepo.

Run once (needs internet):
    pip install ucimlrepo
    python scripts/fetch_uci.py

Datasets are cached as CSVs under data/uci/ so later runs are offline. Any dataset
whose id fails to fetch is reported; drop a CSV named <name>.csv (+ <name>_target.csv)
into data/uci/ to supply it manually.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from atomicplus.datasets import uci  # noqa: E402


def main():
    print("Fetching the paper's 7 UCI datasets into data/uci/ ...\n")
    status = uci.fetch_all()
    width = max(len(n) for n in status)
    for name, msg in status.items():
        print(f"  {name.ljust(width)}  {msg}")
    ok = sum(1 for m in status.values() if m.startswith("ok"))
    print(f"\n{ok}/{len(status)} datasets cached. IDs used: {uci.PAPER_UCI}")


if __name__ == "__main__":
    main()
