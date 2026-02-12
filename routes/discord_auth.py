import secrets
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from services import UserService, TokenService
from services.discord_auth_service import DiscordAuthService
from sqlalchemy.orm import joinedload
from models.user import UserModel
from dependencies import get_current_user

router = APIRouter(tags=["Discord Auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/login")
async def login_discord():
    state = secrets.token_hex(16)
    auth_url = DiscordAuthService.build_discord_auth_url(state)

    response = RedirectResponse(auth_url)

    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        max_age=300,
        samesite="lax",
        secure=False,
        path="/"
    )
    return {"url": auth_url}

@router.get("/callback")
async def discord_callback(code: str, db: Session = Depends(get_db)):
    discord_data = await DiscordAuthService.authenticate_via_discord(code)
    user_service = UserService(db)
    user = await user_service.authenticate_discord_user(discord_data)

    access_token = TokenService.create_access_token(data={"sub": str(user.id)})
    frontend_url = f"http://localhost:5173/auth-success?token={access_token}"
    print(f"Redirecting to: {frontend_url}")
    return RedirectResponse(url=frontend_url)

@router.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).options(joinedload(UserModel.linked_accounts)).all()
    return users

