import os
import pickle
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.data import ZONES, PRODUCTS, MIN_PRICE, MAX_PRICE

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

# ---------- Heuristic (label for distillation) ----------

def _category_fit(p: Dict[str, Any], z: Dict[str, Any]) -> float:
    cat = (p.get("cat") or "").lower()
    zt = (z.get("type") or "").lower()
    tags = [t.lower() for t in p.get("tags", [])]
    fit = 0.1
    if zt and zt in cat:
        fit += 0.6
    if zt == "impulse":
        if "impulse" in tags:
            fit += 0.5
        if cat in {"snacks", "bakery"}:
            fit += 0.3
        if "sweet" in tags or "salty" in tags:
            fit += 0.2
    if zt == "beverages":
        if cat == "beverages":
            fit += 0.5
        if "cold" in tags:
            fit += 0.3
        if "healthy" in tags:
            fit += 0.1
    if zt == "produce":
        if cat == "produce":
            fit += 0.5
        if "fresh" in tags or "healthy" in tags:
            fit += 0.3
    return clamp01(fit)

def _heuristic_score(p: Dict[str, Any], z: Dict[str, Any]) -> float:
    w = z["weight"]
    v = clamp01(p["velocity"])
    m = clamp01(p["margin"])
    price_norm = clamp01((p["price"] - MIN_PRICE) / (MAX_PRICE - MIN_PRICE or 1.0))
    price_score = 1.0 - price_norm
    fit = _category_fit(p, z)
    return float(
        v * w["velocity"] + m * w["margin"] + price_score * w["price"] + fit * w["fit"]
    )

# ---------- Features ----------

def _inverse_price_norm(price: float) -> float:
    pn = (price - MIN_PRICE) / (MAX_PRICE - MIN_PRICE or 1.0)
    return 1.0 - clamp01(pn)

def _tag_string(tags: List[str]) -> str:
    return " ".join(sorted(set(t.lower() for t in (tags or []))))

def _zone_weights(z: Dict[str, Any]) -> Tuple[float, float, float, float]:
    w = z["weight"]
    return (w["velocity"], w["margin"], w["price"], w["fit"])

def _row_from(p: Dict[str, Any], z: Dict[str, Any]) -> Dict[str, Any]:
    wv, wm, wp, wf = _zone_weights(z)
    return {
        "price": float(p["price"]),
        "inv_price_norm": _inverse_price_norm(float(p["price"])),
        "margin": float(p["margin"]),
        "velocity": float(p["velocity"]),
        "cat": (p["cat"] or "").lower(),
        "tags_joined": _tag_string(p.get("tags", [])),
        "zone_type": (z["type"] or "").lower(),
        "w_velocity": float(wv),
        "w_margin": float(wm),
        "w_price": float(wp),
        "w_fit": float(wf),
    }

def build_training_data():
    X_rows: List[Dict[str, Any]] = []
    y_list: List[float] = []
    for z in ZONES:
        for p in PRODUCTS:
            X_rows.append(_row_from(p, z))
            y_list.append(_heuristic_score(p, z))
    return X_rows, np.array(y_list, dtype=np.float32)

CATEGORICAL_COLS = ["cat", "tags_joined", "zone_type"]
NUMERIC_COLS = ["price", "inv_price_norm", "margin", "velocity", "w_velocity", "w_margin", "w_price", "w_fit"]

def make_pipeline() -> Pipeline:
    pre = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLS),
            ("num", "passthrough", NUMERIC_COLS),
        ],
        remainder="drop",
        sparse_threshold=0.3,
    )
    model = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)
    pipe = Pipeline(steps=[("pre", pre), ("rf", model)])
    return pipe

@dataclass
class ModelArtifacts:
    pipeline: Pipeline

def train_and_save(model_path: str = "model.pkl") -> None:
    X_rows, y = build_training_data()
    pipe = make_pipeline()
    pipe.fit(X_rows, y)
    with open(model_path, "wb") as f:
        pickle.dump(ModelArtifacts(pipeline=pipe), f)

def load_model(model_path: str = "model.pkl") -> Optional[ModelArtifacts]:
    if not os.path.exists(model_path):
        return None
    with open(model_path, "rb") as f:
        return pickle.load(f)

_ARTIFACTS_CACHE: Optional[ModelArtifacts] = None

def ensure_loaded(model_path: str = "model.pkl") -> bool:
    global _ARTIFACTS_CACHE
    if _ARTIFACTS_CACHE is None:
        _ARTIFACTS_CACHE = load_model(model_path)
    return _ARTIFACTS_CACHE is not None

def score_product_for_zone_ml(p: Dict[str, Any], z: Dict[str, Any]) -> float:
    if _ARTIFACTS_CACHE is None or _ARTIFACTS_CACHE.pipeline is None:
        raise RuntimeError("ML model not loaded")
    row = _row_from(p, z)
    pred = _ARTIFACTS_CACHE.pipeline.predict([row])[0]
    return float(clamp01(pred))
