from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs

Base = declarative_base()

class User(Base, AsyncAttrs):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    threshold = Column(Float, default=5.0)  # percentage
    notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    monitored_coins = relationship("MonitoredCoin", back_populates="user", cascade="all, delete-orphan")

class MonitoredCoin(Base, AsyncAttrs):
    __tablename__ = "monitored_coins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    coin_id = Column(String, nullable=False)   # CoinGecko id e.g. "bitcoin"
    symbol = Column(String, nullable=False)    # e.g. "BTC"
    last_price = Column(Float, nullable=True)
    last_updated = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "coin_id", name="uix_user_coin"),
    )

    user = relationship("User", back_populates="monitored_coins")