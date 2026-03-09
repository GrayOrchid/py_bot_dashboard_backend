from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from core.database import SessionLocal
from services import UserService
from models.user import UserModel

oauth2_scheme = APIKeyHeader(name="Authorization", auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> UserModel:
    if not token:
        raise HTTPException(status_code=401, detail="Отсутствует заголовок Authorization")

    clean_token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token

    user_service = UserService(db)
    return await user_service.get_user_from_token(clean_token)