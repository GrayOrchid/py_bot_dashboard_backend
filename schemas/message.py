from pydantic import BaseModel

class MessageResponseSchema(BaseModel):
    msg: str