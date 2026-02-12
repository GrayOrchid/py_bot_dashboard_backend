

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from sqlalchemy.orm import joinedload
from models.user import UserModel
from dependencies import get_current_user

router = APIRouter(tags=["Users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).options(joinedload(UserModel.linked_accounts)).all()
    return users

@router.get("/me")
async def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user