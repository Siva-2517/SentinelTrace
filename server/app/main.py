from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.session import engine
from app.models.db_models import Base
from app.api.v1.agents import router as agents_router
from app.api.v1.baselines import router as baselines_router
from app.api.v1.scoring import router as scoring_router
from app.api.v1.eval import router as eval_router
from app.api.v1.dashboard import router as dashboard_router
from app.core.logging_config import setup_logging, logger

# Initialize structured logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Setup
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")


# Mount Routers
app.include_router(agents_router, prefix=settings.API_V1_STR)
app.include_router(baselines_router, prefix=settings.API_V1_STR)
app.include_router(scoring_router, prefix=settings.API_V1_STR)
app.include_router(eval_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe."""
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": settings.VERSION}


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe."""
    return {"status": "ready", "llm_provider": settings.LLM_PROVIDER}


@app.get("/", tags=["Health"])
async def root():
    return {"message": "Sentinel Trace Backend is running"}