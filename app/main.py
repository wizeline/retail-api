from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, catalog, zones

app = FastAPI(
    title="retAIl · Planogram & Zone API",
    version="1.1.0",
    contact={"name": "retAIl API"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(catalog.router, prefix="", tags=["catalog"])
app.include_router(zones.router, prefix="/zones", tags=["zones"])
