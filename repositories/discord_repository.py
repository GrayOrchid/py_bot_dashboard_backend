from sqlalchemy.orm import Session
from models.linked_accounts import LinkedAccountModel
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status


class DiscordRepository:
    def __init__(self, db: Session):
        self.db = db

    def _get_existing_account_by_discord_id(self, discord_id: str) -> LinkedAccountModel | None:
        return self.db.query(LinkedAccountModel).filter_by(
            provider="discord",
            provider_id=discord_id
        ).first()

    def _get_user_discord_account(self, user_id: int) -> LinkedAccountModel | None:
        return self.db.query(LinkedAccountModel).filter_by(
            user_id=user_id,
            provider="discord"
        ).first()

    def link_account(self, user_id: int, full_data: dict) -> LinkedAccountModel:
        discord_user = full_data["user"]
        tokens = full_data["tokens"]
        discord_id = discord_user["id"]
        now = datetime.now(timezone.utc)

        existing = self._get_existing_account_by_discord_id(discord_id)
        if existing and existing.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Этот Discord уже привязан к другому аккаунту"
            )

        account = self._get_user_discord_account(user_id)

        avatar_hash = discord_user.get("avatar")
        avatar_ext = "gif" if avatar_hash and avatar_hash.startswith("a_") else "png"
        avatar_url = (
            f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar_hash}.{avatar_ext}?size=256"
            if avatar_hash else
            "https://cdn.discordapp.com/embed/avatars/0.png?size=256"
        )

        display_name = discord_user.get("global_name") or discord_user.get("username") or "Unknown"

        if account:
            account.display_name = display_name
            account.avatar_url = avatar_url
            account.last_used_at = now
            account.access_token = tokens.get("access_token")
            account.refresh_token = tokens.get("refresh_token")
            expires_in = tokens.get("expires_in", 0)
            account.expires_at = now + timedelta(seconds=expires_in) if expires_in else None
        else:
            account = LinkedAccountModel(
                user_id=user_id,
                provider="discord",
                provider_id=discord_id,
                display_name=display_name,
                avatar_url=avatar_url,
                last_used_at=now,
                access_token=tokens.get("access_token"),
                refresh_token=tokens.get("refresh_token"),
                expires_at=now + timedelta(seconds=tokens.get("expires_in", 0))
            )
            self.db.add(account)

        self.db.commit()
        self.db.refresh(account)
        return account