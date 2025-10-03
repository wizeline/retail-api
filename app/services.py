from __future__ import annotations
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from app.data import ZONES, PRODUCTS, HOTSPOTS, LAYOUTS, MIN_PRICE, MAX_PRICE
from app.ml_model import ensure_loaded, score_product_for_zone_ml

# Enable ML if model.pkl exists
USE_ML = True
MODEL_LOADED = ensure_loaded("model.pkl") if USE_ML else False

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def get_zone(zone_id: str) -> Dict[str, Any]:
    for z in ZONES:
        if z["id"] == zone_id:
            return z
    raise HTTPException(status_code=404, detail=f"Zone '{zone_id}' not found")

def get_product(pid: str) -> Dict[str, Any]:
    for p in PRODUCTS:
        if p["id"] == pid:
            return p
    raise HTTPException(status_code=404, detail=f"Product '{pid}' not found")

def ensure_layout(zone_id: str) -> List[Optional[str]]:
    z = get_zone(zone_id)
    cap = z["capacity"]
    if zone_id not in LAYOUTS:
        LAYOUTS[zone_id] = [None] * cap
    if len(LAYOUTS[zone_id]) != cap:
        cur = LAYOUTS[zone_id]
        if len(cur) < cap:
            LAYOUTS[zone_id] = cur + [None] * (cap - len(cur))
        else:
            LAYOUTS[zone_id] = cur[:cap]
    return LAYOUTS[zone_id]

def category_fit(p: Dict[str, Any], z: Dict[str, Any]) -> float:
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

def _score_heuristic(p: Dict[str, Any], z: Dict[str, Any]) -> float:
    w = z["weight"]
    v = clamp01(p["velocity"])
    m = clamp01(p["margin"])
    price_norm = clamp01((p["price"] - MIN_PRICE) / (MAX_PRICE - MIN_PRICE or 1.0))
    price_score = 1.0 - price_norm
    fit = category_fit(p, z)
    return float(v * w["velocity"] + m * w["margin"] + price_score * w["price"] + fit * w["fit"])

def score_product_for_zone(p: Dict[str, Any], z: Dict[str, Any]) -> float:
    if MODEL_LOADED and USE_ML:
        try:
            return score_product_for_zone_ml(p, z)
        except Exception:
            pass
    return _score_heuristic(p, z)

def compute_metrics(zone_id: str) -> Dict[str, Any]:
    z = get_zone(zone_id)
    layout = ensure_layout(zone_id)
    placed = [pid for pid in layout if pid]
    used = len(placed)
    cap = len(layout)

    if not placed:
        return {
            "zone_id": zone_id,
            "fill_rate": 0.0,
            "est_daily_sales": 0.0,
            "avg_ticket": 0.0,
            "avg_margin_rate": 0.0,
            "categories": 0,
            "score_sum": 0.0,
            "top3": [],
        }

    prods = [get_product(pid) for pid in placed]
    scores = [score_product_for_zone(p, z) for p in prods]
    score_sum = sum(scores)

    factor = 18.0
    est_daily_sales = sum(
        p["price"] * (0.6 + p["velocity"]) * (1.0 + p["margin"] * 0.5) * factor for p in prods
    )
    tx = max(1, int(used * 6))
    avg_ticket = est_daily_sales / tx

    avg_margin_rate = sum(p["margin"] for p in prods) / used
    categories = len(set(p["cat"] for p in prods))
    ranked = sorted(
        [{"id": p["id"], "name": p["name"], "score": score_product_for_zone(p, z)} for p in prods],
        key=lambda x: x["score"],
        reverse=True
    )[:3]

    return {
        "zone_id": zone_id,
        "fill_rate": used / cap if cap else 0.0,
        "est_daily_sales": round(est_daily_sales, 2),
        "avg_ticket": round(avg_ticket, 2),
        "avg_margin_rate": round(avg_margin_rate, 4),
        "categories": categories,
        "score_sum": round(score_sum, 4),
        "top3": ranked,
    }

def predict_best(zone_id: str) -> List[Optional[str]]:
    z = get_zone(zone_id)
    cap = z["capacity"]
    ranked = sorted(PRODUCTS, key=lambda p: score_product_for_zone(p, z), reverse=True)
    unique: List[str] = []
    for p in ranked:
        if p["id"] not in unique:
            unique.append(p["id"])
        if len(unique) >= cap:
            break
    LAYOUTS[zone_id] = unique[:cap]
    return LAYOUTS[zone_id]

def place_from_inventory(zone_id: str, pid: str, to_idx: int):
    layout = ensure_layout(zone_id)
    if not (0 <= to_idx < len(layout)):
        raise HTTPException(status_code=400, detail="Destination slot index out of range")
    try:
        cur = layout.index(pid)
        if cur == to_idx:
            return
        layout[cur], layout[to_idx] = layout[to_idx], layout[cur]
    except ValueError:
        layout[to_idx] = pid

def move_between_slots(zone_id: str, pid: str, from_idx: int, to_idx: int):
    layout = ensure_layout(zone_id)
    if not (0 <= from_idx < len(layout)) or not (0 <= to_idx < len(layout)):
        raise HTTPException(status_code=400, detail="Slot indices out of range")
    if layout[from_idx] != pid:
        raise HTTPException(status_code=400, detail="The given product is not at the source slot")
    layout[from_idx], layout[to_idx] = layout[to_idx], layout[from_idx]
