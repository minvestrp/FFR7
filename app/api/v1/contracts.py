from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.contract import Contract, Investigation
from app.schemas import ContractAnalyzeRequest, ContractResponse, ForensicsTraceRequest, ForensicsResponse
from app.core.security import decode_token, oauth2_scheme
import uuid, random

router = APIRouter(tags=["Security"])

def mock_analyze(contract_id: str):
    """Mock analysis — replace with real Slither integration"""
    pass

@router.post("/contracts/analyze", response_model=ContractResponse, status_code=202)
async def analyze_contract(
    data: ContractAnalyzeRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(token)
    contract = Contract(
        id=str(uuid.uuid4()),
        user_id=payload["sub"],
        address=data.address,
        source_code=data.source_code,
        name=data.name or data.address,
        chain=data.chain,
        status="analyzing",
        risk_score=round(random.uniform(0.1, 9.9), 2),
        vulnerabilities=[
            {"type": "reentrancy", "severity": "high", "line": 42},
            {"type": "access_control", "severity": "medium", "line": 87}
        ] if data.address else [],
        report={"summary": "Analysis in progress", "recommendations": []}
    )
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    return ContractResponse(
        id=contract.id,
        status=contract.status,
        risk_score=contract.risk_score,
        vulnerabilities=contract.vulnerabilities,
        created_at=contract.created_at
    )

@router.get("/contracts/{contract_id}/report")
async def get_report(
    contract_id: str,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Contract not found")
    return {
        "id": contract.id,
        "name": contract.name,
        "chain": contract.chain,
        "risk_score": contract.risk_score,
        "status": contract.status,
        "vulnerabilities": contract.vulnerabilities,
        "report": contract.report,
        "created_at": contract.created_at
    }

@router.post("/forensics/trace", response_model=ForensicsResponse, status_code=202)
async def trace_address(
    data: ForensicsTraceRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(token)
    inv = Investigation(
        id=str(uuid.uuid4()),
        user_id=payload["sub"],
        target_address=data.address,
        chain=data.chain,
        status="done",
        graph_data={
            "nodes": [
                {"id": data.address, "type": "target", "balance": "12.4 ETH"},
                {"id": "0xabc123", "type": "exchange", "label": "Binance"},
                {"id": "0xdef456", "type": "mixer", "label": "Suspicious"}
            ],
            "edges": [
                {"from": data.address, "to": "0xabc123", "value": "5.2 ETH"},
                {"from": "0xdef456", "to": data.address, "value": "3.1 ETH"}
            ]
        },
        findings=[
            {"type": "mixer_interaction", "severity": "high", "description": "Address interacted with known mixer"},
            {"type": "exchange_deposit", "severity": "low", "description": "Regular exchange activity detected"}
        ],
        risk_level="high"
    )
    db.add(inv)
    await db.commit()
    await db.refresh(inv)
    return ForensicsResponse(
        id=inv.id,
        target_address=inv.target_address,
        status=inv.status,
        graph_data=inv.graph_data,
        findings=inv.findings,
        risk_level=inv.risk_level
    )
