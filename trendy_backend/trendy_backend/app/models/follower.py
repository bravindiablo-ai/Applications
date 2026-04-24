from sqlalchemy import Column, Integer, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

followers_table = Table(
    "followers",
    Base.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("follower_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("followed_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    extend_existing=True,
)

class Follower(Base):
    __table__ = followers_table

    follower_user = relationship("User", foreign_keys=[followers_table.c.follower_id], back_populates="following")
    following_user = relationship("User", foreign_keys=[followers_table.c.followed_id], back_populates="followers")
