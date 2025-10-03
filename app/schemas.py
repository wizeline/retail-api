from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field

class ProductOut(BaseModel):
    id: str
    name: str
    cat: str
    price: float
    margin: float
    velocity: float
    tags: List[str] = []
    score: Optional[float] = None

class ZoneOut(BaseModel):
    id: str
    name: str
    type: str
    capacity: int
    weight: Dict[str, float]

class LayoutOut(BaseModel):
    zone_id: str
    layout: List[Optional[str]]

class MetricsOut(BaseModel):
    zone_id: str
    fill_rate: float
    est_daily_sales: float
    avg_ticket: float
    avg_margin_rate: float
    categories: int
    score_sum: float
    top3: List[Dict[str, Any]]

class PredictResponse(BaseModel):
    zone_id: str
    layout: List[Optional[str]]
    metrics: Dict[str, Any]

class MoveRequest(BaseModel):
    origin: Literal["inventory", "slot"] = Field(..., description="Drag source")
    pid: str = Field(..., description="Product ID")
    to_slot: int = Field(..., description="Destination slot index")
    from_slot: Optional[int] = Field(None, description="Source slot if origin='slot'")

class SetLayoutRequest(BaseModel):
    layout: List[Optional[str]]
