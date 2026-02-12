import jwt
import os
from datetime import datetime, timedelta, timezone

class TokenService:
    def create_access_token(data: dict):
        secret_key = os.getenv("JWT_SECRET_KEY")
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

        if not secret_key:
            raise ValueError("FATAL: JWT_SECRET_KEY is not set in environment!")

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, secret_key, algorithm=algorithm)

    def decode_access_token(token: str):
        try:
            secret_key = os.getenv("JWT_SECRET_KEY")
            algorithm = os.getenv("JWT_ALGORITHM", "HS256")

            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None