from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from app.db.base import Base

class RewardTransaction(Base):
    __tablename__ = "reward_transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True, nullable=False)
    points = Column(Integer, nullable=False)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    transaction_metadata = Column(String, nullable=True)

class RewardBalance(Base):
    __tablename__ = "reward_balances"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    points = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
