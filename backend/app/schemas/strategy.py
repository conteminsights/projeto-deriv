"""
ZeeK.Web — Strategy Pydantic Schemas

Data models for strategy configuration, rules, and pages.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TriggerConditionSchema(BaseModel):
    indicator: str  # price, sma, ema, rsi, macd, bb
    operator: str   # >, <, >=, <=, ==, cross_above, cross_below
    value: float
    timeframe: int = 14


class RuleSchema(BaseModel):
    condition: TriggerConditionSchema
    contract_type: str   # CALL, PUT
    duration: int = 1
    duration_unit: str = "t"  # t=tick, m=minute, h=hour


class PageConfigSchema(BaseModel):
    name: str = "Página 1"
    market: str = "R_100"
    mode: str = "CALL_PUT"
    rules: List[RuleSchema] = []


class ManagementConfigSchema(BaseModel):
    initial_stake: float = 2.0
    martingale_enabled: bool = False
    martingale_multiplier: float = 2.0
    martingale_max_steps: int = 5
    multiplier_enabled: bool = False
    multiplier_value: float = 2.0
    defense_mode: str = "none"  # none, barrier, soros
    profit_target: Optional[float] = None
    loss_limit: Optional[float] = None


class StrategyCreate(BaseModel):
    name: str
    description: str = ""
    pages: List[PageConfigSchema] = []
    management: ManagementConfigSchema = ManagementConfigSchema()


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    pages: Optional[List[PageConfigSchema]] = None
    management: Optional[ManagementConfigSchema] = None


class StrategyResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: str
    is_builtin: bool
    pages: List[PageConfigSchema] = []
    management: ManagementConfigSchema = ManagementConfigSchema()
    created_at: str
    updated_at: Optional[str] = None
