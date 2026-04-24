from fastapi import APIRouter, Depends, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
from app.core.analyzer import analyze_solidity

router = APIRouter(prefix="/contracts", tags=["Security"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


class ContractAnalyzeRequest(BaseModel):
    source_code: str
    contract_name: Optional[str] = "Contract"
    chain: Optional[str] = "ethereum"


@router.post("/analyze")
async def analyze_contract(
    data: ContractAnalyzeRequest,
    token: str = Security(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    result = analyze_solidity(data.source_code, data.contract_name or "Contract")
    contract_id = str(uuid.uuid4())
    return {
        "id": contract_id,
        "status": "done",
        "contract_name": data.contract_name,
        "chain": data.chain,
        "risk_score": result["risk_score"],
        "vulnerabilities": result["vulnerabilities"],
        "severity_counts": result["severity_counts"],
        "summary": result["summary"],
        "lines_analyzed": result["lines_analyzed"],
        "created_at": datetime.utcnow().isoformat()
    }


@router.get("/{contract_id}/report")
async def get_report(
    contract_id: str,
    token: str = Security(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return {
        "id": contract_id,
        "status": "done",
        "message": "Use POST /contracts/analyze to get a fresh analysis"
    }
