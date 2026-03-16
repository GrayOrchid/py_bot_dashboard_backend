import secrets
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.database import SessionLocal
from services import UserService, TokenService
from services.discord_auth_service import DiscordAuthService
from fastapi.templating import Jinja2Templates
from fastapi import Request


templates = Jinja2Templates(directory="templates")
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
    return response


@router.get("/callback")
async def discord_callback(request: Request, code: str, db: Session = Depends(get_db)):
    discord_data = await DiscordAuthService.authenticate_via_discord(code)
    user_service = UserService(db)
    user = await user_service.authenticate_discord_user(discord_data)

    discord_acc = next((acc for acc in user.linked_accounts if acc.provider == "discord"), None)
    user_name = discord_acc.display_name if discord_acc else "Unknown User"
    avatar = discord_acc.avatar_url if discord_acc else None

    access_token = TokenService.create_access_token(data={"sub": str(user.id)})

    return templates.TemplateResponse(
        "auth_success.html",
        {
            "request": request,
            "access_token": access_token,
            "user_name": user_name,
            "user_data": {
                "id": str(user.id),
                "avatar": avatar
            }
        }
    )

