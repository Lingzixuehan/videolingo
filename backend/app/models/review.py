# app/models/review.py
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, SmallInteger
from sqlalchemy.orm import relationship

from app.db.session import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    card_id = Column(
        Integer, ForeignKey("cards.id", ondelete="CASCADE"), index=True, nullable=False
    )

    rating = Column(SmallInteger, nullable=False)  # 0=Again,1=Hard,2=Good,3=Easy
    sched_before = Column(JSON, nullable=True)  # {interval,ease_factor,reps,lapses,due_at...}
    sched_after = Column(JSON, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    card = relationship("Card", back_populates="reviews")
