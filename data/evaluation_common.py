"""Shared token/feature/geometry helpers used by the evaluation notebooks.

This module only depends on numpy + sentence-transformers (optional) and is
kept independent of the FastAPI app so notebooks can run it standalone.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import numpy as np

R_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R_KM * 2 * math.asin(math.sqrt(a))


def normalize(v: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.0
    return max(0.0, min(1.0, (v - lo) / (hi - lo)))


# Term-similarity groups: item types that are "close enough" for ground truth.
ITEM_TYPE_GROUPS: Dict[str, set] = {
    "jacket": {"jacket", "coat", "hoodie", "sweater", "pullover"},
    "shirt": {"shirt", "t-shirt", "tshirt", "top", "blouse", "uniform"},
    "pants": {"pant", "pants", "trouser", "trousers", "jeans", "shorts", "leggings"},
    "skirt": {"skirt", "dress", "gown"},
    "sock": {"sock", "socks", "slipper", "slippers", "shoe", "shoes", "footwear"},
    "notebook": {"notebook", "notebooks", "register", "register book"},
    "pen": {"pen", "pens", "ballpoint", "marker", "markers", "highlighter"},
    "pencil": {"pencil", "pencils", "color pencil", "colour pencil", "sketch pen"},
    "bag": {"bag", "backpack", "school bag", "rucksack", "schoolbag"},
    "book": {"book", "books", "story book", "textbook", "workbook", "novel", "reader"},
    "ruler": {"ruler", "geometry box", "geometry", "compass", "protractor", "scale"},
    "crayon": {"crayon", "crayons", "colors", "colours", "paintbox", "stationery set"},
}


def item_group(item_type: Optional[str]) -> Optional[str]:
    if not item_type:
        return None
    t = item_type.strip().lower()
    for group, members in ITEM_TYPE_GROUPS.items():
        if t in members:
            return group
    # fallback: if the item type tokens contain a group keyword
    for group, members in ITEM_TYPE_GROUPS.items():
        toks = t.split()
        if any(m.split()[0] in toks for m in members):
            return group
    return None


def is_ideal_match(donation, request, max_dist_km: float = 25.0) -> bool:
    """True when a request is a reasonable 'ideal' match for a donation.

    Used to build the hand-labelled ground-truth set for Precision@K.
    Ideal = same category, overlapping item-type group, overlapping
    age-group when both are present, and within the max distance.
    """
    if donation["category"] != request["category"]:
        return False
    if not donation.get("lat") or not donation.get("lng") or not request.get("lat") or not request.get("lng"):
        return False
    if haversine_km(donation["lat"], donation["lng"], request["lat"], request["lng"]) > max_dist_km:
        return False

    dg = item_group(donation.get("item_type"))
    rg = item_group(request.get("item_type"))
    if dg is None or rg is None or dg != rg:
        return False

    age_overlap = _age_groups_overlap(donation.get("age_group"), request.get("age_group"))
    if not age_overlap:
        return False

    gender_ok = _genders_compatible(donation.get("gender"), request.get("gender"))
    season_ok = _seasons_compatible(donation.get("season"), request.get("season"))
    return gender_ok and season_ok


def _age_groups_overlap(a: Optional[str], b: Optional[str]) -> bool:
    ra = _age_range(a)
    rb = _age_range(b)
    if ra is None or rb is None:
        return True  # unknown ages are considered compatible
    return max(ra[0], rb[0]) <= min(ra[1], rb[1])


def _age_range(age: Optional[str]) -> Optional[Tuple[float, float]]:
    if not age:
        return None
    import re

    tokens = re.findall(r"\d+", str(age))
    if not tokens:
        if any(k in str(age).lower() for k in ("kid", "child", "infant", "toddler")):
            return (0, 12)
        if any(k in str(age).lower() for k in ("teen", "adolescent", "youth")):
            return (13, 19)
        if str(age).lower() in ("adult", "men", "women"):
            return (18, 60)
        return None
    nums = [int(t) for t in tokens]
    if len(nums) >= 2:
        return (float(min(nums)), float(max(nums)))
    return (float(nums[0]), float(nums[0]))


def _genders_compatible(a: Optional[str], b: Optional[str]) -> bool:
    a = (a or "").lower()
    b = (b or "").lower()
    if not a or not b or a == "unisex" or b == "unisex":
        return True
    return a == b


def _seasons_compatible(a: Optional[str], b: Optional[str]) -> bool:
    a = (a or "").lower()
    b = (b or "").lower()
    if not a or not b:
        return True
    return a == b


# ---------------------------------------------------------------------------
# Embedding caching
# ---------------------------------------------------------------------------
_TEXTS: List[str] = []
_SIMS: Optional[np.ndarray] = None
_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def build_text_similarity_matrix(donations: List[dict], requests: List[dict]) -> np.ndarray:
    """Cosine similarity between donation text and request text (n_don x n_req)."""
    global _SIMS
    if _SIMS is not None and len(_TEXTS) == len(donations):
        return _SIMS

    d_texts = [_text(d) for d in donations]
    r_texts = [_text(r) for r in requests]

    emb_d = _get_embedder().encode(d_texts, show_progress_bar=False)
    emb_r = _get_embedder().encode(r_texts, show_progress_bar=False)

    denom = np.linalg.norm(emb_d, axis=1)[:, None] * np.linalg.norm(emb_r, axis=1)[None, :]
    _SIMS = (emb_d @ emb_r.T) / np.maximum(denom, 1e-12)
    return _SIMS


def _text(record: dict) -> str:
    parts = [
        record.get("item_type", ""),
        record.get("description", ""),
        record.get("category", ""),
        record.get("season", ""),
        record.get("beneficiary_group", ""),
    ]
    return " ".join(p for p in parts if p)


def reset_cache() -> None:
    global _SIMS, _TEXTS
    _SIMS = None
    _TEXTS = []