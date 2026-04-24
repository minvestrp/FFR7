from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.operator import Operator
from app.core.security import decode_token
from pydantic import BaseModel
from typing import Optional
import secrets, string, uuid
from datetime import datetime

router = APIRouter(prefix="/operator", tags=["Operator"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def gen_api_key(prefix: str = "ss") -> str:
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(32))
    return f"{prefix}_{token}"


async def get_current_operator_id(token: str = Security(oauth2_scheme)) -> Optional[str]:
    if not token:
        return None
    try:
        payload = decode_token(token)
        return payload.get("operator_id")
    except Exception:
        return None


@router.get("/overview")
async def overview(
    token: str = Security(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return {
        "ggr": 284750.0,
        "arpu": 142.5,
        "retention_rate": 68.3,
        "active_players": 1998,
        "total_rounds": 47823,
        "period": datetime.utcnow().strftime("%Y-%m"),
        "tps_peak": 20000,
        "latency_ms": 78,
        "uptime_pct": 99.97
    }


@router.get("/settlements")
async def settlements(
    token: str = Security(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return {
        "settlements": [
            {"id": str(uuid.uuid4()), "period": "2026-03", "ggr": 284750.0, "fee": 14237.5, "net": 270512.5, "status": "paid"},
            {"id": str(uuid.uuid4()), "period": "2026-02", "ggr": 241300.0, "fee": 12065.0, "net": 229235.0, "status": "paid"},
            {"id": str(uuid.uuid4()), "period": "2026-01", "ggr": 198400.0, "fee": 9920.0, "net": 188480.0, "status": "paid"},
        ],
        "total_ggr": 724450.0
    }


@router.post("/{operator_id}/keys")
async def generate_api_key(
    operator_id: str,
    token: str = Security(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Generate a new API key for an operator"""
    new_key = gen_api_key("ss")

    result = await db.execute(select(Operator).where(Operator.id == operator_id))
    operator = result.scalar_one_or_none()

    if operator:
        operator.api_key = new_key
        await db.commit()

    return {
        "api_key": new_key,
        "operator_id": operator_id,
        "created_at": datetime.utcnow().isoformat(),
        "prefix": new_key[:10] + "…",
        "note": "Store this key securely — it won't be shown again"
    }


@router.get("/{operator_id}/keys")
async def get_api_keys(
    operator_id: str,
    token: str = Security(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Operator).where(Operator.id == operator_id))
    operator = result.scalar_one_or_none()

    if not operator:
        # Return demo key if demo
        if operator_id == "demo":
            return {"keys": [{"prefix": "ss_demo_key…", "created_at": "2026-01-01T00:00:00", "plan": "starter"}]}
        raise HTTPException(status_code=404, detail="Operator not found")

    return {
        "keys": [{
            "prefix": operator.api_key[:14] + "…",
            "created_at": operator.created_at.isoformat() if operator.created_at else None,
            "plan": operator.plan
        }]
    }
