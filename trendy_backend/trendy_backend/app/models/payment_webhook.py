from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class WebhookEvent(Base):
    __tablename__ = 'webhook_event'

    id = Column(String, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
