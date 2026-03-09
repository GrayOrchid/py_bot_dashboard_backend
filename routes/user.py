from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Annotated

from core.database import SessionLocal
from dependencies import get_current_user
from models.user import UserModel
from schemas.user import UserPublic

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[UserPublic])
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users

@router.get("/me", response_model=UserPublic)
async def get_me(current_user: Annotated[UserModel, Depends(get_current_user)]):
    return current_user

@router.get("/", response_model=List[UserPublic])
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users