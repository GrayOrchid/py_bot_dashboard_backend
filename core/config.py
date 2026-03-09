from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        env_file_encoding="utf-8",
    )

    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/locals.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    DISCORD_REDIRECT_URI: str = "http://localhost:8000/api/auth/discord/callback"
    DISCORD_AUTH_URL: str = "https://discord.com/api/oauth2/authorize"
    DISCORD_TOKEN_URL: str = "https://discord.com/api/oauth2/token"
    DISCORD_USER_URL: str = "https://discord.com/api/users/@me"

    MAIL_SERVER: str = "smtp.mail.ru"
    MAIL_PORT: int = 465
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str = ""
    MAIL_USE_TLS: bool = False
    MAIL_USE_SSL: bool = True

    MAIL_DEBUG: bool = False


settings = Settings()