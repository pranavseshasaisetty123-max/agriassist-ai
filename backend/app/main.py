from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, farmers, chat, soil, weather

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


@app.get("/")
def root_endpoint():
    """Service status health check."""
    return {"status": "healthy", "service": settings.PROJECT_NAME}
