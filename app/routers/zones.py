from fastapi import APIRouter, HTTPException

from app.schemas import (
    LayoutOut,
    MetricsOut,
    PredictResponse,
    MoveRequest,
    SetLayoutRequest,
)
from app.services import (
    ensure_layout,
    compute_metrics,
    predict_best,
    place_from_inventory,
    move_between_slots,
    get_zone,
)
from app.data import LAYOUTS

router = APIRouter()

@router.get("/{zone_id}/layout", response_model=LayoutOut)
def get_layout(zone_id: str):
    layout = ensure_layout(zone_id)
    return {"zone_id": zone_id, "layout": layout}

@router.get("/{zone_id}/metrics", response_model=MetricsOut)
def get_zone_metrics(zone_id: str):
    return compute_metrics(zone_id)

@router.post("/{zone_id}/predict", response_model=PredictResponse)
def post_predict(zone_id: str):
    layout = predict_best(zone_id)
    metrics = compute_metrics(zone_id)
    return {"zone_id": zone_id, "layout": layout, "metrics": metrics}

@router.post("/{zone_id}/move", response_model=PredictResponse)
def post_move(zone_id: str, body: MoveRequest):
    ensure_layout(zone_id)
    if body.origin == "inventory":
        place_from_inventory(zone_id, body.pid, body.to_slot)
    else:
        if body.from_slot is None:
            raise HTTPException(status_code=400, detail="from_slot is required when origin='slot'")
        move_between_slots(zone_id, body.pid, body.from_slot, body.to_slot)
    layout = ensure_layout(zone_id)
    metrics = compute_metrics(zone_id)
    return {"zone_id": zone_id, "layout": layout, "metrics": metrics}

@router.post("/{zone_id}/clear", response_model=PredictResponse)
def post_clear(zone_id: str):
    z = get_zone(zone_id)
    LAYOUTS[zone_id] = [None] * z["capacity"]
    return {"zone_id": zone_id, "layout": LAYOUTS[zone_id], "metrics": compute_metrics(zone_id)}

@router.put("/{zone_id}/layout", response_model=PredictResponse)
def put_layout(zone_id: str, body: SetLayoutRequest):
    z = get_zone(zone_id)
    if len(body.layout) != z["capacity"]:
        raise HTTPException(status_code=400, detail=f"Layout must have {z['capacity']} positions")
    from app.services import get_product
    for pid in body.layout:
        if pid is not None:
            _ = get_product(pid)
    LAYOUTS[zone_id] = body.layout
    return {"zone_id": zone_id, "layout": LAYOUTS[zone_id], "metrics": compute_metrics(zone_id)}
