"""
ZeeK.Web — Setup Model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from app.core.database import Base


class Setup(Base):
    __tablename__ = "setups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100))
    description = Column(String(500), default="")
    is_builtin = Column(Boolean, default=False)

    pages_data = Column(Text)  # JSON serialized pages
    management_data = Column(Text)  # JSON serialized management config

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
