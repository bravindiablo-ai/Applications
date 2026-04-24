from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    content = Column(String, nullable=False)
    media_url = Column(String, nullable=True)
    message_type = Column(String, default="text")  # text, image, video, audio, file
    sent_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    is_burn_after_reading = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    reply_to_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
    group = relationship("Group", back_populates="messages")
    replies = relationship("Message", back_populates="parent")
    parent = relationship("Message", back_populates="replies", remote_side=[id])
    reactions = relationship("MessageReaction", back_populates="message")