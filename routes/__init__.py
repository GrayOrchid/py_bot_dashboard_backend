from fastapi import APIRouter
from .discord_auth import router as discord_router
from .user import router as user_router
from .auth import router as auth_router

main_api_router = APIRouter()

main_api_router.include_router(discord_router, prefix="/auth/discord", tags=["Discord Auth"])
main_api_router.include_router(user_router, prefix="/users", tags=["Users"])
main_api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])

