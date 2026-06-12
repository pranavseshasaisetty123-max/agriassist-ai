from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.core.config import settings
from app.api import auth, farmers, chat, soil, weather, disease, crop_recommendation, market_intelligence, yield_prediction, farm_planner

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set CORS origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(farmers.router, prefix=f"{settings.API_V1_STR}/farmers", tags=["farmers"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(soil.router, prefix=f"{settings.API_V1_STR}/soil", tags=["soil"])
app.include_router(weather.router, prefix=f"{settings.API_V1_STR}/weather", tags=["weather"])
app.include_router(disease.router, prefix=f"{settings.API_V1_STR}/disease", tags=["disease"])
app.include_router(crop_recommendation.router, prefix=f"{settings.API_V1_STR}/crop-recommendations", tags=["crop-recommendations"])
app.include_router(market_intelligence.router, prefix=f"{settings.API_V1_STR}/market-intelligence", tags=["market-intelligence"])
app.include_router(yield_prediction.router, prefix=f"{settings.API_V1_STR}/yield-predictions", tags=["yield-predictions"])
app.include_router(farm_planner.router, prefix=f"{settings.API_V1_STR}/farm-planner", tags=["farm-planner"])




@app.get("/")
def root_endpoint():
    """Service status health check."""
    return {"status": "healthy", "service": settings.PROJECT_NAME}
