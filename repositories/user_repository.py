from sqlalchemy.orm import Session, joinedload
from models.user import UserModel
from datetime import datetime, timezone

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_with_accounts(self, user_id: int):
        return self.db.query(UserModel).options(
            joinedload(UserModel.linked_accounts)
        ).filter(UserModel.id == user_id).first()

    def get_user_by_email(self, email: str) -> UserModel | None:
        return self.db.query(UserModel).filter_by(email=email).first()

    def create_user(self, email: str) -> UserModel:
        now = datetime.now(timezone.utc)
        user = UserModel(email=email, email_verified=True, created_at=now)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def verify_user_email(self, user: UserModel):
        user.email_verified = True
        self.db.commit()
        self.db.refresh(user)

