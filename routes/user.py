from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
from models.user import UserModel
from dependencies import get_current_user
from schemas.user import UserPublic

router = APIRouter(tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users", response_model=List[UserPublic])
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users

@router.get("/me", response_model=UserPublic)
async def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user