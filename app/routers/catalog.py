from typing import List, Optional
from fastapi import APIRouter

from app.data import PRODUCTS, HOTSPOTS, ZONES
from app.schemas import ProductOut, ZoneOut
from app.services import get_zone, score_product_for_zone

router = APIRouter()

@router.get("/zones", response_model=List[ZoneOut])
def list_zones():
    return ZONES

@router.get("/products", response_model=List[ProductOut])
def list_products(q: Optional[str] = None,
                  cat: Optional[str] = None,
                  sort: Optional[str] = "score",
                  zone_id: Optional[str] = None):
    items = PRODUCTS.copy()
    if q:
        ql = q.strip().lower()
        items = [p for p in items if ql in p["name"].lower() or ql in p["cat"].lower()]
    if cat:
        items = [p for p in items if p["cat"] == cat]

    z = get_zone(zone_id) if zone_id else None
    enriched: list[ProductOut] = []
    for p in items:
        score = score_product_for_zone(p, z) if z else None
        enriched.append(ProductOut(**p, score=score))

    if sort == "price_desc":
        enriched.sort(key=lambda x: -x.price)
    elif sort == "price_asc":
        enriched.sort(key=lambda x: x.price)
    elif sort == "margin_desc":
        enriched.sort(key=lambda x: -x.margin)
    elif sort == "velocity_desc":
        enriched.sort(key=lambda x: -x.velocity)
    else:
        enriched.sort(key=lambda x: -(x.score or 0.0))

    return enriched

@router.get("/hotspots")
def get_hotspots():
    return HOTSPOTS

@router.get("/kpis")
def get_kpis():
    import random
    sales = float(f"{(5000 + random.random() * 3000):.0f}")
    ticket = float(f"{(12 + random.random() * 4):.2f}")
    return {
        "sales_today": sales,
        "avg_ticket": ticket,
        "total_skus": len(PRODUCTS),
        "active_zones": len(ZONES),
    }
