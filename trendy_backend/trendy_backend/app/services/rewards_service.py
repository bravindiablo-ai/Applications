from datetime import datetime
from sqlalchemy.orm import Session
from app.models.reward import RewardTransaction, RewardBalance
from typing import Optional, List, Dict, Any


class RewardService:
    """Service for managing user rewards and points."""

    def __init__(self):
        pass

    async def get_promoted_content(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get promoted content for rewards integration."""
        # Placeholder implementation - return empty list for now
        return []

    def record_transaction(self, db: Session, user_id: str, points: int, reason: Optional[str] = None, metadata: Optional[dict] = None, idempotency_key: Optional[str] = None) -> RewardTransaction:
        """Record a transaction and update user balance. Idempotent if idempotency_key provided (best-effort)."""
        return record_transaction(db, user_id, points, reason, metadata, idempotency_key)

    def credit_points(self, db: Session, user_id: str, points: int, reason: str = None, metadata: dict = None, idempotency_key: Optional[str] = None):
        return credit_points(db, user_id, points, reason, metadata, idempotency_key)

    def get_balance(self, db: Session, user_id: str):
        return get_balance(db, user_id)

    def get_transactions(self, db: Session, user_id: str, limit: int = 50) -> List[RewardTransaction]:
        return get_transactions(db, user_id, limit)

    def withdraw_points(self, db: Session, user_id: str, points: int, destination: str) -> dict:
        return withdraw_points(db, user_id, points, destination)


def _get_or_create_balance(db: Session, user_id: str) -> RewardBalance:
    rb = db.query(RewardBalance).filter(RewardBalance.user_id == str(user_id)).first()
    if not rb:
        rb = RewardBalance(user_id=str(user_id), points=0)
        db.add(rb)
        db.flush()
    return rb


def record_transaction(db: Session, user_id: str, points: int, reason: Optional[str] = None, metadata: Optional[dict] = None, idempotency_key: Optional[str] = None) -> RewardTransaction:
    """Record a transaction and update user balance. Idempotent if idempotency_key provided (best-effort)."""
    # naive idempotency: check metadata for key
    if idempotency_key:
        existing = db.query(RewardTransaction).filter(RewardTransaction.transaction_metadata.contains(idempotency_key)).first()
        if existing:
            return existing

    rb = _get_or_create_balance(db, user_id)
    rb.points = (rb.points or 0) + int(points)
    rb.updated_at = datetime.utcnow()
    tx = RewardTransaction(user_id=str(user_id), points=int(points), reason=reason or "credit", created_at=datetime.utcnow(), transaction_metadata=str(metadata or {"idempotency_key": idempotency_key}))
    db.add(tx)
    db.commit()
    db.refresh(rb)
    db.refresh(tx)
    return tx


def credit_points(db: Session, user_id: str, points: int, reason: str = None, metadata: dict = None, idempotency_key: Optional[str] = None):
    tx = record_transaction(db, user_id, points, reason=reason, metadata=metadata, idempotency_key=idempotency_key)
    return {"user_id": tx.user_id, "points": tx.points, "tx_id": tx.id}


def get_balance(db: Session, user_id: str):
    rb = db.query(RewardBalance).filter(RewardBalance.user_id == str(user_id)).first()
    return {"user_id": user_id, "points": rb.points if rb else 0}


def get_transactions(db: Session, user_id: str, limit: int = 50) -> List[RewardTransaction]:
    return db.query(RewardTransaction).filter(RewardTransaction.user_id == str(user_id)).order_by(RewardTransaction.created_at.desc()).limit(limit).all()


def withdraw_points(db: Session, user_id: str, points: int, destination: str) -> dict:
    """Placeholder: create a withdraw transaction. Integrate with payout provider in production."""
    rb = _get_or_create_balance(db, user_id)
    if (rb.points or 0) < points:
        raise ValueError("Insufficient points")
    rb.points = rb.points - points
    rb.updated_at = datetime.utcnow()
    tx = RewardTransaction(user_id=str(user_id), points=-int(points), reason="withdraw", created_at=datetime.utcnow(), transaction_metadata=str({"destination": destination}))
    db.add(tx)
    db.commit()
    db.refresh(rb)
    return {"user_id": user_id, "points": rb.points, "withdraw_tx": tx.id}
