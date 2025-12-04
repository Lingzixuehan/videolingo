from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON, Boolean, Text
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系：用户拥有多张卡片
    cards = []

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_id = Column(String, nullable=False, index=True)
    timestamp = Column(Float, nullable=True, index=True)
    tags = Column(String, nullable=True, index=True)
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False, index=True)  # 操作类型，如 'delete_user'
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 操作人ID
    target_user_id = Column(Integer, nullable=True)  # 被操作的用户ID
    reason = Column(Text, nullable=True)  # 操作理由
    details = Column(JSON, nullable=True)  # 额外详情（JSON格式）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

# 创建所有表
def create_tables():
    from database import engine
    Base.metadata.create_all(bind=engine)