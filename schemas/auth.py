
from pydantic import BaseModel, EmailStr

class SendOTPRequest(BaseModel):
    email: EmailStr
    lang: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class LinkDiscordCallback(BaseModel):
    code: str
    state: str