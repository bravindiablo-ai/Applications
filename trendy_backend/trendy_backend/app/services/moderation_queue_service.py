from sqlalchemy.orm import Session
from app.models.moderation import Report, ModerationQueue
from datetime import datetime


def report_item(db: Session, reporter_id: int, target_type: str, target_id: int, reason: str = None, metadata: dict = None):
    rep = Report(reporter_id=reporter_id, target_type=target_type, target_id=target_id, reason=reason, metadata=metadata or {})
    db.add(rep)
    # enqueue
    mq = ModerationQueue(item_type=target_type, item_id=target_id, reason=reason)
    db.add(mq)
    db.commit()
    db.refresh(rep)
    db.refresh(mq)
    return rep


def get_pending_queue(db: Session, limit: int = 50):
    return db.query(ModerationQueue).filter(ModerationQueue.status == 'pending').order_by(ModerationQueue.created_at.desc()).limit(limit).all()


def resolve_queue_item(db: Session, queue_id: int, admin_id: int, resolution: dict):
    q = db.query(ModerationQueue).filter(ModerationQueue.id == queue_id).first()
    if not q:
        return None
    q.status = 'reviewed'
    q.admin_id = admin_id
    q.resolution = resolution
    q.updated_at = datetime.utcnow()
    db.add(q)
    db.commit()
    db.refresh(q)
    return q
