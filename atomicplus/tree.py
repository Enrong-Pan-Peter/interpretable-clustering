"""Phase 4 - recursive interpretable tree (the product).

Greedy recursion: at each node run the persistence search on that node's points, take the
canonical split (highest persistence), and commit it only if it passes the acceptance gate
(persistence >= threshold and both sides >= min_cluster_size); otherwise the node is a leaf.
Each internal node records its own responsible feature set + persistence. Output is a single
hard partition (leaves) plus the annotated tree. Beam search and the null/stability gate are
Phase-4 follow-ups (see task #13).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import List, Optional

import numpy as np

from . import genome as gm
from .config import AtomicConfig
from .engine import atomic, Individual
from . import gate as _gate


@dataclass
class TreeNode:
    indices: np.ndarray            # indices into the ORIGINAL X of the points at this node
    depth: int
    persistence: float = 0.0       # S of the committed split (0 at a leaf)
    features: Optional[List[int]] = None   # responsible feature subset (None at a leaf)
    children: Optional[List["TreeNode"]] = None
    leaf_id: int = -1
    reason: str = ""
    gate: object = None               # why a leaf: min_size | max_depth | low_persistence | no_split

    @property
    def size(self) -> int:
        return len(self.indices)

    @property
    def is_leaf(self) -> bool:
        return self.children is None


@dataclass
class Tree:
    root: TreeNode
    n: int

    def leaves(self) -> List[TreeNode]:
        out: List[TreeNode] = []
        stack = [self.root]
        while stack:
            nd = stack.pop()
            if nd.is_leaf:
                out.append(nd)
            else:
                stack.extend(nd.children)
        return sorted(out, key=lambda nd: nd.leaf_id)

    def n_leaves(self) -> int:
        return sum(1 for _ in self.leaves())

    def labels(self) -> np.ndarray:
        lab = np.full(self.n, -1, dtype=int)
        for leaf in self.leaves():
            lab[leaf.indices] = leaf.leaf_id
        return lab

    def pretty(self, feature_names=None) -> str:
        def name(f):
            return feature_names[f] if feature_names is not None else f"f{f}"
        lines: List[str] = []

        def rec(nd, prefix):
            if nd.is_leaf:
                lines.append(f"{prefix}* leaf #{nd.leaf_id}  (n={nd.size}, {nd.reason})")
            else:
                feats = ", ".join(name(f) for f in nd.features)
                lines.append(f"{prefix}[split on {feats}]  persistence={nd.persistence:.2f}  n={nd.size}")
                rec(nd.children[0], prefix + "  |- ")
                rec(nd.children[1], prefix + "  |- ")
        rec(self.root, "")
        return "\n".join(lines)


def build_tree(X, config: Optional[AtomicConfig] = None, min_persistence: float = 1.02,
               max_depth: int = 6, min_node_size: Optional[int] = None,
               gate_mode: str = "stability", stability_min: float = 0.5,
               gate_n_sub: int = 5, gate_n_perm: int = 19, null_alpha: float = 0.05,
               beam: int = 1,
               node_seed: int = 0, rng: Optional[np.random.Generator] = None) -> Tree:
    X = np.asarray(X, dtype=float)
    config = config or AtomicConfig(fitness_mode="persistence", k_tilde=5,
                                    pop_size=40, mu=40, lam=24, n_gen=15, archive_rebuild_every=20,
                                    crossover_mode="set_based", mutation_mode="asymmetric")
    if config.fitness_mode != "persistence":
        config = replace(config, fitness_mode="persistence")
    mcs = config.min_cluster_size
    min_node = min_node_size if min_node_size is not None else 2 * mcs
    seed_counter = [node_seed]

    def next_seed() -> int:
        seed_counter[0] += 1
        return seed_counter[0]

    def _candidates(sub):
        """Top-`beam` DISTINCT 2-component partitions by persistence, drawn from the whole
        archive (not just the Pareto front) so beam has real alternatives -- including a
        correct-but-lower-persistence split that the front would hide behind a high trap."""
        out, seen = [], set()
        pairs = sorted(zip(sub.archive.genomes, sub.archive.evals), key=lambda ge: -ge[1].f)
        for g, ev in pairs:
            if ev.labels is None or ev.n_components != 2:
                continue
            lab = ev.labels
            lab = lab if lab[0] == 0 else (1 - lab)
            key = lab.tobytes()
            if key in seen:
                continue
            seen.add(key)
            out.append(Individual(np.asarray(g), ev))
            if len(out) >= beam:
                break
        return out

    def _lookahead(indices, cand):
        """1-ply look-ahead: candidate persistence + best persistence of each child."""
        lab = cand.quality.labels
        score = float(cand.quality.f)
        for side in (indices[np.flatnonzero(lab == 1)], indices[np.flatnonzero(lab == 0)]):
            if len(side) >= 2 * mcs:
                cb = atomic(X[side], config, np.random.default_rng(next_seed())).best()
                if cb is not None and cb.quality.n_components == 2:
                    score += float(cb.quality.f)
        return score

    def grow(indices: np.ndarray, depth: int) -> TreeNode:
        node = TreeNode(indices=indices, depth=depth)
        if node.size < min_node or depth >= max_depth:
            node.reason = "min_size" if node.size < min_node else "max_depth"
            return node
        cands = _candidates(atomic(X[indices], config, np.random.default_rng(next_seed())))
        if not cands:
            node.reason = "no_split"
            return node
        gated = []
        for c in cands:
            rep = _gate.evaluate_gate(X[indices], c, config, mode=gate_mode,
                                      min_persistence=min_persistence, stability_min=stability_min,
                                      n_sub=gate_n_sub, n_perm=gate_n_perm, null_alpha=null_alpha,
                                      base_seed=next_seed())
            if rep.passed:
                gated.append((c, rep))
        if not gated:
            node.reason = "gate_fail"
            return node
        if beam <= 1 or len(gated) == 1:
            best, report = gated[0]
        else:
            best, report = max(gated, key=lambda cr: _lookahead(indices, cr[0]))
        lab = best.quality.labels
        left_local = np.flatnonzero(lab == 1)
        right_local = np.flatnonzero(lab == 0)
        if len(left_local) < mcs or len(right_local) < mcs:
            node.reason = "no_split"
            return node
        node.gate = report
        node.features = sorted(int(i) for i in gm.selected_indices(best.genome))
        node.persistence = float(best.quality.f)
        node.children = [grow(indices[left_local], depth + 1),
                         grow(indices[right_local], depth + 1)]
        return node

    root = grow(np.arange(len(X)), 0)
    tree = Tree(root, len(X))
    # assign leaf ids left-to-right
    lid = [0]

    def assign(nd):
        if nd.is_leaf:
            nd.leaf_id = lid[0]
            lid[0] += 1
        else:
            for c in nd.children:
                assign(c)
    assign(root)
    return tree
