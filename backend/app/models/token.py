"""
ZeeK.Web — Deriv Token Model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from app.core.database import Base


class DerivToken(Base):
    __tablename__ = "deriv_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    token_encrypted = Column(Text, nullable=False)
    label = Column(String(100), default="")
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
