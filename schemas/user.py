from typing import List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .linked_account import LinkedAccountPublic

class UserBase(BaseModel):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    email: str = None
    email_verified: bool = False

class UserPublic(UserBase):
    linked_accounts: List[LinkedAccountPublic] = []

UserSchema = UserPublic