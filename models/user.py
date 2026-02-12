from sqlalchemy import  Integer, Column, DateTime
from sqlalchemy.orm import  relationship
from database import Base
from datetime import datetime, timezone

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    linked_accounts = relationship("LinkedAccountModel", back_populates="user", cascade="all, delete-orphan")