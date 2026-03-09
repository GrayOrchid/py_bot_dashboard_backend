from sqlalchemy import  Integer, Column, DateTime,String,Boolean
from sqlalchemy.orm import  relationship
from core.database import Base
from datetime import datetime, timezone

class UserModel(Base):
    __tablename__ = "users"
    email = Column(String(255), unique=True, index=True, nullable=True)
    email_verified = Column(Boolean, default=False, nullable=False)
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