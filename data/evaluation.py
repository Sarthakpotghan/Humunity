"""Offline matching evaluation for Humunity.

Fully mirrors the online scoring algorithm in
``backend/app/services/matching.py`` (same factors and default weights) but
operates on the CSV exports produced by ``generate_synthetic_data.py`` so the
evaluation notebooks can run without a warm embedding model or a DB session.

Provides:
  * feature/similarity precomputation with caching to ``data/output/``
  * the weighted scoring heuristic (the "system" baseline)
  * Random and Nearest-NGO baselines
  * Precision@K / Recall@K / NDCG@5 / coverage metrics
  * ablation (drop one factor, renormalise the rest)
  * grid-search over weight space for the top-K quality

Run from a notebook or CLI::

    python data/evaluation.py --mode eval --plot
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np

from evaluation_common import (
    build_text_similarity_matrix,
    haversine_km,
    item_group,
    normalize,
)

BASE = Path(__file__).resolve().parent
OUT = BASE / "output"

DEFAULT_WEIGHTS: Dict[str, float] = {
    "urgency": 0.30,
    "similarity": 0.20,
    "seasonal": 0.15,
    "proximity": 0.15,
    "quantity_fit": 0.10,
    "condition": 0.05,
    "reliability": 0.05,
}

FEATURES = sorted(DEFAULT_WEIGHTS.keys())


def load_donations() -> List[dict]:
    with open(OUT / "donations.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_requests() -> List[dict]:
    with open(OUT / "requests.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_ideal() -> Dict[int, set[int]]:
    ideal: Dict[int, set[int]] = {}
    path = OUT / "ideal_matches.csv"
    if not path.exists():
        return ideal
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ideal.setdefault(int(row["donation_id"]), set()).add(int(row["request_id"]))
    return ideal


# ---------------------------------------------------------------------------
# Per-pair feature computation (mirrors app.services.matching)
# ---------------------------------------------------------------------------
def _dist(d: dict, r: dict) -> float:
    try:
        return haversine_km(float(d["lat"]), float(d["lng"]), float(r["lat"]), float(r["lng"]))
    except (TypeError, ValueError, KeyError):
        return float("inf")


def _urgency(r: dict) -> float:
    base = float(r.get("urgency") or 1) / 5.0
    deadline = r.get("deadline") or ""
    if not deadline:
        return base
    try:
        from datetime import date

        days_left = (date.fromisoformat(deadline[:10]) - date.today()).days
    except ValueError:
        return base
    if days_left <= 0:
        return 1.0
    if days_left <= 3:
        return min(1.0, base + 0.3)
    if days_left <= 7:
        return min(1.0, base + 0.15)
    return base


def _seasonal(d: dict) -> float:
    season = (d.get("season") or "").lower()
    if not season:
        return 0.5
    month = __import__("datetime").datetime.utcnow().month
    ranges = {"spring": [3, 4, 5], "summer": [6, 7, 8], "autumn": [9, 10, 11], "winter": [12, 1, 2]}
    if month in ranges.get(season, []):
        return 1.0
    return 0.3


def _quantity_fit(d: dict, r: dict) -> float:
    need = float(r.get("quantity_needed") or 0)
    if need <= 0:
        return 0.0
    try:
        return min(1.0, float(d.get("quantity") or 0) / need)
    except ValueError:
        return 0.0


def _condition(d: dict) -> float:
    return {"new": 1.0, "good": 0.7, "fair": 0.4, "used": 0.4}.get((d.get("condition") or "").lower(), 0.5)


def _reliability(r: dict) -> float:
    try:
        return float(r.get("reliability_score") or 1.0)
    except ValueError:
        return 1.0


def compute_features(donations: List[dict], requests: List[dict], sims: np.ndarray) -> Dict[Tuple[int, int], Dict[str, float]]:
    """Return a pair -> feature-dict mapping for every donation/request pair."""
    out: Dict[Tuple[int, int], Dict[str, float]] = {}
    for di, d in enumerate(donations):
        did = int(d["id"])
        max_dist = 25.0
        for ri, r in enumerate(requests):
            rid = int(r["id"])
            dist = _dist(d, r)
            if not math.isinf(dist):
                prox = max(0.0, 1.0 - dist / max_dist)
            else:
                prox = 0.0
            out[(did, rid)] = {
                "urgency": _urgency(r),
                "similarity": float(sims[di, ri]),
                "seasonal": _seasonal(d),
                "proximity": prox,
                "quantity_fit": _quantity_fit(d, r),
                "condition": _condition(d),
                "reliability": _reliability(r),
                "_distance_km": dist if not math.isinf(dist) else -1.0,
            }
    return out


def score_pair(feats: Dict[str, float], weights: Dict[str, float]) -> float:
    return sum(weights[k] * feats[k] for k in weights)


# ---------------------------------------------------------------------------
# Ranking baselines
# ---------------------------------------------------------------------------
def rank_system(feats_map: Dict[Tuple[int, int], Dict[str, float]], donations: List[dict], requests: List[dict], weights: Dict[str, float]) -> Dict[int, List[int]]:
    ranks: Dict[int, List[int]] = {}
    for d in donations:
        did = int(d["id"])
        scored = [(rid, score_pair(feats_map[(did, rid)], weights)) for rid in (int(r["id"]) for r in requests)]
        scored.sort(key=lambda x: x[1], reverse=True)
        ranks[did] = [rid for rid, _ in scored]
    return ranks


def rank_nearest(donations: List[dict], requests: List[dict]) -> Dict[int, List[int]]:
    ranks: Dict[int, List[int]] = {}
    for d in donations:
        did = int(d["id"])
        ranked = sorted(((int(r["id"]), _dist(d, r)) for r in requests), key=lambda x: x[1])
        ranks[did] = [rid for rid, _ in ranked]
    return ranks


def rank_random(donations: List[dict], requests: List[dict], seed: int = 7) -> Dict[int, List[int]]:
    rng = random.Random(seed)
    rids = [int(r["id"]) for r in requests]
    return {int(d["id"]): rng.sample(rids, len(rids)) for d in donations}


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def precision_at_k(ranks: Dict[int, List[int]], ideal: Dict[int, set[int]], k: int, rids: List[int]) -> float:
    """Mean precision@K over donations that have ground truth and >=K candidates."""
    vals: List[float] = []
    for did in ideal:
        if did not in ranks:
            continue
        topk = ranks[did][:k]
        if len(topk) < k:
            continue
        hits = sum(1 for rid in topk if rid in ideal[did])
        vals.append(hits / k)
    return float(np.mean(vals)) if vals else 0.0


def recall_at_k(ranks: Dict[int, List[int]], ideal: Dict[int, set[int]], k: int) -> float:
    vals: List[float] = []
    for did, ivals in ideal.items():
        if did not in ranks:
            continue
        topk = set(ranks[did][:k])
        hits = len(topk & ivals)
        vals.append(hits / len(ivals))
    return float(np.mean(vals)) if vals else 0.0


def ndcg_at_k(ranks: Dict[int, List[int]], ideal: Dict[int, set[int]], k: int = 5) -> float:
    vals: List[float] = []
    for did, ivals in ideal.items():
        if did not in ranks:
            continue
        rel = {rid: 1 for rid in ivals}
        dcg = sum(rel.get(rid, 0) / math.log2(i + 2) for i, rid in enumerate(ranks[did][:k]))
        best = sorted((ival for ival in ivals), key=lambda rid: 0)[:k]
        idcg = sum(1.0 / math.log2(i + 2) for i in range(min(len(best), k)))
        vals.append(dcg / idcg if idcg > 0 else 0.0)
    return float(np.mean(vals)) if vals else 0.0


def mean_top_distance(ranks: Dict[int, List[int]], feats_map: Dict[Tuple[int, int], Dict[str, float]], k: int = 5) -> float:
    dists: List[float] = []
    for did, topk in ranks.items():
        for rid in topk[:k]:
            dist = feats_map[(did, rid)].get("_distance_km")
            if dist is not None and dist >= 0:
                dists.append(dist)
    return float(np.mean(dists)) if dists else 0.0


def coverage(ranks: Dict[int, List[int]], ideal: Dict[int, set[int]], k: int) -> float:
    """Fraction of ground-truth donations that have >=1 ideal match in top-K."""
    if not ideal:
        return 0.0
    hits = sum(1 for did, ivals in ideal.items() if set(ranks.get(did, [])[:k]) & ivals)
    return hits / len(ideal)


def summarize(ranks: Dict[int, List[int]], ideal: Dict[int, set[int]], feats_map: Dict[Tuple[int, int], Dict[str, float]]) -> Dict[str, float]:
    return {
        "P@1": precision_at_k(ranks, ideal, 1, []),
        "P@3": precision_at_k(ranks, ideal, 3, []),
        "P@5": precision_at_k(ranks, ideal, 5, []),
        "R@5": recall_at_k(ranks, ideal, 5),
        "NDCG@5": ndcg_at_k(ranks, ideal, 5),
        "cov@5": coverage(ranks, ideal, 5),
        "avg_dist_top5_km": mean_top_distance(ranks, feats_map, 5),
    }


def with_label(metrics: Dict[str, float], label: str) -> Dict[str, object]:
    return {"system": label, **metrics}


# ---------------------------------------------------------------------------
# Ablation + weight tuning
# ---------------------------------------------------------------------------
def ablation(feats_map, donations, requests, ideal, weights: Dict[str, float]) -> List[Dict]:
    rows = []
    base = summarize(rank_system(feats_map, donations, requests, weights), ideal, feats_map)
    base_p5 = base["P@5"]
    base_ndcg = base["NDCG@5"]
    rows.append(with_label(base, "full"))
    for drop in FEATURES:
        reduced = {k: v for k, v in weights.items() if k != drop}
        total = sum(reduced.values())
        renorm = {k: v / total for k, v in reduced.items()}
        metrics = summarize(rank_system(feats_map, donations, requests, renorm), ideal, feats_map)
        row = with_label(metrics, f"drop-{drop}")
        row["p5_delta"] = round(metrics["P@5"] - base_p5, 4)
        row["ndcg_delta"] = round(metrics["NDCG@5"] - base_ndcg, 4)
        rows.append(row)
    return rows


WEIGHT_SAMPLES: Dict[str, List[float]] = {
    "urgency": [0.2, 0.3, 0.4],
    "similarity": [0.15, 0.2, 0.3],
    "seasonal": [0.1, 0.15, 0.2],
    "proximity": [0.1, 0.15, 0.25],
    "quantity_fit": [0.05, 0.1, 0.2],
    "condition": [0.0, 0.05, 0.1],
    "reliability": [0.0, 0.05, 0.1],
}


def grid_search(feats_map, donations, requests, ideal, preview: bool = False) -> List[Dict]:
    """Sweep a bounded weight grid; returns rows sorted by NDCG@5 desc."""
    import itertools

    keys = FEATURES
    names = WEIGHT_SAMPLES.keys()
    combos = list(itertools.product(*[WEIGHT_SAMPLES[k] for k in names])) if not preview else list(itertools.product(*[WEIGHT_SAMPLES[k][:2] for k in names]))

    rows: List[Dict[str, Any]] = []
    best_ndcg = -1.0
    for combo in combos:
        cand = dict(zip(keys, combo))
        total = sum(cand.values())
        if total <= 0:
            continue
        cand = {k: v / total for k, v in cand.items()}
        ranks = rank_system(feats_map, donations, requests, cand)
        perf = summarize(ranks, ideal, feats_map)
        if perf["NDCG@5"] > best_ndcg:
            best_ndcg = perf["NDCG@5"]
            rows.append({**cand, "p_norm": total, "P@5": perf["P@5"], "R@5": perf["R@5"], "NDCG@5": perf["NDCG@5"]})
    rows.sort(key=lambda r: float(r["NDCG@5"]), reverse=True)
    return rows


# ---------------------------------------------------------------------------
# Precompute/cache similarities + features
# ---------------------------------------------------------------------------
def precompute(force: bool = False) -> Tuple[List[dict], List[dict], np.ndarray, Dict[Tuple[int, int], Dict[str, float]]]:
    donations = load_donations()
    requests = load_requests()
    sim_path = OUT / "similarities.npy"
    if sim_path.exists() and not force:
        sims = np.load(sim_path)
    else:
        sims = build_text_similarity_matrix(donations, requests)
        np.save(sim_path, sims)
    feats_path = OUT / "features.json"
    if feats_path.exists() and not force:
        raw = json.loads(feats_path.read_text(encoding="utf-8"))
        feats: Dict[Tuple[int, int], Dict[str, float]] = {}
        for k, v in raw.items():
            did, rid = (int(x) for x in k.split(":"))
            feats[(did, rid)] = v
    else:
        feats = compute_features(donations, requests, sims)
        feats_path.write_text(json.dumps({f"{k[0]}:{k[1]}": v for k, v in feats.items()}), encoding="utf-8")
    return donations, requests, sims, feats


RESULTS = OUT / "results"


def _save(name: str, rows: List[dict]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / f"{name}.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Humunity matching evaluation offline")
    parser.add_argument("--mode", choices=["eval", "ablation", "tune", "precompute"], default="eval")
    parser.add_argument("--preview", action="store_true", help="limit grid search for speed")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    donations, requests, sims, feats = precompute(force=args.force)
    ideal = load_ideal()

    if args.mode == "precompute":
        print(f"precomputed: {len(donations)} donations, {len(requests)} requests, {len(feats)} pairs")
        return

    if args.mode == "eval":
        rows = [
            with_label(summarize(rank_random(donations, requests), ideal, feats), "random"),
            with_label(summarize(rank_nearest(donations, requests), ideal, feats), "nearest"),
            with_label(summarize(rank_system(feats, donations, requests, DEFAULT_WEIGHTS), ideal, feats), "system(weighted)"),
        ]
        _save("baselines", rows)
        for r in rows:
            print(json.dumps(r))

    if args.mode == "ablation":
        rows = ablation(feats, donations, requests, ideal, DEFAULT_WEIGHTS)
        _save("ablation", rows)
        for r in rows:
            print(json.dumps(r))

    if args.mode == "tune":
        rows = grid_search(feats, donations, requests, ideal, preview=args.preview)
        _save("tuned_weights", rows)
        for r in rows[:10]:
            print(json.dumps(r))


if __name__ == "__main__":
    main()