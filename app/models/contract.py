import uuid
from sqlalchemy import String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database import Base

class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    address: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    source_code: Mapped[str] = mapped_column(String, nullable=True)
    chain: Mapped[str] = mapped_column(String, default="ethereum")
    status: Mapped[str] = mapped_column(String, default="pending")  # pending|analyzing|done|failed
    risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    vulnerabilities: Mapped[dict] = mapped_column(JSON, default=list)
    report: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    target_address: Mapped[str] = mapped_column(String)
    chain: Mapped[str] = mapped_column(String, default="ethereum")
    status: Mapped[str] = mapped_column(String, default="pending")
    graph_data: Mapped[dict] = mapped_column(JSON, default=dict)
    findings: Mapped[dict] = mapped_column(JSON, default=list)
    risk_level: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
