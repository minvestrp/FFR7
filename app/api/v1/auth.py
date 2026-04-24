from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.operator import Operator
from app.core.security import verify_password, hash_password, create_access_token
from app.schemas import UserRegister, UserLogin, TokenResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid, secrets, string

router = APIRouter(prefix="/auth", tags=["Authentication"])


def gen_api_key(prefix: str = "ss") -> str:
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(32))
    return f"{prefix}_{token}"


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    company_name: Optional[str] = None


class SignupResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    operator_id: str
    api_key: str


@router.post("/signup", response_model=SignupResponse, status_code=201)
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    """Register + auto-create operator + generate API key"""
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password)
    )
    db.add(user)
    await db.flush()

    operator = Operator(
        id=str(uuid.uuid4()),
        user_id=user.id,
        name=data.company_name or f"{data.username}'s Platform",
        api_key=gen_api_key("ss"),
        plan="starter"
    )
    db.add(operator)
    await db.commit()
    await db.refresh(user)
    await db.refresh(operator)

    token = create_access_token({"sub": user.id, "email": user.email, "operator_id": operator.id})
    return SignupResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        operator_id=operator.id,
        api_key=operator.api_key
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email})
    return TokenResponse(access_token=token, user_id=user.id, username=user.username)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Fetch operator if exists
    op_result = await db.execute(select(Operator).where(Operator.user_id == user.id))
    operator = op_result.scalar_one_or_none()

    token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "operator_id": operator.id if operator else None
    })
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username
    )


@router.post("/demo-login")
async def demo_login(db: AsyncSession = Depends(get_db)):
    """Auto-login as demo user — creates if not exists"""
    DEMO_EMAIL = "demo@smartsec.io"
    DEMO_PASS = "demo_smartsec_2025"

    result = await db.execute(select(User).where(User.email == DEMO_EMAIL))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email=DEMO_EMAIL,
            username="demo_operator",
            hashed_password=hash_password(DEMO_PASS)
        )
        db.add(user)
        await db.flush()

    op_result = await db.execute(select(Operator).where(Operator.user_id == user.id))
    operator = op_result.scalar_one_or_none()

    if not operator:
        operator = Operator(
            id="demo",
            user_id=user.id,
            name="Demo Platform",
            api_key="ss_demo_key_readonly",
            plan="starter"
        )
        db.add(operator)

    await db.commit()

    token = create_access_token({
        "sub": user.id,
        "email": DEMO_EMAIL,
        "operator_id": "demo"
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "operator_id": "demo",
        "username": "demo_operator",
        "is_demo": True
    }
