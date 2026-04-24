from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="admin")
