from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import SessionLocal
from schemas.auth import SendOTPRequest, VerifyOTPRequest
from services.otp_service import OTPService

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/send-otp")
async def send_otp(
    request: SendOTPRequest,
    db: Session = Depends(get_db)
):
    service = OTPService(db)
    return await service.send_otp(request.email)

@router.post("/verify-otp")
async def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    service = OTPService(db)
    return await service.verify_otp(request.email, request.otp)

