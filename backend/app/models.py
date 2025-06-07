from sqlalchemy import Column, DateTime, Enum, Numeric, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum
import uuid

Base = declarative_base()

class Direction(enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class Trade(Base):
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    brokerage_account_id = Column(UUID(as_uuid=True), nullable=True)
    symbol = Column(String, nullable=False)
    entry_date = Column(DateTime(timezone=True), nullable=False)
    exit_date = Column(DateTime(timezone=True), nullable=False)
    direction = Column(Enum(Direction), nullable=False)
    entry_price = Column(Numeric(10,2), nullable=False)
    exit_price = Column(Numeric(10,2), nullable=False)
    size = Column(Numeric(10,2), nullable=False)
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
