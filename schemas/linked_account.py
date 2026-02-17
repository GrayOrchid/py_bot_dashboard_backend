from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class LinkedAccountBase(BaseModel):
    id: int
    provider: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    last_used_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class LinkedAccountPublic(LinkedAccountBase):
    pass

class LinkedAccountInternal(LinkedAccountBase):
    user_id: int
    provider_id: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

LinkedAccountSchema = LinkedAccountPublic