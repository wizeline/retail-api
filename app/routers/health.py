from datetime import datetime
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}
