from models.linked_accounts import LinkedAccountModel
from models.user import UserModel
from repositories.base_repository import BaseRepository
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload

class UserRepository(BaseRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_user_with_accounts(self, user_id: int):
        return self.db.query(UserModel).options(
            joinedload(UserModel.linked_accounts)
        ).filter(UserModel.id == user_id).first()

    def sync_discord_user(self, discord_data: dict) -> UserModel:
        d_id = discord_data["id"]
        now = datetime.now(timezone.utc)

        avatar_hash = discord_data.get('avatar')
        avatar_url = f"https://cdn.discordapp.com/avatars/{d_id}/{avatar_hash}.png" if avatar_hash else None

        account = self.db.query(LinkedAccountModel).filter_by(provider="discord", provider_id=d_id).first()

        if not account:
            user = UserModel(created_at=now)
            self.db.add(user)
            self.db.flush()
            account = LinkedAccountModel(user_id=user.id, provider="discord", provider_id=d_id)
            self.db.add(account)

        account.display_name = discord_data.get("global_name") or discord_data.get("username")
        account.avatar_url = avatar_url
        account.last_used_at = now

        account.discriminator = discord_data.get("discriminator", "0")

        self.db.commit()
        self.db.refresh(account.user)
        return account.user

