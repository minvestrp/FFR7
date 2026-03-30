from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import router
from app.database import engine, Base

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SmartSec — AI-Driven Gaming & Blockchain Infrastructure API",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION, "service": "SmartSec API"}
