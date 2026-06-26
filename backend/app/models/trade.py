"""
ZeeK.Web — Trade Model
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, func
from app.core.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    page_id = Column(String(50))
    setup_name = Column(String(100))

    contract_id = Column(String(100), unique=True, index=True)
    symbol = Column(String(20))
    contract_type = Column(String(20))
    stake = Column(Float)
    payout = Column(Float, nullable=True)
    profit = Column(Float, nullable=True)

    status = Column(String(20), default="pending")
    entry_tick = Column(Float)
    exit_tick = Column(Float, nullable=True)
    entry_epoch = Column(Integer)
    exit_epoch = Column(Integer, nullable=True)

    strategy_snapshot = Column(Text)

    created_at = Column(DateTime, default=func.now())
