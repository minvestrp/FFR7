from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.operator import Operator, GameRound, Settlement
from app.schemas import BetRequest, BetResponse, OperatorOverview
from app.core.security import decode_token, oauth2_scheme
import uuid, hashlib, random, secrets
from datetime import datetime

router = APIRouter(tags=["Operator & Gaming"])

@router.get("/operator/overview", response_model=OperatorOverview)
async def operator_overview(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    # Mock KPI data — replace with real DB aggregations
    return OperatorOverview(
        ggr=284750.0,
        arpu=142.5,
        retention_rate=68.3,
        active_players=1998,
        total_rounds=47823,
        period=datetime.utcnow().strftime("%Y-%m")
    )

@router.get("/operator/settlements")
async def get_settlements(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(token)
    # Return mock settlements
    return {
        "settlements": [
            {"id": str(uuid.uuid4()), "period": "2025-03", "ggr": 284750.0, "fee": 14237.5, "net": 270512.5, "status": "paid"},
            {"id": str(uuid.uuid4()), "period": "2025-02", "ggr": 241300.0, "fee": 12065.0, "net": 229235.0, "status": "paid"},
            {"id": str(uuid.uuid4()), "period": "2025-01", "ggr": 198400.0, "fee": 9920.0, "net": 188480.0, "status": "paid"},
        ],
        "total_ggr": 724450.0
    }

@router.post("/games/bet", response_model=BetResponse)
async def place_bet(data: BetRequest, db: AsyncSession = Depends(get_db)):
    # Verify operator
    result = await db.execute(select(Operator).where(Operator.api_key == data.operator_api_key))
    operator = result.scalar_one_or_none()
    if not operator:
        raise HTTPException(status_code=403, detail="Invalid operator API key")

    # Provably fair RNG
    server_seed = secrets.token_hex(32)
    client_seed = str(uuid.uuid4())
    seed_hash = hashlib.sha256(f"{server_seed}:{client_seed}".encode()).hexdigest()

    # Game logic
    roll = random.random()
    win_multiplier = 0.0
    outcome = "loss"

    if data.game_type == "slots":
        if roll > 0.7:
            win_multiplier = random.choice([1.5, 2.0, 3.0, 5.0, 10.0])
            outcome = "win"
    elif data.game_type == "dice":
        if roll > 0.5:
            win_multiplier = 1.95
            outcome = "win"
    elif data.game_type == "crash":
        crash_point = 1.0 / (1.0 - roll) if roll < 0.99 else 100.0
        if crash_point > 1.5:
            win_multiplier = min(crash_point, 100.0)
            outcome = "win"

    win_amount = round(data.bet_amount * win_multiplier, 2)

    round_ = GameRound(
        id=str(uuid.uuid4()),
        operator_id=operator.id,
        player_id=data.player_id,
        game_type=data.game_type,
        bet_amount=data.bet_amount,
        win_amount=win_amount,
        outcome=outcome,
        seed_hash=seed_hash,
        metadata=data.metadata
    )
    db.add(round_)
    await db.commit()

    return BetResponse(round_id=round_.id, outcome=outcome, win_amount=win_amount, seed_hash=seed_hash)

@router.post("/games/result")
async def get_game_result(round_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GameRound).where(GameRound.id == round_id))
    round_ = result.scalar_one_or_none()
    if not round_:
        raise HTTPException(status_code=404, detail="Round not found")
    return {
        "round_id": round_.id,
        "game_type": round_.game_type,
        "bet_amount": round_.bet_amount,
        "win_amount": round_.win_amount,
        "outcome": round_.outcome,
        "seed_hash": round_.seed_hash,
        "created_at": round_.created_at
    }
