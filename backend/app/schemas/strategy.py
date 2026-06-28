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
    contract_type: str   # CALL, PUT, MULTUP, MULTDOWN, DIGITODD, DIGITEVEN, DIGITOVER, DIGITUNDER
    duration: int = 1
    duration_unit: str = "t"  # t=tick, m=minute, h=hour
    multiplier: int = 0  # > 0 for MULTIPLIER mode
    barrier: int = 0  # digit 0-9 for DIGITOVER/DIGITUNDER; 0 = not used


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
    # New management fields
    mini_meta_enabled: bool = False
    mini_meta_target: float = 50.0
    mini_meta_max_entries: int = 0
    auto_reload_enabled: bool = False
    auto_reload_minutes: int = 30
    auto_reload_entries: int = 0
    limits_enabled: bool = False
    daily_loss_limit: float = 0
    daily_profit_target: float = 0
    session_loss_limit: float = 0
    consecutive_loss_limit: int = 0


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
