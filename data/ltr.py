import json
import csv
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import ndcg_score, average_precision_score
from sklearn.preprocessing import StandardScaler
import joblib

from evaluation_common import (
    build_text_similarity_matrix,
    haversine_km,
    item_group,
    is_ideal_match,
    normalize,
)

BASE = Path(__file__).resolve().parent
OUT = BASE / "output"
RESULTS_DIR = OUT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = OUT / "ltr_model.joblib"
SCALER_PATH = OUT / "ltr_scaler.joblib"


def load_donations():
    with open(OUT / "donations.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_requests():
    with open(OUT / "requests.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_ideal():
    ideal = {}
    path = OUT / "ideal_matches.csv"
    if not path.exists():
        return ideal
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ideal.setdefault(int(row["donation_id"]), set()).add(int(row["request_id"]))
    return ideal


def load_similarities():
    path = OUT / "similarities.npy"
    if not path.exists():
        donations = load_donations()
        requests = load_requests()
        return build_text_similarity_matrix(donations, requests)
    return np.load(path)


def build_ltr_dataset():
    donations = load_donations()
    requests = load_requests()
    ideal_matches = load_ideal()
    similarities = load_similarities()

    don_id_to_idx = {int(d["id"]): i for i, d in enumerate(donations)}
    req_id_to_idx = {int(r["id"]): i for i, r in enumerate(requests)}

    rows = []
    for don in donations:
        don_id = int(don["id"])
        don_idx = don_id_to_idx[don_id]
        for req in requests:
            req_id = int(req["id"])
            req_idx = req_id_to_idx[req_id]

            if don["category"] != req["category"]:
                continue

            sim = similarities[don_idx, req_idx]
            if sim < 0.3:
                continue

            ideal = is_ideal_match({
                **don,
                "lat": float(don.get("lat", 0) or 0),
                "lng": float(don.get("lng", 0) or 0),
            }, {
                **req,
                "lat": float(req.get("lat", 0) or 0),
                "lng": float(req.get("lng", 0) or 0),
            })

            try:
                lat1 = float(don.get("lat", 0) or 0)
                lng1 = float(don.get("lng", 0) or 0)
                lat2 = float(req.get("lat", 0) or 0)
                lng2 = float(req.get("lng", 0) or 0)
            except (ValueError, TypeError):
                continue
            if lat1 == 0 or lng1 == 0 or lat2 == 0 or lng2 == 0:
                continue

            dist = haversine_km(lat1, lng1, lat2, lng2)
            proximity = max(0.0, 1.0 - dist / 50.0)

            try:
                dq = float(don.get("quantity", 1) or 1)
                rq = float(req.get("quantity_needed", 1) or 1)
            except (ValueError, TypeError):
                continue
            quantity_fit = min(dq / max(rq, 1), 1.0)

            condition_map = {"NEW": 1.0, "LIKE_NEW": 0.85, "GOOD": 0.7, "FAIR": 0.4, "POOR": 0.15}
            condition = condition_map.get(don.get("condition", "GOOD"), 0.5)

            try:
                reliability = float(req.get("reliability_score", 0.5) or 0.5)
            except (ValueError, TypeError):
                reliability = 0.5

            seasonal = 1.0 if (don.get("season") == req.get("season") and don.get("season")) else 0.0

            try:
                urgency = float(req.get("urgency", 1) or 1) / 5.0
            except (ValueError, TypeError):
                urgency = 0.2

            rows.append({
                "donation_id": don_id,
                "request_id": req_id,
                "urgency": urgency,
                "seasonal": seasonal,
                "proximity": proximity,
                "quantity_fit": quantity_fit,
                "condition": condition,
                "reliability": reliability,
                "similarity": sim,
                "ideal": ideal,
                "distance_km": dist,
            })

    df = pd.DataFrame(rows)
    feature_cols = ["urgency", "seasonal", "proximity", "quantity_fit", "condition", "reliability", "similarity"]
    X = df[feature_cols].values
    y = df["ideal"].astype(int).values
    groups = df["donation_id"].values

    return X, y, groups, df[feature_cols], df


def train_ltr():
    X, y, groups, feature_df, meta_df = build_ltr_dataset()

    unique_donors = np.unique(groups)
    train_donors, test_donors = train_test_split(unique_donors, test_size=0.2, random_state=42)
    train_mask = np.isin(groups, train_donors)
    test_mask = np.isin(groups, test_donors)

    X_train, y_train = X[train_mask], y[train_mask]
    X_test, y_test = X[test_mask], y[test_mask]
    groups_train = groups[train_mask]
    groups_test = groups[test_mask]

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=3,
        min_samples_split=10,
        min_samples_leaf=5,
        subsample=0.8,
        random_state=42,
    )

    model.fit(X_train_s, y_train)

    param_grid = {
        "n_estimators": [100, 200, 300],
        "learning_rate": [0.05, 0.1, 0.15],
        "max_depth": [2, 3, 4],
    }
    grid = GridSearchCV(
        GradientBoostingRegressor(min_samples_split=10, min_samples_leaf=5, subsample=0.8, random_state=42),
        param_grid,
        cv=3,
        scoring="neg_mean_squared_error",
        n_jobs=-1,
    )
    grid.fit(X_train_s, y_train)
    best_model = grid.best_estimator_

    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    return best_model, scaler, X_test_s, y_test, groups_test, feature_df.iloc[test_mask]


def evaluate_ltr(model, scaler, X_test, y_test, groups_test, feature_df):
    preds = model.predict(X_test)

    results = []
    for donor_id in np.unique(groups_test):
        mask = groups_test == donor_id
        y_true = y_test[mask]
        y_pred = preds[mask]
        if len(y_true) < 2:
            continue
        true_relevance = y_true.reshape(1, -1)
        pred_scores = y_pred.reshape(1, -1)
        ndcg5 = ndcg_score(true_relevance, pred_scores, k=5)
        ap = average_precision_score(y_true, y_pred)
        results.append({"donation_id": int(donor_id), "ndcg@5": float(ndcg5), "ap": float(ap), "num_candidates": int(len(y_true))})

    df_res = pd.DataFrame(results)
    avg_ndcg5 = float(df_res["ndcg@5"].mean())
    avg_ap = float(df_res["ap"].mean())

    feature_importance = dict(zip(
        ["urgency", "seasonal", "proximity", "quantity_fit", "condition", "reliability", "similarity"],
        [float(v) for v in model.feature_importances_]
    ))

    return {
        "avg_ndcg@5": avg_ndcg5,
        "avg_ap": avg_ap,
        "feature_importance": feature_importance,
        "best_params": getattr(model, "best_params_", None),
        "per_donor": df_res.to_dict("records"),
    }


def load_ltr_model():
    if MODEL_PATH.exists() and SCALER_PATH.exists():
        return joblib.load(MODEL_PATH), joblib.load(SCALER_PATH)
    return None, None


def predict_ltr(model, scaler, features: dict) -> float:
    if model is None or scaler is None:
        return 0.0
    feat_order = ["urgency", "seasonal", "proximity", "quantity_fit", "condition", "reliability", "similarity"]
    x = np.array([[features[f] for f in feat_order]])
    x_s = scaler.transform(x)
    return float(model.predict(x_s)[0])


if __name__ == "__main__":
    print("Training LTR model...")
    model, scaler, X_test, y_test, groups_test, feat_df = train_ltr()
    print("Evaluating...")
    results = evaluate_ltr(model, scaler, X_test, y_test, groups_test, feat_df)
    print(f"Avg NDCG@5: {results['avg_ndcg@5']:.4f}")
    print(f"Avg AP: {results['avg_ap']:.4f}")
    print(f"Feature importance: {results['feature_importance']}")

    with open(RESULTS_DIR / "ltr_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {RESULTS_DIR / 'ltr_results.json'}")