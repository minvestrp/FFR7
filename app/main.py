from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import router
from app.database import engine, Base
import asyncio, json, random, time

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SmartSec — AI-Driven Gaming & Blockchain Infrastructure API",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# ── WebSocket connections ──
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

manager = ConnectionManager()

@app.websocket("/ws/crash")
async def crash_ws(websocket: WebSocket):
    """Real-time crash game WebSocket"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg  = json.loads(data)
            # Echo back with server timestamp
            await websocket.send_json({"type": "ack", "ts": time.time(), **msg})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/stats")
async def stats_ws(websocket: WebSocket):
    """Real-time platform stats"""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.send_json({
                "type": "stats",
                "active_players": random.randint(1800, 2200),
                "rounds_today": random.randint(47000, 50000),
                "wagered_today": round(random.uniform(1100000, 1400000), 2),
                "ts": time.time()
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "service": "SmartSec API",
        "features": ["smart-contract-audit", "blockchain-forensics", "gaming-api", "websockets"]
    }

@app.get("/")
async def root():
    return {"message": "SmartSec API", "docs": "/docs", "version": settings.APP_VERSION}
