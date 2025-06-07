from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from .models import Direction

class TradeBase(BaseModel):
    symbol: str
    entry_date: datetime
    exit_date: datetime
    direction: Direction
    entry_price: Decimal
    exit_price: Decimal
    size: Decimal
    notes: Optional[str] = None

class TradeCreate(TradeBase):
    pass

class Trade(TradeBase):
    id: UUID
    user_id: UUID
    brokerage_account_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
