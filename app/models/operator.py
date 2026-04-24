import uuid
from sqlalchemy import String, DateTime, Float, JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database import Base

class Operator(Base):
    __tablename__ = "operators"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)
    api_key: Mapped[str] = mapped_column(String, unique=True, default=lambda: str(uuid.uuid4()))
    plan: Mapped[str] = mapped_column(String, default="starter")  # starter|business|enterprise
    is_active: Mapped[str] = mapped_column(String, default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class GameRound(Base):
    __tablename__ = "game_rounds"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    operator_id: Mapped[str] = mapped_column(String, ForeignKey("operators.id"))
    player_id: Mapped[str] = mapped_column(String)
    game_type: Mapped[str] = mapped_column(String)
    bet_amount: Mapped[float] = mapped_column(Float)
    win_amount: Mapped[float] = mapped_column(Float, default=0.0)
    outcome: Mapped[str] = mapped_column(String)  # win|loss|draw
    seed_hash: Mapped[str] = mapped_column(String)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Settlement(Base):
    __tablename__ = "settlements"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    operator_id: Mapped[str] = mapped_column(String, ForeignKey("operators.id"))
    period: Mapped[str] = mapped_column(String)  # 2025-01
    ggr: Mapped[float] = mapped_column(Float)
    fee: Mapped[float] = mapped_column(Float)
    net: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending|paid
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
