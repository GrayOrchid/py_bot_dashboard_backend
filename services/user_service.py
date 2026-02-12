from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from repositories import UserRepository
from schemas import UserSchema
from services.token_service import TokenService

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    async def authenticate_discord_user(self, discord_data: dict) -> UserSchema:
        user_model = self.repository.sync_discord_user(discord_data)
        return UserSchema.model_validate(user_model)

    async def get_user_from_token(self, token: str):
        payload = TokenService.decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Payload error")

        user = self.repository.get_user_with_accounts(int(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user