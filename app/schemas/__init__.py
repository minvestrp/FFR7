from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str

class ContractAnalyzeRequest(BaseModel):
    address: Optional[str] = None
    source_code: Optional[str] = None
    name: Optional[str] = None
    chain: str = "ethereum"

class ContractResponse(BaseModel):
    id: str
    status: str
    risk_score: Optional[float]
    vulnerabilities: list
    created_at: datetime

class ForensicsTraceRequest(BaseModel):
    address: str
    chain: str = "ethereum"
    depth: int = 2

class ForensicsResponse(BaseModel):
    id: str
    target_address: str
    status: str
    graph_data: dict
    findings: list
    risk_level: Optional[str]

class BetRequest(BaseModel):
    player_id: str
    game_type: str
    bet_amount: float
    operator_api_key: str
    metadata: dict = {}

class BetResponse(BaseModel):
    round_id: str
    outcome: str
    win_amount: float
    seed_hash: str

class OperatorOverview(BaseModel):
    ggr: float
    arpu: float
    retention_rate: float
    active_players: int
    total_rounds: int
    period: str
