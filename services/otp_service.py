import secrets
from typing import Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from core import redis_client, settings
from repositories.user_repository import UserRepository
from schemas.user import UserSchema
from services.token_service import TokenService
from templates.mail_templates import OTP_TEXT_TEMPLATE

class OTPService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)
        self.redis = redis_client

    async def _send_email(self, to_email: str, subject: str, body: str) -> None:
        message = MIMEMultipart()
        message["From"] = settings.MAIL_FROM or settings.MAIL_USERNAME
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain", "utf-8"))

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.MAIL_SERVER,
                port=settings.MAIL_PORT,
                username=settings.MAIL_USERNAME,
                password=settings.MAIL_PASSWORD,
                use_tls=settings.MAIL_USE_TLS,
                validate_certs=True,
            )
            print(f"[MAIL] Отправлено на {to_email}")
        except Exception as e:
            print(f"[MAIL ERROR] {to_email}: {type(e).__name__}: {e}")


    async def send_otp(self, email: str) -> Dict[str, str]:
        attempts_key = f"otp_attempts:{email}"
        attempts = await self.redis.incr(attempts_key)

        if attempts == 1:
            await self.redis.expire(attempts_key, 300)

        if attempts > 3:
            raise HTTPException(
                status_code=429,
                detail="Слишком много запросов. Подождите 5 минут."
            )

        otp = f"{secrets.randbelow(1000000):06d}"
        key = f"otp:email:{email}"
        await self.redis.setex(key, 300, otp)

        subject = "Код подтверждения для входа"
        body = OTP_TEXT_TEMPLATE.format(
            otp=otp,
            valid_minutes=5
        )

        await self._send_email(email, subject, body)

        return {"message": "Код отправлен на вашу почту"}

    async def verify_otp(self, email: str, otp: str) -> Dict[str, Any]:
        """Проверка OTP и выдача токена"""
        fail_key = f"otp_fail:{email}"
        fails = await self.redis.get(fail_key)
        fails = int(fails) if fails else 0

        if fails >= 5:
            raise HTTPException(
                status_code=429,
                detail="Слишком много неудачных попыток. Подождите 15 минут"
            )

        key = f"otp:email:{email}"
        stored_otp = await self.redis.get(key)

        if not stored_otp:
            raise HTTPException(
                status_code=400,
                detail="Код истёк или не существует"
            )

        if stored_otp != otp:
            await self.redis.incr(fail_key)
            await self.redis.expire(fail_key, 900)  # 15 минут
            raise HTTPException(status_code=400, detail="Неверный код")

        await self.redis.delete(key)
        await self.redis.delete(fail_key)

        user = self.repository.get_user_by_email(email)
        if not user:
            user = self.repository.create_user(email)
        elif not user.email_verified:
            self.repository.verify_user_email(user)

        token = TokenService.create_access_token({
            "sub": str(user.id),
            "email": user.email
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": UserSchema.model_validate(user)
        }