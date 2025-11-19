# app/models/card.py
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    deck = Column(String(100), index=True, nullable=True)

    # 基础内容
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)

    # 可扩展字段：标签、例句、语音、来源等
    tags = Column(JSON, nullable=True)  # list[str]
    extras = Column(JSON, nullable=True)  # dict

    # SRS 调度字段（Anki 风格）
    state = Column(String(20), default="new")  # new/learning/review/suspended
    due_at = Column(DateTime, nullable=True)  # 下次到期时间（UTC）
    interval = Column(Integer, default=0)  # 间隔（天）
    ease_factor = Column(Float, default=2.5)  # 易度
    reps = Column(Integer, default=0)  # 总复习次数
    lapses = Column(Integer, default=0)  # 失忆次数

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="cards")
    reviews = relationship("Review", back_populates="card", cascade="all, delete-orphan")
