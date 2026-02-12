from typing import List
from pydantic import BaseModel
from datetime import datetime
from .linked_account import LinkedAccountSchema

class UserSchema(BaseModel):
    id: int
    created_at: datetime
    linked_accounts: List[LinkedAccountSchema] = []

    class Config:
        from_attributes = True