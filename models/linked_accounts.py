from sqlalchemy import String, Integer, Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import  relationship
from core.database import Base

class LinkedAccountModel(Base):
    __tablename__ = "linked_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    provider = Column(String(50), nullable=False, index=True)
    provider_id = Column(String(100), nullable=False, index=True)
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    discriminator = Column(String(10), nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    access_token = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    user = relationship("UserModel", back_populates="linked_accounts")
    expires_at = Column(DateTime, nullable=True)
    __table_args__ = (
        UniqueConstraint('provider', 'provider_id', name='uq_provider_account'),
    )