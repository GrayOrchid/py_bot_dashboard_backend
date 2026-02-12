from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LinkedAccountSchema(BaseModel):
    id: int
    user_id: int
    provider: str
    provider_id: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    discriminator: Optional[str] = None
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True